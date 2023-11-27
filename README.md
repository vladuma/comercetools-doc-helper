# What is this
This is a repo with a PostgreSQL database containg Commercetools documentation (parsed in Nov 2023), with configured `pgvector` extension to enable vector search.
Documnetation pieces vere embedded using OpenAI API.
There is a Python backend app with routes to perform search on the database.
Frontend is a simple React app that uses backend API to answer questions about Commercetools.

# Setup
## 1. Prerequisits 
Create `.env` file (use `.env-sample` and an example), add your OpenAI API key to the file.

## 2. Run
Use `docker compose up --build` to run the app (make sure Docker is installed and running)

## 3. The app
- frontend is served at `localhost:3000`
- API is served at `localhost:80`

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
- You can re-parse the documentation using the `doc_parser.py` script in the `database` folder. Run it with `python3 ./database/doc_parser.py`, make sure you have Python and necessary dependensies installed locally. 
- The script will add records to the database.
- You can erase all data by deleting `/database/data/` directory.
- When trying to run the app you may see a database error (`pg_notify is not found`), this can happen because git failed to create empty directory. You can fix the issue by creating the missing directory manualy. Here is a list of all contents of `/database/data/`:
    - PG_VERSION
    - pg_dynshmem
    - pg_multixact
    - pg_snapshots
    - pg_tblspc
    - postgresql.auto.con
    - base
    - pg_hba.conf
    - pg_notify
    - pg_stat
    - pg_twophase
    - postgresql.con
    - global
    - pg_ident.conf
    - pg_replslot
    - pg_stat_tmp
    - pg_wal
    - postmaster.opt
    - pg_commit_ts
    - pg_logical
    - pg_serial
    - pg_subtrans
    - pg_xac
- You can connect to the database using the credentials in `docker-compose.yml` file.