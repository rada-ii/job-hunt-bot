import openai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()


class CoverLetterGenerator:
    def __init__(self):
        """Initialize with legacy OpenAI client (v0.28.1 compatible)"""
        openai.api_key = os.getenv('OPENAI_API_KEY')
        print("Using legacy OpenAI client")

    def generate_cover_letter(self, job_title, company, user_name="", user_email="", user_phone="",
                              years_experience="2-3", key_skills="", job_description=""):
        """Generate personalized cover letter using ACTUAL user data - NO placeholders"""

        if not user_name or not user_email:
            return "Error: Name and email are required to generate cover letter."

        current_date = datetime.now().strftime("%B %d, %Y")
        skills_text = self._format_skills(key_skills)
        experience_text = self._format_experience(years_experience)

        # Create professional header
        header_lines = [user_name]
        if user_email:
            header_lines.append(user_email)
        if user_phone:
            header_lines.append(user_phone)

        header_lines.extend(['', current_date, '', 'Hiring Manager', f'{company}', ''])

        prompt = f"""Write a professional business cover letter body (3 paragraphs only - no header/footer) using these EXACT details:

ACTUAL USER DATA:
- Name: {user_name}
- Experience: {experience_text} experience
- Skills: {skills_text}
- Job: {job_title} at {company}

REQUIREMENTS:
1. Write 3 short, professional paragraphs
2. Paragraph 1: Interest in the {job_title} position at {company}
3. Paragraph 2: Mention {experience_text} experience and {skills_text} skills
4. Paragraph 3: Thank them and request interview
5. NO header, NO signature, NO placeholders
6. Professional but conversational tone
7. Each paragraph 2-3 sentences maximum

Start with "Dear Hiring Manager," and end with formal closing."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Write professional cover letter body paragraphs using ONLY real data provided. Never use [Your Name] or placeholders. Write as {user_name} applying for {job_title} at {company}."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )

            letter_body = response.choices[0].message.content

            # Clean any remaining placeholders
            letter_body = self._force_replace_placeholders(letter_body, user_name, user_email, user_phone,
                                                           key_skills, job_title, company, years_experience)

            # Combine header + body + signature
            full_letter = self._create_formatted_letter(header_lines, letter_body, user_name)

            return full_letter

        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._create_manual_letter(job_title, company, user_name, user_email, user_phone,
                                              years_experience, key_skills)

    def _create_formatted_letter(self, header_lines, letter_body, user_name):
        """Create properly formatted business letter"""

        # Clean the letter body
        body_lines = letter_body.split('\n')
        cleaned_body = []

        for line in body_lines:
            line = line.strip()
            # Remove placeholder lines, empty lines, and AI-generated signature lines
            if line and '[' not in line and not line.startswith('Sincerely') and not line == user_name:
                cleaned_body.append(line)

        # Add proper spacing between paragraphs
        formatted_body = []
        for i, line in enumerate(cleaned_body):
            formatted_body.append(line)
            # Add blank line after paragraphs (but not after "Dear" line or last line)
            if line and not line.startswith('Dear') and i < len(cleaned_body) - 1:
                formatted_body.append('')

        # Combine all parts with OUR signature only
        full_letter = header_lines + formatted_body + ['', 'Sincerely,', '', user_name]

        return '\n'.join(full_letter)

    def _format_skills(self, key_skills):
        if not key_skills:
            return "relevant technical skills"
        skills = [skill.strip() for skill in key_skills.split(',')]
        if len(skills) == 1:
            return skills[0]
        elif len(skills) == 2:
            return f"{skills[0]} and {skills[1]}"
        else:
            return f"{', '.join(skills[:-1])}, and {skills[-1]}"

    def _format_experience(self, years_experience):
        mapping = {
            "0-1": "entry-level",
            "2-3": "solid",
            "4-5": "extensive",
            "6-10": "senior-level",
            "10+": "comprehensive"
        }
        return mapping.get(years_experience, "relevant")

    def _force_replace_placeholders(self, text, user_name, user_email, user_phone, key_skills, job_title, company,
                                    years_experience):
        replacements = {
            "[Your Name]": user_name, "[Your Full Name]": user_name, "[Name]": user_name,
            "[Your Email]": user_email, "[EMAIL]": user_email,
            "[Your Phone]": user_phone if user_phone else "",
            "[Your Skills]": key_skills if key_skills else "relevant technical skills",
            "[Position]": job_title, "[Job Title]": job_title,
            "[Company]": company, "[Company Name]": company,
            "[Years Experience]": years_experience,
            "[Hiring Manager]": "Hiring Manager",
            "[Date]": datetime.now().strftime("%B %d, %Y")
        }

        for placeholder, replacement in replacements.items():
            if replacement:
                text = text.replace(placeholder, replacement)
            else:
                # Remove lines containing empty placeholders
                lines = text.split('\n')
                text = '\n'.join(line for line in lines if placeholder not in line)

        return text

    def _create_manual_letter(self, job_title, company, user_name, user_email, user_phone, years_experience,
                              key_skills):
        """Fallback manual letter if AI fails"""
        current_date = datetime.now().strftime("%B %d, %Y")

        # Header
        header_lines = [user_name]
        if user_email:
            header_lines.append(user_email)
        if user_phone:
            header_lines.append(user_phone)

        header_lines.extend(['', current_date, '', 'Hiring Manager', f'{company}', ''])

        # Body
        skills_mention = self._format_skills(key_skills) if key_skills else "technical expertise"
        experience_desc = self._format_experience(years_experience)

        body = [
            'Dear Hiring Manager,',
            '',
            f'I am writing to express my strong interest in the {job_title} position at {company}. Your company\'s reputation and this role align perfectly with my career goals.',
            '',
            f'With {experience_desc} experience in software development, I bring hands-on expertise in {skills_mention}. My background includes successful project delivery and collaborative problem-solving that would benefit your development team.',
            '',
            f'I would welcome the opportunity to discuss how my skills can contribute to {company}\'s continued success. Thank you for considering my application.',
            '',
            'Sincerely,',
            '',
            user_name
        ]

        return '\n'.join(header_lines + body)