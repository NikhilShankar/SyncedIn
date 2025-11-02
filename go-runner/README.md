# Docker Desktop Manager

A standalone Go application that automatically manages Docker Desktop installation and runs an embedded docker-compose configuration.

## Features

✅ **Standalone Executable**
- Docker-compose.yml is embedded directly into the .exe file
- No external files needed - just run the executable!
- Automatically extracts and uses the embedded configuration

✅ **Checks if Docker Desktop is installed**
- Detects Docker Desktop on Windows, macOS, and Linux
- Searches common installation paths
- Verifies docker command availability

✅ **Automatic Installation (Windows)**
- Downloads Docker Desktop installer if not found
- Runs installation wizard
- Prompts user for confirmation before installing

✅ **Starts Docker Desktop if not running**
- Automatically launches Docker Desktop
- Waits for Docker daemon to be ready (up to 60 seconds)
- Shows progress indicator

✅ **Runs docker-compose**
- Looks for `docker-compose.yml` or `docker-compose.yaml` in the same directory as the executable
- Executes `docker-compose up -d`
- Shows real-time output

## Building the Executable

### Windows

```bash
# Build for Windows (64-bit)
go build -o docker-manager.exe docker-manager.go
```

### macOS

```bash
# Build for macOS
go build -o docker-manager docker-manager.go
chmod +x docker-manager
```

### Linux

```bash
# Build for Linux
go build -o docker-manager docker-manager.go
chmod +x docker-manager
```

### Cross-compilation

Build for different platforms from any OS:

```bash
# Windows from Linux/Mac
GOOS=windows GOARCH=amd64 go build -o docker-manager.exe docker-manager.go

# macOS from Linux/Windows
GOOS=darwin GOARCH=amd64 go build -o docker-manager docker-manager.go

# Linux from Windows/Mac
GOOS=linux GOARCH=amd64 go build -o docker-manager docker-manager.go
```

## Usage

Simply run the executable - that's it! The docker-compose configuration is embedded inside.

**Windows**: 
- Double-click `docker-manager.exe` 
- Or run from command prompt: `docker-manager.exe`

**macOS/Linux**: 
- Run from terminal: `./docker-manager`

The executable will:
1. Check/install/start Docker Desktop automatically
2. Extract the embedded docker-compose.yml to the current directory
3. Run `docker-compose up -d`

### Example - Just One File!

```
my-project/
└── docker-manager.exe        # Everything you need in one file!
```

After running, you'll also see:
```
my-project/
├── docker-manager.exe
└── docker-compose.yml         # Auto-extracted (for reference/modification)
```

## What It Does

1. **Installation Check**: Verifies if Docker Desktop is installed
   - If not installed (Windows only): Offers to download and install
   - If not installed (Mac/Linux): Provides manual installation instructions

2. **Running Check**: Verifies if Docker Desktop is running
   - If not running: Automatically starts Docker Desktop
   - Waits for Docker daemon to be ready

3. **Execute docker-compose**: Runs your docker-compose file
   - Executes `docker-compose up -d`
   - Shows container startup progress

## Customization

### Modifying the Embedded Docker Compose

To change the docker-compose configuration that's embedded in the executable:

1. Edit `docker-compose.yml` in your source directory
2. Rebuild the executable using `build.bat` or `build.sh`
3. The new docker-compose configuration will be embedded in the new .exe

### Changing Docker Compose Behavior

You can modify the `runDockerCompose()` function to change behavior:

```go
// Example: Run docker-compose with different flags
cmd := exec.Command("docker-compose", "up", "-d", "--build")

// Example: Run docker-compose down instead
cmd := exec.Command("docker-compose", "down")

// Example: Run docker-compose with specific file
cmd := exec.Command("docker-compose", "-f", "custom-compose.yml", "up", "-d")
```

## Requirements

- **Go 1.16+** (for building)
- **Docker Desktop** (will be installed if missing)
- **docker-compose** (usually included with Docker Desktop)

## Platform Support

| Platform | Install Check | Auto-Install | Auto-Start | docker-compose |
|----------|--------------|--------------|------------|----------------|
| Windows  | ✅           | ✅           | ✅         | ✅             |
| macOS    | ✅           | ⚠️ Manual    | ✅         | ✅             |
| Linux    | ✅           | ⚠️ Manual    | ✅         | ✅             |

⚠️ = Manual installation required (provides instructions)

## Notes

- On Windows, the installer download is automatic but requires user confirmation
- On macOS/Linux, Docker Desktop must be installed manually if missing
- The program waits up to 60 seconds for Docker to start
- Requires internet connection for downloading Docker Desktop installer (Windows only)

## Troubleshooting

**"Docker Desktop is not installed"**
- On Windows: Accept the download and installation prompt
- On Mac/Linux: Install Docker Desktop from https://www.docker.com/products/docker-desktop

**"Docker did not start within 60 seconds"**
- Docker Desktop may be taking longer to start
- Check if Docker Desktop is opening properly
- Try starting Docker Desktop manually first

## License

Free to use and modify as needed.
