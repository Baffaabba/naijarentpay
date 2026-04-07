# 9jaRentPay

A Django-based rental management platform for Nigeria — connecting landlords and tenants with digital rent payments, applications, messaging, and wallet management.

## Features

- **Dual-role accounts** — separate dashboards for Landlords and Tenants
- **Property listings** — create, manage, and browse verified rental properties with multiple photos
- **Rental applications** — tenants apply with income/employment details; landlords approve or reject
- **Leases** — digital lease records linking landlord, tenant, and property
- **Wallet** — fund via Paystack or Flutterwave (card, bank transfer, USSD); savings goals with auto-save
- **Saved cards** — Paystack card tokenisation for future payments
- **Payments** — rent payment tracking and history
- **Messaging** — real-time threaded conversations between landlords and tenants
- **Notifications** — in-app bell with unread badge; email notifications
- **Membership tiers** — Free / Standard / Premium, auto-computed from KYC and profile completion
- **KYC** — ID document upload and verification workflow
- **Auto logout** — 5-minute idle timer with warning toast; 30-minute server-side session expiry
- **Public browse** — unauthenticated users can browse and search properties

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.x, Python 3.13 |
| Database | SQLite (dev) |
| Frontend | HTMX 1.9, Alpine.js 3, Tailwind CSS (CDN) |
| Payments | Paystack, Flutterwave |
| Image handling | Pillow |
| Environment | django-environ |
| CORS | django-cors-headers |

## Getting Started

### Prerequisites

- Python 3.11+
- pip or uv

### Installation

```bash
git clone https://github.com/your-username/naijarentpay.git
cd naijarentpay

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development |
| `PAYSTACK_PUBLIC_KEY` | From your Paystack dashboard |
| `PAYSTACK_SECRET_KEY` | From your Paystack dashboard |
| `FLUTTERWAVE_PUBLIC_KEY` | From your Flutterwave dashboard |
| `FLUTTERWAVE_SECRET_KEY` | From your Flutterwave dashboard |
| `FLUTTERWAVE_WEBHOOK_HASH` | Flutterwave webhook secret hash |
| `SITE_URL` | Base URL, e.g. `http://localhost:8000` |
| `EMAIL_HOST_USER` | SMTP email address |
| `EMAIL_HOST_PASSWORD` | SMTP password |

### Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run

```bash
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000`.

## Project Structure

```
├── accounts/        # Custom User model, auth, registration, KYC, settings
├── applications/    # Rental applications (apply, approve, reject)
├── dashboard/       # Tenant & landlord dashboard views and URLs
├── leases/          # Lease records
├── messaging/       # Landlord–tenant conversations
├── notifications/   # In-app notification model, signals, bell dropdown
├── payments/        # Rent payment tracking
├── properties/      # Property listings, images, reviews, search
├── wallet/          # Wallet, savings goals, funding requests, saved cards
├── templates/       # All HTML templates (base, partials, per-app)
├── media/           # User-uploaded files (gitignored)
└── ninejarentpay/   # Django project settings, URLs, WSGI/ASGI
```

## Payment Webhooks

Register these URLs in your payment gateway dashboards:

| Gateway | Webhook URL |
|---------|-------------|
| Paystack | `https://your-domain.com/wallet/paystack/webhook/` |
| Flutterwave | `https://your-domain.com/wallet/flutterwave/webhook/` |

## License

MIT
