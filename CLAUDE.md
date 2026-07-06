# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start development server
python manage.py runserver

# Database
python manage.py makemigrations
python manage.py migrate

# Admin user
python manage.py createsuperuser

# Django shell (for ad-hoc queries)
python manage.py shell
```

No test suite exists — the app is manually tested via the browser.

## Architecture

CRM2 is a **Django 4.0.10** loan-management CRM for a Romanian-speaking financial institution. All application logic lives in a single Django app: `accounts/`.

### Key files

| File | Purpose |
|---|---|
| `accounts/models.py` | 8 core models (see below) |
| `accounts/views.py` | ~67KB — all views, business logic |
| `accounts/functions.py` | Loan calculation engine (payment schedules, arrears) |
| `accounts/filters.py` | `django-filter` FilterSet classes for list views |
| `accounts/forms.py` | Django forms for Client, Contract, Payment, etc. |
| `accounts/decorators.py` | Custom auth decorators: `unauthenticated_user`, `allowed_users`, `admin_only` |
| `accounts/urls.py` | 50+ URL patterns; `crm1/urls.py` delegates everything here |
| `accounts/templates/accounts/` | 28 HTML templates (base: `my_main.html`) |
| `accounts/templates/pdf/` | `.docx` and `.xlsx` document templates |

### Core models

- **Client** — physical or juridical persons with bank/ID details
- **Contract** — loan contracts (amount, term, rate, currency MDL/EUR, status, calculation method)
- **Payment** — repayments linked to a Contract
- **Fidejusor** — personal guarantors on a contract
- **Gajist** — vehicle/asset collateral on a contract
- **PenaltyWaive / InterestWaive** — adjustments that reduce penalties or interest owed
- **Arrears** — snapshot of overdue amounts per contract

### Loan calculation engine (`functions.py`)

`create_spread_sheet()` generates full repayment schedules. Three methods are supported, chosen per contract:

1. **Declining Balance** — monthly interest on remaining principal
2. **Declining Balance OLD** — legacy variant of the above
3. **Fixed Flat** — fixed monthly interest regardless of remaining balance

The engine handles grace periods, advance payments, penalty/interest waivers, and multi-currency exchange rates.

### Document generation

Views use `docxtpl` to merge model data into `.docx` templates stored in `accounts/templates/pdf/`. There are separate templates for physical clients, juridical clients, guarantors, and collateral notices. PDF export uses `xhtml2pdf` / `reportlab`; Excel export uses `openpyxl`.

### Authorization

Group-based via Django's built-in `User`/`Group` system. The `accounts/decorators.py` decorators enforce two roles: `admin` and `customer`. Most write operations require `admin`.

### Frontend

Plain Django templates with Bootstrap. `django-tables2` renders sortable data tables; `django-filter` powers list-view filtering. `widget_tweaks` is used for form field customization in templates.

### Settings notes

- Database: SQLite3 (`db.sqlite3`)
- `DEBUG = True`, `ALLOWED_HOSTS = ['*']` — development configuration
- Email: Gmail SMTP (configured in `crm1/settings.py`)
- Static files: `/static/`; Media/uploads: `/images/`
