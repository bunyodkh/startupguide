# Startup Guide (SG) — Hub

A community platform for the startup ecosystem. Builders can sign up, create profiles, explore ecosystem entities (accelerators, incubators, universities, etc.), and access a knowledge wiki of resources.

## Stack

- **Backend:** Django 4+, django-allauth (email auth), django-unfold (admin)
- **Frontend:** Plain HTML/CSS, HTMX
- **Database:** SQLite (development)
- **Email:** SMTP via Resend
- **i18n:** English, Uzbek, Russian (django-modeltranslation)
- **Images:** django-imagekit + Pillow (auto-thumbnails)

## Apps

| App | Purpose |
|-----|---------|
| `users` | Custom signup/login forms, `BuilderProfile` model |
| `hub` | Ecosystem entities (`EcosystemEntity`) and categories |
| `wiki` | Knowledge base — resources, guides, reports |

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=smtp.resend.com
EMAIL_PROVIDER=resend
RESEND_API_KEY=your-resend-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Run migrations and start the dev server:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Static files are served from `assets/`. Run `python manage.py collectstatic` before deploying.

## Project Structure

```
config/       Django project config (settings, urls, wsgi)
users/        Auth, BuilderProfile
hub/          Ecosystem entities
wiki/         Resource library
templates/    All HTML templates
assets/       CSS, images, and other static assets
```

## Password Requirements

Min. 8 characters — must include a letter, a number, and a special character (enforced via `config/validators.py`).
