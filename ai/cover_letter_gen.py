import openai
from dotenv import load_dotenv
import os
from typing import Optional

load_dotenv()


class CoverLetterGenerator:
    def __init__(self):
        """Initialize with legacy OpenAI client (v0.28.1 compatible)"""
        # Set API key directly (legacy format)
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self._has_api_key = bool(os.getenv('OPENAI_API_KEY'))
        print("✅ Using legacy OpenAI client")

    def generate_cover_letter(self, job_title: str, company_name: str, location: Optional[str] = None, 
                            job_snippet: Optional[str] = None, use_ai: bool = True) -> str:
        """
        Generate a generic, professional cover letter without requiring personal information.
        
        Args:
            job_title: The job title/position
            company_name: The company name
            location: Optional job location
            job_snippet: Optional job description snippet for context
            use_ai: Whether to use AI for polishing (falls back to deterministic if API unavailable)
            
        Returns:
            A professional, generic cover letter ready for use
        """
        # Create base deterministic template
        base_letter = self._create_deterministic_template(job_title, company_name, location, job_snippet)
        
        # If AI not requested or no API key, return base template
        if not use_ai or not self._has_api_key:
            return base_letter
            
        # Try to polish with AI
        try:
            return self._polish_with_ai(base_letter, job_title, company_name)
        except Exception as e:
            print(f"⚠️ AI polishing failed: {e}")
            return base_letter
    
    def _create_deterministic_template(self, job_title: str, company_name: str, 
                                     location: Optional[str] = None, job_snippet: Optional[str] = None) -> str:
        """Create a clean, deterministic cover letter template without placeholders."""
        
        # Build location context
        location_text = f" in {location}" if location else ""
        
        # Create professional, generic cover letter
        letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}{location_text}. This opportunity aligns perfectly with my career aspirations and professional background.

Having researched your organization, I am impressed by your commitment to excellence and innovation in the industry. The {job_title} role presents an exciting challenge where I can contribute meaningfully to your team's success while continuing to grow professionally.

My background has equipped me with relevant skills and experience that would be valuable for this position. I am particularly drawn to the collaborative environment and growth opportunities that {company_name} offers, and I am excited about the possibility of contributing to your continued success.

I would welcome the opportunity to discuss how my qualifications and enthusiasm can benefit your organization. Thank you for considering my application, and I look forward to hearing from you soon.

Sincerely,
[Applicant Name]"""

        return letter
    
    def _polish_with_ai(self, base_letter: str, job_title: str, company_name: str) -> str:
        """Polish the base letter using AI while maintaining its generic nature."""
        
        prompt = f"""Please improve this cover letter while keeping it generic and professional. 

IMPORTANT CONSTRAINTS:
1. Keep it concise and professional
2. Do NOT add specific technical skills, personal details, or company facts not already mentioned
3. Do NOT make personal claims about experience or achievements
4. Maintain the generic, neutral tone suitable for any applicant
5. Focus on enthusiasm, professionalism, and alignment with the role
6. Keep the length similar to the original (~160 words)

Cover Letter to improve:
{base_letter}

Job: {job_title} at {company_name}

Return only the improved cover letter without any explanations or additional text."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional writing assistant. Improve cover letters while keeping them generic, concise, and suitable for any applicant. Never add specific skills, personal details, or company facts not already provided."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_legacy_template(self, job_title: str, company: str, job_description: str = "") -> str:
        """Legacy method for generating templates with placeholders - kept for backwards compatibility."""
        # This method is deprecated and will be removed in future versions
        print("⚠️ Using deprecated legacy template method")
        
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
    """Test the new automated cover letter generator"""
    print("🧪 TESTING NEW AUTOMATED COVER LETTER GENERATOR")
    print("=" * 60)

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
    else:
        print("❌ No API key found in environment")

    # Test generator
    generator = CoverLetterGenerator()

    sample_job = {
        "title": "Software Developer",
        "company": "Tech Company",
        "location": "San Francisco, CA"
    }

    print(f"\n🤖 Testing automated generation for: {sample_job['title']} @ {sample_job['company']}")
    
    # Test deterministic version (no AI)
    print("\n📄 DETERMINISTIC VERSION (no AI):")
    print("=" * 50)
    deterministic_letter = generator.generate_cover_letter(
        sample_job["title"],
        sample_job["company"],
        sample_job["location"],
        use_ai=False
    )
    print(deterministic_letter)
    print("=" * 50)
    
    # Check if it's truly generic (no placeholders)
    if "[Your" not in deterministic_letter and "[Applicant Name]" in deterministic_letter:
        print("✅ Deterministic letter is properly automated!")
    else:
        print("⚠️ Deterministic letter may still have placeholders")
    
    # Test AI version if available
    if api_key:
        print("\n🤖 AI-POLISHED VERSION:")
        print("=" * 50)
        ai_letter = generator.generate_cover_letter(
            sample_job["title"],
            sample_job["company"],
            sample_job["location"],
            use_ai=True
        )
        print(ai_letter)
        print("=" * 50)
        
        if "[Your" not in ai_letter:
            print("✅ AI letter is properly automated!")
        else:
            print("⚠️ AI letter may still have placeholders")
    else:
        print("\n⚠️ Skipping AI test - no API key available")
    
    print(f"\nWord count (deterministic): ~{len(deterministic_letter.split())} words")
    print("✅ Test complete!")


if __name__ == "__main__":
    test_generator()