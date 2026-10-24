# EduCore — Student Management System

A full-stack student management system built with Django and PostgreSQL. Goes way beyond basic CRUD — includes a REST API with JWT authentication, live search, charts, bulk delete, CSV export, profile pictures, and a clean responsive UI.

---

## Features

- JWT Authentication — login/logout with token-based auth
- REST API — full API built with Django REST Framework
- Dashboard — stats cards, bar chart, doughnut chart (Chart.js)
- Student CRUD — create, read, update, delete students
- Live Search — search by name, email, or phone
- Filters — filter by course and status
- Bulk Delete — select multiple students and delete at once
- CSV Export — download all student data as a spreadsheet
- Profile Pictures — upload and display student photos
- Pagination — built-in API pagination
- Responsive — works on mobile and desktop

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.1.2 |
| Database | PostgreSQL 16 (Docker) |
| API | Django REST Framework |
| Auth | JWT (djangorestframework-simplejwt) |
| Charts | Chart.js |
| Styling | Vanilla CSS |
| Container | Docker |

---

## Project Structure

```
educore/
├── educore/              # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── students/             # Main app
│   ├── models.py         # Student model
│   ├── views.py          # Template + API views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # URL routing
│   └── migrations/
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── student_form.html
│   ├── student_detail.html
│   └── student_confirm_delete.html
├── static/
│   ├── css/style.css
│   └── js/main.js
├── manage.py
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Get JWT token |
| POST | `/api/token/refresh/` | Refresh JWT token |
| GET | `/api/students/` | List all students |
| POST | `/api/students/` | Create student |
| GET | `/api/students/<id>/` | Get student detail |
| PUT | `/api/students/<id>/` | Update student |
| DELETE | `/api/students/<id>/` | Delete student |
| GET | `/api/students/stats/` | Dashboard stats |
| GET | `/api/students/export_csv/` | Export CSV |
| POST | `/api/students/bulk_delete/` | Bulk delete |

### API Query Params

```
/api/students/?search=john          # search by name/email/phone
/api/students/?course=Python        # filter by course
/api/students/?status=active        # filter by status
/api/students/?ordering=-enrolled_at # sort by field
/api/students/?page=2               # pagination
```

---

## Setup

### Requirements

- Python 3.10+
- Docker Desktop
- pip

### 1. Clone the repo

```bash
git clone https://github.com/Sohayeeb/educore.git
cd educore
```

### 2. Create virtual environment

```bash
# Windows
py -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL with Docker

```bash
docker run --name django_postgres \
  -e POSTGRES_DB=django_db \
  -e POSTGRES_USER=django_user \
  -e POSTGRES_PASSWORD=django_password \
  -p 5432:5432 -d postgres:16
```

### 5. Run migrations

```bash
py manage.py migrate
```

### 6. Create admin user

```bash
py manage.py createsuperuser
```

### 7. Run the server

```bash
py manage.py runserver
```

Open `http://127.0.0.1:8000` and log in.

---

## Student Model

| Field | Type | Notes |
|---|---|---|
| name | CharField | Required |
| email | EmailField | Unique |
| phone | CharField | Required |
| course | CharField | Choices dropdown |
| status | CharField | active / inactive / graduated / suspended |
| address | TextField | Optional |
| profile_picture | ImageField | Optional |
| gpa | DecimalField | 0.00 - 4.00 |
| enrolled_at | DateField | Auto set on create |
| updated_at | DateTimeField | Auto updated |

---

## Pages

| URL | Page |
|---|---|
| `/` | Dashboard |
| `/login/` | Login |
| `/students/create/` | Add student |
| `/students/<id>/` | Student detail |
| `/students/<id>/update/` | Edit student |
| `/students/<id>/delete/` | Delete confirmation |
| `/admin/` | Django admin |
| `/api/` | REST API root |

## Website URL

`/https://educore-eta-ten.vercel.app/`
