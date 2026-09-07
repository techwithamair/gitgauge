import os

from groq import Groq


class AIServiceError(Exception):
    """Raised when an AI request cannot be completed."""


class AIService:
    """Generates text through Groq without containing Streamlit code."""

    MODEL = "openai/gpt-oss-20b"

    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None

    def generate_portfolio_summary(self, portfolio, analysis, recommendations):
        prompt = self._build_summary_prompt(portfolio, analysis, recommendations)
        return self._send_prompt(prompt, 220)

    def generate_readme(self, repository, details):
        prompt = self._build_readme_prompt(repository, details)
        return self._send_prompt(prompt, 900)

    def _build_summary_prompt(self, portfolio, analysis, recommendations):
        facts = "\n".join(f"- {item}" for item in analysis["observations"])
        actions = "\n".join(f"- {item['title']}" for item in recommendations)

        return f"""
You summarize objective GitHub portfolio presentation facts for a student.
Use only the supplied facts. Do not infer programming ability, employability,
personality, or seniority. Do not assign a score, grade, percentile, or ranking.
Write three or four clear sentences. Mention one verified strength and the most
useful verified improvement. If information is absent, do not guess it.

GitHub username: {portfolio.username}

Verified facts:
{facts}

Rule-based recommendations:
{actions or '- No improvements were triggered by the current rules.'}
"""

    def _build_readme_prompt(self, repository, details):
        return f"""
Create an editable GitHub README in valid Markdown. Use only the repository facts
and project details supplied below. Do not invent features, commands,
dependencies, results, users, metrics, licenses, screenshots, or deployment URLs.
Omit a section when its information is unavailable. Keep the writing clear and
suitable for a student software project.

Repository facts:
- Name: {repository.name}
- Existing description: {repository.description or 'Not provided'}
- Primary language: {repository.language or 'Not detected'}
- Repository URL: {repository.url}

Student-provided details:
- Problem: {details['problem']}
- Features: {details['features']}
- Technologies: {details['technologies'] or 'Not provided'}
- Installation: {details['installation'] or 'Not provided'}
- Run command: {details['run_command'] or 'Not provided'}
- Additional notes: {details['additional'] or 'Not provided'}

Use these sections when applicable:
# Project Name
Overview
Features
Tech Stack
Getting Started
Usage
Additional Notes
"""

    def _send_prompt(self, prompt, max_tokens):
        if self.client is None:
            raise AIServiceError("GROQ_API_KEY is not configured.")

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            content = response.choices[0].message.content
            if not content:
                raise AIServiceError("The AI returned an empty response.")
            return content.strip()
        except AIServiceError:
            raise
        except Exception as error:
            raise AIServiceError(f"The Groq request failed: {error}")
