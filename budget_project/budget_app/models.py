from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def get_current_date():
    return timezone.now().date()


COLOR_CHOICES = [
    ('#FF5733', 'Red'),
    ('#33FF57', 'Green'),
    ('#3366FF', 'Blue'),
    ('#FFFF33', 'Yellow'),
    ('#FF33FF', 'Purple'),
    ('#FFA07A', 'Light Salmon'),
    ('#32CD32', 'Lime Green'),
    ('#1E90FF', 'Dodger Blue'),
    ('#FFD700', 'Gold'),
    ('#9932CC', 'Dark Orchid'),
    ('#20B2AA', 'Light Sea Green'),
    ('#FF69B4', 'Hot Pink'),
    ('#7B68EE', 'Medium Slate Blue'),
    ('#00FF7F', 'Spring Green'),
    ('#FF4500', 'Orange Red'),
    ('#8A2BE2', 'Blue Violet'),
    ('#ADFF2F', 'Green Yellow'),
    ('#00CED1', 'Dark Turquoise'),
    ('#FF6347', 'Tomato'),
]

ICON_CHOICES = [
    ('🏠', 'Housing'),           # Home
    ('🚗', 'Transportation'),    # Car
    ('🍔', 'Food'),              # Food
    ('💡', 'Utilities'),         # Utilities
    ('🏥', 'Healthcare'),        # Healthcare
    ('💳', 'Debt Payments'),     # Debt Payments
    ('🎬', 'Entertainment'),     # Entertainment
    ('🎓', 'Education'),         # Education
    ('💇', 'Personal Care'),     # Personal Care
    ('👚', 'Clothing'),          # Clothing
    ('💰', 'Savings'),           # Savings
    ('🎁', 'Gifts'),             # Gifts
    ('💸', 'Taxes'),             # Taxes
    ('🧸', 'Childcare'),         # Childcare
    ('✈️', 'Travel'),           # Travel
    ('💼', 'Employment Income'), # Employment Income
    ('💼', 'Self-Employment Income'),  # Self-Employment Income
    ('💰', 'Investment Income'),      # Investment Income
    ('🏢', 'Rental Income'),          # Rental Income
    ('🔀', 'Other Sources of Income'), # Other Sources of Income
]

class Circle(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_circles')
    members = models.ManyToManyField(User)
    icon = models.CharField(max_length=2, default='🏠')  # Default emoji for 'Housing'
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default=1)  # Use a CharField for color with a max length of 7

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, default=1)
    icon = models.CharField(max_length=2, default='🏠')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default=1)

    def __str__(self):
        return f"{self.name}"  # Display the circle name and category name
        # return f"{self.circle.name} - {self.name}"  # Display the circle name and category name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Transaction(models.Model):  
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    TRANSACTION_TYPE_CHOICES = [  
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, default='expense')  
    date_of_transaction = models.DateField(default=get_current_date)
    date_of_update = models.DateField(default=get_current_date)
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(99999999.99)  
        ]
    )
    description = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)
    recurrence = models.BooleanField(default=False)
    RECURRENCE_UNITS_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]
    units_of_recurrence = models.CharField(
        max_length=7,
        choices=RECURRENCE_UNITS_CHOICES,
        blank=True,
        null=True,
        default='months'  
    )
    interval_of_recurrence = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        default=1
    )
    recurrence_end_date = models.DateField(null=True, blank=True)

    def validate_recurrence_end_date(self):
        if self.recurrence_end_date and self.recurrence_end_date <= self.date_of_transaction:
            raise ValidationError("Recurrence end date must be after the date of transaction.")
    

    def __str__(self):
        return f"{self.date_of_transaction} - {self.category} - {self.description} - {self.author.username} - {self.amount}"

    def clean(self):
        self.validate_recurrence_end_date()

class Goal(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(99999999.99)
        ]
    )
    PERIOD_TYPE_CHOICES = [
        ('rolling', 'Rolling'),
        ('fixed', 'Fixed'),
    ]
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES)
    period = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.category} - {self.sub_category} - {self.amount}"


def create_personal_circle(user):
    # Create a "Personal" circle for the user
    personal_circle = Circle.objects.create(name="Personal", admin=user)
    
    # Create a default category linked to the "Personal" circle
    Category.objects.create(name="Default", circle=personal_circle)

# Override the User model to create a Personal circle and set it as the default category
User.add_to_class('personal_circle', models.OneToOneField(
    Circle, null=True, on_delete=models.SET_NULL, related_name='personal_owner'
))

def user_post_save(sender, instance, **kwargs):
    if not hasattr(instance, 'personal_circle'):
        create_personal_circle(instance)

models.signals.post_save.connect(user_post_save, sender=User)