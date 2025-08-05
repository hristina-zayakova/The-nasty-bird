from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from decimal import Decimal

# Create your models here.

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., Groceries & Food, Transportation & Fuel, Entertainment & Dining)"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional description of what this category includes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is currently in use"
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for displaying categories"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
        unique_together = ['user', 'name']  # Prevent duplicate category names per user

    def clean(self):
        super().clean()

        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 2:
                raise ValidationError({'name': 'Category name must be at least 2 characters long'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    @property
    def slug(self):
        return slugify(self.name)
