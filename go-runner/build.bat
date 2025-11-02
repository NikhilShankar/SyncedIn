@echo off
echo Building Docker Desktop Manager...
echo.

REM Check if Go is installed
go version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Go is not installed or not in PATH
    echo Please install Go from https://golang.org/dl/
    pause
    exit /b 1
)

echo Go is installed
echo.

REM Initialize Go module if go.mod doesn't exist
if not exist go.mod (
    echo Initializing Go module...
    go mod init docker-manager
    echo.
)

REM Build the executable
echo Building executable...
go build -ldflags="-s -w" -o docker-manager.exe docker-manager.go

if errorlevel 1 (
    echo.
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ✓ Build successful!
echo.
echo The executable 'docker-manager.exe' has been created.
echo Place your docker-compose.yml in the same directory and run docker-manager.exe
echo.
pause
