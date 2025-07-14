#!/usr/bin/env python3
"""
Demo script for Resume Parser
Showcases the MCP-style resume parser capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.parser import ResumeParser
from mcp.models import ParseResult


def demo_parser():
    """Demonstrate parser capabilities"""
    print("🚀 Resume Parser Demo")
    print("=" * 50)
    
    # Initialize parser
    parser = ResumeParser()
    
    # Sample resumes for different job types
    resumes = [
        {
            "name": "Software Engineer Resume",
            "text": """
Alice Johnson
Email: alice.johnson@tech.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/alicejohnson

SUMMARY
Full-stack software engineer with 4 years experience in Python, JavaScript, and cloud technologies. Passionate about building scalable applications and mentoring junior developers.

EXPERIENCE
Senior Developer - TechCorp (2021-2023)
- Led development of microservices using Python and Docker
- Implemented CI/CD pipelines with Jenkins and AWS
- Mentored 3 junior developers and conducted code reviews
- Used React, Node.js, and PostgreSQL for full-stack development

Software Developer - StartupXYZ (2019-2021)
- Built REST APIs using Express and Node.js
- Developed React frontend with TypeScript
- Implemented database solutions with MongoDB
- Deployed applications on AWS using Docker

SKILLS
Programming: Python, JavaScript, TypeScript, Java, SQL
Frameworks: React, Node.js, Express, Django, Flask
Tools: Git, Docker, AWS, Jenkins, Jira
Databases: PostgreSQL, MongoDB, Redis

EDUCATION
Bachelor of Science in Computer Science
University of Technology - 2019
            """
        },
        {
            "name": "Data Scientist Resume",
            "text": """
Bob Smith
Email: bob.smith@data.com
Phone: +1 555-987-6543
LinkedIn: linkedin.com/in/bobsmith

SUMMARY
Data scientist with expertise in machine learning, statistical analysis, and data visualization. Experienced in Python, R, and SQL for data processing and model development.

EXPERIENCE
Senior Data Scientist - DataCorp (2020-2023)
- Developed machine learning models using Python and scikit-learn
- Conducted statistical analysis and A/B testing
- Built data pipelines with Apache Spark and SQL
- Created interactive dashboards with Tableau and Power BI

Data Analyst - AnalyticsXYZ (2018-2020)
- Performed data analysis using Python and R
- Built predictive models for business forecasting
- Created data visualizations with matplotlib and ggplot2
- Worked with large datasets using SQL and pandas

SKILLS
Programming: Python, R, SQL, MATLAB
ML Libraries: scikit-learn, TensorFlow, PyTorch, pandas
Tools: Jupyter, Git, Docker, AWS
Databases: PostgreSQL, MongoDB, Redis

EDUCATION
Master of Science in Statistics
Data University - 2018
            """
        }
    ]
    
    # Process each resume
    for resume_data in resumes:
        print(f"\n📄 Processing: {resume_data['name']}")
        print("-" * 40)
        
        # Parse the resume
        result = parser.parse_text(resume_data['text'])
        
        if result.success and result.resume:
            resume = result.resume
            
            # Display contact info
            contact = resume.contact_info
            print(f"👤 Contact: {contact.name} | {contact.email}")
            
            # Display sections
            print(f"📋 Sections found:")
            for section, blocks in resume.sections.items():
                if blocks:
                    print(f"  • {section.value.title()}: {len(blocks)} blocks")
            
            # Display top keywords
            print(f"🔑 Top Keywords ({len(resume.all_keywords)}):")
            for keyword in resume.all_keywords[:8]:
                print(f"  • {keyword}")
            
            # Show keyword distribution by section
            print(f"📊 Keywords by Section:")
            for section, blocks in resume.sections.items():
                if blocks:
                    section_keywords = []
                    for block in blocks:
                        section_keywords.extend(block.keywords)
                    unique_keywords = list(set(section_keywords))
                    if unique_keywords:
                        print(f"  {section.value.title()}: {', '.join(unique_keywords[:5])}")
        else:
            print("❌ Failed to parse resume")
            for error in result.errors:
                print(f"  • {error}")
    
    print(f"\n🎉 Demo completed!")


if __name__ == "__main__":
    demo_parser() 