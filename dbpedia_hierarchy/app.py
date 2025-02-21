from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from hierarchy import build_combined_hierarchy
from similarity import (
    compute_hierarchical_similarity,
    compute_vector_similarity,
    compute_combined_similarity
)

app = FastAPI(
    title="DBpedia API - Hierarchy & Similarity",
    description="Primenjuje BFS za kategorije i racuna razlicite oblike slicnosti medju DBpedia resursima.",
    version="1.0.0"
)

# ----------------------------------------------------
# 1) Hijerarhija (BFS)
# ----------------------------------------------------
class HierarchyRequest(BaseModel):
    category_uris: List[str]
    depth: int = 2

@app.post("/hierarchy")
def build_hierarchy_endpoint(request: HierarchyRequest):
    """
    Kreira 'objedinjenu' hijerarhiju za vise kategorija (BFS do odredjene dubine).
    """
    try:
        result = build_combined_hierarchy(request.category_uris, max_depth=request.depth)
        return {"hierarchies": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------------------------------
# 2) Sličnost (hijerarhijska, vektorska, kombinovana)
# ----------------------------------------------------
class SimilarityRequest(BaseModel):
    uri1: str
    uri2: str
    depth: int = 2

@app.post("/similarity/hierarchical")
def hierarchical_similarity(req: SimilarityRequest):
    """
    Vraća hijerarhijsku sličnost (npr. Jaccard) baziranu na *superkategorijama*.
    """
    try:
        score = compute_hierarchical_similarity(req.uri1, req.uri2, req.depth)
        return {"hierarchical_similarity": score}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/similarity/vector")
def vector_similarity(req: SimilarityRequest):
    """
    Vraća vektorsku (Sentence-BERT) sličnost između [0.0, 1.0].
    """
    try:
        score = compute_vector_similarity(req.uri1, req.uri2)
        return {"vector_similarity": score}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/similarity/combined")
def combined_similarity(req: SimilarityRequest):
    """
    Kombinuje hijerarhijsku i vektorsku sličnost (prosek).
    """
    try:
        score = compute_combined_similarity(req.uri1, req.uri2, req.depth)
        return {"combined_similarity": score}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
