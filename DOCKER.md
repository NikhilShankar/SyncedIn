# Docker Setup for AI Resume Generator

## Quick Start

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Running with Docker Compose (Recommended)

1. **Start the application:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Open your browser and navigate to: http://localhost:8765
   - The Streamlit interface will be ready to use

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Where do PDFs get downloaded?

Generated PDFs are automatically saved to your **host machine** in these directories:
- `./generated/` - Main output directory for PDFs and LaTeX files
- `./output/` - Alternative output directory

The docker-compose.yml configures volume mapping so files created inside the container are persisted on your local machine. You'll find the PDFs in the same directories as if you ran the app locally.

## Configuration

### Setting Your API Key

You have three options:

**Option 1: Via the Web Interface (Easiest)**
- Start the app and enter your Anthropic API key in the sidebar
- No configuration files needed

**Option 2: Using .env file**
- Create a `.env` file in the project root:
  ```env
  ANTHROPIC_API_KEY=sk-ant-your-key-here
  ```
- The docker-compose.yml is already configured to mount this file

**Option 3: Environment Variable in docker-compose.yml**
- Edit `docker-compose.yml` and uncomment:
  ```yaml
  environment:
    - ANTHROPIC_API_KEY=your_api_key_here
  ```

## Manual Docker Commands

If you prefer not to use docker-compose:

### Build the image:
```bash
docker build -t resume-generator .
```

### Run the container:
```bash
docker run -d \
  -p 8765:8765 \
  -v ./generated:/app/generated \
  -v ./output:/app/output \
  -v ./.env:/app/.env:ro \
  --name ai-resume-generator \
  resume-generator
```

### View logs:
```bash
docker logs -f ai-resume-generator
```

### Stop the container:
```bash
docker stop ai-resume-generator
docker rm ai-resume-generator
```

## Port Configuration

The default port is **8765** (instead of the standard 8501) to avoid conflicts with other Streamlit apps.

To change the port:
1. Edit `docker-compose.yml` and change `"8765:8765"` to `"YOUR_PORT:8765"`
2. Access the app at `http://localhost:YOUR_PORT`

## Troubleshooting

### PDF compilation fails
- The Docker image includes a full LaTeX installation (texlive-xetex)
- If PDFs fail to generate, check the logs: `docker-compose logs`

### Fonts not rendering correctly
- Custom Lato fonts are installed during image build
- Rebuild the image if needed: `docker-compose build --no-cache`

### Cannot access the app
- Ensure port 8765 is not in use: `netstat -ano | findstr :8765` (Windows)
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs`

### Volumes not mounting (Windows)
- Ensure Docker Desktop has file sharing enabled for your drive
- Settings > Resources > File Sharing > Add `D:\` (or your drive)

## Development

### Rebuilding after code changes:
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

### Hot reload (for development):
Mount the source code as a volume in docker-compose.yml:
```yaml
volumes:
  - .:/app  # Mount entire directory
  - ./generated:/app/generated
  - ./output:/app/output
```

## System Requirements

**Image Size:** ~2.5 GB (includes full LaTeX distribution)

**Memory:** Recommended 2GB+ RAM

**Disk Space:**
- Docker image: ~2.5 GB
- Generated files: Varies based on usage