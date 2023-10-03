from .models import Category, Transaction, Circle, Goal, SubCategory
import csv
from datetime import datetime, timedelta
from django.utils import timezone


def reset_demo_user_data(user):
    # Delete existing data for the "demo-user"
    Transaction.objects.filter(author=user).delete()
    Category.objects.filter(circle__admin=user).delete()
    Circle.objects.filter(admin=user).delete()
    Goal.objects.filter(category__circle__admin=user).delete()
    SubCategory.objects.filter(category__circle__admin=user).delete()
    # Create the "Family" circle for the "demo-user"

    family_circle = Circle.objects.create(
        name="Family",
        admin=user,
        color='#33FF57',  # Specify a color from COLOR_CHOICES
        icon='👨‍👩‍👧',  # Specify an icon from ICON_CHOICES
    )

    family_circle.members.add(user)


    # Create two circles for the "demo-user"
    personal_circle = Circle.objects.create(
        name="Personal",
        admin=user,
        color='#FF5733',  # Specify the color
        icon='🏠',  # Specify the icon
    )

    personal_circle.members.add(user)


    # Create categories under the "Family" circle
    categories_data = [
        ('Housing', '🏠', '#FF5733'),                  # Home
        ('Transportation', '🚗', '#33FF57'),           # Car
        ('Groceries', '🍔', '#3366FF'),                    # Food
        ('Utilities', '💡', '#FFFF33'),               # Utilities
        ('Debt Payments', '💳', '#FFA07A'),           # Debt Payments
        ('Entertainment', '🎬', '#32CD32'),           # Entertainment
        ('Restaurant', '🎓', '#1E90FF'),               # Education
        ('Miscellaneous', '💇', '#FFD700'),           # Personal Care
        ('Pet', '💰', '#20B2AA'),                 # Savings
        ('Taxes', '💸', '#7B68EE'),                   # Taxes
        ('Furniture', '🧸', '#00FF7F'),               # Furniture
        ('Travel', '✈️', '#FF4500'),                 # Travel
        ("Jordan's Income", '💼', '#8A2BE2'),       # Employment Income
        ("Riley's Income", '💼', '#ADFF2F'),  # Self-Employment Income
        ('Investment Income', '💰', '#00CED1'),       # Investment Income
        ('Rental Income', '🏢', '#FF6347'),           # Rental Income
        ('Other Sources of Income', '🔀', '#FF5733'), # Other Sources of Income
    ]

    for category_data in categories_data:
        Category.objects.create(
            name=category_data[0],
            circle=family_circle,
            icon=category_data[1],
            color=category_data[2],
        )

    # Create categories under the "Personal" circle
    personal_categories_data = [
    ('Gifts', '🎁', '#FF4500'),          # Gifts
    ('Clothing', '👚', '#9932CC'),       # Clothing
    ('Hobby', '🎨', '#8A2BE2'),          # Hobby
    ('Healthcare', '🏥', '#FF6347'),     # Healthcare
    ('Treats', '🍬', '#FF5733'),         # Treats
    ('Party', '🎉', '#FF33FF'),          # Party
    ('Subscriptions', '🎉', '#FF33FF'),    # Subscriptions
    ('Personal Share of Income', '💰', '#20B2AA'),  # Personal Share of Income
]

    for category_data in personal_categories_data:
        Category.objects.create(
            name=category_data[0],
            circle=personal_circle,
            icon=category_data[1],
            color=category_data[2],
        )

    csv_file_path = 'budget_app/static/budget_app/demo_transactions2.csv'
    create_transactions_from_csv(csv_file_path, user)

def create_transactions_from_csv(csv_file_path, user):
    today = datetime.now().date()  # Get the current date

    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.DictReader(file, delimiter=';')
        for column in reader:
            transaction_type = column['type']
            category_name = column['category']
            sub_category_name = column.get('sub_category', None)
            
            # Parse the date from the CSV and calculate the relative date
            date_str = column['date_of_transaction']
            parsed_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            days_difference = (datetime(2024, 2, 25).date() - parsed_date).days
            relative_date = today - timedelta(days=days_difference)

            # Rest of your code remains the same
            description = column.get('description', '')
            comment = column.get('comment', '')
            recurrence = column['recurrence'].lower() == 'true'
            units_of_recurrence = column['units_of_recurrence']
            interval_of_recurrence = int(column['interval_of_recurrence'])
            recurrence_end_date = (
                datetime.strptime(column['recurrence_end_date'], '%d/%m/%Y').date()
                if column['recurrence_end_date']
                else None
            )
            amount = float(column['amount'])

            try:
                category = Category.objects.get(circle__members=user, name=category_name)
                sub_category = None
                if sub_category_name:
                    sub_category = category.subcategory_set.get(name=sub_category_name)

                Transaction.objects.create(
                    category=category,
                    sub_category=sub_category,
                    author=user,
                    type=transaction_type,
                    date_of_update=relative_date,
                    date_of_transaction=relative_date,
                    description=description,
                    comment=comment,
                    recurrence=recurrence,
                    units_of_recurrence=units_of_recurrence,
                    interval_of_recurrence=interval_of_recurrence,
                    recurrence_end_date=recurrence_end_date,
                    amount=amount,
                )
            except Category.DoesNotExist:
                print(f"Category '{category_name}' not found for user {user.username}. Skipping transaction.")