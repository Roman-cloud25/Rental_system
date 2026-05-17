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
rental-system/
├── users/          # Auth and user profiles
├── properties/     # Listings (CRUD, search, filters)
├── bookings/       # Booking system
├── reviews/        # Reviews and ratings
├── analytics/      # Search and view history
├── common/         # Cities list, shared models
├── rental/         # Django settings and URLs
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Environment variables

Copy `.env.example` → `.env` and fill in your values.  

---

*Project — Django backend course*
