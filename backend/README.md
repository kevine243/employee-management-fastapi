USER GUIDE

<!-- # Employee Management System
This is a simple employee management system built with FastAPI and React. It allows you to manage employees, departments, and roles. You can also assign employees to departments and roles. -->

First create a postgreSQL database and run the following command to create the tables:
alembic is used for database migrations, so you need to run the following command to create the tables:

```bash
alembic upgrade head
```

first create a .env file in the root of the project and add the following variables:

```env
DATABASE_URL=....
SECRET_KEY=....
ACCESS_TOKEN_EXPIRE_MINUTES=....
ALGORITHM=....
FRONTEND_URL=....

you can use any mail server for testing, but here we are using Mailtrap, so add the following variables as well:
# Mailtrap
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=....
MAIL_USERNAME=....
MAIL_PASSWORD=....
MAIL_FROM=....
MAIL_STARTTLS=True
MAIL_SSL_TLS=False
```
