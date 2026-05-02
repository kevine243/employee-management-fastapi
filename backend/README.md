# Employee Management System

A full-stack employee management system built with **FastAPI** and **React**.  
It allows you to manage employees, departments, and roles with a complete authentication system.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- uv (Python package manager)

---

## Backend Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd employee-management/backend
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Create the `.env` file

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Database
# Format: postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/employee_management

# Security
# Generate a secure key with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# Frontend URL (used for email confirmation links)
FRONTEND_URL=http://localhost:5173

# Email (Mailtrap for development)
# Sign up at https://mailtrap.io to get your credentials
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_FROM=noreply@employee-management.com
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```

### 4. Create the database

```bash
# Connect to PostgreSQL and create the database
psql -U postgres
CREATE DATABASE employee_management;
\q
```

### 5. Run migrations

```bash
uv run alembic upgrade head
```

### 6. Seed the database

This will create the default roles (admin, editor, employee) and the first admin user.

```bash
uv run python -m app.scripts.seed
```

> ⚠️ Default admin credentials:
>
> - Email: `admin@company.com`
> - Password: `admin123`
> - **Change these immediately after first login!**

### 7. Start the server

```bash
uv run uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

---

## Frontend Setup

### 1. Install dependencies

```bash
cd ../frontend
npm install
```

### 2. Create the `.env` file

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Start the development server

```bash
npm run dev
```

Frontend available at: `http://localhost:5173`

---

## API Overview

### Auth

| Method | Endpoint                       | Description            | Auth     |
| ------ | ------------------------------ | ---------------------- | -------- |
| POST   | `/api/v1/auth/login`           | Login                  | Public   |
| POST   | `/api/v1/auth/logout`          | Logout                 | Required |
| POST   | `/api/v1/auth/refresh-token`   | Refresh access token   | Public   |
| GET    | `/api/v1/auth/confirm-email`   | Confirm email          | Public   |
| POST   | `/api/v1/auth/forgot-password` | Request password reset | Public   |
| GET    | `/api/v1/auth/reset-password`  | Verify reset token     | Public   |
| POST   | `/api/v1/auth/reset-password`  | Reset password         | Public   |

### Users

| Method | Endpoint                             | Description      | Role          |
| ------ | ------------------------------------ | ---------------- | ------------- |
| GET    | `/api/v1/users/`                     | List all users   | Admin, Editor |
| GET    | `/api/v1/users/me`                   | Get current user | Required      |
| GET    | `/api/v1/users/{id}`                 | Get user by ID   | Admin, Editor |
| POST   | `/api/v1/users/create_user`          | Create user      | Admin         |
| PATCH  | `/api/v1/users/{id}/edit`            | Update user      | Admin, Editor |
| DELETE | `/api/v1/users/{id}/delete`          | Delete user      | Admin         |
| PUT    | `/api/v1/users/{id}/roles/{role_id}` | Assign role      | Admin         |
| DELETE | `/api/v1/users/{id}/roles/{role_id}` | Remove role      | Admin         |
| PUT    | `/api/v1/users/me/password`          | Change password  | Required      |
| POST   | `/api/v1/users/me/avatar`            | Upload avatar    | Required      |
| DELETE | `/api/v1/users/me/avatar`            | Delete avatar    | Required      |

### Departments

| Method | Endpoint                          | Description       | Role          |
| ------ | --------------------------------- | ----------------- | ------------- |
| GET    | `/api/v1/departments/all`         | List departments  | Admin, Editor |
| GET    | `/api/v1/departments/{id}`        | Get department    | Admin, Editor |
| POST   | `/api/v1/departments/create`      | Create department | Admin, Editor |
| PATCH  | `/api/v1/departments/{id}/edit`   | Update department | Admin, Editor |
| DELETE | `/api/v1/departments/{id}/delete` | Delete department | Admin         |

---

## Roles

| Role       | Description                                            |
| ---------- | ------------------------------------------------------ |
| `admin`    | Full access — can manage users, departments, and roles |
| `editor`   | Can create and edit users and departments              |
| `employee` | Read-only access to their own profile                  |

---

## Common Issues

**Migration fails**

```bash
# Reset the database and start fresh
uv run alembic downgrade base
uv run alembic upgrade head
```

**Email not sending**

- Check your Mailtrap credentials in `.env`
- Make sure `MAIL_STARTTLS=True` and `MAIL_SSL_TLS=False` for Mailtrap

**CORS errors**

- Make sure `FRONTEND_URL` in `.env` matches your frontend URL
- Check `allow_origins` in `main.py`
