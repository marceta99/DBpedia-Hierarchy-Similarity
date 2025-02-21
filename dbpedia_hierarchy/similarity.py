from typing import Set
from collections import deque

from SPARQLWrapper import SPARQLWrapper, JSON
import torch
from sentence_transformers import SentenceTransformer

# Inicijalizujemo model jednom (sprečava višestruko učitavanje)
_sbert_model = SentenceTransformer('all-MiniLM-L6-v2')


def _get_supercategories(category_uri: str) -> Set[str]:
    """
    Pomoćna funkcija za hijerarhijsku sličnost:
    Vraća skup superkategorija (nadkategorija) za dati URI (koji mora biti Category:).
    """
    endpoint = "https://dbpedia.org/sparql"
    query = f"""
    SELECT ?superCat
    WHERE {{
      <{category_uri}> skos:broader ?superCat .
    }}
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    supercats = set()
    for binding in results["results"]["bindings"]:
        supercats.add(binding["superCat"]["value"])
    return supercats


def _get_all_categories(uri: str, depth: int = 2) -> Set[str]:
    """
    BFS do zadate dubine nad superkategorijama.
    Vraća skup kategorija (uključujući i polaznu ako je Category:).
    """
    visited = set()
    queue = deque([(uri, 0)])
    visited.add(uri)

    while queue:
        current, level = queue.popleft()
        
        if level < depth:
            supercats = _get_supercategories(current)
            for sc in supercats:
                if sc not in visited:
                    visited.add(sc)
                    queue.append((sc, level + 1))

    return visited


def compute_hierarchical_similarity(uri1: str, uri2: str, depth: int = 2) -> float:
    """
    Računa hijerarhijsku sličnost nad superkategorijama (Jaccard).
    """
    cats1 = _get_all_categories(uri1, depth)
    cats2 = _get_all_categories(uri2, depth)

    if not cats1 or not cats2:
        return 0.0

    intersection = cats1.intersection(cats2)
    union = cats1.union(cats2)
    return len(intersection) / len(union)


def _get_label_or_abstract(uri: str) -> str:
    """
    Dohvata labelu (ili abstract) iz DBpedia za date resurs.
    Ovde samo primer: rdfs:label (en).
    """
    endpoint = "https://dbpedia.org/sparql"
    query = f"""
    SELECT ?label
    WHERE {{
      <{uri}> rdfs:label ?label .
      FILTER (lang(?label) = 'en')
    }}
    LIMIT 1
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    try:
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            return results["results"]["bindings"][0]["label"]["value"]
    except:
        pass
    
    # Ako ne nađemo labelu, vrati sam URI kao fallback
    return uri


def compute_vector_similarity(uri1: str, uri2: str) -> float:
    """
    Računa vektorsku (embeddings) sličnost pomoću Sentence-BERT modela.
    """
    text1 = _get_label_or_abstract(uri1)
    text2 = _get_label_or_abstract(uri2)

    emb1 = _sbert_model.encode(text1, convert_to_tensor=True)
    emb2 = _sbert_model.encode(text2, convert_to_tensor=True)

    cos_sim = torch.nn.functional.cosine_similarity(emb1, emb2, dim=0).item()
    return float(cos_sim)


def compute_combined_similarity(uri1: str, uri2: str, depth: int = 2) -> float:
    """
    Kombinuje hijerarhijsku i vektorsku sličnost (prosek).
    """
    sim_hier = compute_hierarchical_similarity(uri1, uri2, depth)
    sim_vec = compute_vector_similarity(uri1, uri2)
    return (sim_hier + sim_vec) / 2.0
