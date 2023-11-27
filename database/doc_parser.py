import os
import re
import requests
from bs4 import BeautifulSoup
import psycopg2
from urllib.parse import urljoin, urlparse
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPEN_AI_KEY"],
)

# Database connection parameters
db_params = {
    'dbname': 'parser_db',
    'user': 'parser',
    'password': 'parser_db_password',
    'host': 'localhost',
    'port': 5432
}

# Connect to your database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Function to create table (if not exists)
def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentation (
            id SERIAL PRIMARY KEY,
            url TEXT,
            heading TEXT,
            content TEXT,
            token_count INTEGER,
            vector FLOAT8[]
        );
    """)
    conn.commit()

# Function to insert data into the database
def insert_data(url, heading, content, token_count, vector):
    cursor.execute("""
        INSERT INTO documentation (url, heading, content, token_count, vector)
        VALUES (%s, %s, %s, %s, %s);
    """, (url, heading, content, token_count, vector))
    conn.commit()

def get_all_links(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        link_path = link['href'].split('#')[0]
        full_url = urljoin(url, link_path)
        if urlparse(url).netloc == urlparse(full_url).netloc:
            links.add(full_url)
    return links

def get_vector_from_openai(text):
    try:
        response = client.embeddings.create(
            input=[text.replace("\n", " ")],
            model="text-embedding-ada-002"
        )

        vector = response.data[0].embedding
        token_count = response.usage.total_tokens

        return (vector, token_count)
    except Exception as e:
        print(f"An error occurred while vectorizing text: {e}")
        return (None, None)
    
def get_section_text(section):
    texts = section.find_all(text=True)
    return ' '.join(text.strip() for text in texts) 

# Function to parse and process a page
def parse_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    for section in soup.find_all('section'):
        header = section.find(re.compile('^h[1-6]$'))
        if header:
            heading = ' '.join(header.stripped_strings)

            content = get_section_text(section)
            print('heading:', heading)
            print('content:', content)

            if content:
                vector, token_count = get_vector_from_openai(content)
                if vector is not None:
                    print('token_count:', token_count)
                    insert_data(url, heading, content, token_count, vector)

# Function to crawl the website
def crawl_site(start_url):
    visited = set()
    pages_to_visit = get_all_links(start_url)

    while pages_to_visit:
        current_page = pages_to_visit.pop()
        if current_page not in visited:
            print(f"Processing: {current_page}")
            parse_page(current_page)
            visited.add(current_page)
            pages_to_visit.update(get_all_links(current_page) - visited)

# Main script
if __name__ == '__main__':
    create_table()
    start_url = 'https://docs.commercetools.com/docs/composable-commerce'
    crawl_site(start_url)
