# H4WK5INT - Comprehensive OSINT Platform

## 🎯 Overview
H4WK5INT is a comprehensive GUI-based OSINT (Open Source Intelligence) platform designed to streamline the entire intelligence gathering lifecycle. Built by H4WK3Y3, this tool provides a unified interface for conducting various types of intelligence operations with anonymized Tor routing and professional reporting capabilities.

## 🚀 Features

### Core OSINT Modules
- **SOCMINT** - Social Media Intelligence
- **HUMINT** - Human Intelligence  
- **IMINT** - Image Intelligence
- **GEOINT** - Geospatial Intelligence
- **TECHINT** - Technical Intelligence
- **FININT** - Financial Intelligence
- **COMINT** - Communications Intelligence
- **WEBINT** - Web Intelligence

### Platform Capabilities
- 🔒 **Tor Routing** - Anonymized operations through Tor network
- 📊 **Advanced Reporting** - PDF, Markdown, CSV, JSON export formats
- 🔐 **Security Features** - End-to-end encryption and secure authentication
- 🎨 **Modern GUI** - React-based responsive web interface
- 🐳 **Docker Ready** - Containerized deployment for easy setup
- 🤖 **AI-Powered Analysis** - Machine learning for pattern recognition
- 👥 **Team Collaboration** - Multi-user support with role-based access
- 📈 **Real-time Monitoring** - Live updates and notifications

## 🏗️ Architecture

### Frontend (React.js + TypeScript)
- Material-UI components
- Real-time dashboard updates
- Interactive visualizations
- Responsive design

### Backend (FastAPI + Python)
- RESTful API architecture
- PostgreSQL database
- Redis caching
- Celery task queue
- Tor proxy integration

### Security Layer
- JWT authentication
- AES-256 encryption
- Activity logging
- GDPR compliance

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/system3-O/H4WK5INT.git
cd H4WK5INT

# Start the platform
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Manual Setup
```bash
# Backend setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend setup
cd frontend
npm install
npm start
```

## 📖 Documentation

- [User Guide](docs/user-guide.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/h4wk5int

# Security
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# Tor Configuration
TOR_PROXY=socks5://127.0.0.1:9050
USE_TOR=true

# Report Storage
REPORTS_PATH=./reports/generated
```

## 🛡️ Security Features

- **Tor Integration** - All external requests routed through Tor
- **Data Encryption** - AES-256 encryption for sensitive data
- **Audit Logging** - Comprehensive activity tracking
- **Access Control** - Role-based permissions system
- **Session Security** - Secure JWT token management

## 📊 OSINT Modules Detail

### Social Media Intelligence (SOCMINT)
- Profile enumeration across platforms
- Social graph mapping
- Content timeline analysis
- Cross-platform correlation

### Human Intelligence (HUMINT)
- People search and verification
- Employment history research
- Educational background checks
- Professional network analysis

### Image Intelligence (IMINT)
- Reverse image search
- EXIF metadata extraction
- Facial recognition
- Geolocation from images

### Technical Intelligence (TECHINT)
- Domain/subdomain enumeration
- Port scanning and service detection
- Technology stack identification
- SSL certificate analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**H4WK3Y3** - *Initial work* - [system3-O](https://github.com/system3-O)

## 🙏 Acknowledgments

- Open source intelligence community
- Security researchers and ethical hackers
- Contributors and testers

## ⚠️ Disclaimer

This tool is designed for legitimate OSINT research and security testing purposes only. Users are responsible for ensuring their activities comply with applicable laws and regulations. The authors assume no liability for misuse of this software.

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2025-01-15