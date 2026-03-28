# Django Portfolio - Production Deployment Guide

A comprehensive guide for deploying your Django portfolio to a VPS with Docker, Nginx, and automated CI/CD.

> **Note:** For local development setup, see [../README.md](../README.md).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Preparation](#vps-preparation)
3. [Production Deployment](#production-deployment)
4. [SSL Certificate Setup](#ssl-certificate-setup)
5. [CI/CD Configuration](#cicd-configuration)
6. [Database Management](#database-management)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### VPS Requirements

- Ubuntu 22.04 LTS (recommended) or similar
- Minimum 2GB RAM (4GB recommended)
- 20GB+ storage
- Domain name pointing to VPS IP

### Accounts & Services

- GitHub account
- Domain name (e.g., from Namecheap, GoDaddy)
- VPS (DigitalOcean, Linode, AWS EC2, Hetzner, etc.)

---

## VPS Preparation

### 1. Initial Server Setup

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl git wget ufw fail2ban
```

### 2. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

### 3. Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## Production Deployment

### 1. Clone Repository on VPS

```bash
# Create project directory
mkdir -p ~/portfolio
cd ~/portfolio

# Clone your repository
git clone https://github.com/yourusername/portfolio.git .
```

### 2. Create Production Environment File

```bash
# Copy production env example
cp .env.production.example .env.production

# Edit with your settings
nano .env.production
```

Update with your values:

```ini
# SECURITY
SECRET_KEY=generate-a-strong-secret-key-here
DEBUG=False

# Hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-vps-ip

# Database (PostgreSQL)
POSTGRES_DB=portfolio
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=use-a-strong-password-here
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Ports
HTTP_PORT=80
HTTPS_PORT=443
```

### 3. Generate Secret Key

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 4. Deploy with Docker Compose

```bash
# Copy production env to active env
cp .env.production .env

# Build and start services
docker-compose up -d --build

# Check container status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 5. Run Initial Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

---

## SSL Certificate Setup

### Option 1: Let's Encrypt with Certbot (Recommended)

```bash
# Create directory for certificates
mkdir -p ~/portfolio/nginx/ssl

# Install Certbot
sudo apt install -y certbot

# Stop Nginx temporarily (port 80 needs to be free)
docker-compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ~/portfolio/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ~/portfolio/nginx/ssl/key.pem

# Set permissions
chmod 600 ~/portfolio/nginx/ssl/key.pem
chmod 644 ~/portfolio/nginx/ssl/cert.pem

# Restart services
docker-compose up -d nginx
```

### Option 2: Self-Signed Certificate (Testing Only)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Portfolio/CN=yourdomain.com"
```

### Auto-Renew Let's Encrypt Certificates

Create a cron job:

```bash
sudo crontab -e
```

Add this line:

```
0 3 1 * * certbot renew --quiet && docker-compose -f /home/ubuntu/portfolio/docker-compose.yml restart nginx
```

---

## CI/CD Configuration

### 1. GitHub Secrets Setup

Navigate to your GitHub repository:
`Settings → Secrets and variables → Actions`

Add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `VPS_HOST` | Your VPS IP or domain | `192.168.1.100` or `example.com` |
| `VPS_USER` | SSH username | `ubuntu` or `root` |
| `VPS_SSH_KEY` | Private SSH key | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `VPS_PORT` | SSH port (optional) | `22` |

### 2. Generate SSH Key for GitHub Actions

```bash
# Generate dedicated SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copy public key to VPS
ssh-copy-id -i ~/.ssh/github_actions.pub user@your-vps-ip

# Copy private key to GitHub Secrets
cat ~/.ssh/github_actions | xclip -sel clip
# Paste as VPS_SSH_KEY secret
```

### 3. Trigger Deployment

```bash
# Push to main branch
git add .
git commit -m "Update portfolio"
git push origin main

# GitHub Actions will automatically:
# 1. Run tests
# 2. Build Docker image
# 3. Deploy to VPS
```

---

## Database Management

### Backup Database

```bash
# Backup PostgreSQL database
docker-compose exec db pg_dump -U portfolio_user portfolio > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup SQLite (if using)
cp db.sqlite3 backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

### Restore Database

```bash
# Restore PostgreSQL
cat backup_20240101_120000.sql | docker-compose exec -T db psql -U portfolio_user portfolio
```

### Database Migrations

```bash
# Create migrations after model changes
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 web
```

### Health Check

```bash
# Check if services are running
docker-compose ps

# Test health endpoint
curl http://localhost/health/

# Test from outside
curl https://yourdomain.com/health/
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run any new migrations
docker-compose exec web python manage.py migrate
```

### Clean Up Docker

```bash
# Remove unused images
docker image prune -a

# Remove stopped containers
docker container prune

# Remove unused volumes (CAUTION)
docker volume prune
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs web

# Check if port is in use
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Restart containers
docker-compose restart
```

### Database Connection Error

```bash
# Check database is running
docker-compose ps db

# Test connection
docker-compose exec db psql -U portfolio_user -d portfolio

# Check DATABASE_URL in .env
docker-compose exec web env | grep DATABASE
```

### Static Files Not Loading

```bash
# Re-collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check Nginx configuration
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

### SSL Certificate Issues

```bash
# Check certificate paths
ls -la nginx/ssl/

# Test SSL
openssl s_client -connect yourdomain.com:443

# Renew certificate
sudo certbot renew --force-renewal
```

### 502 Bad Gateway

```bash
# Check if Django is running
docker-compose ps web

# Check Django logs
docker-compose logs web

# Verify Nginx can reach Django
docker-compose exec nginx ping web
```

### Permission Denied Errors

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker volume permissions
docker-compose down
sudo chown -R 999:999 ~/portfolio/media
docker-compose up -d
```

---

## Production Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY is unique and secure
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SSL certificate installed and auto-renewing
- [ ] Database backups configured
- [ ] Firewall configured (UFW)
- [ ] Fail2ban installed and running
- [ ] Monitoring setup (optional)

---

## Optional Enhancements

### 1. Enable Docker Auto-Update

Install Watchtower:

```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --interval 86400
```

### 2. Add Monitoring with Prometheus

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

## Support

For issues or questions:
- Check the troubleshooting section
- Review Django documentation: https://docs.djangoproject.com/
- Docker documentation: https://docs.docker.com/
- GitHub Actions: https://docs.github.com/en/actions

---

**Built with ❤️ using Django, Docker, and Nginx**
