# Doctor Booking System

A backend system built with Django and Django REST Framework featuring role-based access, dynamic slot generation, and proper handling of booking conflicts and concurrency.

---

## Tech Stack

- Python 3.x
- Django
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- SQLite (default)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/nishal-nm/doctor-booking-system.git
cd doctor-booking-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the root directory

```
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superadmin

```bash
python manage.py createsuperuser
```

Enter email, full name, and password when prompted.  
The created superuser will have the role `superadmin` by default.

### 7. Run the development server

```bash
python manage.py runserver
```

---

## User Roles

| Role | Access |
|------|--------|
| Superadmin | Custom dashboard (templates), manage doctors, approve/reject leaves, view slots |
| Doctor | API — manage leave requests, view appointments |
| Customer | API — list doctors, view available slots, book appointments |

---

## Superadmin Dashboard

Access the custom template-based dashboard at:

```
http://127.0.0.1:8000/dashboard/
```

Login with your superadmin credentials. From the dashboard you can:
- Create, update, and delete doctors
- View and approve or reject doctor leave requests
- View dynamically generated slots for any doctor on any date

---

## API Endpoints

### Auth

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register/` | Public | Register as customer |
| POST | `/api/auth/login/` | Public | Login and receive JWT tokens |
| POST | `/api/auth/logout/` | Authenticated | Logout |
| POST | `/api/auth/token/refresh/` | Authenticated | Refresh access token |

### Doctors (Superadmin)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/doctors/` | Superadmin | List all doctors |
| POST | `/api/doctors/` | Superadmin | Create a doctor |
| PUT | `/api/doctors/<id>/` | Superadmin | Update a doctor |
| DELETE | `/api/doctors/<id>/` | Superadmin | Delete a doctor |
| GET | `/api/doctors/<id>/slots/?date=YYYY-MM-DD` | Superadmin | View dynamically generated slots for a doctor |
| GET | `/api/doctors/leaves/all/` | Superadmin | List all leave requests |
| PUT | `/api/doctors/leaves/<id>/status/` | Superadmin | Approve or reject a leave request |

### Leaves (Doctor)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/api/doctors/leaves/` | Doctor | Create a leave request |
| GET | `/api/doctors/leaves/` | Doctor | View own leave requests |

### Appointments (Customer)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/appointments/doctors/` | Customer | List all doctors |
| GET | `/api/appointments/doctors/<id>/slots/?date=YYYY-MM-DD` | Customer | View available slots |
| POST | `/api/appointments/book/` | Customer | Book an appointment |
| GET | `/api/appointments/my/` | Customer | View own appointments |

### Appointments (Doctor)

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/appointments/doctor/my/` | Doctor | View own appointments |

---

## Authentication

All API endpoints except register and login require a JWT access token in the request header:

```
Authorization: Bearer <access_token>
```

---

## Booking a Slot — Example Request

```json
POST /api/appointments/book/
{
    "doctor_id": 1,
    "date": "2026-05-10",
    "start_time": "09:00"
}
```

---

## Key Features

- Slots are generated dynamically and never stored in the database
- Slots are generated based on:
  - Doctor working days
  - Start and end time
  - Slot duration
  - Maximum consultations per day
- Approved leave dates are automatically excluded from available slots
- Already booked slots are excluded in real time
- Double booking is prevented using both database constraints (`unique_together`) and runtime validation
- Race conditions are handled using `select_for_update` inside `transaction.atomic`
- Superadmin dashboard built entirely with Django templates — no Django Admin used