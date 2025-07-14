#!/usr/bin/env python3
"""
Test script for Resume Parser
Tests the MCP-style resume parser with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.parser import ResumeParser
from mcp.models import ParseResult


def test_text_parsing():
    """Test parsing resume text"""
    print("🧪 Testing Resume Parser - Text Input")
    print("=" * 50)
    
    # Sample resume text
    sample_resume = """
John Doe
Email: john.doe@example.com
Phone: +1 555-123-4567
LinkedIn: linkedin.com/in/johndoe

SUMMARY
Experienced software engineer with 5+ years in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable applications and leading development teams.

EXPERIENCE
Senior Software Engineer - TechCorp (2020-2023)
- Led development of microservices architecture using Python and Docker
- Implemented CI/CD pipelines reducing deployment time by 60%
- Mentored 3 junior developers and conducted code reviews
- Used React, Node.js, and AWS for frontend and backend development

Software Developer - StartupXYZ (2018-2020)
- Built REST APIs using Node.js and Express
- Developed frontend applications with React and TypeScript
- Collaborated with product team to deliver user-focused features
- Implemented database solutions with PostgreSQL and MongoDB

SKILLS
Programming: Python, JavaScript, TypeScript, Java, SQL
Frameworks: React, Node.js, Express, Django, Flask
Tools: Git, Docker, AWS, Jenkins, Jira
Databases: PostgreSQL, MongoDB, Redis

EDUCATION
Bachelor of Science in Computer Science
University of Technology - 2018

PROJECTS
E-commerce Platform - Built full-stack application using React and Node.js
- Implemented user authentication and payment processing
- Used MongoDB for data storage and Redis for caching
- Deployed on AWS with Docker containers
    """
    
    # Initialize parser
    parser = ResumeParser()
    
    # Parse the text
    result = parser.parse_text(sample_resume)
    
    # Display results
    print_results(result)
    
    return result.success


def test_contact_extraction():
    """Test contact information extraction"""
    print("\n🧪 Testing Contact Information Extraction")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Basic Contact Info",
            "text": """
John Smith
Email: john.smith@email.com
Phone: (555) 123-4567
Location: New York, NY
            """
        },
        {
            "name": "LinkedIn Contact",
            "text": """
Jane Doe
Email: jane.doe@company.com
LinkedIn: linkedin.com/in/janedoe
Phone: +1-555-987-6543
            """
        }
    ]
    
    parser = ResumeParser()
    
    for test_case in test_cases:
        print(f"\n📄 Testing: {test_case['name']}")
        result = parser.parse_text(test_case['text'])
        
        if result.success and result.resume:
            contact = result.resume.contact_info
            print(f"  Name: {contact.name}")
            print(f"  Email: {contact.email}")
            print(f"  Phone: {contact.phone}")
            print(f"  LinkedIn: {contact.linkedin}")
        else:
            print("  ❌ Failed to parse")


def test_keyword_extraction():
    """Test keyword extraction"""
    print("\n🧪 Testing Keyword Extraction")
    print("=" * 35)
    
    test_text = """
Software Engineer with expertise in Python, JavaScript, and React.
Experience with AWS, Docker, and microservices architecture.
Skills include machine learning, data analysis, and API development.
    """
    
    parser = ResumeParser()
    result = parser.parse_text(test_text)
    
    if result.success and result.resume:
        print("📋 Extracted Keywords:")
        for keyword in result.resume.all_keywords:
            print(f"  • {keyword}")
    else:
        print("❌ Failed to extract keywords")


def test_section_parsing():
    """Test section parsing"""
    print("\n🧪 Testing Section Parsing")
    print("=" * 30)
    
    test_text = """
SUMMARY
Experienced developer with Python skills.

EXPERIENCE
Software Engineer at TechCorp.

SKILLS
Python, JavaScript, React.

EDUCATION
Computer Science degree.
    """
    
    parser = ResumeParser()
    result = parser.parse_text(test_text)
    
    if result.success and result.resume:
        print("📊 Parsed Sections:")
        for section, blocks in result.resume.sections.items():
            if blocks:
                print(f"  {section.value.title()}: {len(blocks)} blocks")
                for i, block in enumerate(blocks[:2]):  # Show first 2 blocks
                    print(f"    Block {i+1}: {len(block.content)} chars, "
                          f"{len(block.keywords)} keywords")
    else:
        print("❌ Failed to parse sections")


def print_results(result: ParseResult):
    """Print parsing results"""
    print("📊 PARSING RESULTS")
    print("=" * 50)
    
    if result.success:
        print("✅ Parsing successful!")
        
        if result.resume:
            resume = result.resume
            
            # Contact info
            print(f"\n👤 Contact Information:")
            contact = resume.contact_info
            print(f"  Name: {contact.name}")
            print(f"  Email: {contact.email}")
            print(f"  Phone: {contact.phone}")
            print(f"  LinkedIn: {contact.linkedin}")
            
            # Sections
            print(f"\n📋 Parsed Sections:")
            for section, blocks in resume.sections.items():
                if blocks:
                    print(f"  {section.value.title()}: {len(blocks)} blocks")
            
            # Keywords
            print(f"\n🔑 Extracted Keywords ({len(resume.all_keywords)}):")
            for keyword in resume.all_keywords[:10]:  # Show first 10
                print(f"  • {keyword}")
            if len(resume.all_keywords) > 10:
                print(f"  ... and {len(resume.all_keywords) - 10} more")
        
        # Messages
        if result.messages:
            print(f"\n📝 Messages:")
            for message in result.messages:
                print(f"  {message}")
    
    else:
        print("❌ Parsing failed!")
        for error in result.errors:
            print(f"  • {error}")


if __name__ == "__main__":
    print("🚀 Resume Parser Test Suite")
    print("=" * 50)
    
    # Run all tests
    success = test_text_parsing()
    
    if success:
        test_contact_extraction()
        test_keyword_extraction()
        test_section_parsing()
    
    print("\n🎉 Testing completed!") 