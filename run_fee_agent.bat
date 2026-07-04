@echo off
cd /d C:\Users\vinit\.gemini\antigravity\scratch\fee_inquiry_agent
start "" cmd /c "python app.py"
timeout /t 3 >nul
start http://127.0.0.1:5000