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
      {"name": "LinkedIn", "url": "url", "icon": "linkedin"},
      {"name": "Portfolio", "url": "url", "icon": "web"},
      {"name": "LeetCode", "url": "url", "icon": "code"}
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
        print("✅ Already using new links format")
        return data

    # Convert old format to new
    links = []

    if static_info.get('linkedin'):
        links.append({
            "name": "LinkedIn",
            "url": static_info['linkedin'],
            "icon": "linkedin"
        })

    if static_info.get('github'):
        links.append({
            "name": "GitHub",
            "url": static_info['github'],
            "icon": "github"
        })

    if static_info.get('portfolio'):
        links.append({
            "name": "Portfolio",
            "url": static_info['portfolio'],
            "icon": "web"
        })

    if static_info.get('leetcode'):
        links.append({
            "name": "LeetCode",
            "url": static_info['leetcode'],
            "icon": "code"
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

    print(f"✅ Migrated {len(links)} links to new format")
    return data


def migrate_file(file_path):
    """Migrate a single JSON file."""

    print(f"\n📄 Processing: {file_path}")

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Migrate
    data = migrate_links_format(data)

    # Create backup
    backup_path = Path(str(file_path) + '.backup')
    try:
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Backup saved: {backup_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")

    # Save migrated file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ File updated: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Migrate specific file
        file_path = sys.argv[1]
        migrate_file(file_path)
    else:
        # Migrate common files
        print("🔄 Migrating resume data files to new links format...")

        files_to_migrate = [
            "resume_data_enhanced.json",
            "resume_data.json"
        ]

        for file_name in files_to_migrate:
            if Path(file_name).exists():
                migrate_file(file_name)
            else:
                print(f"⏭️  Skipping {file_name} (not found)")

        print("\n✅ Migration complete!")
        print("\nThe new format allows you to add/remove links dynamically.")
        print("You can edit them in the Settings page or directly in the JSON file.")
