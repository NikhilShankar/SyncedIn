"""
Configuration Manager for SyncedIn Resume Generator
Handles global configuration, user management, and path resolution
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def get_base_data_dir():
    """
    Get the base data directory based on environment.
    - In Docker: /data (bind mount)
    - Local dev: Check for LOCAL_DEV env var, otherwise use Documents/SyncedIn
    """
    # Check if running in Docker
    if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
        return "/data"

    # Check for LOCAL_DEV environment variable (for development)
    if os.environ.get('LOCAL_DEV') == 'true':
        print("🔧 LOCAL_DEV mode: Using ./local_data")
        return "./local_data"

    # Check if resume_data_enhanced.json exists in current directory
    # This indicates we're running in the project directory
    if os.path.exists('resume_data_enhanced.json') and os.path.exists('main_app.py'):
        print("🔧 Development mode detected: Using ./local_data (resume_data_enhanced.json found in current directory)")
        return "./local_data"

    # Production local mode - use Documents/SyncedIn
    import platform
    if platform.system() == "Windows":
        docs_path = Path(os.environ.get('USERPROFILE', '')) / 'Documents' / 'SyncedIn'
    else:
        docs_path = Path.home() / 'Documents' / 'SyncedIn'

    return str(docs_path)


# Constants
BASE_DATA_DIR = get_base_data_dir()
GLOBAL_CONFIG_FILE = "global_config.json"
RESUME_DATA_FILE = "resume_data_enhanced.json"
TRACKING_FILE = "applications_tracking.json"

# Available Claude models (full API model names)
AVAILABLE_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-3-5-sonnet-20241022",
    "claude-opus-4-20250514",
    "claude-3-5-haiku-20241022"
]

DEFAULT_GLOBAL_CONFIG = {
    "anthropic_api_key": "",
    "available_models": AVAILABLE_MODELS,
    "selected_model": "claude-sonnet-4-20250514",
    "users": [],
    "current_user": None,
    "created_at": datetime.now().isoformat(),
    "last_updated": datetime.now().isoformat()
}

# Print data directory on module load (helpful for debugging)
print("\n" + "="*70)
print(f"📁 SyncedIn Data Directory: {BASE_DATA_DIR}")
print(f"   Full absolute path: {os.path.abspath(BASE_DATA_DIR)}")
if os.path.exists(BASE_DATA_DIR):
    print(f"   ✅ Directory exists")
else:
    print(f"   ⚠️  Will be created on first use")
print("="*70 + "\n")


def get_global_config_path() -> str:
    """Get the path to global_config.json"""
    return os.path.join(BASE_DATA_DIR, GLOBAL_CONFIG_FILE)


def ensure_data_dir_exists():
    """Ensure the base data directory exists"""
    Path(BASE_DATA_DIR).mkdir(parents=True, exist_ok=True)


def load_global_config() -> Dict:
    """Load global configuration, create if doesn't exist"""
    ensure_data_dir_exists()
    config_path = get_global_config_path()

    if not os.path.exists(config_path):
        # Create default config
        save_global_config(DEFAULT_GLOBAL_CONFIG)
        return DEFAULT_GLOBAL_CONFIG.copy()

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading global config: {e}")
        return DEFAULT_GLOBAL_CONFIG.copy()


def save_global_config(config: Dict):
    """Save global configuration"""
    ensure_data_dir_exists()
    config_path = get_global_config_path()
    config['last_updated'] = datetime.now().isoformat()

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving global config: {e}")
        raise


def is_first_run() -> bool:
    """Check if this is the first run (no config exists or no users)"""
    config = load_global_config()
    return not config.get('users') or not config.get('current_user')


def get_current_user() -> Optional[str]:
    """Get the current active username"""
    config = load_global_config()
    return config.get('current_user')


def get_all_users() -> List[str]:
    """Get list of all usernames"""
    config = load_global_config()
    return config.get('users', [])


def get_api_key() -> str:
    """Get the Anthropic API key"""
    config = load_global_config()
    return config.get('anthropic_api_key', '')


def get_selected_model() -> str:
    """Get the selected model"""
    config = load_global_config()
    return config.get('selected_model', 'claude-sonnet-4-20250514')


def update_api_key(api_key: str):
    """Update the Anthropic API key"""
    config = load_global_config()
    config['anthropic_api_key'] = api_key
    save_global_config(config)


def update_selected_model(model: str):
    """Update the selected model"""
    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Invalid model: {model}")

    config = load_global_config()
    config['selected_model'] = model
    save_global_config(config)


def get_user_base_dir(username: str) -> str:
    """Get the base directory for a user"""
    return os.path.join(BASE_DATA_DIR, username)


def get_user_paths(username: str) -> Dict[str, str]:
    """Get all paths for a specific user"""
    base_dir = get_user_base_dir(username)
    return {
        'base_dir': base_dir,
        'resumes_dir': os.path.join(base_dir, 'Resumes'),
        'content_dir': os.path.join(base_dir, 'Content'),
        'stats_dir': os.path.join(base_dir, 'Stats'),
        'resume_data': os.path.join(base_dir, 'Content', RESUME_DATA_FILE),
        'tracking_file': os.path.join(base_dir, 'Stats', TRACKING_FILE),
    }


def create_user_directories(username: str):
    """Create directory structure for a new user"""
    paths = get_user_paths(username)

    # Create directories
    Path(paths['resumes_dir']).mkdir(parents=True, exist_ok=True)
    Path(paths['content_dir']).mkdir(parents=True, exist_ok=True)
    Path(paths['stats_dir']).mkdir(parents=True, exist_ok=True)

    # Create empty tracking file
    if not os.path.exists(paths['tracking_file']):
        with open(paths['tracking_file'], 'w', encoding='utf-8') as f:
            json.dump([], f)

    print(f"Created directories for user: {username}")


def copy_template_resume(username: str):
    """Copy template resume to user's content directory"""
    paths = get_user_paths(username)

    # Check if user already has a resume file
    if os.path.exists(paths['resume_data']):
        print(f"Resume data already exists for {username}")
        return

    # Priority 1: Check if resume_data_enhanced.json exists in current directory (development mode)
    if os.path.exists('resume_data_enhanced.json'):
        try:
            print(f"📋 Found resume_data_enhanced.json in project directory - copying to {username}")
            with open('resume_data_enhanced.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            with open(paths['resume_data'], 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Copied existing resume_data_enhanced.json to {username}")
            return
        except Exception as e:
            print(f"⚠️  Error copying resume_data_enhanced.json: {e}")
            # Fall through to template

    # Priority 2: Use resume_template_minimal.json
    template_file = "resume_template_minimal.json"
    if os.path.exists(template_file):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)

            with open(paths['resume_data'], 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            print(f"📝 Copied template resume to {username}")
        except Exception as e:
            print(f"⚠️  Error copying template: {e}")
    else:
        # Priority 3: Create a basic empty structure if template doesn't exist
        basic_resume = {
            "config": {
                "page_limit": 2,
                "bullets": {"total_min": 16, "total_max": 24}
            },
            "static_info": {
                "name": "Your Name",
                "address": "Your Address",
                "phone": "+1234567890",
                "email": "your.email@example.com",
                "links": [
                    {"name": "LinkedIn", "url": "https://linkedin.com/in/yourprofile", "icon": "linkedin"},
                    {"name": "GitHub", "url": "https://github.com/yourusername", "icon": "github"}
                ]
            },
            "summaries": [
                {
                    "id": "summary_1",
                    "label": "General",
                    "text": "Your professional summary here..."
                }
            ],
            "skills": {
                "languages": ["Python", "JavaScript"],
                "languages_mandatory": ["Python"],
                "frameworks": ["React", "Node.js"],
                "frameworks_mandatory": ["React"],
                "platforms": ["AWS", "Docker"],
                "platforms_mandatory": ["AWS"],
                "tools": ["Git", "VS Code"],
                "tools_mandatory": ["Git"],
                "database": ["PostgreSQL"],
                "database_mandatory": ["PostgreSQL"]
            },
            "companies": [],
            "education": [],
            "projects": []
        }

        with open(paths['resume_data'], 'w', encoding='utf-8') as f:
            json.dump(basic_resume, f, indent=2, ensure_ascii=False)

        print(f"📝 Created basic resume template for {username}")


def create_user(username: str) -> bool:
    """
    Create a new user with directory structure and template resume
    Returns True if successful, False if user already exists
    """
    # Sanitize username (replace spaces with underscores, alphanumeric only)
    username = username.strip().replace(' ', '_')
    username = ''.join(c for c in username if c.isalnum() or c == '_')

    if not username:
        raise ValueError("Invalid username")

    config = load_global_config()

    # Check if user already exists
    if username in config.get('users', []):
        return False

    # Create user directories and files
    create_user_directories(username)
    copy_template_resume(username)

    # Add user to config
    if 'users' not in config:
        config['users'] = []
    config['users'].append(username)

    # If this is the first user, set as current
    if not config.get('current_user'):
        config['current_user'] = username

    save_global_config(config)
    return True


def switch_user(username: str) -> bool:
    """
    Switch to a different user
    Returns True if successful, False if user doesn't exist
    """
    config = load_global_config()

    if username not in config.get('users', []):
        return False

    config['current_user'] = username
    save_global_config(config)
    return True


def initialize_first_user(username: str, api_key: str, model: str = "claude-sonnet-4-20250514"):
    """Initialize the system with the first user during setup"""
    # Sanitize username
    username = username.strip().replace(' ', '_')
    username = ''.join(c for c in username if c.isalnum() or c == '_')

    if not username:
        raise ValueError("Invalid username")

    if model not in AVAILABLE_MODELS:
        raise ValueError(f"Invalid model: {model}")

    # Create user
    create_user(username)

    # Update global config
    config = load_global_config()
    config['anthropic_api_key'] = api_key
    config['selected_model'] = model
    config['current_user'] = username
    save_global_config(config)

    print(f"Initialized system with user: {username}")


def get_current_user_paths() -> Optional[Dict[str, str]]:
    """Get paths for the current active user"""
    current_user = get_current_user()
    if not current_user:
        return None
    return get_user_paths(current_user)
