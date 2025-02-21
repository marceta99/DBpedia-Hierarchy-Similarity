from typing import Dict, List
from collections import deque
from SPARQLWrapper import SPARQLWrapper, JSON


def _get_subcategories(category_uri: str) -> List[str]:
    """
    Dohvata potkategorije za dati category_uri (DBpedia) koristeći SPARQL.
    SPARQL upit:
      ?subCat skos:broader <category_uri>
    """
    endpoint = "https://dbpedia.org/sparql"
    query = f"""
    SELECT ?subCat
    WHERE {{
      ?subCat skos:broader <{category_uri}>
    }}
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    results = sparql.query().convert()
    subcats = []
    for binding in results["results"]["bindings"]:
        subcats.append(binding["subCat"]["value"])
    return subcats


def build_hierarchy_for_category(category_uri: str, max_depth: int = 2) -> Dict[int, List[str]]:
    """
    Vrši BFS nad potkategorijama počevši od 'category_uri', 
    do 'max_depth' nivoa. Rezultat je dict gde je ključ dubina,
    a vrednost lista kategorija na toj dubini.
    
    Primer rezultata za max_depth=2:
    {
      0: ["http://dbpedia.org/resource/Category:X"],
      1: ["..."],
      2: ["..."]
    }
    """
    visited = set()
    queue = deque([(category_uri, 0)])
    
    # Rezultat: mapiranje dubine -> lista kategorija na toj dubini
    hierarchy_levels: Dict[int, List[str]] = {}
    
    while queue:
        current_cat, depth = queue.popleft()
        
        if current_cat not in visited:
            visited.add(current_cat)
            
            if depth not in hierarchy_levels:
                hierarchy_levels[depth] = []
            hierarchy_levels[depth].append(current_cat)
            
            # Ako nismo dostigli max_depth, dodajemo potkategorije u red
            if depth < max_depth:
                subcats = _get_subcategories(current_cat)
                for sc in subcats:
                    if sc not in visited:
                        queue.append((sc, depth + 1))
    
    return hierarchy_levels


def build_combined_hierarchy(category_uris: List[str], max_depth: int = 2) -> Dict[str, Dict[int, List[str]]]:
    """
    Pravi hijerarhiju (BFS) za svaku kategoriju iz liste 'category_uris'
    i objedinjene rezultate vraća kao:
    {
      "http://dbpedia.org/resource/Category:Foo": { 0: [...], 1: [...], ... },
      "http://dbpedia.org/resource/Category:Bar": { 0: [...], 1: [...], ... },
      ...
    }
    """
    combined_result = {}
    for cat_uri in category_uris:
        hierarchy = build_hierarchy_for_category(cat_uri, max_depth)
        combined_result[cat_uri] = hierarchy
    return combined_result
