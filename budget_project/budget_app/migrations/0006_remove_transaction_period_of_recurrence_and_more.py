# Generated by Django 4.2.5 on 2023-10-02 19:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("budget_app", "0005_alter_transaction_comment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="period_of_recurrence",
        ),
        migrations.AddField(
            model_name="transaction",
            name="interval_of_recurrence",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="units_of_recurrence",
            field=models.CharField(
                blank=True,
                choices=[
                    ("days", "Days"),
                    ("weeks", "Weeks"),
                    ("months", "Months"),
                    ("years", "Years"),
                ],
                max_length=7,
                null=True,
            ),
        ),
    ]
