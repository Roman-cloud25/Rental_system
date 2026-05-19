# Rental System API

Backend API for a housing rental platform in Germany.

**Stack:** Python 3.13 · Django 6 · Django REST Framework · MySQL · Docker

---

## What it does

- **Users** — register, login, logout (tenant / landlord roles)
- **Listings** — create, edit, delete, search and filter
- **Bookings** — book a property, confirm or cancel
- **Reviews** — leave a review after a completed stay
- **Analytics** — search history, popular listings

---

## How to run locally

**Requirements:** Python 3.13, Docker Desktop, Git

```bash
# 1. Clone the project
git clone https://github.com/YOUR_USERNAME/rental-system.git
cd rental-system

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Start MySQL in Docker
docker-compose up -d

# 6. Apply migrations
python manage.py migrate

# 7. Load cities and property types
python manage.py load_initial_data

# 8. Create admin user
python manage.py createsuperuser

# 9. Start the server
python manage.py runserver
```

Open in browser:
- API docs → http://localhost:8000/swagger/
- Admin panel → http://localhost:8000/admin/

---

## Project structure

```
Project/
├── rental/                 # Django project settings, URLs, WSGI
│   ├── settings.py
│   └── urls.py
├── users/                  # User model, registration, login, profile, password change
├── properties/             # Listings: CRUD, filters, search, soft delete
├── bookings/               # Bookings: create, confirm, reject, cancel
├── reviews/                # Reviews and ratings
├── analytics/              # Search history, view history, landlord stats
├── common/                 # Cities model, initial data loader
├── generate_test_data.py   # Faker: generates 20 German rental listings
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh           # Container startup: migrate + load data + run server
├── backup.sh               # MySQL backup script (runs via cron)
└── requirements.txt
```

---

## Environment variables

Copy `.env.example` → `.env` and fill in your values.  

---

*Project — Django backend course*
