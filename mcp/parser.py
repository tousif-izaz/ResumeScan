"""
Resume Parser with Keyword Extraction and LLM Section Correction
Handles PDF, DOCX, and text input with intelligent section parsing
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Import parsing libraries
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None

from .models import (
    ParsedResume, ParseResult, ResumeSection, 
    ResumeBlock, ContactInfo
)

# Gemini LLM imports
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load .env for API keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ResumeParser:
    """Intelligent resume parser with keyword extraction and LLM correction"""
    
    def __init__(self, use_llm_correction: bool = True):
        # Section detection patterns
        self.section_patterns = {
            ResumeSection.SUMMARY: [
                r"summary", r"profile", r"objective", r"about",
                r"professional summary", r"career summary"
            ],
            ResumeSection.EXPERIENCE: [
                r"experience", r"work history", r"employment",
                r"professional experience", r"work experience"
            ],
            ResumeSection.EDUCATION: [
                r"education", r"academic", r"degree", r"university",
                r"college", r"school"
            ],
            ResumeSection.SKILLS: [
                r"skills", r"competencies", r"technologies",
                r"tools", r"programming languages"
            ],
            ResumeSection.PROJECTS: [
                r"projects", r"portfolio", r"achievements",
                r"key projects", r"notable projects"
            ],
            ResumeSection.CERTIFICATIONS: [
                r"certifications", r"certificates", r"licenses",
                r"accreditations", r"training"
            ]
        }
        
        # Keyword extraction patterns
        self.tech_keywords = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php",
            "ruby", "go", "rust", "swift", "kotlin", "scala", "r", "matlab",
            
            # Frameworks & Libraries
            "react", "vue", "angular", "node.js", "express", "django", "flask",
            "spring", "laravel", "asp.net", "jquery", "bootstrap", "tailwind",
            
            # Databases
            "sql", "mysql", "postgresql", "mongodb", "redis", "oracle",
            "sqlite", "mariadb", "cassandra", "dynamodb",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins",
            "git", "github", "gitlab", "ci/cd", "terraform", "ansible",
            
            # Tools & Platforms
            "jira", "confluence", "slack", "figma", "adobe", "photoshop",
            "excel", "powerpoint", "word", "tableau", "power bi"
        ]
        
        # Contact extraction patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        self.linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        self.use_llm_correction = use_llm_correction and GEMINI_API_KEY is not None and genai is not None
        if self.use_llm_correction:
            genai.configure(api_key=GEMINI_API_KEY)
    
    def parse_file(self, file_path: str) -> ParseResult:
        """Parse resume from file (PDF, DOCX, TXT)"""
        try:
            if not os.path.exists(file_path):
                return ParseResult(
                    success=False,
                    errors=[f"File not found: {file_path}"]
                )
            
            # Determine file type and extract text
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                text = self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                text = self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                text = self._extract_txt_text(file_path)
            else:
                return ParseResult(
                    success=False,
                    errors=[f"Unsupported file format: {file_ext}"]
                )
            
            if not text.strip():
                return ParseResult(
                    success=False,
                    errors=["No text content found in file"]
                )
            
            # Parse the extracted text
            return self._parse_text(text, file_path)
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"Error parsing file: {str(e)}"]
            )
    
    def parse_text(self, text: str) -> ParseResult:
        """Parse resume from text input"""
        try:
            if not text.strip():
                return ParseResult(
                    success=False,
                    errors=["No text content provided"]
                )
            
            return self._parse_text(text)
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"Error parsing text: {str(e)}"]
            )
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if pdfplumber is None:
            raise ImportError("pdfplumber is required for PDF parsing")
        
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if Document is None:
            raise ImportError("python-docx is required for DOCX parsing")
        
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        return text
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _parse_text(self, text: str, file_path: Optional[str] = None) -> ParseResult:
        """Parse text into structured resume data, with optional LLM correction"""
        try:
            # Extract contact information
            contact_info = self._extract_contact_info(text)
            
            # Parse sections
            sections = self._parse_sections(text)
            
            # Extract keywords from all content
            all_keywords = self._extract_keywords(text)
            
            # Create parsed resume
            parsed_resume = ParsedResume(
                raw_text=text,
                contact_info=contact_info,
                sections=sections,
                all_keywords=all_keywords,
                file_path=file_path
            )
            
            # LLM post-processing for section correction
            if self.use_llm_correction:
                llm_result = self._llm_section_correction(parsed_resume)
                if llm_result.success:
                    return llm_result
                # If LLM fails, fall back to original
                else:
                    return ParseResult(
                        success=True,
                        resume=parsed_resume,
                        messages=["LLM correction failed, using initial parse."] + llm_result.errors
                    )
            return ParseResult(
                success=True,
                resume=parsed_resume,
                messages=["Resume parsed successfully"]
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"Error parsing text: {str(e)}"]
            )
    
    def _extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from text"""
        contact_info = ContactInfo()
        
        # Extract email
        emails = re.findall(self.email_pattern, text)
        if emails:
            contact_info.email = emails[0]
        
        # Extract phone
        phones = re.findall(self.phone_pattern, text)
        if phones:
            contact_info.phone = ''.join(phones[0])
        
        # Extract LinkedIn
        linkedin_matches = re.findall(self.linkedin_pattern, text)
        if linkedin_matches:
            contact_info.linkedin = f"https://{linkedin_matches[0]}"
        
        # Extract name (simple heuristic - first line that's not a header)
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if (line and 
                len(line) > 2 and 
                len(line) < 50 and
                not any(keyword in line.lower() 
                       for keyword in ['resume', 'cv', 'email', 'phone', 'linkedin'])):
                contact_info.name = line
                break
        
        return contact_info
    
    def _parse_sections(self, text: str) -> Dict[ResumeSection, List[ResumeBlock]]:
        """Parse text into resume sections"""
        sections = {section: [] for section in ResumeSection}
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        current_section = ResumeSection.SUMMARY
        current_content = []
        
        for paragraph in paragraphs:
            # Check if this paragraph starts a new section
            section_found = False
            for section, patterns in self.section_patterns.items():
                if any(re.search(pattern, paragraph.lower()) for pattern in patterns):
                    # Save previous section content
                    if current_content:
                        block = self._create_block(current_content, current_section)
                        sections[current_section].append(block)
                    
                    current_section = section
                    current_content = [paragraph]
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(paragraph)
        
        # Add final section
        if current_content:
            block = self._create_block(current_content, current_section)
            sections[current_section].append(block)
        
        return sections
    
    def _create_block(self, content: List[str], section: ResumeSection) -> ResumeBlock:
        """Create a resume block with keywords"""
        text = '\n'.join(content)
        keywords = self._extract_keywords(text)
        
        return ResumeBlock(
            content=text,
            section=section,
            keywords=keywords
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        # Find technical keywords
        for keyword in self.tech_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Find other common resume keywords
        common_keywords = [
            "leadership", "management", "project", "team", "development",
            "analysis", "design", "implementation", "testing", "deployment",
            "agile", "scrum", "kanban", "waterfall", "methodology",
            "research", "data", "analytics", "machine learning", "ai",
            "frontend", "backend", "fullstack", "api", "rest", "graphql",
            "microservices", "architecture", "database", "optimization"
        ]
        
        for keyword in common_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # Remove duplicates 

    def _llm_section_correction(self, parsed_resume: ParsedResume) -> ParseResult:
        """Call Gemini Pro to verify/correct section splits"""
        if not self.use_llm_correction:
            return ParseResult(success=True, resume=parsed_resume, messages=["LLM correction disabled"])
        try:
            prompt = self._build_llm_prompt(parsed_resume)
            model = genai.GenerativeModel("models/gemini-2.0-flash")
            response = model.generate_content(prompt)
            # Extract first JSON object from response
            import re, json
            text = response.text.strip()
            if not text:
                raise ValueError("Empty response from Gemini LLM.")
            # Find first JSON object in the response
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                raise ValueError(f"No JSON object found in LLM response: {text[:200]}")
            json_str = match.group(0)
            llm_data = json.loads(json_str)
            # Rebuild ParsedResume from LLM output
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
    def _build_llm_prompt(self, parsed_resume: ParsedResume) -> str:
        """Build prompt for Gemini to verify/correct sections"""
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
    def _parsed_resume_from_llm(self, llm_data: dict, original: ParsedResume) -> ParsedResume:
        """Rebuild ParsedResume from LLM output, fallback to original for missing fields"""
        # Only update sections and keywords
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
        # Rebuild all_keywords
        all_keywords = list({kw for blocks in new_sections.values() for block in blocks for kw in block.keywords})
        return ParsedResume(
            raw_text=original.raw_text,
            contact_info=original.contact_info,
            sections=new_sections,
            all_keywords=all_keywords,
            file_path=original.file_path
        ) 