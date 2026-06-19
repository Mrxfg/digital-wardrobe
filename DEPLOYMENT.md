# Deployment Guide

## Prerequisites on VM

1. **Install Docker and Docker Compose:**
```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

2. **Install Git:**
```bash
apt-get install git -y
```

## Deployment Steps

### 1. Connect to VM
```bash
ssh root@your-server-ip
```

### 2. Clone Repository
```bash
cd /opt
git clone https://github.com/Mrxfg/digital-wardrobe.git
cd digital-wardrobe
```

### 3. Configure Environment
```bash
# Copy and edit production environment file
cp .env.production .env
nano .env
```

**Required changes in .env:**
- `DB_PASSWORD`: Strong password for PostgreSQL
- `SECRET_KEY`: Random secret key (generate with: `openssl rand -hex 32`)
- `BOT_TOKEN`: Your Telegram bot token

### 4. Build and Start Services
```bash
# Build and start containers
docker compose up -d

# Check if containers are running
docker compose ps

# View logs
docker compose logs -f backend
```

### 5. Verify Deployment
```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"digital-wardrobe-api","version":"1.0.0"}
```

### 6. Configure Firewall (if needed)
```bash
# Allow port 8000
ufw allow 8000/tcp

# Check status
ufw status
```

## Updating the Application

```bash
cd /opt/digital-wardrobe

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build

# Check logs
docker compose logs -f backend
```

## Useful Commands

**View logs:**
```bash
docker compose logs -f backend
docker compose logs -f db
```

**Restart services:**
```bash
docker compose restart backend
docker compose restart db
```

**Stop services:**
```bash
docker compose down
```

**Database backup:**
```bash
docker compose exec db pg_dump -U wardrobe_user digital_wardrobe > backup_$(date +%Y%m%d).sql
```

**Database restore:**
```bash
docker compose exec -T db psql -U wardrobe_user digital_wardrobe < backup_20260619.sql
```

**Access database:**
```bash
docker compose exec db psql -U wardrobe_user -d digital_wardrobe
```

**Clean up old images:**
```bash
docker system prune -a
```

## Troubleshooting

**Container won't start:**
```bash
docker compose logs backend
docker compose ps
```

**Database connection issues:**
```bash
# Check if database is healthy
docker compose exec db pg_isready -U wardrobe_user

# Check database logs
docker compose logs db
```

**Reset everything (WARNING: deletes all data):**
```bash
docker compose down -v
docker compose up -d
```

## Production Checklist

- [ ] Changed DB_PASSWORD to strong password
- [ ] Generated new SECRET_KEY
- [ ] Added real BOT_TOKEN
- [ ] Firewall configured
- [ ] SSL/TLS configured (use nginx reverse proxy)
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Domain name configured (optional)

## API Access

After deployment, your API will be available at:
- `http://your-server-ip:8000`
- API docs: `http://your-server-ip:8000/docs`
- Health check: `http://your-server-ip:8000/health`

## Nginx Reverse Proxy (Optional but Recommended)

For production, use nginx with SSL:

```bash
# Install nginx
apt-get install nginx certbot python3-certbot-nginx -y

# Create nginx config
nano /etc/nginx/sites-available/wardrobe
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/wardrobe /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL certificate (if domain configured)
certbot --nginx -d your-domain.com
```
