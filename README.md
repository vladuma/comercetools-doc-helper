# What is this
This is a repo with a PostgreSQL database containg Commercetools documentation (parsed in Nov 2023), with configured `pgvector` extension to enable vector search.
Documnetation pieces vere embedded using OpenAI API.
There is a Python backend app with routes to perform search on the database.
Frontend is a simple React app that uses backend API to answer questions about Commercetools.

# Setup
## 1. Create `.env` file (use `.env-sample` and an example), add your OpenAI API key to the file.

## 2. Run `docker compose up --build` (make sure Docker is installed and running)

## 3. The app
a. frontend is served at `localhost:3000`
b. API is served at `localhost:80`

# The API 
Consists of 2 routes: `/search` & `/ask`

## `/search`
Body:
- query: your question, a string. Required.
- similarity_treshold: similarity score, a float from 0 to 1.
- match_count: how many DB records to return, a number. 

Example: 
```
{
    "query": "",
    "similarity_treshold": 0.5,
    "match_count": 10
}
```

Returns a list of pieces of CT documentation that match your query.

## `/ask`
Body:
- query: your question, a string. Required.

Example:
```
{
    "query": ""
}
```

Retruns an answer to your question based on ChatGPT-4 analysis of CT docs related to the query.

# Manage database
You can re-parse the documentation using the `doc_parser.py` script in the `database` folder. Run it with `python3 ./database/doc_parser.py`, make sure you have Python and necessary dependensies installed locally. 
Th script will add records to the database.
You can erase all data by deleting `/database/data/` directory.
Tou can connect to the database using the credentials in `docker-compose.yml` file.