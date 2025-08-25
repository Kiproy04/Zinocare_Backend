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
- PostgreSQL / SQLite 
- Celery + Redis 

---

## 📦 Project Structure (apps)

accounts/ # User + profiles (Mkulima, Vet)
livestock/ # Animal model
vaccinations/ # Vaccine, VaccineTargetSpecies, VaccinationSchedule, VaccinationRecord
consultations/ # Consultation workflow
notifications/ # Notification scheduling

---

## 🛠 API Endpoints

🔑 1: Authentication & Accounts API

Endpoints

POST /api/auth/register/ → create account + profile (Mkulima or Vet)

POST /api/auth/login/ → return JWT access & refresh tokens

GET /api/auth/me/ → get current user + profile

🐄 2: Livestock API

GET /api/livestock/animals/ → list user’s animals

POST /api/livestock/animals/ → add a new animal

GET /api/livestock/animals/{id}/ → view details

PUT/PATCH /api/livestock/animals/{id}/ → update animal

DELETE /api/livestock/animals/{id}/ → remove animal

💉 3: Vaccination API

GET /api/vaccines/ → list vaccines

POST /api/vaccines/ (admin only)

POST /api/vaccinations/schedules/ → create vaccination schedule for an animal

POST /api/vaccinations/records/ → log completed vaccination

🩺 4: Consultations API

POST /api/consultations/ → farmer requests a consultation

GET /api/consultations/ → list (farmer sees requests, vet sees assigned)

PATCH /api/consultations/{id}/ → vet updates status (Scheduled, Completed, Cancelled)

🔔 5: Notifications API

GET /api/notifications/ → list notifications

(Later: hook into Celery to auto-send reminders)

