from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Category, Transaction, User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.db.models import Count




class NewTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'category', 'type', 'description', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'type': forms.RadioSelect(choices=Transaction.CATEGORY_CHOICES),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(author=user)
        self.fields['date'].initial = timezone.now().date()

        # Set the default category to the one with the most items
        most_common_category = Category.objects.filter(author=user).annotate(num_transactions=Count('transaction')).order_by('-num_transactions').first()
        if most_common_category:
            self.fields['category'].initial = most_common_category



class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    
@login_required
def index(request):
    if request.method == "POST":
        transaction_form = NewTransactionForm(request.user, request.POST)
        category_form = NewCategoryForm(request.POST)

        if transaction_form.is_valid():
            new_transaction = transaction_form.save(commit=False)
            new_transaction.author = request.user
            new_transaction.save()
            return redirect("index")
    

        elif category_form.is_valid():
            new_category = category_form.save(commit=False)
            new_category.author = request.user
            new_category.save()
            return redirect("index")

    else:
        transaction_form = NewTransactionForm(request.user)
        category_form = NewCategoryForm()

    transactions = Transaction.objects.filter(author=request.user)

    return render(request, "budget_app/index.html", {
        "transactions": transactions,
        "transaction_form": transaction_form,
        "category_form": category_form,
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "budget_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return redirect("index")
        else:
            return render(request, "budget_app/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "budget_app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "budget_app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect("index")
    else:
        if request.user.is_authenticated:
            return redirect("index")
        else:
            return render(request, "budget_app/register.html")

