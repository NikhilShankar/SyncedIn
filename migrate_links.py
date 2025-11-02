"""
Migration script to convert old profile links format to new array format.

Old format:
{
  "static_info": {
    "linkedin": "url",
    "portfolio": "url",
    "leetcode": "url"
  }
}

New format:
{
  "static_info": {
    "links": [
      {"title": "LinkedIn", "url": "url"},
      {"title": "Portfolio", "url": "url"},
      {"title": "LeetCode", "url": "url"}
    ]
  }
}
"""

import json
import sys
from pathlib import Path


def migrate_links_format(data):
    """Convert old links format to new array format."""

    if 'static_info' not in data:
        print("⚠️  No static_info found in data")
        return data

    static_info = data['static_info']

    # Check if already in new format
    if 'links' in static_info and isinstance(static_info['links'], list):
        print("[OK] Already using new links format")
        return data

    # Convert old format to new
    links = []

    if static_info.get('linkedin'):
        links.append({
            "title": "LinkedIn",
            "url": static_info['linkedin']
        })

    if static_info.get('github'):
        links.append({
            "title": "GitHub",
            "url": static_info['github']
        })

    if static_info.get('portfolio'):
        links.append({
            "title": "Portfolio",
            "url": static_info['portfolio']
        })

    if static_info.get('leetcode'):
        links.append({
            "title": "LeetCode",
            "url": static_info['leetcode']
        })

    # Add the new links array
    static_info['links'] = links

    # Remove old fields (optional - keep for backward compatibility)
    # Keeping them doesn't hurt and maintains backward compatibility
    # if 'linkedin' in static_info:
    #     del static_info['linkedin']
    # if 'portfolio' in static_info:
    #     del static_info['portfolio']
    # if 'leetcode' in static_info:
    #     del static_info['leetcode']

    print(f"[OK] Migrated {len(links)} links to new format")
    return data


def migrate_file(file_path):
    """Migrate a single JSON file."""

    print(f"\n[FILE] Processing: {file_path}")

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return False

    # Migrate
    data = migrate_links_format(data)

    # Create backup
    backup_path = Path(str(file_path) + '.backup')
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[BACKUP] Backup saved: {backup_path}")
    except Exception as e:
        print(f"[WARNING] Could not create backup: {e}")

    # Save migrated file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[OK] File updated: {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error saving file: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Migrate specific file
        file_path = sys.argv[1]
        migrate_file(file_path)
    else:
        # Migrate common files
        print("[INFO] Migrating resume data files to new links format...")

        files_to_migrate = [
            "resume_data_enhanced.json",
            "resume_data.json"
        ]

        for file_name in files_to_migrate:
            if Path(file_name).exists():
                migrate_file(file_name)
            else:
                print(f"[SKIP] Skipping {file_name} (not found)")

        print("\n[OK] Migration complete!")
        print("\nThe new format allows you to add/remove links dynamically.")
        print("You can edit them in the Settings page or directly in the JSON file.")
