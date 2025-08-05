from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from expenses.models import Expense
from budgets.models import Budget
from profiles.models import Profile
from categories.models import Category

User = get_user_model()


class UserAuthenticationTests(TestCase):

    databases = '__all__'

    def setUp(self):
        pass

    def test_user_registration_creates_profile(self):
        user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123'
        )

        profile = Profile.objects.create(
            user=user,
            first_name='New',
            last_name='User'
        )

        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(profile.currency, 'BGN')
        self.assertEqual(profile.full_name, 'New User')

        self.assertEqual(user.onboarding_step, 'signup')
        self.assertFalse(user.is_onboarding_complete)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_onboarding_flow(self):
        user = User.objects.create_user(
            email='onboarding@example.com',
            password='testpass123'
        )
        Profile.objects.create(user=user, first_name='Onboarding', last_name='User')

        self.assertEqual(user.onboarding_step, 'signup')
        self.assertFalse(user.is_onboarding_complete)

        next_step = user.get_next_onboarding_step()
        self.assertEqual(next_step, 'personal_info')

        user.onboarding_step = 'personal_info'
        user.save()

        next_step = user.get_next_onboarding_step()
        self.assertEqual(next_step, 'preferences')

        user.onboarding_step = 'preferences'
        user.save()

        next_step = user.get_next_onboarding_step()
        self.assertEqual(next_step, 'complete')

        user.onboarding_step = 'complete'
        user.save()

        self.assertTrue(user.is_onboarding_complete)
        self.assertIsNone(user.get_next_onboarding_step())

    def test_user_profile_update(self):
        user = User.objects.create_user(
            email='update@example.com',
            password='testpass123'
        )
        profile = Profile.objects.create(
            user=user,
            first_name='Original',
            last_name='Name',
            currency='BGN'
        )

        profile.first_name = 'Updated'
        profile.last_name = 'Profile'
        profile.currency = 'USD'
        profile.email_notifications = False
        profile.save()

        updated_profile = Profile.objects.get(user=user)

        self.assertEqual(updated_profile.first_name, 'Updated')
        self.assertEqual(updated_profile.last_name, 'Profile')
        self.assertEqual(updated_profile.currency, 'USD')
        self.assertEqual(updated_profile.full_name, 'Updated Profile')
        self.assertFalse(updated_profile.email_notifications)

    def test_user_profile_methods(self):
        user = User.objects.create_user(
            email='method@example.com',
            password='testpass123'
        )
        profile = Profile.objects.create(
            user=user,
            first_name='Method',
            last_name='Test',
            currency='EUR'
        )

        category = Category.objects.create(name='Testing', user=user)
        now = timezone.now()

        Expense.objects.create(
            user=user,
            category=category,
            amount=Decimal('150.00'),
            description='Test expense',
            date=now.date()
        )

        Budget.objects.create(
            user=user,
            amount=Decimal('500.00'),
            period='monthly',
            start_date=now.replace(day=1).date(),
            end_date=now.replace(day=28).date()
        )

        self.assertEqual(profile.full_name, 'Method Test')
        self.assertTrue(profile.has_expenses)
        self.assertEqual(profile.get_total_expenses_this_month(), Decimal('150.00'))

        current_budget = profile.get_current_monthly_budget()
        self.assertIsNotNone(current_budget)
        self.assertEqual(current_budget.amount, Decimal('500.00'))

        remaining = profile.get_remaining_budget()
        self.assertIsNotNone(remaining)
        self.assertFalse(profile.is_over_budget())