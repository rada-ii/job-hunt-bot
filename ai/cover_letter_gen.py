import openai
from dotenv import load_dotenv
import os

load_dotenv()


class CoverLetterGenerator:
    def __init__(self):
        """Initialize with legacy OpenAI client (v0.28.1 compatible)"""
        # Set API key directly (legacy format)
        openai.api_key = os.getenv('OPENAI_API_KEY')
        print("✅ Using legacy OpenAI client")

    def generate_cover_letter(self, job_title, company, job_description=""):
        """Generate COMPLETELY GENERIC cover letter template"""

        prompt = f"""Create a professional cover letter TEMPLATE for this job:

Position: {job_title}
Company: {company}
Job Details: {job_description}

CRITICAL REQUIREMENTS:
1. This must be a REUSABLE TEMPLATE with placeholders only
2. Use ONLY these placeholder formats:
   - [Your Full Name]
   - [Your Email]
   - [Your Phone]
   - [Your Address]
   - [City, State ZIP Code]
   - [Date]

3. For experience placeholders use:
   - [Your years of experience] years of experience in [Your field]
   - [Your relevant technical skills]
   - [Your key achievement or project example]
   - [Your education/certifications if relevant]

4. DO NOT use ANY real names, personal information, or specific skills
5. DO NOT mention specific technologies, companies, or personal details
6. Keep it completely generic and customizable
7. Make it suitable for ANY applicant for ANY position

Structure:
- Standard business letter format
- 3 paragraphs maximum
- Generic professional language
- Placeholders for all personal information

Write a universal template:"""

        try:
            # Legacy OpenAI API call (v0.28.1 format)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a template creator. Create ONLY generic cover letter templates with bracketed placeholders like [Your Name]. Never use real names, addresses, specific skills, or personal information. This template must work for any person applying to any job."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )

            template = response.choices[0].message.content

            # Safety filter - remove any personal info that might slip through
            personal_info_filters = [
                ("Rada Ivanković", "[Your Full Name]"),
                ("Rada", "[Your Name]"),
                ("ra.da@live.com", "[Your Email]"),
                ("AI Automation Specialist", "[Your Current Job Title]"),
                ("Python", "[Your Programming Language]"),
                ("Selenium", "[Your Technical Skill]"),
                ("OpenAI", "[Your Technology]"),
                ("Streamlit", "[Your Framework]"),
                ("web scraping", "[Your Technical Skill]"),
                ("automation", "[Your Specialization]")
            ]

            for old, new in personal_info_filters:
                template = template.replace(old, new)

            return template

        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            # Fallback generic template
            return f"""[Your Full Name]
[Your Address]
[City, State ZIP Code]
[Your Email]
[Your Phone]

[Date]

Hiring Manager
{company}
[Company Address]
[City, State ZIP Code]

Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. With [Your years of experience] years of experience in [Your field], I am excited about the opportunity to contribute to your team and help achieve your company's goals.

In my previous role as [Your Previous Job Title], I successfully [Your key achievement or responsibility]. My experience with [Your relevant skills] and proven track record in [Your area of expertise] make me well-suited for this position. I am particularly drawn to {company} because [Your research about company - values, mission, recent news, etc.].

I would welcome the opportunity to discuss how my skills and experience can benefit your organization. Thank you for considering my application, and I look forward to hearing from you soon.

Sincerely,
[Your Full Name]

---
🤖 AI generation unavailable. Please customize this template with your personal information.
Error details: {str(e)[:100]}..."""


def test_generator():
    """Test the cover letter generator with legacy API"""
    print("🧪 TESTING LEGACY COVER LETTER GENERATOR")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
    else:
        print("❌ No API key found in environment")
        return

    # Test generator
    generator = CoverLetterGenerator()

    sample_job = {
        "title": "Software Developer",
        "company": "Tech Company",
        "description": "Looking for developer with programming experience"
    }

    print(f"\n🤖 Generating cover letter for: {sample_job['title']} @ {sample_job['company']}")

    cover_letter = generator.generate_cover_letter(
        sample_job["title"],
        sample_job["company"],
        sample_job["description"]
    )

    print("\n📄 GENERATED TEMPLATE:")
    print("=" * 60)
    print(cover_letter)
    print("=" * 60)

    # Check if template is generic
    if "[Your Name]" in cover_letter or "[Your Full Name]" in cover_letter:
        print("✅ Template is generic!")
    else:
        print("⚠️ Template may contain personal info")


if __name__ == "__main__":
    test_generator()