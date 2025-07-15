"""
parser_llm.py
LLM-powered section correction for resume parsing using Gemini Pro
"""

import os
import re
import json
from dotenv import load_dotenv
from typing import TYPE_CHECKING

# Only import google.generativeai if available
try:
    import google.generativeai as genai
except ImportError:
    genai = None

if TYPE_CHECKING:
    from .models import ParsedResume, ParseResult

# Load .env for API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLM_MODEL_NAME = "models/gemini-2.0-flash"

class ResumeSectionLLMCorrector:
    """LLM-powered section corrector for resumes using Gemini Pro"""
    def __init__(self):
        self.enabled = GEMINI_API_KEY is not None and genai is not None
        if self.enabled:
            genai.configure(api_key=GEMINI_API_KEY)

    def correct_sections(self, parsed_resume: 'ParsedResume') -> 'ParseResult':
        """Call Gemini Pro to verify/correct section splits"""
        from .models import ParseResult
        if not self.enabled:
            return ParseResult(success=True, resume=parsed_resume, messages=["LLM correction disabled"])
        try:
            prompt = self._build_llm_prompt(parsed_resume)
            model = genai.GenerativeModel(LLM_MODEL_NAME)
            response = model.generate_content(prompt)
            text = response.text.strip()
            if not text:
                raise ValueError("Empty response from Gemini LLM.")
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON object found in LLM response: {text[:200]}")
            json_str = match.group(0)
            llm_data = json.loads(json_str)
            corrected_resume = self._parsed_resume_from_llm(llm_data, parsed_resume)
            return ParseResult(
                success=True,
                resume=corrected_resume,
                messages=["Sections verified/corrected by Gemini Pro"]
            )
        except Exception as e:
            return ParseResult(
                success=False,
                resume=parsed_resume,
                errors=[f"LLM correction error: {str(e)}"]
            )

    def _build_llm_prompt(self, parsed_resume: 'ParsedResume') -> str:
        context_text = parsed_resume.raw_text[:5000]
        section_summary = "\n".join([
            f"{section.value}: {len(blocks)} blocks" for section, blocks in parsed_resume.sections.items() if blocks
        ])
        prompt = f"""
You are an expert resume parser. Given the following raw resume text and the current section splits, verify if the sections are correct. If not, return a corrected JSON structure with the following format:
{{
  "sections": {{
    "summary": [{{"content": "...", "keywords": ["...", ...]}}],
    "experience": [{{"content": "...", "keywords": ["...", ...]}}],
    ...
  }}
}}

IMPORTANT: Only output valid JSON. Do not include any explanation, markdown, or text before or after the JSON. Your response must start with '{{' and end with '}}'.

Raw Resume Text (truncated):
{context_text}

Current Section Summary:
{section_summary}

If the sections are correct, return the same structure. Only output valid JSON. Do not include any explanation.
"""
        return prompt

    def _parsed_resume_from_llm(self, llm_data: dict, original: 'ParsedResume') -> 'ParsedResume':
        from .models import ResumeSection, ResumeBlock, ParsedResume
        new_sections = {}
        for section in ResumeSection:
            section_key = section.value
            blocks = []
            if (
                "sections" in llm_data and
                section_key in llm_data["sections"]
            ):
                for block in llm_data["sections"][section_key]:
                    blocks.append(ResumeBlock(
                        content=block.get("content", ""),
                        section=section,
                        keywords=block.get("keywords", [])
                    ))
            new_sections[section] = blocks
        all_keywords = list({kw for blocks in new_sections.values() for block in blocks for kw in block.keywords})
        return ParsedResume(
            raw_text=original.raw_text,
            contact_info=original.contact_info,
            sections=new_sections,
            all_keywords=all_keywords,
            file_path=original.file_path
        ) 