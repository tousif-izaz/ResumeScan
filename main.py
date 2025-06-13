import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

# === MCP Elements ===
# Model = `llm` (Gemini)
# Context = input variables
# Prompt = Task instruction

prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are a resume assistant. Extract the following fields from the resume text:
- Name
- Email
- Phone
- Skills

Resume Text:
{text}
"""
)

chain = LLMChain(llm=llm, prompt=prompt)

# === Test input ===
test_resume = """
John Doe
Email: john.doe@example.com
Phone: +1 555-123-4567

Skills: Python, SQL, Machine Learning, Data Analysis
"""

if __name__ == "__main__":
    response = chain.run(text=test_resume)
    print("📄 Extracted Resume Info:\n", response)
