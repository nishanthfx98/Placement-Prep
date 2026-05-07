@echo off
echo Starting PlacementAI Backend...
cd backend
pip install -r requirements.txt -q
start cmd /k "python app.py"
cd ..
echo Starting PlacementAI Frontend...
cd frontend
start cmd /k "npm run dev"
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
