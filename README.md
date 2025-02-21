
DBpedia Hierarchy & Similarity
This project provides a Python-based REST API (built with FastAPI) to:

Build a category hierarchy from DBpedia using a breadth-first search (BFS).
Compute similarity between DBpedia resources using either:
Hierarchical similarity (based on supercategories)
Vector similarity (using Sentence-BERT embeddings)
Combined similarity (average of both)
Project Structure
Copy
.
├── dbpedia_hierarchy/
│   ├── app.py
│   ├── hierarchy.py
│   ├── similarity.py
│   └── ...
├── venv/
├── .gitignore
└── README.md
dbpedia_hierarchy/
Contains the core Python source files:

hierarchy.py: BFS logic to build category hierarchies up to a specified depth.
similarity.py: Functions to calculate hierarchical, vector, and combined similarity.
app.py: FastAPI application exposing all endpoints.
venv/
Local Python virtual environment (ignored by Git).

.gitignore
Specifies which files/folders to exclude from version control (e.g., venv/, __pycache__/, etc.).

README.md
Project documentation (this file).

Requirements
Python 3.8+
FastAPI
Uvicorn
SPARQLWrapper
requests (optional if you use it for certain queries)
sentence-transformers
PyTorch
(Adjust this list based on your actual usage.)

Installation
Clone this repository:

bash
Copy
git clone https://github.com/marceta99/DBpedia-Hierarchy-Similarity.git
cd dbpedia-hierarchy-similarity
Create and activate a virtual environment (recommended):

bash
Copy
python -m venv venv
source venv/bin/activate   # On Linux/Mac
# On Windows:
# .\venv\Scripts\activate
Install dependencies (example):

bash
Copy
pip install fastapi uvicorn SPARQLWrapper requests sentence-transformers torch
If you have a requirements.txt, you can do:

bash
Copy
pip install -r requirements.txt
Usage
Navigate to the dbpedia_hierarchy folder (or stay in the root, but be sure to specify the correct module path when running uvicorn).

Run the FastAPI server:

bash
Copy
uvicorn dbpedia_hierarchy.app:app --reload
The --reload flag automatically restarts the server on code changes.
If you are in the dbpedia_hierarchy folder, use:
bash
Copy
uvicorn app:app --reload
Open your browser at http://127.0.0.1:8000/docs to access the interactive Swagger UI.

API Endpoints
1. Hierarchy Generation
POST /hierarchy
Generates a BFS-based category hierarchy for one or more DBpedia category URIs up to a given depth.

Request Body (JSON):

json
Copy
{
  "category_uris": [
    "http://dbpedia.org/resource/Category:Programming_languages",
    "http://dbpedia.org/resource/Category:Software"
  ],
  "depth": 2
}
Response Example:

json
Copy
{
  "hierarchies": {
    "http://dbpedia.org/resource/Category:Programming_languages": {
      "0": ["http://dbpedia.org/resource/Category:Programming_languages"],
      "1": ["..."],
      "2": ["..."]
    },
    "http://dbpedia.org/resource/Category:Software": {
      "0": ["http://dbpedia.org/resource/Category:Software"],
      "1": ["..."],
      "2": ["..."]
    }
  }
}
2. Similarity
A) Hierarchical Similarity
POST /similarity/hierarchical
Calculates a Jaccard-based similarity score between two DBpedia category URIs by examining shared supercategories.

Request Body (JSON):

json
Copy
{
  "uri1": "http://dbpedia.org/resource/Category:Python_(programming_language)",
  "uri2": "http://dbpedia.org/resource/Category:Programming_languages",
  "depth": 2
}
Response Example:

json
Copy
{
  "hierarchical_similarity": 0.72
}
B) Vector Similarity
POST /similarity/vector
Calculates the cosine similarity between Sentence-BERT embeddings of the labels/abstracts of two DBpedia resources.

Request Body (JSON):

json
Copy
{
  "uri1": "http://dbpedia.org/resource/Python_(programming_language)",
  "uri2": "http://dbpedia.org/resource/Programming_language"
}
Response Example:

json
Copy
{
  "vector_similarity": 0.85
}
C) Combined Similarity
POST /similarity/combined
Returns the average of the hierarchical and vector similarity scores.

Request Body (JSON):

json
Copy
{
  "uri1": "http://dbpedia.org/resource/Python_(programming_language)",
  "uri2": "http://dbpedia.org/resource/Programming_language",
  "depth": 2
}
Response Example:

json
Copy
{
  "combined_similarity": 0.78
}
Notes & Recommendations
SPARQL Endpoint: All queries use the official DBpedia SPARQL endpoint. Ensure you have a stable internet connection and be mindful of query performance.
Caching: For production use, implement caching of SPARQL results and embeddings to avoid repeated lookups.
Timeouts & Error Handling: You can add custom timeouts and robust error handling in your SPARQL queries and FastAPI routes.
Embedding Model: This project uses the all-MiniLM-L6-v2 model for Sentence-BERT. Feel free to experiment with other models for better performance or domain specificity.
License
MIT License (adjust if you have a specific license file).

Contributing
Fork the repository.
Create a new branch for your feature or bug fix.
Commit your changes and open a pull request.