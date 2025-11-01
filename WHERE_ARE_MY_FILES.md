# Where Are My Generated Files?

## When Running with Docker

Your files are saved in:
- **Windows**: `C:\Users\YourName\Documents\SyncedIn\`
- **Linux/Mac**: `~/Documents/SyncedIn/`

### File Structure:
```
Documents/SyncedIn/
├── global_config.json
├── YourName/
│   ├── Resumes/
│   │   └── CompanyName/
│   │       ├── CompanyName_1.pdf          ← YOUR PDFs ARE HERE!
│   │       ├── CompanyName_2.pdf
│   │       ├── CompanyName-JobDescription.txt
│   │       └── CompanyName_1-Json.json
│   ├── Content/
│   │   └── resume_data_enhanced.json
│   └── Stats/
│       └── applications_tracking.json
```

---

## When Running Locally (with launch.bat or python main_app.py)

Your files are saved in **ONE** of these locations (checked in order):

### Option 1: Documents/SyncedIn (PREFERRED)
If your Documents folder exists:
- **Windows**: `C:\Users\YourName\Documents\SyncedIn\`
- **Linux/Mac**: `~/Documents/SyncedIn/`

### Option 2: local_data (FALLBACK)
If Documents folder doesn't exist:
- In the project directory: `D:\Repos\SyncedIn\ML\local_data\`

### How to Check?
When you start the app, look at the console/terminal output. You'll see:
```
📁 SyncedIn Data Directory: C:\Users\YourName\Documents\SyncedIn
   (Will be created on first use)
```

This tells you EXACTLY where your files will be saved!

---

## Quick Access

### Find Your Latest PDF:
1. Open the app: `http://localhost:8765`
2. Look at the top - it shows which user you're logged in as
3. Go to that folder: `Documents/SyncedIn/{YourName}/Resumes/`
4. Find the company folder
5. The highest numbered PDF is the latest: `CompanyName_3.pdf`

### Example:
If you're user "John" and generated a resume for "Google":
- **Full path**: `C:\Users\YourName\Documents\SyncedIn\John\Resumes\Google\Google_1.pdf`

---

## Troubleshooting

### "I can't find my PDFs!"

1. **Check the console output** when you start the app - it shows the data directory path
2. **Check both locations**: Documents/SyncedIn AND local_data
3. **Look for the company name folder** in `Resumes/CompanyName/`
4. **Windows users**: Make sure you're looking in `C:\Users\YourActualUsername\Documents\SyncedIn\`

### "The folder doesn't exist!"

The folders are created automatically when you:
1. Complete the first-run setup wizard
2. Generate your first resume

If you haven't done these yet, the folder won't exist.

### "I want to change the location"

Edit `config_manager.py` and modify the `get_base_data_dir()` function to return your preferred path.

---

## File Descriptions

| File | Description |
|------|-------------|
| `CompanyName_1.pdf` | Your generated resume PDF (version 1) |
| `CompanyName_2.pdf` | Updated resume (version 2) |
| `CompanyName-JobDescription.txt` | The job description you used |
| `CompanyName_1-Json.json` | The resume data used for version 1 |
| `global_config.json` | Your API key and settings |
| `resume_data_enhanced.json` | Your full resume content |
| `applications_tracking.json` | Job application tracking data |

---

**Pro Tip**: Bookmark your Resumes folder for quick access!
- Windows: `C:\Users\YourName\Documents\SyncedIn\YourName\Resumes`
- Mac: `~/Documents/SyncedIn/YourName/Resumes`
