# George Ogola - Django Portfolio

A production-ready Django portfolio website with CV tracking, analytics, Docker containerization, and automated CI/CD deployment.

![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat&logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)

---

## Quick Start - Local Development

### 1. Clone and Setup

```bash
cd /path/to/portfolio

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

The `.env` file is already configured for local development. To customize:

```bash
# Copy from example (if .env doesn't exist)
cp .env.example .env
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

**Access your portfolio:** http://localhost:8000

**Access admin panel:** http://localhost:8000/admin/

---

## Project Structure

```
portfolio/
├── portfolio/          # Django project settings
├── core/               # Core app (models, views, templates)
├── api/                # REST API endpoints
├── templates/          # Django templates
├── static/             # Static files (CSS, JS, images)
├── media/              # User uploads (CV, project images)
├── core/fixtures/      # Initial data fixtures
├── nginx/              # Nginx configuration (production)
├── .github/workflows/  # CI/CD pipeline (production)
├── Dockerfile          # Docker build (production)
├── docker-compose.yml  # Docker services (production)
├── docs/               # Documentation
│   ├── DEPLOYMENT.md   # Production deployment guide
│   ├── django_portfolio_cicd.md
│   └── Portfolio_Website_Design_Brief.md
├── .env                # Local environment (gitignored)
├── .env.example        # Environment template
├── .env.production.example  # Production env template
├── README.md           # This file
└── manage.py           # Django management script
```

---

## Models

| Model | Description |
|-------|-------------|
| `ContactMessage` | Stores contact form submissions |
| `CVDownload` | Tracks CV downloads with metadata |
| `Skill` | Technical skills with categories |
| `Experience` | Professional experience timeline |
| `Project` | Featured projects/case studies |
| `SiteSettings` | Site-wide configuration (singleton) |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/contact/` | POST | Submit contact message |
| `/api/cv-download/` | POST | Track and download CV |
| `/api/projects/` | GET | List featured projects |
| `/api/projects/<slug>/` | GET | Project details |
| `/api/experience/` | GET | List experience records |
| `/api/skills/` | GET | List technical skills |
| `/api/config/` | GET | Site configuration |

---

## Admin Panel

Access at `/admin/` to manage your portfolio:

1. **Site Settings** - Configure site title, upload CV, social links
2. **Projects** - Add/edit featured projects
3. **Experience** - Add professional experience
4. **Skills** - Manage technical skills
5. **Contact Messages** - View submissions from contact form
6. **CV Downloads** - Track who downloaded your CV

### Upload CV via Admin

1. Go to `/admin/core/sitesettings/1/change/`
2. Upload your CV file in the **CV file** field
3. Update other settings (email, location, social links)
4. Click **Save**

---

## Development Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations (after model changes)
python manage.py makemigrations

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Load initial data
python manage.py loaddata initial_skills.json initial_experience.json initial_projects.json
```

---

## Production Deployment

For production deployment with Docker, Nginx, and CI/CD, see **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)**.

### Quick Production Overview

```bash
# On your VPS with Docker installed
git clone https://github.com/yourusername/portfolio.git
cd portfolio
cp .env.production.example .env.production
# Edit .env.production with your settings
docker-compose up -d --build
```

---

## Environment Variables

### Local Development (.env)

```ini
SECRET_KEY=django-insecure-local-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:8000
```

### Production (.env.production)

```ini
SECRET_KEY=generate-strong-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@localhost:5432/portfolio
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Tech Stack

- **Backend:** Django 5.0, Django REST Framework
- **Database:** PostgreSQL (production), SQLite (development)
- **Frontend:** Django Templates, Tailwind CSS
- **Server:** Gunicorn, Nginx (production)
- **Container:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

---

## License

MIT License

---

## Contact

- **Email:** gogola89@gmail.com
- **GitHub:** github.com/gogola89
- **LinkedIn:** linkedin.com/in/gogola89

---

**Built with ❤️ in Nairobi, Kenya**
