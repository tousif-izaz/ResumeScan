#!/usr/bin/env python3
"""
Streamlit App for Resume Parser Testing
Upload PDF, DOCX, or paste text to test the MCP-style resume parser
"""

import streamlit as st
import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.parser import ResumeParser
from mcp.models import ParseResult


def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Resume Parser Demo",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Resume Parser Demo")
    st.markdown("Upload a resume file (PDF/DOCX) or paste text to test the parser")
    
    # Initialize parser
    parser = ResumeParser()
    
    # Sidebar for input method selection
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["File Upload", "Text Input"]
    )
    
    if input_method == "File Upload":
        handle_file_upload(parser)
    else:
        handle_text_input(parser)


def handle_file_upload(parser: ResumeParser):
    """Handle file upload functionality"""
    st.header("📁 File Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx', 'txt'],
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Parse the file
            result = parser.parse_file(tmp_file_path)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            # Display results
            display_results(result, uploaded_file.name)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


def handle_text_input(parser: ResumeParser):
    """Handle text input functionality"""
    st.header("📝 Text Input")
    
    # Sample resume text
    sample_text = """John Doe
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

SKILLS
Programming: Python, JavaScript, TypeScript, Java, SQL
Frameworks: React, Node.js, Express, Django, Flask
Tools: Git, Docker, AWS, Jenkins, Jira
Databases: PostgreSQL, MongoDB, Redis

EDUCATION
Bachelor of Science in Computer Science
University of Technology - 2018"""
    
    # Text input area
    resume_text = st.text_area(
        "Paste your resume text here:",
        value=sample_text,
        height=400,
        help="Paste your resume text and click 'Parse Resume'"
    )
    
    if st.button("Parse Resume", type="primary"):
        if resume_text.strip():
            result = parser.parse_text(resume_text)
            display_results(result, "Text Input")
        else:
            st.warning("Please enter some text to parse.")


def display_results(result: ParseResult, source_name: str):
    """Display parsing results"""
    st.header("📊 Parsing Results")
    
    if result.success and result.resume:
        resume = result.resume
        
        # Success message
        st.success("✅ Resume parsed successfully!")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "👤 Contact Info", 
            "📋 Sections", 
            "🔑 Keywords", 
            "📄 Raw Text"
        ])
        
        with tab1:
            display_contact_info(resume.contact_info)
        
        with tab2:
            display_sections(resume.sections)
        
        with tab3:
            display_keywords(resume.all_keywords, resume.sections)
        
        with tab4:
            display_raw_text(resume.raw_text)
        
        # Show messages
        if result.messages:
            st.info("📝 Processing Messages:")
            for message in result.messages:
                st.write(f"• {message}")
    
    else:
        st.error("❌ Failed to parse resume!")
        for error in result.errors:
            st.error(f"• {error}")


def display_contact_info(contact_info):
    """Display contact information"""
    st.subheader("Contact Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Name", contact_info.name or "Not found")
        st.metric("Email", contact_info.email or "Not found")
    
    with col2:
        st.metric("Phone", contact_info.phone or "Not found")
        st.metric("LinkedIn", contact_info.linkedin or "Not found")


def display_sections(sections):
    """Display parsed sections"""
    st.subheader("Parsed Sections")
    
    for section, blocks in sections.items():
        if blocks:
            with st.expander(f"{section.value.title()} ({len(blocks)} blocks)"):
                for i, block in enumerate(blocks):
                    st.markdown(f"**Block {i+1}:**")
                    st.text_area(
                        f"Content (Block {i+1})",
                        value=block.content,
                        height=100,
                        key=f"{section.value}_{i}",
                        disabled=True
                    )
                    if block.keywords:
                        st.write(f"**Keywords:** {', '.join(block.keywords)}")
                    st.divider()


def display_keywords(all_keywords, sections):
    """Display keyword analysis"""
    st.subheader("Keyword Analysis")
    
    # Overall keywords
    st.write(f"**Total Keywords Found:** {len(all_keywords)}")
    
    if all_keywords:
        # Display keywords in a nice format
        cols = st.columns(4)
        for i, keyword in enumerate(all_keywords):
            cols[i % 4].write(f"• {keyword}")
    
    # Keywords by section
    st.subheader("Keywords by Section")
    for section, blocks in sections.items():
        if blocks:
            section_keywords = []
            for block in blocks:
                section_keywords.extend(block.keywords)
            unique_keywords = list(set(section_keywords))
            
            if unique_keywords:
                with st.expander(f"{section.value.title()} Keywords"):
                    cols = st.columns(3)
                    for i, keyword in enumerate(unique_keywords):
                        cols[i % 3].write(f"• {keyword}")


def display_raw_text(raw_text):
    """Display raw text"""
    st.subheader("Raw Text")
    st.text_area(
        "Original text content:",
        value=raw_text,
        height=300,
        disabled=True
    )


if __name__ == "__main__":
    main() 