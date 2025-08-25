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

