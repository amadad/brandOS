import getpass
import os

# For GPT-4
os.environ["OPENAI_API_KEY"] = getpass.getpass()

from financial_datasets.generator import DatasetGenerator

# Create the dataset generator
generator = DatasetGenerator(
   model="gpt-3.5-turbo-0125",
   api_key=os.environ["OPENAI_API_KEY"],
)

# Generate the dataset!
dataset = generator.generate_from_pdf(
   url="https://www.berkshirehathaway.com/letters/2023ltr.pdf",
   max_questions=10,
)

for index, item in enumerate(dataset.items):
  print(f"Question {index + 1}: {item.question}")
  print(f"Answer: {item.answer}")
  print(f"Context: {item.context}")
  print()

  !pip install -U -q financial-datasets

https://github.com/virattt/financial-datasets/tree/main