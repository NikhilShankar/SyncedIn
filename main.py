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
from datetime import date


def generate_resume(job_description, resume_data_path='resume_data_enhanced.json',
                   template_path='resume_template.tex', base_output_dir='./generated', shouldRewrite=False):
    """
    Generate a tailored resume based on job description.

    Args:
        job_description: Job description text to tailor the resume for
        resume_data_path: Path to the full resume data JSON file
        template_path: Path to the LaTeX template file
        base_output_dir: Directory to save generated files

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
        trimmed_resume_data, (is_valid, validation_message) = selector.select_resume_content(full_resume_data, job_description, should_rewrite_selected=shouldRewrite)
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
    # 1. Get the current date
    current_date = date.today()

    # 2. Format the date as DD-MM-YYYY
    formatted_date = current_date.strftime("%d-%m-%Y")

    # 3. Print the result
    print(formatted_date)
    output_dir = os.path.join(base_output_dir, f"""{trimmed_resume_data["title"]}-{formatted_date}""")
    trimmed_json_path = os.path.join(output_dir, 'resume_data_trimmed.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(trimmed_json_path, 'w') as f:
        json.dump(trimmed_resume_data, f, indent=2)
    print(f"\n   💾 Trimmed data saved to: {trimmed_json_path}")
    print(f"Returned response from LLM : {trimmed_resume_data}")

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
    About the job
About League

Founded in 2014, League is the leading healthcare consumer experience (CX) platform, powered by artificial intelligence (AI), reaching more than 63 million people around the world and delivering the highest level of personalization in the industry. Payers, providers, and consumer health partners build on League’s platform to deliver high-engagement healthcare solutions proven to improve health outcomes. League has raised over $285 million in venture capital funding to date, powering the digital experiences for some of healthcare’s most trusted brands, including Highmark Health, Manulife, Medibank, and Shoppers Drug Mart.

Why join League

Make an impact - Your work will directly improve the health outcomes of millions of lives
Cutting-edge Technology: Work with sophisticated tech stack: Kotlin, Jetpack Compose and scalable architectures
Inclusive culture: Be part of a globally distributed team working collaboratively

The Role

As Senior Software Engineer, Android, you build native mobile applications for Android. You work as part of a small cross-functional team to deliver features on our roadmap, as well as continually maintaining and improving a specific area of our product. You are responsible for large pieces of work, as well as setting best practices.

The team is a fast-moving, collaborative group dedicated to delivering high-quality features for our clients. We are passionate about positively impacting Canadians' lives through innovative health solutions that leverage our platform offerings. We value continuous learning, open communication, and a commitment to excellence.

In This Role, You Will

Build, test and maintain native mobile applications, with an emphasis on leveraging Jetpack Compose, Navigation, CLEAN Architecture and MVI for building modern and performant user interfaces. 
Ability to work with CI tools to support mobile builds and releases
Participate in technical design and planning discussions
Uphold standards for quality by performing code reviews, fixing bugs, creating automated tests, and monitoring performance
Collaborate with UX designers to build polished user interfaces

What You Bring

You have experience building and maintaining native Android apps
You know how to write high-quality, testable code, and understand the tradeoffs between expediency and maintainability
You have strong UX and design sensibilities, and know how to bring complex designs to reality
You are a strong communicator, and you can explain complex technical concepts to designers, support, and other engineers without a problem
When things break, you’re eager and able to help fix things
Experience in a startup environment is a plus!

Security-related Responsibilities

Compliance with Information Security Policies
Compliance with League’s secure coding practice
Responsibility and accountability for executing League's policies and procedures
Notification of HR, Legal, Compliance & Security of any incidents, breaches or policy violations 

What We Offer

Comprehensive Health Benefits: We prioritize your well-being with complete medical, dental, and vision coverage
Bonus Program: Be rewarded for your contributions with our performance-based bonus program
Employee Stock Option Program: Become an owner and share in our success through our stock option program
Unlimited Paid Time Off: Take the time you need to recharge and maintain a healthy work-life balance
Spending Accounts: Manage your healthcare and dependent care expenses with tax-advantaged spending accounts
Wellness Days: Prioritize your mental and physical health with dedicated wellness days throughout the year
Growth Opportunities: We invest in your future with abundant opportunities for professional development and advancement
Mentorship Program: Benefit from guidance and support from experienced leaders in your field
Flexible Ways of Working: Enjoy the freedom to work in a way that suits your life and boosts your productivity

The Application Process

We believe applying for a job should be straightforward and transparent. Here’s what to expect:

Submit Your Application: You’ll receive a confirmation email right away.
Intro sessions: Learn more about our culture, get alignment on your compensation expectation prior to committing to next steps
Take-home assessment
Meet the Engineering Team: Dive into technical discussions and learn how you can make an impact at League.
Final Steps: Meet our cross-functional team and the hiring managers and share experiences on collaboration
Offer and onboarding!

We value your time and effort—our team is committed to providing updates throughout the process.

CANADA APPLICANTS ONLY: The Canada-specific compensation range below for this full-time position is exclusive of bonus, equity and benefits. This range reflects the minimum and maximum target for base salaries for the position across all Canadian locations. The salary range is intentional to account for the performance and career progressions a Leaguer will experience in the role throughout their time at League. Where in the band you may land is determined by job-related skills/experience. Your recruiter can share more about the specific salary range specific to your skills and experience during the hiring process.

Compensation range for Canada applicants only

$117,800—$141,900 CAD

Our employees come from different backgrounds, and we celebrate those differences. We are looking for the best candidates for our open roles, but do not expect applicants to meet every qualification in order to be considered. If you are excited about what you could accomplish at League and believe you can add value to our team, we would love to hear from you.

We are committed to equal employment opportunity regardless of race, color, ancestry, religion, sex, national origin, sexual orientation, age, citizenship, marital status, disability, gender identity or Veteran status. If you are an individual in need of assistance at any time during our recruitment process, please contact us at recruitinginfo@league.com.

Our Application Process

Applying to a role you love can be exhausting, and understanding the next steps can feel vague and uncertain. You have done the hard part of submitting your application; let's do ours by sharing potential next steps

You should receive a confirmation email after submitting your application.
A recruiter (not a computer) reviews all applications at League.
If we see alignment with League's needs, a recruiter will reach out to learn more about your goals. The recruiter will also share the team-specific interview process depending on the roles you are exploring.
The final step is an offer, which we hope you will accept!
Prior to joining us, we conduct reference and background checks. Additional checks could be required for US Candidates, depending on the role you are exploring.

Here are some additional resources to learn more about League:

Learn about our platform, leadership team and partners
Highmark Health, Google Cloud, League: new digital front door to seamless care
Former Providence President and Workday EVP of Corporate Strategy join League Board of Directors
League raises $95 million USD in Series C to build world’s leading healthcare CX platform
Forbes x League: The Platformization Of Healthcare Is Here
Fast Company x League: If we want better innovations in healthtech, we need more competition

Recognize and Avoid Employment scams. Practice safe job searching.

Scammers are getting craftier and leveraging fake job postings to get personal information. Know the warning signs and protect yourself from scammers. Learn more here.

Use of AI Notice

We are committed to ensuring fairness and transparency throughout our hiring process. League may use Artificial Intelligence (AI) tools to assist in the screening of applicants for this position. Please check out our stance on using AI in recruitment here.

Privacy Policy

Review our Privacy Policy for information on how League is protecting personal data.
"""

    # You can also read job description from a file:
    # with open('job_description.txt', 'r') as f:
    #     job_description = f.read()

    try:
        generate_resume(
            job_description=job_description,
            resume_data_path='resume_data_enhanced.json',
            template_path='resume_template.tex',
            base_output_dir='./generated',
            shouldRewrite=True
        )
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()