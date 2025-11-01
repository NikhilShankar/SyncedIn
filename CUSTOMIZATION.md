# Resume Template Customization Guide

This guide explains how to customize section titles, enable/disable sections, and personalize your resume layout using the `display_settings` configuration.

## Overview

The `display_settings` section in your `resume_data_enhanced.json` allows you to:
- **Customize section titles** (e.g., "Professional Summary" → "Career Highlights")
- **Enable/disable sections** (e.g., hide Projects section)
- **Rename skill categories** (e.g., "Languages" → "Programming Languages")

## Configuration Structure

Add or modify the `display_settings` section in your `resume_data_enhanced.json`:

```json
{
  "display_settings": {
    "sections": {
      "summary": {
        "enabled": true,
        "title": "Professional Summary"
      },
      "experience": {
        "enabled": true,
        "title": "Professional Experience"
      },
      "skills": {
        "enabled": true,
        "title": "Technical Skills",
        "categories": [
          "Languages",
          "Platforms",
          "Skills",
          "Frameworks",
          "Tools",
          "Database"
        ]
      },
      "education": {
        "enabled": true,
        "title": "Education"
      },
      "projects": {
        "enabled": true,
        "title": "Personal Projects"
      }
    }
  }
}
```

## Common Customizations

### 1. Change Section Titles

Modify the `title` field for any section:

```json
{
  "display_settings": {
    "sections": {
      "summary": {
        "enabled": true,
        "title": "Career Highlights"  // Changed from "Professional Summary"
      },
      "skills": {
        "enabled": true,
        "title": "Core Competencies",  // Changed from "Technical Skills"
        "categories": ["Languages", "Platforms", "Skills", "Frameworks", "Tools", "Database"]
      }
    }
  }
}
```

### 2. Disable Sections

Set `enabled` to `false` to completely remove a section:

```json
{
  "display_settings": {
    "sections": {
      "projects": {
        "enabled": false,  // Projects section will not appear
        "title": "Personal Projects"
      }
    }
  }
}
```

**Use cases:**
- Hide projects if you have extensive work experience
- Disable summary for internship/entry-level resumes
- Remove sections that don't apply to the specific job

### 3. Customize Skill Category Names

The `categories` array in the skills section maps to your skill data in this order:
1. `categories[0]` → `skills.languages`
2. `categories[1]` → `skills.platforms`
3. `categories[2]` → `skills.skills`
4. `categories[3]` → `skills.frameworks`
5. `categories[4]` → `skills.tools`
6. `categories[5]` → `skills.database`

**Example - Professional rename:**
```json
{
  "skills": {
    "enabled": true,
    "title": "Technical Expertise",
    "categories": [
      "Programming Languages",
      "Development Platforms",
      "Core Competencies",
      "Frameworks & Libraries",
      "Development Tools",
      "Databases"
    ]
  }
}
```

**Example - Simplified rename:**
```json
{
  "skills": {
    "enabled": true,
    "title": "Skills",
    "categories": [
      "Languages",
      "Platforms",
      "Abilities",
      "Technologies",
      "Tools",
      "Data"
    ]
  }
}
```

## Real-World Examples

### Example 1: Senior Engineer Resume

Focus on experience, downplay projects:

```json
{
  "display_settings": {
    "sections": {
      "summary": {
        "enabled": true,
        "title": "Executive Summary"
      },
      "experience": {
        "enabled": true,
        "title": "Professional Experience"
      },
      "skills": {
        "enabled": true,
        "title": "Technical Leadership",
        "categories": [
          "Languages",
          "Platforms",
          "Expertise",
          "Frameworks",
          "Tools",
          "Database"
        ]
      },
      "education": {
        "enabled": true,
        "title": "Education"
      },
      "projects": {
        "enabled": false,
        "title": "Personal Projects"
      }
    }
  }
}
```

### Example 2: Career Changer / Student Resume

Emphasize projects and skills:

```json
{
  "display_settings": {
    "sections": {
      "summary": {
        "enabled": true,
        "title": "About Me"
      },
      "experience": {
        "enabled": true,
        "title": "Work Experience"
      },
      "skills": {
        "enabled": true,
        "title": "Technical Skills",
        "categories": [
          "Languages",
          "Tools & Platforms",
          "Skills",
          "Frameworks",
          "Technologies",
          "Databases"
        ]
      },
      "education": {
        "enabled": true,
        "title": "Education & Certifications"
      },
      "projects": {
        "enabled": true,
        "title": "Featured Projects"
      }
    }
  }
}
```

### Example 3: Freelancer / Consultant Resume

Different terminology for independent work:

```json
{
  "display_settings": {
    "sections": {
      "summary": {
        "enabled": true,
        "title": "Professional Profile"
      },
      "experience": {
        "enabled": true,
        "title": "Client Engagements"
      },
      "skills": {
        "enabled": true,
        "title": "Areas of Expertise",
        "categories": [
          "Languages",
          "Platforms",
          "Specializations",
          "Frameworks",
          "Tools",
          "Technologies"
        ]
      },
      "education": {
        "enabled": true,
        "title": "Qualifications"
      },
      "projects": {
        "enabled": true,
        "title": "Portfolio Highlights"
      }
    }
  }
}
```

## Important Notes

1. **Backward Compatibility**: If `display_settings` is not present, the system uses default values
2. **Skill Categories Order**: Must match the order: languages, platforms, skills, frameworks, tools, database
3. **Empty Sections**: Sections with no content won't appear even if enabled
4. **LLM Integration**: The LLM will respect these settings when generating resumes

## Troubleshooting

**Q: My custom titles aren't showing up**
- Ensure `display_settings` is at the same level as `config` and `static_info` in your JSON
- Check for JSON syntax errors (missing commas, quotes)
- Verify the section name matches exactly: `summary`, `experience`, `skills`, `education`, `projects`

**Q: Skill categories are in wrong order**
- The categories array must have exactly 6 elements
- Order must be: Languages, Platforms, Skills, Frameworks, Tools, Database
- You can change the names but not the order or count

**Q: Section still appears even when disabled**
- Make sure `"enabled": false` (lowercase, boolean)
- Regenerate the resume (changes don't apply to existing PDFs)

## Testing Your Changes

After modifying `display_settings`:

1. Save your `resume_data_enhanced.json`
2. Generate a new resume through the Streamlit app or run:
   ```bash
   python fill_latex_template_v2.py
   ```
3. Check the generated PDF to verify your customizations
4. Adjust as needed and regenerate

## Tips for Best Results

- **Keep titles concise**: Long section titles may not format well
- **Be consistent**: Use similar naming style across all sections
- **Consider your audience**: Use industry-standard terminology
- **Test thoroughly**: Generate a sample resume before final use
- **Save backups**: Keep copies of working configurations

---

For more information, see the main README.md or contact support.
