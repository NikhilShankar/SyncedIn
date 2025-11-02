# Docker Desktop Manager

A Go application that automatically manages Docker Desktop installation and runs docker-compose files.

## Features

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

1. Place your `docker-compose.yml` file in the same directory as the executable
2. Run the executable:
   - **Windows**: Double-click `docker-manager.exe` or run from command prompt
   - **macOS/Linux**: Run `./docker-manager` from terminal

### Example Directory Structure

```
my-project/
├── docker-manager.exe        # The executable
└── docker-compose.yml         # Your docker-compose file
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

You can modify the `runDockerCompose()` function to change the docker-compose behavior:

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

**"docker-compose.yml not found"**
- Ensure the docker-compose file is in the same directory as the executable
- File must be named `docker-compose.yml` or `docker-compose.yaml`

## License

Free to use and modify as needed.
