#!/bin/bash
# Quick test script to verify the setup

echo "🔍 MeetMind AI - Setup Verification"
echo "===================================="
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
        return 0
    else
        echo "❌ $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
        return 0
    else
        echo "❌ $1/"
        return 1
    fi
}

echo "📁 Directory Structure:"
check_dir "backend"
check_dir "backend/app"
check_dir "backend/app/models"
check_dir "backend/app/schemas"
check_dir "backend/app/routes"
check_dir "backend/app/crud"
check_dir "frontend"
check_dir "frontend/pages"
check_dir "frontend/utils"

echo ""
echo "📄 Backend Files:"
check_file "backend/Dockerfile"
check_file "backend/requirements.txt"
check_file "backend/app/main.py"
check_file "backend/app/config.py"
check_file "backend/app/database.py"
check_file "backend/app/models/meeting.py"
check_file "backend/app/schemas/meeting.py"
check_file "backend/app/routes/health.py"
check_file "backend/app/crud/meeting.py"

echo ""
echo "📄 Frontend Files:"
check_file "frontend/Dockerfile"
check_file "frontend/requirements.txt"
check_file "frontend/app.py"
check_file "frontend/utils/api_client.py"
check_file "frontend/pages/1_Upload_Meeting.py"
check_file "frontend/pages/2_View_Minutes.py"
check_file "frontend/pages/3_Action_Items.py"

echo ""
echo "📄 Configuration Files:"
check_file "docker-compose.yml"
check_file ".env"
check_file ".gitignore"
check_file ".dockerignore"
check_file "README.md"

echo ""
echo "✨ Verification complete!"
echo ""
echo "To start the application, run:"
echo "  docker-compose up --build"
echo ""
