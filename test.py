import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content("Summarize this: I am a skilled Python developer with NLP experience.")
print(response.text)
