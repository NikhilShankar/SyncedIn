# SyncedIn Resume Generator - Usage Guide

AI-powered resume generation system with multi-user support, built with Claude AI and LaTeX.

---

## Table of Contents
- [Quick Start for End Users](#for-end-users)
- [Publishing to Docker Hub](#for-publishers-publishing-to-docker-hub)
- [Features](#features)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## For End Users

### Quick Start (Recommended: Docker Compose)

**Prerequisites:**
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Text editor (to customize docker-compose.yml if needed)

#### Method 1: Using Docker Compose (Easiest)

1. **Download the docker-compose.yml file**
   ```bash
   # Create a project folder
   mkdir syncedin-resume
   cd syncedin-resume

   # Download docker-compose.yml
   curl -O https://raw.githubusercontent.com/your-repo/syncedin-resume/main/docker-compose.yml
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Open the app**
   - Visit: **http://localhost:8765**
   - Complete the setup wizard:
     - Enter your Anthropic API Key ([get one here](https://console.anthropic.com/))
     - Select AI model (Claude Sonnet 4.5 recommended)
     - Enter your name

**That's it!** 🎉

**Manage the app:**
```bash
# View logs
docker-compose logs -f

# Stop the app
docker-compose down

# Restart the app
docker-compose restart

# Update to latest version
docker-compose pull
docker-compose up -d
```

---

#### Method 2: Using Docker Run (Manual)

**Step 1: Pull the Docker Image**
```bash
docker pull niks1267/syncedin-resume:v2Nov1
```

**Step 2: Run the Container**
```bash
# Windows (PowerShell)
docker run -d -p 8765:8765 -v $env:USERPROFILE\Documents\SyncedIn:/data --name resume-generator niks1267/syncedin-resume:v2Nov1

# Linux/Mac
docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data --name resume-generator niks1267/syncedin-resume:v2Nov1
```

**Step 3: Open the App**
- Visit: **http://localhost:8765**
- Complete the setup wizard

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

### Using Docker Compose (Recommended)

**View Logs:**
```bash
docker-compose logs -f
```

**Stop the App:**
```bash
docker-compose down
```

**Start the App:**
```bash
docker-compose up -d
```

**Restart the App:**
```bash
docker-compose restart
```

**Update to Latest Version:**
```bash
docker-compose pull
docker-compose up -d
```

**Rebuild After Code Changes:**
```bash
docker-compose up --build
```

---

### Using Docker Run (Manual)

**View Logs:**
```bash
docker logs resume-generator
```

**Stop the Container:**
```bash
docker stop resume-generator
```

**Start the Container:**
```bash
docker start resume-generator
```

**Restart the Container:**
```bash
docker restart resume-generator
```

**Remove the Container:**
```bash
docker stop resume-generator
docker rm resume-generator
```

**Update to Latest Version:**
```bash
# Stop and remove old container
docker stop resume-generator
docker rm resume-generator

# Pull latest image
docker pull niks1267/syncedin-resume:v2Nov1

# Run new container
docker run -d -p 8765:8765 -v ~/Documents/SyncedIn:/data --name resume-generator niks1267/syncedin-resume:v2Nov1
```

**Note:** Your data in `Documents/SyncedIn` (or `local_data` if using Docker Compose) is preserved across updates!

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

### Core Features
- **AI-Powered Resume Generation**: Uses Claude AI to intelligently tailor resumes to job descriptions
- **Multi-User Support**: Multiple people can use the same installation with isolated data
- **Professional PDF Output**: LaTeX-based PDF generation for polished, ATS-friendly resumes
- **Application Tracking**: Track which companies you've applied to and their status
- **Statistics Dashboard**: View application insights and analytics
- **Edit & Regenerate**: Fine-tune generated resumes with manual edits
- **Version Control**: Automatic versioning of resume PDFs (v1, v2, v3...)

### New Features
- **Dynamic Profile Links**: Add any social/professional links (LinkedIn, GitHub, Portfolio, YouTube, etc.)
  - No more hardcoded fields - add what you need!
  - Links appear as clickable hyperlinks in PDF, separated by pipes
  - Manage via Settings page or Edit Resume page

- **Customizable Display Settings**:
  - Toggle sections on/off (Summary, Experience, Skills, Projects, Education)
  - Rename section titles to match your style
  - Customize skill category names

- **Docker Compose Support**: Simplified deployment with single-command setup

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

### First Time Setup

1. **Launch the App**
   ```bash
   docker-compose up -d
   ```
   Visit: http://localhost:8765

2. **Complete Setup Wizard**
   - Enter your Anthropic API key
   - Select Claude Sonnet 4.5 (recommended)
   - Enter your name

3. **Configure Your Profile Links** (New!)
   - Go to **Settings** → **Profile Links** tab
   - Add your professional links:
     - LinkedIn: `https://linkedin.com/in/yourprofile`
     - GitHub: `https://github.com/yourusername`
     - Portfolio: `https://yourportfolio.com`
     - Any other links you want on your resume!
   - Click **Add Link** for each one

4. **Edit Your Resume Data**
   - Go to **Edit Resume Data** page
   - Add your work experience, skills, projects, education
   - Save changes

---

### Generating a Resume

1. **Go to "Generate Resume" Tab**
   - Enter **Company Name** (e.g., "Google")
   - Paste the **Job Description**

2. **Choose Options**
   - **Rewrite Mode**: AI rewrites bullets to match job description
   - **Exact Mode**: Uses your original bullet points

3. **Click "Generate Resume"**
   - AI selects best content for the job
   - PDF is generated with LaTeX
   - Opens automatically when ready

4. **Find Your PDF**
   - Saved in: `Documents/SyncedIn/YourName/Resumes/Google/`
   - Filename: `Google_1.pdf` (version numbers auto-increment)

---

### Fine-Tuning a Resume

1. **Go to "Edit & Regenerate" Tab**
   - Select the company/resume you want to edit
   - View the AI's selections

2. **Make Manual Changes**
   - Check/uncheck experience bullets
   - Add/remove skills
   - Select different projects
   - Edit summary

3. **Click "Regenerate PDF"**
   - New version created: `Google_2.pdf`
   - Previous versions preserved

---

### Managing Profile Links

**Option 1: Settings Page**
1. Go to **Settings** → **Profile Links**
2. See all current links
3. Edit titles/URLs inline
4. Delete unwanted links with 🗑️ button
5. Add new links with the form at bottom
6. Click **Save All Changes**

**Option 2: Edit Resume Page**
1. Go to **Edit Resume Data** → **Static Info** section
2. Scroll to **Profile Links** area
3. Edit, add, or delete links
4. Click **Save Links**

**Your links appear in PDFs like this:**
```
LinkedIn | GitHub | Portfolio
```
(All clickable hyperlinks, separated by pipes)

---

### Tracking Applications

1. **Go to "Application Stats" Tab**
2. View all companies you've generated resumes for
3. Track:
   - Number of resume versions
   - Application dates
   - Response status
4. Export to CSV for external tracking

---

### Multi-User Features

**Create Additional Users:**
1. **Settings** → **User Management**
2. Click **+ Create New User**
3. Enter name and click **Create**

**Switch Between Users:**
1. **Settings** → **User Management**
2. Select user from dropdown
3. Click **Switch**

Each user has completely isolated:
- Resume data
- Generated PDFs
- Profile links
- Application tracking
- Settings

---

## Advanced Usage

### Customizing Display Settings

1. Go to **Edit Resume Data** → **Display Settings**
2. Toggle sections on/off:
   - ☑️ Professional Summary
   - ☑️ Experience
   - ☐ Skills (hide if not relevant)
   - ☑️ Education
   - ☑️ Projects

3. Rename section titles:
   - "Professional Summary" → "About Me"
   - "Professional Experience" → "Work History"
   - "Personal Projects" → "Key Projects"

4. Customize skill categories:
   - Default: Languages, Platforms, Skills, Frameworks, Tools, Database
   - Change to whatever you need!

---

## For Publishers (Publishing to Docker Hub)

### Prerequisites
- Docker installed
- Docker Hub account ([sign up here](https://hub.docker.com/signup))
- Git Bash or Linux terminal (for line ending conversion)

### Steps to Publish

1. **Fix Line Endings (Important!)**
   ```bash
   # Convert entrypoint.sh to Unix line endings
   dos2unix entrypoint.sh
   # Or if dos2unix not available:
   sed -i 's/\r$//' entrypoint.sh
   ```

2. **Login to Docker Hub**
   ```bash
   docker login
   ```

3. **Build the Image**
   ```bash
   # Replace with your Docker Hub username and version
   docker build -t yourusername/syncedin-resume:v2Nov1 .
   docker build -t yourusername/syncedin-resume:latest .
   ```

4. **Test Locally**
   ```bash
   # Test with docker-compose
   docker-compose up

   # Or test with docker run
   docker run -d -p 8765:8765 -v ./local_data:/data yourusername/syncedin-resume:latest
   ```
   Visit `http://localhost:8765` to verify everything works.

5. **Push to Docker Hub**
   ```bash
   docker push yourusername/syncedin-resume:v2Nov1
   docker push yourusername/syncedin-resume:latest
   ```

6. **Update docker-compose.yml**
   - Edit `docker-compose.yml`
   - Change `image: niks1267/syncedin-resume:v2Nov1` to your image name
   - Commit and push to your repository

### Updating the Image

```bash
# Make your code changes

# Fix line endings
dos2unix entrypoint.sh

# Rebuild
docker build -t yourusername/syncedin-resume:v2Nov2 .
docker build -t yourusername/syncedin-resume:latest .

# Test
docker-compose up

# Push
docker push yourusername/syncedin-resume:v2Nov2
docker push yourusername/syncedin-resume:latest
```

### Publishing Checklist

- [ ] Line endings fixed in `entrypoint.sh`
- [ ] All new features tested locally
- [ ] Docker image builds successfully
- [ ] docker-compose.yml updated with new image tag
- [ ] Usage.md updated with new features
- [ ] Pushed to Docker Hub
- [ ] README updated with new image name

---

## Support & Contributing

**Issues or Questions?**
- Check the [Troubleshooting](#troubleshooting) section
- Review container logs: `docker-compose logs -f`
- Verify your API key is valid
- Make sure Documents/SyncedIn folder is accessible

**Want to Contribute?**
- Fork the repository
- Make your changes
- Test with docker-compose
- Submit a pull request

---

Built with ❤️ using Claude AI, Streamlit, and LaTeX
