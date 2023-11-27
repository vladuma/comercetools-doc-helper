import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import execute_values
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_params = {
    'dbname': 'parser_db',
    'user': 'parser',
    'password': 'parser_db_password',
    'host': 'db',
    'port': 5432
}

client = OpenAI(
    api_key=os.environ["OPEN_AI_KEY"],
)

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

def vectorize_query(query):
    response = client.embeddings.create(
        input=[query.replace("\n", " ")],
        model="text-embedding-ada-002"
    )

    vector = response.data[0].embedding
    return vector

def perform_vector_search(query_vector, similarity_threshold = 0.5, match_count = 10):
    search_query = """
    SELECT url, heading, content, token_count FROM search_by_vector_similarity(
      %s::vector,
      %s::float,
      %s::int
    );
    """
    cursor.execute(search_query, (query_vector, similarity_threshold, match_count))
    return cursor.fetchall()

@app.post("/search")
async def search(request: Request):
    body = await request.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")

    similarity_threshold = float(body.get("similarity_threshold") or 0.5)
    match_count = int(body.get("match_count") or 10)
    
    query_vector = vectorize_query(query)

    try:
        results = perform_vector_search(query_vector, similarity_threshold, match_count)
        results_list = [
            {
                "url": row[0],
                "heading": row[1],
                "content": row[2]
            }
            for row in results
        ]
        return {"results": results_list}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: Request):
    body = await request.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")

    similarity_threshold = 0.66
    match_count = 40

    query_vector = vectorize_query(query)

    try:
        results = perform_vector_search(query_vector, similarity_threshold, match_count)

        content_aggregate = []
        token_count_aggregate = 0

        for row in results:
            if (token_count_aggregate <= 3000):
                content_aggregate.append(f"## {row[2]}")
                token_count_aggregate += row[3]
        
        composed_prompt = f"Context: \n".join(content_aggregate) + "\n\nQuestion: " + query
        print(composed_prompt)
        print(token_count_aggregate)
        
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
                 As a student preparing to become a certified Comercetools Functional Architect,
                 you will engage in an open book examination designed to evaluate your expertise 
                 in the Comercetools platform. The examination will consist of a series of 
                 questions related to various aspects of Comercetools.
                 Each question may be accompanied by multiple answer choices. 
                 Be attentive to the instructions within each question to determine if it 
                 requires a single answer or allows for multiple correct answers. 
                 In instances where the question type is not specified, assume that it 
                 is a single-answer question.
                 Alongside the questions, you will be provided with relevant context and 
                 data pertinent to the scenario at hand. It is imperative that you apply your 
                 knowledge of Comercetools, your general understanding of eCommerce, and practical 
                 logic to analyze the information given and deduce the most accurate response.
                 Provide response in the following format: say 'Correct answer(s) is/ are', then 
                 list all correct numbers/letters of correct option(s),
                 if letter is not avaiable - spell out correct options.
                 Remember, the use of available resources is encouraged, but the ultimate goal is 
                 to demonstrate your ability to synthesize information and apply your learned 
                 skills to successfully address the problems presented. Good luck in showcasing 
                 your proficiency as a Comercetools Functional Architect.
                """},
                {"role": "user", "content": composed_prompt},
            ]
        )

        answer = chat_response.choices[0].message.content if chat_response.choices else "No response"

        return {"answer": answer}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"message": "Vector search API is up and running!"}
