# Resume Parser - MCP Architecture

A clean, testable resume parsing system built with MCP (Model-Context-Prompt) architecture. The parser can extract structured information from PDF, DOCX, and text input with intelligent section parsing and keyword extraction.

## 🏗️ Architecture

```
mcp/
├── __init__.py          # MCP package initialization
├── models.py            # Pydantic data models
└── parser.py            # Resume parser with keyword extraction
```

## 🚀 Features

- **Multi-format Support**: PDF, DOCX, and text input
- **Intelligent Section Parsing**: Automatically detects and categorizes resume sections
- **Contact Information Extraction**: Name, email, phone, LinkedIn
- **Keyword Extraction**: Technical skills and relevant keywords
- **Clean Data Models**: Type-safe Pydantic models
- **Testable Design**: Modular, testable components

## 📋 Supported Resume Sections

- **Contact**: Personal information
- **Summary**: Professional summary/objective
- **Experience**: Work history
- **Education**: Academic background
- **Skills**: Technical competencies
- **Projects**: Notable projects
- **Certifications**: Professional certifications

## 🔧 Installation

```bash
pip install -r requirements.txt
```

## 🧪 Testing

Run the test suite:
```bash
python test_parser.py
```

Run the demo:
```bash
python demo_parser.py
```

## 🌐 Web Interface

Start the Streamlit app:
```bash
streamlit run app.py
```

The web interface provides:
- File upload (PDF/DOCX/TXT)
- Text input with sample data
- Interactive results display
- Contact information extraction
- Section-by-section analysis
- Keyword analysis

## 📊 Example Output

```python
# Parsed resume structure
ParsedResume(
    contact_info=ContactInfo(
        name="John Doe",
        email="john.doe@example.com",
        phone="+1 555-123-4567",
        linkedin="https://linkedin.com/in/johndoe"
    ),
    sections={
        ResumeSection.SUMMARY: [ResumeBlock(...)],
        ResumeSection.EXPERIENCE: [ResumeBlock(...)],
        ResumeSection.SKILLS: [ResumeBlock(...)],
        # ...
    },
    all_keywords=["python", "javascript", "react", "docker", "aws", ...]
)
```

## 🔑 Extracted Keywords

The parser extracts technical keywords including:
- **Programming Languages**: Python, JavaScript, Java, C++, etc.
- **Frameworks**: React, Django, Flask, Node.js, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, etc.
- **Cloud & DevOps**: AWS, Docker, Kubernetes, Git, etc.
- **Tools**: Jira, Jenkins, Figma, etc.

## 🏛️ MCP Architecture Benefits

1. **Model**: Clean Pydantic data models with type safety
2. **Context**: Structured parsing with section detection
3. **Prompt**: Intelligent keyword extraction and categorization

## 📝 Usage Examples

### Text Input
```python
from mcp.parser import ResumeParser

parser = ResumeParser()
result = parser.parse_text(resume_text)
```

### File Input
```python
result = parser.parse_file("resume.pdf")
```

### Access Results
```python
if result.success:
    resume = result.resume
    print(f"Name: {resume.contact_info.name}")
    print(f"Keywords: {resume.all_keywords}")
    
    for section, blocks in resume.sections.items():
        if blocks:
            print(f"{section.value}: {len(blocks)} blocks")
```

## 🎯 Next Steps

This is the foundation for the resume parser. Future enhancements could include:
- RAG system for role matching
- Job description matching
- PDF generation
- LangGraph workflow integration
- Advanced NLP for better parsing