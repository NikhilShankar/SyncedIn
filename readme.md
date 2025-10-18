# AI-Powered Resume Generator

An intelligent resume generator that uses Claude AI (Haiku) to tailor your resume to specific job descriptions. The system analyzes job requirements and automatically selects the most relevant experience bullets, skills, and projects to fit within a 2-page resume.

## Features

- 🤖 **AI-Powered Selection**: Uses Claude Haiku to intelligently select resume content
- 📄 **LaTeX Generation**: Produces professional, ATS-friendly PDFs
- 🎯 **Job-Tailored**: Customizes content based on job description
- ⚖️ **Constraint-Based**: Respects min/max limits for bullets, skills, and projects
- 📊 **Validation**: Ensures all constraints are met before generating

## Project Structure

```
.
├── resume_data_enhanced.json    # Your complete resume data with configs
├── resume_template.tex          # LaTeX template
├── llm_selector.py             # Claude AI integration
├── fill_latex_template_v2.py   # LaTeX template filler
├── main.py                     # Main orchestrator
├── requirements.txt            # Python dependencies
├── .env                        # API keys (create from .env.example)
└── generated/                  # Output directory (auto-created)
    ├── resume_filled.tex
    ├── resume_filled.pdf
    └── resume_data_trimmed.json
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install LaTeX

You need `lualatex` installed for PDF compilation:

**Windows:**
- Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://www.tug.org/texlive/)

**Mac:**
```bash
brew install --cask mactex
```

**Linux:**
```bash
sudo apt-get install texlive-full
```

### 3. Configure API Key

Create a `.env` file from the template:

```bash
cp ..env ..env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key from: https://console.anthropic.com/

## Usage

### Method 1: Using main.py (Recommended)

Edit `main.py` to set your job description, then run:

```bash
python main.py
```

### Method 2: Direct Function Call

```python
from main import generate_resume

job_description = """
Senior Android Developer
- 5+ years Android experience
- Kotlin, Jetpack Compose
- Experience with fintech apps
"""

tex_path, pdf_path = generate_resume(
   job_description=job_description,
   resume_data_path='resume_data_enhanced_default.json',
   template_path='resume_template.tex',
   output_dir='./generated'
)
```

### Method 3: Test LLM Selector Only

```bash
python llm_selector.py
```

This will test the LLM selection without compiling the PDF.

## Resume Data Configuration

Your `resume_data_enhanced.json` contains:

### 1. Config Section
```json
{
  "config": {
    "page_limit": 2,
    "bullets": {
      "total_min": 16,
      "total_max": 20
    },
    "skills_per_category": { ... },
    "projects": {
      "min": 2,
      "max": 3
    }
  }
}
```

### 2. Companies with Bullet Constraints
```json
{
  "id": "slice",
  "mandatory": true,
  "bullet_constraints": {
    "min": 4,
    "max": 6
  },
  "bullets": [
    {
      "text": "Your bullet point text...",
      "mandatory": false
    }
  ]
}
```

### 3. Skills with Mandatory Items
```json
{
  "skills": {
    "languages": ["Kotlin", "Java", ...],
    "languages_mandatory": ["Kotlin", "Java"]
  }
}
```

## How It Works

1. **Load Data**: Reads your complete resume from `resume_data_enhanced.json`
2. **LLM Selection**: 
   - Sends full resume + job description to Claude Haiku
   - Claude selects most relevant bullets, skills, and projects
   - Returns trimmed JSON in same structure
3. **Validation**: Ensures all min/max constraints are met
4. **Template Filling**: Populates LaTeX template with selected content
5. **PDF Generation**: Compiles LaTeX to professional PDF

## Output Files

- `generated/resume_filled.tex` - LaTeX source file
- `generated/resume_filled.pdf` - Final resume PDF
- `generated/resume_data_trimmed.json` - Selected content (for debugging)

## Customization

### Adjust Constraints

Edit the `config` section in `resume_data_enhanced.json`:

```json
"bullets": {
  "total_min": 18,    // Increase for more content
  "total_max": 22
}
```

### Modify Per-Company Limits

```json
{
  "id": "slice",
  "bullet_constraints": {
    "min": 5,    // More bullets for recent role
    "max": 7
  }
}
```

### Change AI Model

In `.env`:
```
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # Use Sonnet for better selection
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Ensure `.env` file exists and contains your API key
- Check the key is valid at https://console.anthropic.com/

### "lualatex command not found"
- Install TeX Live or MiKTeX (see Setup section)
- Ensure LaTeX is in your system PATH

### PDF Compilation Failed
- Check LaTeX logs in the console output
- Manually compile: `lualatex generated/resume_filled.tex`
- Common issues: Missing LaTeX packages

### Validation Errors
- LLM didn't meet constraints (rare with good prompts)
- Check `resume_data_trimmed.json` to see what was selected
- Adjust constraints in your `config` section

## Cost Estimation

Using Claude 3.5 Haiku:
- Input: ~15K tokens (full resume + job description)
- Output: ~8K tokens (trimmed resume)
- Cost per generation: ~$0.01 USD

## Next Steps

Once the basic system is working, we'll add:
- ✅ Streamlit web interface
- ✅ Job description file upload
- ✅ Multiple resume versions
- ✅ Resume comparison view

## License

MIT License - Feel free to modify and use!