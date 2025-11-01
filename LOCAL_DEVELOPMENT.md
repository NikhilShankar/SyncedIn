# Running Locally - Quick Guide

## Issue You Were Facing

When running `launch.bat`, the app was:
- ❌ Using template data instead of your actual resume
- ❌ Files saved in an unknown location
- ❌ Confusing about where everything is

## ✅ FIXED!

The app now automatically detects when you're running in development mode and:
1. Uses `./local_data` folder in your project directory
2. Automatically copies your `resume_data_enhanced.json` to the user's folder
3. Shows you EXACTLY where files are saved

---

## How to Run (Simple Steps)

### First Time Setup

1. **Run the app:**
   ```bash
   launch.bat
   ```

2. **Watch the console - it will show:**
   ```
   ======================================================================
   🔧 Development mode detected: Using ./local_data
   📁 SyncedIn Data Directory: ./local_data
      Full absolute path: D:\Repos\SyncedIn\ML\local_data
      ⚠️  Will be created on first use
   ======================================================================
   ```

3. **Open browser:** `http://localhost:8501`

4. **Complete the setup wizard:**
   - Enter your API key
   - Choose a model
   - Enter your name (e.g., "Nikhil")

5. **The console will show:**
   ```
   📋 Found resume_data_enhanced.json in project directory - copying to Nikhil
   ✅ Copied existing resume_data_enhanced.json to Nikhil
   ```

6. **Your files are now here:**
   ```
   D:\Repos\SyncedIn\ML\local_data\
   ├── global_config.json
   └── Nikhil/
       ├── Resumes/           ← YOUR PDFS GO HERE!
       ├── Content/
       │   └── resume_data_enhanced.json  ← YOUR RESUME DATA (copied from project)
       └── Stats/
           └── applications_tracking.json
   ```

---

## Where Are My Files?

### Development Mode (running with launch.bat):
```
D:\Repos\SyncedIn\ML\local_data\{YourName}\Resumes\
```

**Example:**
```
D:\Repos\SyncedIn\ML\local_data\Nikhil\Resumes\Google\Google_1.pdf
```

### Docker Mode:
```
Documents/SyncedIn/{YourName}/Resumes/
```

---

## Quick Checks

### 1. Where is the app looking for files?
**Check the console when you start the app!** It shows:
```
📁 SyncedIn Data Directory: ./local_data
   Full absolute path: D:\Repos\SyncedIn\ML\local_data
```

### 2. Is my resume data being used?
**Check the console during setup!** It should show:
```
📋 Found resume_data_enhanced.json in project directory - copying to Nikhil
✅ Copied existing resume_data_enhanced.json to Nikhil
```

### 3. Where is my PDF saved?
**After generating a resume, the app shows:**
```
📁 Your PDF is saved at:
D:\Repos\SyncedIn\ML\local_data\Nikhil\Resumes\Google\Google_1.pdf
```

---

## Folder Structure

```
D:\Repos\SyncedIn\ML\
├── resume_data_enhanced.json        ← Your original resume (kept safe)
├── launch.bat                       ← Run this to start the app
├── main_app.py
└── local_data/                      ← Created automatically
    ├── global_config.json           ← API key, settings
    └── Nikhil/
        ├── Resumes/                 ← 📄 YOUR PDFs ARE HERE!
        │   ├── Google/
        │   │   ├── Google_1.pdf
        │   │   ├── Google_2.pdf
        │   │   └── Google-JobDescription.txt
        │   └── Meta/
        │       └── Meta_1.pdf
        ├── Content/
        │   └── resume_data_enhanced.json  ← Copy of your resume (used by app)
        └── Stats/
            └── applications_tracking.json
```

---

## Resetting Everything

If you want to start fresh:

1. **Stop the app** (Ctrl+C in the terminal)

2. **Delete the local_data folder:**
   ```bash
   rmdir /s local_data
   ```

3. **Run again:**
   ```bash
   launch.bat
   ```

4. **Go through setup wizard again**

Your original `resume_data_enhanced.json` in the project directory is never touched, so it's always safe!

---

## Tips

### Viewing Your PDFs
1. Open File Explorer
2. Navigate to: `D:\Repos\SyncedIn\ML\local_data\{YourName}\Resumes\`
3. PDFs are organized by company name!

### Editing Your Resume Data
**Option 1: Via File (Recommended)**
Edit `D:\Repos\SyncedIn\ML\local_data\{YourName}\Content\resume_data_enhanced.json`

**Option 2: Via Settings UI**
Go to Settings → Profile Links (for links only)

**Option 3: Edit Original**
Edit `D:\Repos\SyncedIn\ML\resume_data_enhanced.json`, then delete `local_data` folder and re-run setup

---

## Common Issues

### "Content is using template data"
**Fix:** Delete the `local_data` folder and run `launch.bat` again. The setup wizard will copy your actual resume data.

### "Can't find my PDFs"
**Fix:** Look at the console! It shows the exact path when you generate a resume.

### "Wrong resume data being used"
**Fix:** Check `local_data\{YourName}\Content\resume_data_enhanced.json` - this is what the app uses, not the one in the project root.

---

## Development vs Production

| Mode | Data Location | Used For |
|------|---------------|----------|
| **Development** (launch.bat) | `./local_data` | Testing locally |
| **Docker** | `Documents/SyncedIn` | Production use |

---

**The app is smart!** It detects which mode you're in and uses the right paths automatically.
