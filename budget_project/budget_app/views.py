from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Category, Transaction, User, Circle, Goal, SubCategory
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import timezone 
from django.db.models import Count
from .reset_demo_user import reset_demo_user_data

class NewTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['category', 'sub_category', 'type', 'date_of_transaction', 'description', 'comment', 'recurrence', 'units_of_recurrence', 'interval_of_recurrence', 'recurrence_end_date', 'amount']

    def __init__(self, user, *args, **kwargs):
        super(NewTransactionForm, self).__init__(*args, **kwargs)
        # Limit the category choices to those of the user's circles
        self.fields['category'].queryset = Category.objects.filter(circle__members=user)

        # Customize the display of the Category field choices
        self.fields['category'].label_from_instance = lambda obj: f"{obj.circle.name} - {obj.name}"


class NewCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'circle', 'icon', 'color']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the 'user' argument from kwargs
        super(NewCategoryForm, self).__init__(*args, **kwargs)
        
        if user:
            # Limit the circle choices to those that the user is a member of
            self.fields['circle'].queryset = Circle.objects.filter(members=user)

@login_required
def index(request):
    if request.method == "POST":
        transaction_form = NewTransactionForm(request.user, request.POST)
        category_form = NewCategoryForm(user=request.user, data=request.POST)  # Pass user=request.user

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
        category_form = NewCategoryForm(user=request.user)  # Pass user=request.user

    transactions = Transaction.objects.filter(author=request.user).order_by('-date_of_update')

    return render(request, "budget_app/index.html", {
        "transactions": transactions,
        "transaction_form": transaction_form,
        "category_form": category_form,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            demo_username = "user-demo"
            if username == demo_username:
                reset_demo_user_data(user)
                login(request, user)
                return redirect("index")
            else:
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
            # Create two circles for the "demo-user"
            personal_circle = Circle.objects.create(
                name="Personal",
                admin=user,
                color='#FF5733',  # Specify the color
                icon='🏠',  # Specify the icon
                )
            personal_circle.members.add(user)
            
            Category.objects.create(
            name='Miscellaneous',
            circle=personal_circle,
            icon='🍬',
            color='#FF33FF',
            )

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


