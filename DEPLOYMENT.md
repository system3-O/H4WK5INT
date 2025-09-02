# H4WK5INT OSINT Platform - Deployment Guide

This guide provides step-by-step instructions for deploying the H4WK5INT OSINT platform.

## Prerequisites

- Docker and Docker Compose
- Git
- At least 4GB RAM
- 10GB free disk space

## Quick Start with Docker Compose

1. **Clone the repository:**
```bash
git clone https://github.com/system3-O/H4WK5INT.git
cd H4WK5INT
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

3. **Start the platform:**
```bash
docker-compose up --build
```

4. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

## Manual Setup

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup database:**
```bash
# Install PostgreSQL and create database
createdb h4wk5int
```

5. **Configure environment:**
```bash
cp ../.env.example .env
# Edit .env with your database credentials
```

6. **Run the application:**
```bash
python app.py
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm start
```

## Production Deployment

### Using Docker Compose (Recommended)

1. **Update environment variables for production:**
```bash
# Edit .env file
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key
JWT_SECRET=your-strong-jwt-secret
DATABASE_URL=postgresql://user:password@postgres:5432/h4wk5int
```

2. **Start with production profile:**
```bash
docker-compose --profile production up -d
```

### Manual Production Setup

1. **Backend (using Gunicorn):**
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Frontend (build and serve):**
```bash
cd frontend
npm run build
# Serve build folder with nginx or Apache
```

## Configuration

### Environment Variables

Key environment variables to configure:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Tor Configuration
TOR_PROXY=socks5://127.0.0.1:9050
USE_TOR=true

# External APIs (optional)
GOOGLE_API_KEY=your-google-api-key
SHODAN_API_KEY=your-shodan-api-key
```

### Database Setup

The application will automatically create tables on first run. For production:

1. **Create PostgreSQL database:**
```sql
CREATE DATABASE h4wk5int;
CREATE USER h4wk5int WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE h4wk5int TO h4wk5int;
```

2. **Run initial setup:**
```bash
python app.py
```

### Tor Setup

For anonymized OSINT operations:

1. **Install Tor:**
```bash
# Ubuntu/Debian
sudo apt install tor

# CentOS/RHEL
sudo yum install tor

# macOS
brew install tor
```

2. **Configure Tor:**
```bash
# Edit /etc/tor/torrc
SocksPort 9050
ControlPort 9051
```

3. **Start Tor service:**
```bash
sudo systemctl start tor
sudo systemctl enable tor
```

## Security Considerations

### Production Security

1. **Change default credentials:**
   - Update SECRET_KEY and JWT_SECRET
   - Change default admin password
   - Use strong database passwords

2. **Enable HTTPS:**
   - Configure SSL certificates
   - Update CORS_ORIGINS for HTTPS

3. **Network security:**
   - Use firewall rules
   - Limit database access
   - Consider VPN for admin access

4. **Regular updates:**
   - Keep dependencies updated
   - Monitor security advisories
   - Regular backups

### Default Credentials

- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT: Change the default admin password immediately after first login!**

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL format
   - Check firewall settings

2. **Tor connection issues:**
   - Verify Tor is running on port 9050
   - Check proxy configuration
   - Test with `curl --proxy socks5://127.0.0.1:9050 http://httpbin.org/ip`

3. **Frontend build errors:**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Verify TypeScript configuration

4. **CORS errors:**
   - Update CORS_ORIGINS in .env
   - Check frontend API URL configuration

### Logs

Check application logs:

```bash
# Docker Compose
docker-compose logs backend
docker-compose logs frontend

# Manual setup
tail -f backend/h4wk5int.log
```

## API Documentation

Once running, access the API documentation:
- API Info: http://localhost:5000/api/info
- Health Check: http://localhost:5000/api/health

## Support

For issues and support:
1. Check the troubleshooting section
2. Review application logs
3. Open an issue on GitHub

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is designed for legitimate OSINT research and security testing purposes only. Users are responsible for ensuring their activities comply with applicable laws and regulations.