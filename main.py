import os
import re
import requests
from bs4 import BeautifulSoup
import marvin 
from pydantic import BaseModel, Field

marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")
GOVINFO_API_KEY = os.getenv("GOVINFO_API_KEY")

# Provide a date in to get Congressional records from
YEAR = "2024"
MONTH = "01"
DAY = "29"

# Marvin class that defines a bill
class Bill(BaseModel):
    title: str = Field(description='Official title of the bill')
    number: str = Field(description='H.R. or S. + bill number')
    summary: str = Field(description='A cohesive, fluent, TL;DR style summary of the bill.')

# Get Congressional documents released on the provided date
crec = requests.get(f"https://api.govinfo.gov/packages/CREC-{YEAR}-{MONTH}-{DAY}/granules?pageSize=1000&granuleClass=DAILYDIGEST&api_key={GOVINFO_API_KEY}&offsetMark=*").json()

# Exit if no results are found
# Check if 'count' key exists in the crec dictionary and if it's 0
if 'count' not in crec or crec["count"] == 0:
    print("No results found.")
    exit()

# Get info about the Daily Digests from the House and Senate
daily_digest_house = next((item for item in crec["granules"] if item["title"] == "Daily Digest/House of Representatives"), None)
daily_digest_senate = next((item for item in crec["granules"] if item["title"] == "Daily Digest/Senate"), None)

# Exit if no results are found
if daily_digest_house is None or daily_digest_senate is None:
	print("Daily Digest not found.")
	exit()

# Get links for the Daily Digests from the House and Senate
daily_digest_house_rec = requests.get(f"{daily_digest_house['granuleLink']}?api_key={GOVINFO_API_KEY}").json()
daily_digest_senate_rec = requests.get(f"{daily_digest_senate['granuleLink']}?api_key={GOVINFO_API_KEY}").json()

# Get the text of the Daily Digests from the House and Senate
daily_digest_house_soup = BeautifulSoup(requests.get(f"{daily_digest_house_rec['download']['txtLink']}?api_key={GOVINFO_API_KEY}").content, 'html.parser')
daily_digest_senate_soup = BeautifulSoup(requests.get(f"{daily_digest_senate_rec['download']['txtLink']}?api_key={GOVINFO_API_KEY}").content, 'html.parser')

# Replace multiple spaces with a single space to reduce # of tokens and save on API costs ;)
daily_digest_house_text = re.sub(' +', ' ', daily_digest_house_soup.pre.text)
daily_digest_senate_text = re.sub(' +', ' ', daily_digest_senate_soup.pre.text)

# The magic: extract bills from the Daily Digests using Marvin!
bills = marvin.extract(daily_digest_house_text + "\n" + daily_digest_senate_text, Bill)

# Print the bills!
print("Bills:\n")
for bill in bills:
	pprint_messages(f"{bill.number}: {bill.title}\n{bill.summary}\n\n")
