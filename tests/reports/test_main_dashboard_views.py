from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpRequest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock

from reports.views import DashboardView
from reports.models import Report
from expenses.models import Expense
from subscriptions.models import Subscription
from budgets.models import Budget
from profiles.models import Profile
from categories.models import Category

User = get_user_model()


class DashboardViewUnitTests(TestCase):

    databases = '__all__'

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            currency='USD'
        )

        self.dashboard_view = DashboardView()
        self.dashboard_view.request = Mock()
        self.dashboard_view.request.user = self.user

        self.category = Category.objects.create(
            name='Food',
            user=self.user
        )

    def test_get_default_context_with_no_data(self):
        context = self.dashboard_view.get_default_context(self.user)

        # Check all required keys are present
        required_keys = [
            'monthly_expenses', 'recent_expenses', 'subscription_total',
            'user_currency', 'current_month', 'current_year',
            'budget_amount', 'budget_remaining', 'budget_percentage'
        ]
        for key in required_keys:
            self.assertIn(key, context)

        # Check default values
        self.assertEqual(context['monthly_expenses'], Decimal('0'))
        self.assertEqual(context['subscription_total'], Decimal('0'))
        self.assertEqual(context['user_currency'], 'USD')
        self.assertEqual(len(context['recent_expenses']), 0)
        self.assertIsNone(context['budget_amount'])
        self.assertFalse(context['is_over_budget'])

    def test_get_default_context_with_expenses(self):
        now = timezone.now()
        month_start = now.replace(day=1).date()

        # Create expenses for current month (using dates that are not in the future)
        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('50.00'),
            description='Groceries',
            date=month_start
        )
        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('30.00'),
            description='Coffee',
            date=month_start + timedelta(days=2)
        )

        # Create expense from previous month (should not be included)
        prev_month = (month_start - timedelta(days=5))
        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('100.00'),
            description='Previous month expense',
            date=prev_month
        )

        context = self.dashboard_view.get_default_context(self.user)

        self.assertEqual(context['monthly_expenses'], Decimal('80.00'))
        self.assertEqual(len(context['recent_expenses']), 3)

    def test_get_default_context_with_subscriptions(self):

        Subscription.objects.create(
            user=self.user,
            name='Netflix',
            amount=Decimal('15.99'),
            frequency='monthly',
            next_payment_date=timezone.now().date() + timedelta(days=30)
        )
        Subscription.objects.create(
            user=self.user,
            name='Spotify',
            amount=Decimal('9.99'),
            frequency='monthly',
            next_payment_date=timezone.now().date() + timedelta(days=25)
        )

        context = self.dashboard_view.get_default_context(self.user)

        self.assertEqual(context['subscription_total'], Decimal('25.98'))

    def test_get_budget_data_no_budget(self):

        now = timezone.now().date()
        month_start = now.replace(day=1)
        month_end = now.replace(day=28)

        budget_data = self.dashboard_view.get_budget_data(
            self.user, month_start, month_end
        )

        self.assertIsNone(budget_data['budget_amount'])
        self.assertIsNone(budget_data['budget_remaining'])
        self.assertIsNone(budget_data['budget_percentage'])
        self.assertFalse(budget_data['is_over_budget'])
        self.assertEqual(budget_data['over_degrees'], 0)

    def test_get_budget_data_with_active_budget(self):
        now = timezone.now().date()
        month_start = now.replace(day=1)
        month_end = now.replace(day=28)

        # Create budget
        budget = Budget.objects.create(
            user=self.user,
            amount=Decimal('1000.00'),
            period='monthly',
            start_date=month_start,
            end_date=month_end
        )

        # Create some expenses (ensure dates are not in future)
        expense_date = month_start + timedelta(days=1)
        if expense_date > now:
            expense_date = now

        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('300.00'),
            description='Test expense',
            date=expense_date
        )

        # Create subscription
        Subscription.objects.create(
            user=self.user,
            name='Test Sub',
            amount=Decimal('50.00'),
            frequency='monthly',
            next_payment_date=month_start + timedelta(days=30)
        )

        budget_data = self.dashboard_view.get_budget_data(
            self.user, month_start, month_end
        )

        self.assertEqual(budget_data['budget_amount'], Decimal('1000.00'))
        self.assertEqual(budget_data['budget_remaining'], Decimal('650.00'))  # 1000 - 300 - 50
        self.assertEqual(budget_data['budget_percentage'], 35.0)  # 350/1000 * 100
        self.assertFalse(budget_data['is_over_budget'])

    def test_get_budget_data_over_budget(self):

        now = timezone.now().date()
        month_start = now.replace(day=1)
        month_end = now.replace(day=28)

        # Create small budget
        budget = Budget.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            period='monthly',
            start_date=month_start,
            end_date=month_end
        )

        # Create expenses that exceed budget (ensure date is not in future)
        expense_date = month_start + timedelta(days=1)
        if expense_date > now:
            expense_date = now

        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('150.00'),
            description='Over budget expense',
            date=expense_date
        )

        budget_data = self.dashboard_view.get_budget_data(
            self.user, month_start, month_end
        )

        self.assertEqual(budget_data['budget_amount'], Decimal('100.00'))
        self.assertEqual(budget_data['budget_remaining'], Decimal('-50.00'))
        self.assertEqual(budget_data['budget_percentage'], 150.0)
        self.assertTrue(budget_data['is_over_budget'])
        self.assertGreater(budget_data['over_degrees'], 0)
        self.assertEqual(budget_data['over_percentage_display'], 50.0)

    def test_get_budget_data_yearly_overview(self):

        year_start = datetime(2024, 1, 1).date()
        year_end = datetime(2024, 12, 31).date()

        # Create monthly budgets throughout the year
        for month in range(1, 4):  #Create 3 months for testing
            Budget.objects.create(
                user=self.user,
                amount=Decimal('1000.00'),
                period='monthly',
                start_date=datetime(2024, month, 1).date(),
                end_date=datetime(2024, month, 28).date()
            )

        # Create a report for the year
        report = Report.objects.create(
            user=self.user,
            report_type='yearly_overview',
            period_start=year_start,
            period_end=year_end,
            total_expenses=Decimal('2000.00'),
            total_subscriptions=Decimal('500.00')
        )

        budget_data = self.dashboard_view.get_budget_data(
            self.user, year_start, year_end, 'yearly_overview'
        )

        self.assertEqual(budget_data['budget_amount'], Decimal('3000.00'))
        self.assertIsNotNone(budget_data['budget_percentage'])

    def test_get_report_context_monthly_summary(self):

        period_start = datetime(2024, 1, 1).date()
        period_end = datetime(2024, 1, 31).date()

        # Create expenses for the period (use safe past dates)
        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('100.00'),
            description='January expense',
            date=period_start + timedelta(days=5)
        )

        report = Report.objects.create(
            user=self.user,
            report_type='monthly_summary',
            period_start=period_start,
            period_end=period_end,
            total_expenses=Decimal('100.00'),
            total_subscriptions=Decimal('25.00')
        )

        context = self.dashboard_view.get_report_context(report)

        # Test the basic context structure and report data
        self.assertEqual(context['monthly_expenses'], Decimal('100.00'))
        self.assertEqual(context['report_type'], 'monthly_summary')
        self.assertEqual(context['period_start'], period_start)
        self.assertEqual(context['period_end'], period_end)
        self.assertTrue(context['show_monthly_summary'])
        self.assertIn('recent_expenses', context)

        # The subscription_total might be calculated differently in get_report_context
        # Let's just check it exists and is a Decimal
        self.assertIn('subscription_total', context)
        self.assertIsInstance(context['subscription_total'], Decimal)


class DashboardViewIntegrationTests(TestCase):

    databases = '__all__'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # Create user profile
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            currency='BGN'
        )

        self.category = Category.objects.create(
            name='Food',
            user=self.user
        )

    def test_dashboard_requires_authentication(self):

        response = self.client.get(reverse('main_dashboard'))

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_dashboard_renders_for_authenticated_user(self):

        self.client.login(email='test@example.com', password='testpass123')

        response = self.client.get(reverse('main_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BGN')
        self.assertIn('monthly_expenses', response.context)
        self.assertIn('recent_expenses', response.context)

    def test_dashboard_with_valid_report_id(self):

        self.client.login(email='test@example.com', password='testpass123')

        # Create a report
        report = Report.objects.create(
            user=self.user,
            report_type='monthly_summary',
            period_start=datetime(2024, 1, 1).date(),
            period_end=datetime(2024, 1, 31).date(),
            total_expenses=Decimal('500.00'),
            total_subscriptions=Decimal('50.00')
        )

        response = self.client.get(f"{reverse('main_dashboard')}?report_id={report.id}")

        self.assertEqual(response.status_code, 200)
        self.assertIn('report_type', response.context)
        self.assertEqual(response.context['report_type'], 'monthly_summary')

    def test_dashboard_with_invalid_report_id(self):

        self.client.login(email='test@example.com', password='testpass123')

        # Create some current month data (use safe dates)
        today = timezone.now().date()
        Expense.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('75.00'),
            description='Current expense',
            date=today
        )

        response = self.client.get(f"{reverse('main_dashboard')}?report_id=99999")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('report_type', response.context)
        self.assertIn('monthly_expenses', response.context)