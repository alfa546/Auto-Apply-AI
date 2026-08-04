# Auto Apply AI - SAAS Platform Documentation

## 🏗️ Architecture Overview

Auto Apply AI has been transformed into a **multi-tenant SAAS platform** with separate admin portal.

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │   Users      │         │   Admin Users   │              │
│  │  (Port 3000) │         │  (Port 3001)    │              │
│  └──────┬───────┘         └────────┬────────┘              │
│         │                          │                         │
│         │ CORS                     │ CORS                    │
│         ▼                          ▼                         │
│  ┌────────────────┐        ┌──────────────┐               │
│  │ Main Backend   │        │ Admin Backend│               │
│  │  (Port 8000)   │        │  (Port 8001) │               │
│  │                │        │              │               │
│  │ - User APIs    │        │ - User Mgmt  │               │
│  │ - Search APIs  │        │ - Vault Mgmt │               │
│  │ - Auto Apply   │        │ - Analytics  │               │
│  │ - Email APIs   │        │ - Monitoring │               │
│  └────────┬───────┘        └──────┬───────┘               │
│           │                       │                          │
│           └───────────┬───────────┘                          │
│                       │                                      │
│                      ▼                                       │
│           ┌──────────────────┐                               │
│           │  API Vault       │  (Encrypted Key Storage)      │
│           │  - 5-6 Keys/API  │  - Auto Rotation              │
│           │  - Failover      │  - Health Monitoring          │
│           └────────┬─────────┘                               │
│                    │                                          │
│                    ▼                                          │
│           ┌────────────────┐                                  │
│           │  PostgreSQL    │  (Shared Database)               │
│           │  - Users       │  - Plans                         │
│           │  - Subscriptions│  - API Usage                     │
│           │  - Vault Keys  │                                  │
│           └────────────────┘                                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+
- Redis 7+

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/auto-apply-ai.git
cd auto-apply-ai
```

### 2. Environment Setup
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# Important: Set VAULT_MASTER_KEY for encryption
```

### 3. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Or Start Manually

#### Backend (Main API - Port 8000)
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Backend (Admin API - Port 8001)
```bash
cd backend_admin

# Create virtual environment
python -m venv venv
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:admin_app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend (Main - Port 3000)
```bash
cd frontend
npm install
npm run dev
```

#### Frontend (Admin - Port 3001)
```bash
cd admin-frontend
npm install
npm run dev
```

## 📁 Project Structure

```
Auto-Apply-AI/
├── backend/                          # Main backend API
│   ├── src/app/
│   │   ├── api/
│   │   │   ├── admin/                # Admin endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   └── vault.py          # Vault management
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── search.py
│   │   │   └── ...
│   │   ├── models.py                 # Database models
│   │   ├── auth.py                   # Authentication
│   │   ├── config.py                 # Configuration
│   │   └── services/
│   │       └── vault/                # API Vault Service
│   │           ├── __init__.py
│   │           ├── encryption.py     # AES-256 encryption
│   │           ├── key_manager.py    # Rotation & failover
│   │           └── health_monitor.py # Health tracking
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── backend_admin/                    # Separate admin backend
│   ├── main.py                       # Admin FastAPI app
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                         # Main user frontend
│   ├── src/app/
│   │   ├── components/
│   │   ├── profile/
│   │   ├── opportunities/
│   │   └── layout.tsx
│   ├── package.json
│   └── Dockerfile
│
├── admin-frontend/                   # Separate admin frontend
│   ├── src/app/
│   │   ├── page.tsx                  # Admin dashboard
│   │   └── layout.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml                # Production deployment
├── nginx.conf                        # Reverse proxy config
├── start_admin.bat                   # Windows: Start admin
├── start_admin.sh                    # Mac/Linux: Start admin
└── IMPLEMENTATION_PHASES.md          # Detailed phase plan

```

## 🔐 Security Features

### 1. Role-Based Access Control (RBAC)
- **USER**: Regular platform users
- **ADMIN**: Can manage users, vault, subscriptions
- **SUPER_ADMIN**: Full system access

### 2. API Vault
- All API keys encrypted with AES-256
- Users never see actual API keys
- 5-6 keys per API service with auto-rotation
- Automatic failover when key limit exhausted
- Health monitoring for all keys

### 3. Rate Limiting
- Per-user daily/monthly limits based on plan
- IP-based rate limiting
- Automatic counter reset

### 4. Subscription Plans
- **Free**: Limited applications & API calls
- **Pro**: Higher limits, priority support
- **Enterprise**: Unlimited, custom features

## 🗄️ Database Models

### Core SAAS Models
- **User**: Email, role, verification status
- **Plan**: Free/Pro/Enterprise with limits
- **Subscription**: User plan & billing status
- **APIUsage**: Track per-user API consumption

### Existing Models (Enhanced)
- Profile, UserSettings, JobFound, Application, EmailInteraction

## 🔑 API Vault System

### How It Works

1. **Key Registration**: Admin adds API keys via `/admin/vault/keys/{service}`
2. **Encryption**: Keys encrypted with VAULT_MASTER_KEY
3. **Rotation**: System automatically rotates keys when limits reached
4. **Failover**: If one key fails, system jumps to next available key
5. **Monitoring**: Health checks track key availability

### Key Limits (Example)
```python
# OpenAI Keys
Key 1: 1000 calls/day, 30000/month
Key 2: 1000 calls/day, 30000/month
Key 3: 1000 calls/day, 30000/month
...
Key 6: 1000 calls/day, 30000/month

# When Key 1 exhausted → Auto jump to Key 2
# When Key 2 exhausted → Auto jump to Key 3
# When all exhausted → Alert admin
```

### Rotation Strategies
- **Round Robin**: Use least recently used key
- **Random**: Random key selection
- **Least Used**: Use key with lowest usage count

## 📊 Admin Portal Features

### Dashboard
- Total services & active keys overview
- Encryption status
- Real-time health monitoring

### API Vault Management
- Add/remove API keys
- View key status (usage, limits, errors)
- Manual rotation trigger
- Reset daily/monthly counters
- Health check per service

### User Management (Coming Soon)
- View all users
- Suspend/activate accounts
- Manage subscriptions
- View usage analytics

### Analytics (Coming Soon)
- API usage trends
- Most used services
- Error rates
- Revenue metrics

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/auto_apply_db

# Security
SECRET_KEY=your-secret-key-here
VAULT_MASTER_KEY=your-vault-master-key-here  # REQUIRED for encryption

# API Keys (stored in vault)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ADZUNA_APP_ID=...
ADZUNA_APP_KEY=...
JOOBLE_API_KEY=...

# Email
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/gmail/callback

# CORS
CORS_ORIGINS=http://localhost:3000
```

#### Admin Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost/auto_apply_db
SECRET_KEY=your-secret-key-here
VAULT_MASTER_KEY=your-vault-master-key-here
```

## 🚢 Deployment

### Docker Compose (Recommended)
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With SSL
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set up PostgreSQL & Redis
2. Deploy backend to port 8000
3. Deploy admin backend to port 8001
4. Deploy frontend to port 3000
5. Deploy admin frontend to port 3001
6. Configure nginx reverse proxy
7. Set up SSL certificates

### Nginx Configuration
```nginx
# Main app
server {
    listen 80;
    server_name app.yourplatform.com;
    location / {
        proxy_pass http://localhost:3000;
    }
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}

# Admin app
server {
    listen 80;
    server_name admin.yourplatform.com;
    location / {
        proxy_pass http://localhost:3001;
    }
    location /api/ {
        proxy_pass http://localhost:8001;
    }
}
```

## 📝 Implementation Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: SAAS Foundation | ✅ Complete | User roles, plans, subscriptions, rate limiting |
| Phase 2: API Vault | ✅ Complete | Encryption, rotation, failover, health monitoring |
| Phase 3: Admin Portal | ✅ Complete | Separate backend/frontend for admin |
| Phase 4: Email UX | ⏳ Pending | Simplified email connection flow |
| Phase 5: Branding | ⏳ Pending | Domain separation, hidden admin links |
| Phase 6: Deployment | ✅ Complete | Docker compose, nginx, SSL |

## 🎯 Key Benefits

### For Users
- ✅ No need to manage API keys
- ✅ 1-click email setup
- ✅ Fair usage with plans
- ✅ Automatic failover

### For Admins
- ✅ Complete control over API keys
- ✅ Real-time monitoring
- ✅ User management
- ✅ Analytics dashboard
- ✅ Hidden admin portal

### For Platform
- ✅ Centralized API key management
- ✅ Cost optimization through rotation
- ✅ Scalable multi-tenant architecture
- ✅ Revenue through subscriptions

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change ports in docker-compose.yml or .env
   PORTS=8001,3001
   ```

2. **Database connection failed**
   ```bash
   # Check PostgreSQL is running
   docker-compose ps postgres
   
   # View logs
   docker-compose logs postgres
   ```

3. **API keys not working**
   ```bash
   # Check vault status
   curl http://localhost:8001/api/v1/admin/vault/status \
     -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
   ```

4. **Rate limit exceeded**
   ```bash
   # Check user plan limits
   # Admin can reset counters via /admin/vault/reset-daily
   ```

## 📚 API Documentation

### Main Backend (Port 8000)
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Admin Backend (Port 8001)
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🤝 Contributing

1. Follow the phase plan in `IMPLEMENTATION_PHASES.md`
2. Create feature branches
3. Test all changes
4. Update documentation

## 📄 License

MIT License

---

**Built with**: FastAPI, Next.js, PostgreSQL, Redis, Docker
**Architecture**: Multi-tenant SAAS with separated admin portal
**Security**: AES-256 encryption, RBAC, rate limiting