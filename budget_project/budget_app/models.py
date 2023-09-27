from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator  

class Category(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    CATEGORY_CHOICES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=CATEGORY_CHOICES, default='expense')
    description = models.CharField(max_length=255, blank=True)  
    comment = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} ({self.date}) - {self.description}"
