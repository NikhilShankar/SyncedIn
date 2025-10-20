@echo off
REM Resume Generator - Quick Launch Script for Windows

echo 🚀 Starting AI Resume Generator...
echo.

REM Check if streamlit is installed
where streamlit >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
)

REM Check if resume data exists
if not exist "resume_data_enhanced.json" (
    echo ⚠️  Warning: resume_data_enhanced.json not found in current directory
    echo    Make sure you're in the correct folder
)

REM Check if template exists
if not exist "resume_template.tex" (
    echo ⚠️  Warning: resume_template.tex not found in current directory
    echo    Make sure you're in the correct folder
)

REM Create necessary directories
if not exist "generated" mkdir generated
if not exist "output" mkdir output
if not exist "resume_backups" mkdir resume_backups

echo.
echo ✅ Launching Streamlit app...
echo 📱 App will open in your browser at http://localhost:8501
echo.
echo 💡 Tips:
echo    - Enter your API key in the sidebar
echo    - Start with Haiku model (cheaper)
echo    - Keep rewrite mode OFF (safer)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch streamlit with main_app.py
streamlit run main_app.py