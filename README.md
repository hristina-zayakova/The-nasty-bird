# Budgie — Personal Finance Manager

A Django-based personal finance application for tracking expenses, managing budgets, monitoring subscriptions, and generating financial reports.

---

## Features

### Expense Tracking
Log and categorize daily expenses with full CRUD support. Filter and view spending history across custom date ranges and categories.

### Budget Management
Create and manage budgets across different time periods. The dashboard provides real-time visualizations — including donut charts — to show how spending compares against defined budgets. Handles multiple active budgets per period.

### Subscription Monitoring
Track recurring subscriptions with automated cost calculations across billing cycles (monthly, yearly, etc.). Get a clear picture of fixed outgoings at a glance.

### Financial Reports
Generate summaries and breakdowns of financial activity over time. Reports aggregate data across expenses, budgets, and subscriptions to give a full financial overview.

### User Accounts & Profiles
Custom authentication using email (no username required). Each user has a personal profile and isolated financial data.

### Admin Interface
Extended Django admin with custom functionality for managing users, categories, and application data.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django (Python) |
| Database | PostgreSQL |
| Frontend | Bootstrap, Chart.js |
| Static Files | WhiteNoise |
| Environment | python-decouple |
| Deployment | Azure (App Service) |
| CI/CD | GitHub Actions |

---

## Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/hristina-zayakova/The-nasty-bird
cd budgie

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Copy .env.example to .env and fill in your own values
cp .env.example .env

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000`.

---

## Testing

The project includes a comprehensive test suite covering unit and integration tests across all major apps.

```bash
python manage.py test
```

---

## Project Structure

```
budgie/
├── accounts/        # Custom user model & authentication
├── budgets/         # Budget management
├── categories/      # Expense categories
├── expenses/        # Expense tracking
├── reports/         # Financial reporting
├── subscriptions/   # Subscription monitoring
├── profiles/        # User profiles
└── Budgie/            # Project settings & URLs
```

---

## Deployment

The application is deployed on **Azure App Service** with continuous deployment via **GitHub Actions**. Static files are served via WhiteNoise. Environment variables are managed through Azure App Service configuration settings.

---

## License

This project was developed as an academic exam project.
