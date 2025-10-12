"""
Main orchestrator for the AI-powered resume generator.

This script:
1. Loads the full resume data from JSON
2. Takes a job description as input
3. Uses Claude Haiku to select the most relevant content
4. Fills the LaTeX template with the selected content
5. Compiles the LaTeX to PDF
"""

import os
import json
import sys
from llm_selector import ResumeSelector
from fill_latex_template_v2 import fill_latex_template, compile_latex_to_pdf


def generate_resume(job_description, resume_data_path='resume_data_enhanced.json',
                   template_path='resume_template.tex', output_dir='./generated'):
    """
    Generate a tailored resume based on job description.

    Args:
        job_description: Job description text to tailor the resume for
        resume_data_path: Path to the full resume data JSON file
        template_path: Path to the LaTeX template file
        output_dir: Directory to save generated files

    Returns:
        tuple: (tex_path, pdf_path, validation_result)
            - tex_path: Path to generated .tex file
            - pdf_path: Path to generated .pdf file (or None if compilation failed)
            - validation_result: (is_valid: bool, message: str)
    """

    print("="*70)
    print("AI-POWERED RESUME GENERATOR")
    print("="*70)

    # 1. Load full resume data
    print(f"\n📂 Loading resume data from: {resume_data_path}")
    try:
        with open(resume_data_path, 'r') as f:
            full_resume_data = json.load(f)
        print(f"   ✅ Loaded successfully")
    except FileNotFoundError:
        print(f"   ❌ Error: File not found - {resume_data_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"   ❌ Error: Invalid JSON format in {resume_data_path}")
        sys.exit(1)

    # 2. Use LLM to select relevant content
    print(f"\n🤖 Using Claude Haiku to select relevant content...")
    print(f"   Job Description Preview: {job_description[:100]}...")

    try:
        selector = ResumeSelector()
        trimmed_resume_data, (is_valid, validation_message) = selector.select_resume_content(full_resume_data, job_description)
        print(f"   ✅ Content selection complete")

        # Print selection summary
        total_bullets = sum(len(c['bullets']) for c in trimmed_resume_data['companies'])
        print(f"\n   📊 Selection Summary:")
        print(f"      - Total bullets: {total_bullets}")
        print(f"      - Companies: {len(trimmed_resume_data['companies'])}")
        print(f"      - Projects: {len(trimmed_resume_data['projects'])}")
        print(f"      - Summary type: {list(trimmed_resume_data['summaries'].keys())[0]}")

        # Show validation status
        if not is_valid:
            print(f"\n   ⚠️  Validation warnings detected (see above)")
            print(f"   💡 PDF will still be generated for review")

    except Exception as e:
        print(f"   ❌ Error during LLM selection: {e}")
        raise

    # 3. Save trimmed data (for debugging/inspection)
    trimmed_json_path = os.path.join(output_dir, 'resume_data_trimmed.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(trimmed_json_path, 'w') as f:
        json.dump(trimmed_resume_data, f, indent=2)
    print(f"\n   💾 Trimmed data saved to: {trimmed_json_path}")

    # 4. Fill LaTeX template
    print(f"\n📝 Filling LaTeX template...")
    tex_output_path = os.path.join(output_dir, 'resume_filled.tex')

    try:
        filled_tex = fill_latex_template(
            template_path=template_path,
            trimmed_resume_data=trimmed_resume_data,
            output_path=tex_output_path
        )
        print(f"   ✅ LaTeX file generated: {filled_tex}")
    except Exception as e:
        print(f"   ❌ Error filling template: {e}")
        raise

    # 5. Compile to PDF
    print(f"\n🔨 Compiling LaTeX to PDF...")

    try:
        pdf_path = compile_latex_to_pdf(filled_tex, output_dir=output_dir)

        if pdf_path:
            print(f"   ✅ Resume PDF generated: {pdf_path}")
        else:
            print(f"   ❌ PDF compilation failed - please check LaTeX logs")
            print(f"   💡 You can manually compile: {filled_tex}")
            pdf_path = None
    except Exception as e:
        print(f"   ❌ Error during PDF compilation: {e}")
        pdf_path = None

    # 6. Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\n📄 Generated Files:")
    print(f"   - LaTeX: {filled_tex}")
    if pdf_path:
        print(f"   - PDF: {pdf_path}")
    print(f"   - Trimmed Data: {trimmed_json_path}")

    if not is_valid:
        print(f"\n⚠️  Validation Issues Detected:")
        print(f"   {validation_message.replace(chr(10), chr(10) + '   ')}")
        print(f"\n   💡 Review the PDF and trimmed JSON to verify results")

    return filled_tex, pdf_path, (is_valid, validation_message)


def main():
    """Main entry point with example usage."""

    # Example job description
    job_description = """
    Senior Android Developer - Fintech
    
    We are seeking an experienced Android developer to join our growing fintech team.
    
    Key Requirements:
    - 5+ years of Android development experience
    - Expert proficiency in Kotlin and Java
    - Strong experience with Jetpack Compose and modern Android architecture (MVVM/MVI)
    - Experience with payment systems and financial applications
    - Proficient in CI/CD pipelines, unit testing, and performance optimization
    - Experience mentoring junior developers and conducting code reviews
    
    Nice to Have:
    - Experience with UPI payment systems
    - Background in fintech or banking applications
    - Knowledge of Clean Architecture principles
    - Experience with microservices architecture
    """

    # You can also read job description from a file:
    # with open('job_description.txt', 'r') as f:
    #     job_description = f.read()

    try:
        generate_resume(
            job_description=job_description,
            resume_data_path='resume_data_enhanced.json',
            template_path='resume_template.tex',
            output_dir='./generated'
        )
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()