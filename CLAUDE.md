# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a resume generation system with two main components:
1. **FastAPI web service** (`main.py`) - Simple REST API with basic endpoints
2. **LaTeX resume generator** (`fill_latex_template.py`) - Converts JSON resume data to customized LaTeX/PDF resumes

## Architecture

The resume generation system follows a template-based approach:
- `resume_data.json` contains structured resume data (experience, skills, projects, education)
- `resume_template.tex` is a LaTeX template with placeholders (e.g., `{{NAME}}`, `{{EXPERIENCE_ITEMS}}`)
- `fill_latex_template.py` performs template substitution and compiles to PDF

Key architectural decisions:
- **Modular content selection**: Select specific companies, projects, and summary types per resume
- **LaTeX escaping**: All user data is escaped to prevent LaTeX compilation errors
- **Font handling**: Uses Lato font family from local files via `fontspec` package

## Commands

### Running the FastAPI server
```bash
# Install FastAPI and dependencies first
pip install fastapi uvicorn

# Run the development server
uvicorn main:app --reload
```

### Generating resume PDF
```bash
# Generate resume with default selections
python fill_latex_template.py
```

### LaTeX compilation (manual)
The system uses `lualatex` for PDF compilation. Ensure you have:
- MiKTeX or TeX Live installed
- `lualatex` command available in PATH

## Key Files

- `resume_data.json` - All resume content in structured format
- `resume_template.tex` - LaTeX template with placeholders
- `fill_latex_template.py` - Main resume generation logic
- `main.py` - FastAPI web service
- `fonts/` - Lato font family files

## Development Notes

### Resume Customization
The system supports multiple resume variants by selecting:
- Summary type: `android`, `fullstack`, `ml`, `general`
- Companies with specific bullet points
- Projects subset
- All selections are defined in `fill_latex_template.py` main block

### LaTeX Template Structure
Template uses these placeholder patterns:
- `{{STATIC_VAR}}` for simple text replacement
- `{{SECTION_ITEMS}}` for dynamic content generation (experience, education, projects)

The `escape_latex_special_chars()` function handles LaTeX character escaping for user content.