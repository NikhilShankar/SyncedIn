#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resume JSON Migration Script
Migrates resume JSON from v1.0 (hardcoded skill categories) to v2.0 (flexible skill sections)
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
import shutil

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_json_version(data):
    """Get the version of the resume JSON format"""
    return data.get('version', '1.0')


def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = file_path.parent / f"{file_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path


def migrate_v1_to_v2(data):
    """
    Migrate from v1.0 to v2.0 format

    v1.0 format:
    {
      "skills": {
        "languages": [...],
        "languages_mandatory": [...],
        "platforms": [...],
        "platforms_mandatory": [...],
        ...
      },
      "config": {
        "skills_per_category": {
          "languages": {"min": 5, "max": 8},
          ...
        }
      }
    }

    v2.0 format:
    {
      "version": "2.0",
      "skills": [
        {
          "title": "Languages",
          "items": [...],
          "mandatoryItems": [...],
          "min": 5,
          "max": 8
        },
        ...
      ]
    }
    """

    if 'skills' not in data or not isinstance(data['skills'], dict):
        print("⚠️  No skills section found or already in v2.0 format")
        return data

    old_skills = data['skills']

    # Check if already in v2.0 format (array-based)
    if isinstance(old_skills, list):
        print("ℹ️  Skills already in v2.0 format (array-based)")
        data['version'] = '2.0'
        return data

    # Get skills constraints from config
    skills_config = data.get('config', {}).get('skills_per_category', {})

    # Define the standard category order and their display titles with default min/max
    category_mapping = [
        ('languages', 'Languages', 5, 8),
        ('platforms', 'Platforms', 5, 8),
        ('skills', 'Skills', 8, 12),
        ('frameworks', 'Frameworks', 8, 15),
        ('tools', 'Tools', 6, 10),
        ('database', 'Database', 4, 6)
    ]

    new_skills = []

    for category_key, display_title, default_min, default_max in category_mapping:
        items = old_skills.get(category_key, [])
        mandatory_items = old_skills.get(f"{category_key}_mandatory", [])

        if items:  # Only add if there are items
            # Get min/max from config or use defaults
            category_config = skills_config.get(category_key, {})
            min_count = category_config.get('min', default_min)
            max_count = category_config.get('max', default_max)

            skill_section = {
                "title": display_title,
                "items": items,
                "mandatoryItems": mandatory_items,
                "min": min_count,
                "max": max_count
            }
            new_skills.append(skill_section)
            print(f"  ✓ Migrated {display_title}: {len(items)} items, {len(mandatory_items)} mandatory, min={min_count}, max={max_count}")

    # Update data with new structure
    data['skills'] = new_skills
    data['version'] = '2.0'

    print(f"✅ Migrated {len(new_skills)} skill sections to v2.0 format")
    return data


def migrate_file(file_path, dry_run=False):
    """
    Migrate a resume JSON file

    Args:
        file_path: Path to the JSON file
        dry_run: If True, only show what would be done without modifying files
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    print(f"\n{'='*60}")
    print(f"Processing: {file_path}")
    print(f"{'='*60}\n")

    # Load JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

    # Check version
    current_version = get_json_version(data)
    print(f"Current version: {current_version}")

    if current_version == '2.0':
        print("✅ Already on version 2.0, no migration needed")
        return True

    if dry_run:
        print("\n🔍 DRY RUN MODE - No files will be modified\n")

    # Perform migration
    print(f"\nMigrating from v{current_version} to v2.0...\n")
    migrated_data = migrate_v1_to_v2(data)

    if dry_run:
        print("\n📄 Preview of migrated structure:")
        print(json.dumps({"skills": migrated_data.get('skills', [])}, indent=2)[:500] + "...")
        print("\n✅ Dry run completed. Run without --dry-run to apply changes.")
        return True

    # Backup original file
    backup_path = backup_file(file_path)

    # Write migrated data
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(migrated_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully migrated: {file_path}")
        print(f"   Backup saved as: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        print(f"   Your original file is safe at: {backup_path}")
        return False


def migrate_data_in_memory(data):
    """
    Migrate resume data in memory without touching files.

    Args:
        data: Resume data dictionary

    Returns:
        tuple: (migrated_data, success: bool, message: str)
    """
    try:
        current_version = get_json_version(data)

        if current_version == '2.0':
            return data, True, "Already on version 2.0"

        # Perform migration
        migrated_data = migrate_v1_to_v2(data)
        return migrated_data, True, f"Successfully migrated from v{current_version} to v2.0"
    except Exception as e:
        return data, False, f"Migration failed: {str(e)}"


def migrate_with_backup(file_path, backup_suffix='_v1.0_backup'):
    """
    Migrate a resume JSON file with custom backup suffix.

    Args:
        file_path: Path to the JSON file
        backup_suffix: Suffix to add to backup file (default: '_v1.0_backup')

    Returns:
        tuple: (success: bool, message: str, backup_path: str or None)
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return False, f"File not found: {file_path}", None

    # Load JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}", None
    except Exception as e:
        return False, f"Error reading file: {e}", None

    # Check version
    current_version = get_json_version(data)

    if current_version == '2.0':
        return True, "Already on version 2.0, no migration needed", None

    # Create backup with custom suffix
    backup_path = file_path.parent / f"{file_path.stem}{backup_suffix}{file_path.suffix}"

    # If backup already exists, add timestamp
    if backup_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.stem}{backup_suffix}_{timestamp}{file_path.suffix}"

    try:
        shutil.copy2(file_path, backup_path)
    except Exception as e:
        return False, f"Failed to create backup: {e}", None

    # Perform migration
    try:
        migrated_data = migrate_v1_to_v2(data)
    except Exception as e:
        return False, f"Migration failed: {e}", str(backup_path)

    # Write migrated data
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(migrated_data, f, indent=2, ensure_ascii=False)
        return True, f"Successfully migrated from v{current_version} to v2.0", str(backup_path)
    except Exception as e:
        return False, f"Error writing file: {e}. Your original file is safe at: {backup_path}", str(backup_path)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Migrate resume JSON from v1.0 to v2.0 format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to preview changes
  python migrate_resume_json.py resume_data_enhanced.json --dry-run

  # Perform actual migration
  python migrate_resume_json.py resume_data_enhanced.json

  # Migrate multiple files
  python migrate_resume_json.py resume1.json resume2.json resume3.json
        """
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='JSON file(s) to migrate'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    print("🔄 Resume JSON Migration Tool")
    print("="*60)

    success_count = 0
    total_count = len(args.files)

    for file_path in args.files:
        if migrate_file(file_path, dry_run=args.dry_run):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"📊 Migration Summary")
    print(f"{'='*60}")
    print(f"Total files: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")

    if success_count == total_count:
        print("\n✅ All migrations completed successfully!")
        return 0
    else:
        print("\n⚠️  Some migrations failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
