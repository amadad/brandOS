
import os
import google.generativeai as genai

GOOGLE_API_KEY=os.getenv("AIzaSyB1n0UNJ3OZqZy-t8kj9H8fdlG89vfgZdI")
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("What is the meaning of life?")