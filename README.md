# 🎯 MeetMind AI - Meeting Minutes & Action Item Extractor

An AI-powered application for automatically extracting meeting minutes and action items from meeting recordings.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- At least 4GB available RAM
- Git

### Launch the Application

```bash
# Clone and navigate to the project
git clone <repository-url>
cd MeetMind-AI

# Build and start all containers
docker-compose up --build
```

**Access the application:**
- **Frontend (Streamlit):** http://localhost:8501
- **Backend API (FastAPI):** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Database:** localhost:5432

## 📋 Project Structure

```
MeetMind-AI/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # Database connection & session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── meeting.py           # Meeting database model (SQLAlchemy)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── meeting.py           # Pydantic schemas for request/response
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py            # Health check endpoint
│   │   └── crud/
│   │       ├── __init__.py
│   │       └── meeting.py           # Database CRUD operations
│   ├── Dockerfile                   # Backend container configuration
│   └── requirements.txt             # Python dependencies
│
├── frontend/                         # Streamlit Frontend
│   ├── app.py                       # Main application entry point
│   ├── pages/
│   │   ├── 1_Upload_Meeting.py     # Meeting upload page
│   │   ├── 2_View_Minutes.py       # Minutes viewing page
│   │   └── 3_Action_Items.py       # Action items management page
│   ├── utils/
│   │   ├── __init__.py
│   │   └── api_client.py           # API client for backend communication
│   ├── Dockerfile                  # Frontend container configuration
│   └── requirements.txt            # Python dependencies
│
├── docker-compose.yml              # Multi-container orchestration
├── .env                            # Environment variables
├── .gitignore                      # Git ignore configuration
└── README.md                       # Project documentation
```

## 🏗️ Architecture

### Components

1. **Frontend (Streamlit)**
   - User interface for uploading meetings
   - Viewing extracted minutes
   - Managing action items
   - Ports: 8501

2. **Backend (FastAPI)**
   - RESTful API for meeting management
   - Health check endpoint
   - Database integration
   - Ports: 8000

3. **Database (PostgreSQL)**
   - Stores meeting data
   - Stores meeting minutes
   - Stores action items
   - Ports: 5432

### Database Schema

#### Meetings Table
```sql
CREATE TABLE meetings (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  duration_minutes INTEGER,
  participants JSON,
  minutes TEXT,
  action_items JSON,
  recording_path VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📦 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Streamlit | 1.28.1 |
| Backend | FastAPI | 0.104.1 |
| API Server | Uvicorn | 0.24.0 |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0.23 |
| Containerization | Docker | Latest |
| Orchestration | Docker Compose | 3.8 |

## 🔧 Environment Configuration

All configuration is managed through the `.env` file. Copy `.env.example` to `.env` if needed.

```env
# Database Configuration
DATABASE_USER=meetmind_user
DATABASE_PASSWORD=meetmind_password
DATABASE_NAME=meetmind_db
DATABASE_URL=postgresql://meetmind_user:meetmind_password@db:5432/meetmind_db

# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# AI Configuration
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo
OPENROUTER_API_KEY=
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL=gpt-4o-mini
AI_MODEL=

# Frontend Configuration
API_URL=http://backend:8000
STREAMLIT_PORT=8501
```

## 🐳 Docker Commands

### Build and Start

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d --build

# Start without rebuilding
docker-compose up
```

### View Logs

```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Stop and Remove

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers with volumes
docker-compose down -v
```

### Execute Commands

```bash
# Access backend container shell
docker-compose exec backend bash

# Access frontend container shell
docker-compose exec frontend bash

# Access database container
docker-compose exec db psql -U meetmind_user -d meetmind_db
```

## 📊 API Endpoints

### Health Check
- **GET** `/health` - Check API and database health
  ```bash
  curl http://localhost:8000/health
  ```
  Response:
  ```json
  {
    "status": "healthy",
    "service": "MeetMind AI Backend",
    "database": "connected"
  }
  ```

### Root Endpoint
- **GET** `/` - Get API information

## ✅ Health Checks

The docker-compose configuration includes health checks for all services:

- **Backend**: Checks `/health` endpoint every 30s
- **Frontend**: Checks Streamlit health endpoint every 30s
- **Database**: Checks PostgreSQL connectivity every 10s

View health status:
```bash
docker-compose ps
```

## 🚦 Service Dependencies

```
Frontend → Backend → Database
  (8501)    (8000)    (5432)
```

- Frontend depends on Backend being healthy
- Backend depends on Database being healthy
- Services will not start until dependencies are ready

## 🔐 Security Notes

**Development Only:**
- Default credentials are used for simplicity
- DEBUG mode is enabled
- Change these for production!

**For Production:**
```env
DATABASE_USER=<secure-username>
DATABASE_PASSWORD=<secure-password>
DEBUG=False
```

## 📖 Feature Pages

### 1. Upload Meeting (📹)
- Upload meeting recordings (MP3, MP4, WAV, WebM)
- Add meeting details (title, description, participants)
- Process meetings with AI

### 2. View Minutes (📋)
- Browse all processed meetings
- View extracted meeting minutes
- See participant information
- Filter and search meetings

### 3. Action Items (✅)
- Track action items from meetings
- Filter by status (Pending, In Progress, Completed)
- Assign items to participants
- Set due dates and priority levels

## 🛠️ Development

### Local Development without Docker

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Database Initialization

Tables are automatically created when the backend starts.

To manually initialize:
```bash
docker-compose exec backend python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🐛 Troubleshooting

### Container fails to start
```bash
# Check logs
docker-compose logs -f <service-name>

# Verify ports are not in use
netstat -an | grep LISTEN
```

### Database connection error
```bash
# Verify database is running
docker-compose exec db pg_isready

# Check database credentials in .env
cat .env | grep DATABASE
```

### Frontend can't connect to backend
```bash
# Verify backend is running and healthy
docker-compose ps

# Check API_URL in frontend
curl http://backend:8000/health
```

### Permission errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## 📌 Performance Notes

- Initial build takes 2-3 minutes
- First application startup includes database initialization
- PostgreSQL data persists in named volume `postgres_data`

## 🚀 Next Steps

1. **AI Integration:** Implement speech-to-text transcription
2. **NLP Processing:** Extract key topics and action items
3. **User Authentication:** Add user login and session management
4. **Export Functionality:** PDF/Word export of minutes
5. **Meeting Analytics:** Dashboard with meeting statistics
6. **Email Notifications:** Send action items to participants
7. **Meeting Scheduler:** Integrate with calendar systems

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Docker Compose logs
3. Open an issue on GitHub

---

**Happy Meeting Minutes Extraction! 🎯**
