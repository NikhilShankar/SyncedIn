# Quick Setup Guide

## What Makes This Special?

This creates a **standalone executable** with the docker-compose.yml embedded inside! 
No need to carry around multiple files - just one .exe does everything!

## Prerequisites
- Install Go from https://golang.org/dl/ (version 1.16 or higher)

## Setup Steps

### Option 1: Use Build Scripts (Recommended)

**Windows:**
1. Open Command Prompt or PowerShell in the project folder
2. Run: `build.bat`
3. The executable `docker-manager.exe` will be created

**Linux/Mac:**
1. Open Terminal in the project folder
2. Run: `chmod +x build.sh` (first time only)
3. Run: `./build.sh`
4. The executable `docker-manager` will be created

### Option 2: Manual Build

1. Initialize Go module:
```bash
go mod init docker-manager
```

2. Build the executable:

**Windows:**
```bash
go build -o docker-manager.exe docker-manager.go
```

**Linux/Mac:**
```bash
go build -o docker-manager docker-manager.go
chmod +x docker-manager
```

## Running the Application

Simply run the executable - no other files needed!

- **Windows:** Double-click `docker-manager.exe` or run `docker-manager.exe` in CMD
- **Linux/Mac:** Run `./docker-manager` in terminal

The executable has everything embedded inside:
- ✅ Docker Desktop installer detection/download
- ✅ Docker startup automation
- ✅ Your docker-compose configuration (embedded!)

## Modifying Your Docker Compose Configuration

Want to change what containers are launched?

1. Edit `docker-compose.yml` in the source folder
2. Run the build script again (`build.bat` or `build.sh`)
3. Your new configuration is now embedded in the .exe!

## Troubleshooting

**Error: "no required module provides package"**
- Solution: Run `go mod init docker-manager` before building

**Error: "go.mod file not found"**
- Solution: The build scripts now create this automatically, or run `go mod init docker-manager`

**Error: "Go is not recognized"**
- Solution: Install Go from https://golang.org/dl/ and add it to your PATH

## What Happens When You Run It?

1. ✅ Checks if Docker Desktop is installed
2. ✅ Downloads and installs Docker Desktop if missing (Windows only)
3. ✅ Starts Docker Desktop if not running
4. ✅ Waits for Docker to be ready
5. ✅ Extracts the embedded docker-compose.yml
6. ✅ Runs your containers with `docker-compose up -d`

Enjoy your standalone Docker management tool! 🐳
