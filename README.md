# Personal Finance Manager + Insights

A web-based personal finance application built with Python and Flask. Users can manage income and expenses, organize transactions into categories, set budgets, view financial reports, and securely manage their accounts.

## Features

- User registration and login
- Password hashing with scrypt
- Password reset by email
- CSRF protection
- Authentication rate limiting
- Transaction creation, editing, deletion, search, filtering, sorting, and pagination
- User-owned and system categories
- Monthly budgets and budget progress
- Financial summaries and category expense reports
- PostgreSQL database support
- Responsive web interface
- Security headers and secure session cookies

## Technology

- Python
- Flask
- PostgreSQL
- Psycopg 3
- Flask-WTF
- Brevo transactional email
- HTML, CSS, JavaScript

## Project Structure

```
personal_finance_manager/
├── app.py
├── config.py
├── database/
│   ├── connection.py
│   ├── init_db.py
│   ├── schema.sql
│   └── seed.sql
├── models/
├── routes/
├── services/
├── utils/
├── templates/
├── public/
├── requirements.txt
└── vercel.json
```

The application follows a layered architecture:

```
Routes
   ↓
Services
   ↓
PostgreSQL
```

Routes handle HTTP concerns, services contain application and database logic, and models represent application data.

## Local Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file with the required configuration:

```text
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key
FLASK_DEBUG=true
SESSION_COOKIE_SECURE=false

BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=your_verified_sender_email
BREVO_SENDER_NAME=Personal Finance Manager
```

Initialize the database:

```bash
python -m database.init_db
```

Run locally:

```bash
flask --app app run --debug
```

The Flask development server is for local development only. Production deployments should use the hosting platform's production runtime rather than `app.run()`.

## Production Configuration

At minimum, production must provide:

- `DATABASE_URL`
- `SECRET_KEY`
- `FLASK_DEBUG=false`
- `BREVO_API_KEY`
- `BREVO_SENDER_EMAIL`

`SESSION_COOKIE_SECURE` defaults to enabled whenever debug mode is disabled. It can still be explicitly configured when required by the deployment environment.

The application also limits request bodies to 1 MB by default through `MAX_CONTENT_LENGTH`. This can be overridden with an environment variable when a deployment requires a different limit.

Never commit `.env` or production credentials to the repository.

## Database

The authoritative database schema is:

```
database/schema.sql
```

Initial system data is defined in:

```
database/seed.sql
```

Database changes should be reviewed as migrations/schema changes rather than relying on application startup to modify production data.

## Security

The application currently includes:

- Secure password hashing
- CSRF protection
- Secure session-cookie settings
- Content Security Policy
- HSTS when HTTPS session cookies are enabled
- Authentication and password-reset rate limiting
- Parameterized SQL queries
- Database constraints and ownership checks
- Generic error responses for unexpected server errors
- Request-size limits

## Author

Jubilent Shonhayi

Computer Science Student
