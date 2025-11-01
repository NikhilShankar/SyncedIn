# SyncedIn Resume Generator - Usage Guide

AI-powered resume generation system with multi-user support, built with Claude AI and LaTeX.

---

## For Publishers (Publishing to Docker Hub)

### Prerequisites
- Docker installed
- Docker Hub account ([sign up here](https://hub.docker.com/signup))

### Steps to Publish

1. **Login to Docker Hub**
   ```bash
   docker login
   ```

2. **Build the Image** (replace `yourusername` with your Docker Hub username)
   ```bash
   docker build -t yourusername/syncedin-resume:latest .
   ```

3. **Test Locally** (optional but recommended)
   ```bash
   docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data yourusername/syncedin-resume:latest
   ```
   Visit `http://localhost:8765` to test.

4. **Push to Docker Hub**
   ```bash
   docker push yourusername/syncedin-resume:latest
   ```

5. **Share the Image Name**
   ```
   yourusername/syncedin-resume:latest
   ```

### Updating the Image
```bash
# Make your code changes, then rebuild and push
docker build -t yourusername/syncedin-resume:latest .
docker push yourusername/syncedin-resume:latest
```

---

## For End Users

### Quick Start (3 Simple Steps)

#### Step 1: Pull the Docker Image
```bash
docker pull yourusername/syncedin-resume:latest
```

#### Step 2: Run the Container
```bash
# Windows (PowerShell)
docker run -d -p 8765:8765 -v $env:USERPROFILE\Documents\SyncedIn:/data --name resume-generator yourusername/syncedin-resume:latest

# Linux/Mac
docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data --name resume-generator yourusername/syncedin-resume:latest
```

#### Step 3: Open the App
Open your browser and go to: **http://localhost:8765**

You'll see a setup wizard on first run. Enter:
- Your Anthropic API Key ([get one here](https://console.anthropic.com/))
- Your preferred AI model (Claude Sonnet 4.5 recommended)
- Your name

That's it! 🎉

---

## Where Are My Files?

All your resume files are saved in your `Documents/SyncedIn` folder:

```
Documents/SyncedIn/
├── global_config.json          # Your settings
├── YourName/
│   ├── Resumes/
│   │   └── CompanyName/
│   │       ├── CompanyName_1.pdf
│   │       ├── CompanyName_2.pdf
│   │       └── ...
│   ├── Content/
│   │   └── resume_data_enhanced.json
│   └── Stats/
│       └── applications_tracking.json
```

- **Windows**: `C:\Users\YourName\Documents\SyncedIn\`
- **Linux/Mac**: `~/Documents/SyncedIn/`

You can browse, copy, and share these files directly from your file explorer!

---

## Multi-User Support

### Creating Additional Users

1. Open the app: `http://localhost:8765`
2. Go to **Settings** (⚙️ tab in sidebar)
3. Under **User Management**, select **"+ Create New User"**
4. Enter the new user's name and click **Create**

Each user gets their own folder in `Documents/SyncedIn/`.

### Switching Between Users

1. Go to **Settings** → **User Management**
2. Select a user from the dropdown
3. Click **Switch**

All resume data, PDFs, and application tracking are kept separate per user!

---

## Managing the Container

### View Logs
```bash
docker logs resume-generator
```

### Stop the Container
```bash
docker stop resume-generator
```

### Start the Container
```bash
docker start resume-generator
```

### Restart the Container
```bash
docker restart resume-generator
```

### Remove the Container
```bash
docker stop resume-generator
docker rm resume-generator
```

### Update to Latest Version
```bash
# Stop and remove old container
docker stop resume-generator
docker rm resume-generator

# Pull latest image
docker pull yourusername/syncedin-resume:latest

# Run new container (use same command from Step 2 above)
docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data --name resume-generator yourusername/syncedin-resume:latest
```

**Note:** Your data in `Documents/SyncedIn` is preserved!

---

## Configuration

### Changing API Key or Model

1. Open the app: `http://localhost:8765`
2. Go to **Settings** (⚙️)
3. Update your API key or select a different model
4. Click **Save**

### Using a Different Port

If port 8765 is already in use:
```bash
docker run -d -p 9000:8765 -v ~/Documents/SyncedIn:/data --name resume-generator yourusername/syncedin-resume:latest
```
Then access via `http://localhost:9000`

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs resume-generator
```

**Verify the container is running:**
```bash
docker ps
```

### Can't Access the App

1. Make sure the container is running: `docker ps`
2. Check the port: `docker port resume-generator`
3. Try: `http://localhost:8765`

### Setup Wizard Won't Go Away

If you're stuck on the setup wizard:
1. Make sure you entered a valid API key (starts with `sk-ant-`)
2. Enter a username
3. Click "Get Started"

If it still doesn't work, check the logs: `docker logs resume-generator`

### Missing API Key Warning

Go to **Settings** → **API & Model** tab → Enter your Anthropic API key.

### Files Not Appearing in Documents/SyncedIn

**Windows Users:**
- Make sure you used the correct path: `-v $env:USERPROFILE\Documents\SyncedIn:/data`
- Check if Docker Desktop has permission to access your Documents folder:
  - Docker Desktop → Settings → Resources → File Sharing
  - Add `C:\Users\YourName\Documents` if not listed

**Linux/Mac Users:**
- Verify the path exists: `ls ~/Documents/SyncedIn`
- Create it if needed: `mkdir -p ~/Documents/SyncedIn`

### PDF Generation Fails

LaTeX is pre-installed in the container. If PDF generation fails:
1. Check the error message in the app
2. View logs: `docker logs resume-generator`
3. Make sure your resume JSON data is valid

### Reset Everything

To start fresh:
```bash
# Stop and remove container
docker stop resume-generator
docker rm resume-generator

# Optional: Remove your data (WARNING: This deletes all resumes!)
# Windows: rmdir /s Documents\SyncedIn
# Linux/Mac: rm -rf ~/Documents/SyncedIn

# Start container again
docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data --name resume-generator yourusername/syncedin-resume:latest
```

---

## Features

- **AI-Powered Resume Generation**: Uses Claude AI to tailor resumes to job descriptions
- **Multi-User Support**: Multiple people can use the same installation
- **Professional PDF Output**: LaTeX-based PDF generation
- **Application Tracking**: Track which companies you've applied to
- **Statistics Dashboard**: View application insights
- **Edit & Regenerate**: Fine-tune generated resumes
- **Version Control**: Automatic versioning of resume PDFs

## System Requirements

- **Docker**: Version 20.10 or higher
- **Memory**: At least 2GB RAM recommended
- **Disk Space**: ~1.5GB for Docker image + space for your resume files

## Support

For issues:
1. Check this troubleshooting guide
2. Review container logs: `docker logs resume-generator`
3. Verify API key is valid
4. Make sure Documents/SyncedIn folder is accessible

---

## Example Workflow

1. **First Time Setup**
   - Run the Docker container
   - Complete the setup wizard (API key + name)

2. **Generate a Resume**
   - Go to **Generate Resume** tab
   - Enter company name and job description
   - Click **Generate**
   - Your tailored resume PDF is created!

3. **Fine-Tune**
   - Go to **Edit & Regenerate** tab
   - Select/deselect experience bullets
   - Choose different skills
   - Click **Regenerate PDF**

4. **Track Applications**
   - Go to **Application Stats** tab
   - View all companies you've applied to
   - Mark when you hear back

5. **Find Your PDFs**
   - Open `Documents/SyncedIn/YourName/Resumes/`
   - PDFs are organized by company name
   - Copy and send to employers!

---

Built with ❤️ using Claude AI, Streamlit, and LaTeX
