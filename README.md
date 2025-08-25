# Zinocare Backend

A Django + Django REST Framework backend for managing livestock, vaccinations, consultations, and notifications for farmers (**Mkulima**) and vets.

---

## ✨ Features

- **Accounts**: Custom `User` with roles (`mkulima`, `vet`, `admin`) + `MkulimaProfile`, `VetProfile`
- **Livestock**: Animal registry linked to `MkulimaProfile`
- **Vaccinations**: Vaccines, target species, schedules, administration records (with validation)
- **Consultations**: Farmer–Vet consultation workflow with status lifecycle
- **Notifications**: Scheduled reminders (SMS/Email/Push) with delivery status tracking
- **UUIDs everywhere** for safer IDs
- **Validation in `clean()`** + unique constraints and indexes

---

## 🧱 Tech Stack

- Python, Django, Django REST Framework
- PostgreSQL (recommended) / SQLite (dev)
- Celery + Redis (optional, for async notifications)
- Docker (optional)

---

## 📦 Project Structure (apps)

