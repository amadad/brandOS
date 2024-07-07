import os
import glob
import json
import instructor
import openai
import markdown
from bs4 import BeautifulSoup
from typing import List
from pydantic import BaseModel, Field

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the Pydantic models
class QAContext(BaseModel):
    question: str = Field(..., description="A question based on the blog post content")
    answer: str = Field(..., description="The answer to the question")
    context: str = Field(..., description="The relevant context from the blog post")

class BlogPostQA(BaseModel):
    qa_pairs: List[QAContext] = Field(..., description="List of 10 question-answer-context pairs")

# Initialize the instructor client
client = instructor.patch(openai.ChatCompletion)

def extract_text_from_markdown(markdown_content):
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def generate_qa_pairs(blog_post_content):
    prompt = f"""
    Given the following blog post content, generate 10 question-answer-context pairs:

    {blog_post_content[:4000]}  # Limit content to 4000 characters to avoid token limits

    Generate diverse questions covering different aspects of the blog post.
    Ensure that the answer is concise and the context provides supporting information.
    """

    try:
        response = client.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_model=BlogPostQA
        )
        return response.qa_pairs
    except Exception as e:
        print(f"Error generating QA pairs: {str(e)}")
        return []

def process_markdown_files(directory_path):
    markdown_files = glob.glob(os.path.join(directory_path, "*.md"))
    print(f"Found {len(markdown_files)} markdown files in {directory_path}")
    
    all_qa_pairs = []
    
    for file_path in markdown_files:
        print(f"Processing file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            
            blog_post_content = extract_text_from_markdown(markdown_content)
            print(f"Extracted {len(blog_post_content)} characters from the markdown file")
            
            qa_pairs = generate_qa_pairs(blog_post_content)
            print(f"Generated {len(qa_pairs)} QA pairs")

            # Convert Pydantic models to dictionaries
            qa_pairs_dict = [qa_pair.dict() for qa_pair in qa_pairs]
            all_qa_pairs.extend(qa_pairs_dict)
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

    if all_qa_pairs:
        # Save all QA pairs to a JSON file
        output_file = "qa_pairs_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
        print(f"QA pairs have been saved to {output_file}")
    else:
        print("No QA pairs were generated.")

if __name__ == "__main__":
    directory_path = "/Users/amadad/Desktop/test/"
    process_markdown_files(directory_path)