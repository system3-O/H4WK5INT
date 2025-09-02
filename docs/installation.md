# H4WK5INT Installation Guide

## Prerequisites

- Docker & Docker Compose
- Git
- 4GB+ RAM
- 10GB+ disk space

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/system3-O/H4WK5INT.git
   cd H4WK5INT
   ```

2. **Run the setup script:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

## Manual Installation

### 1. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
- Database credentials
- API keys (optional)
- Security settings

### 2. Database Setup

Start PostgreSQL:
```bash
docker-compose up -d postgres
```

### 3. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm start
```

### 5. Services Setup

Start Redis and Tor:
```bash
docker-compose up -d redis tor
```

## Docker Deployment

### Development
```bash
docker-compose up --build
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

### Database
- Default: PostgreSQL 15
- Credentials in `.env` file
- Auto-migration on startup

### Tor Integration
- SOCKS proxy on port 9050
- Configurable in `.env`
- Can be disabled for testing

### API Keys
Add your API keys to `.env`:
- Shodan API
- VirusTotal API
- Hunter.io API
- Social media APIs

## Security

### Important Security Settings

1. **Change default passwords:**
   ```bash
   # In .env file
   SECRET_KEY=your-strong-secret-key
   JWT_SECRET=your-jwt-secret
   ```

2. **Use HTTPS in production:**
   - Configure SSL certificates
   - Use reverse proxy (Nginx)

3. **Network security:**
   - Use private networks
   - Configure firewall rules
   - Monitor access logs

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Stop conflicting services
   sudo systemctl stop apache2
   ```

2. **Database connection errors:**
   ```bash
   # Check database status
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Tor connection issues:**
   ```bash
   # Check Tor status
   docker-compose logs tor
   
   # Test Tor connection
   curl --proxy socks5://localhost:9050 https://check.torproject.org/api/ip
   ```

### Logs

View application logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Performance

Monitor resource usage:
```bash
# Container stats
docker stats

# System resources
htop
df -h
```

## Updates

Update the application:
```bash
git pull origin main
docker-compose pull
docker-compose up --build -d
```

## Backup

### Database Backup
```bash
docker-compose exec postgres pg_dump -U h4wk5int h4wk5int > backup.sql
```

### Reports Backup
```bash
tar -czf reports_backup.tar.gz backend/reports/
```

## Support

- Check documentation in `docs/` folder
- Review logs for error messages
- Create issues on GitHub repository
- Check community forums