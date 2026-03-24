

import json
import math
import re
import time
from collections import defaultdict


# ---------------------------------------------------------------------------
# Minimal stop-word list (no external deps required)
# ---------------------------------------------------------------------------
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "are", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "that", "this",
    "these", "those", "it", "its", "he", "she", "they", "we", "you", "i",
    "me", "him", "her", "us", "them", "my", "your", "his", "our", "their",
    "what", "which", "who", "when", "where", "how", "all", "as", "if",
    "not", "no", "so", "up", "out", "about", "into", "than", "then",
    "there", "also", "just", "more", "one", "two", "after", "before",
    "over", "through", "between", "after", "while", "during", "without",
    "under", "around", "among", "s", "t", "re", "ll", "ve", "d", "m",
}


# ---------------------------------------------------------------------------
# quitar sufijos basura
# ---------------------------------------------------------------------------
class SimpleStemmer:
    # Lista de sufijos ordenados de mayor a menor longitud para priorizar
    # los recortes más específicos primero (ej. "ational" antes que "al")
    suffixes = [
        "ational", "tional", "enci", "anci", "izer", "ising", "izing",
        "ation", "ator", "alism", "ness", "ment", "ful", "ous", "ive",
        "ize", "ise", "ing", "ers", "ies", "es", "er", "ed", "ly", "al",
        "s",
    ]

    def stem(self, word: str) -> str:
        # Las palabras muy cortas se dejan igual para no mutilarlas
        if len(word) <= 3:
            return word
        # Prueba cada sufijo en orden; aplica el primero que encaje
        # siempre que la raíz resultante tenga más de 2 caracteres
        for suffix in self.suffixes:
            if word.endswith(suffix) and len(word) - len(suffix) > 2:
                return word[: len(word) - len(suffix)]
        return word


stemmer = SimpleStemmer()


# ---------------------------------------------------------------------------
# Text processing pipeline
# ---------------------------------------------------------------------------
def tokenize(text: str) -> list[str]:
    # Convierte a minúsculas, elimina todo lo que no sea letra/número/espacio
    # y separa por espacios — produce tokens crudos sin normalizar
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()


def preprocess(text: str) -> list[str]:
    # Pipeline completa: tokeniza → filtra stopwords y tokens de 1 char → stemming
    # Se usa tanto al indexar como al procesar consultas, garantizando que
    # query y documentos queden en el mismo espacio de términos
    tokens = tokenize(text)
    return [
        stemmer.stem(tok)
        for tok in tokens
        if tok not in STOP_WORDS and len(tok) > 1
    ]


# ---------------------------------------------------------------------------
# Inverted Index
# ---------------------------------------------------------------------------
class InvertedIndex:
    def __init__(self):
        # Índice principal: término → { doc_id → frecuencia }
        self.index: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
        # Índice posicional: término → { doc_id → [posiciones] } — listo para búsqueda de frases
        self.positions: dict[str, dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))
        self.doc_lengths: dict[int, int] = {}   # doc_id → cantidad de tokens del documento
        self.doc_store: dict[int, dict] = {}    # doc_id → documento original completo

    def add_document(self, doc: dict):
        # Agrega un documento al índice: concatena título + texto, los preprocesa
        # y registra la frecuencia y posición de cada token
        doc_id = doc["id"]
        self.doc_store[doc_id] = doc
        combined = doc.get("title", "") + " " + doc.get("text", "")
        tokens = preprocess(combined)
        self.doc_lengths[doc_id] = len(tokens)
        for pos, token in enumerate(tokens):
            self.index[token][doc_id] += 1
            self.positions[token][doc_id].append(pos)

    def build(self, documents: list[dict]):
        # Construye el índice completo iterando sobre todos los documentos del corpus
        for doc in documents:
            self.add_document(doc)

    @property
    def vocabulary(self) -> set[str]:
        # Conjunto de todos los términos únicos indexados
        return set(self.index.keys())

    @property
    def num_docs(self) -> int:
        # Total de documentos en el índice
        return len(self.doc_store)

    @property
    def avg_doc_length(self) -> float:
        # Longitud promedio de documento en tokens — usada por BM25 para normalización
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)


# ---------------------------------------------------------------------------
# animo plebe
# ---------------------------------------------------------------------------
class BM25:
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = index
        self.k1 = k1   # controla la saturación de frecuencia de término
        self.b = b      # controla la penalización por longitud del documento

    def idf(self, term: str) -> float:
        # Inverse Document Frequency: términos raros en el corpus tienen IDF alto,
        # términos muy comunes tienen IDF bajo (cercano a 0)
        n = self.index.num_docs
        df = len(self.index.index.get(term, {}))
        if df == 0:
            return 0.0
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def score(self, doc_id: int, query_terms: list[str]) -> float:
        # Calcula el score BM25 de un documento para una consulta dada.
        # Por cada término de la query: pondera TF normalizado × IDF y los suma.
        # TF se satura (no crece infinito) y se ajusta por longitud del documento.
        dl = self.index.doc_lengths.get(doc_id, 0)
        avgdl = self.index.avg_doc_length
        score = 0.0
        for term in query_terms:
            tf = self.index.index.get(term, {}).get(doc_id, 0)
            if tf == 0:
                continue
            idf = self.idf(term)
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (dl / (avgdl or 1)))
            score += idf * (numerator / denominator)
        return score


# ---------------------------------------------------------------------------
# Autom
# ---------------------------------------------------------------------------
class Autocomplete:
  

    def __init__(self):
        self._trie: dict = {}
        self._df: dict[str, int] = {}   # término -> frecuencia documental

    def build(self, index: InvertedIndex):
        # Construye el trie insertando cada término del vocabulario
        # carácter por carácter; el nodo hoja guarda el término completo en "$"
        for term, postings in index.index.items():
            self._df[term] = len(postings)
            node = self._trie
            for char in term:
                node = node.setdefault(char, {})
            node["$"] = term  # marcador de hoja — guarda el término completo

    def _collect(self, node: dict, results: list[str]):
        # Recorre recursivamente el subárbol del trie a partir de un nodo
        # y recolecta todos los términos completos que encuentre
        for key, child in node.items():
            if key == "$":
                results.append(child)
            else:
                self._collect(child, results)

    def suggest(self, prefix: str, limit: int = 8) -> list[str]:
        # Busca el prefijo en el trie carácter a carácter; si no existe retorna vacío.
        # Si existe, recolecta todos los términos del subárbol y los ordena
        # por frecuencia documental descendente
        prefix = prefix.lower().strip()
        if not prefix:
            return []
        node = self._trie
        for char in prefix:
            node = node.get(char)
            if node is None:
                return []
        results: list[str] = []
        self._collect(node, results)
        # Ordena por frecuencia documental descendente, luego alfabéticamente
        results.sort(key=lambda t: (-self._df.get(t, 0), t))
        return results[:limit]


# ---------------------------------------------------------------------------
# Main Search Engine
# ---------------------------------------------------------------------------
class MusicSearchEngine:
    def __init__(self, corpus_path: str = "corpus.json"):
        self.index = InvertedIndex()
        self.bm25 = None
        self.autocomplete = Autocomplete()
        self._load(corpus_path)

    def _load(self, path: str):
        # Lee el corpus JSON, construye el índice invertido,
        # inicializa el scorer BM25 y el autocomplete en un solo paso
        with open(path, "r", encoding="utf-8") as f:
            documents = json.load(f)
        self.index.build(documents)
        self.bm25 = BM25(self.index)
        self.autocomplete.build(self.index)

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 10) -> dict:
        # Flujo completo de búsqueda:
        # 1. Preprocesa la query con la misma pipeline del índice
        # 2. Une las posting lists de todos los tokens → candidatos
        # 3. Puntúa cada candidato con BM25
        # 4. Ordena descendente y devuelve los top_k con metadatos
        start = time.time()
        query_tokens = preprocess(query)

        if not query_tokens:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "search_time_ms": 0,
                "stats": self.stats(),
            }

        # Reúne documentos candidatos (unión de posting lists)
        candidates: set[int] = set()
        for term in query_tokens:
            candidates |= set(self.index.index.get(term, {}).keys())

        # Puntúa cada candidato
        scored = [
            (doc_id, self.bm25.score(doc_id, query_tokens))
            for doc_id in candidates
        ]
        scored.sort(key=lambda x: -x[1])
        scored = scored[:top_k]

        results = []
        for doc_id, score in scored:
            doc = self.index.doc_store[doc_id]
            results.append(
                {
                    "id": doc_id,
                    "title": doc.get("title", ""),
                    "artist": doc.get("artist", ""),
                    "category": doc.get("category", ""),
                    "source": doc.get("source", ""),
                    "text": doc.get("text", ""),
                    "score": round(score, 4),
                }
            )

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return {
            "query": query,
            "query_terms": query_tokens,
            "results": results,
            "total_results": len(results),
            "search_time_ms": elapsed_ms,
            "stats": self.stats(),
        }

    # ------------------------------------------------------------------
    def suggest(self, prefix: str, limit: int = 8) -> list[str]:
        # Delega al autocomplete; devuelve sugerencias para el prefijo dado
        return self.autocomplete.suggest(prefix, limit)

    # ------------------------------------------------------------------
    def stats(self) -> dict:
        # Estadísticas generales del índice para mostrar en la UI
        return {
            "total_documents": self.index.num_docs,
            "vocabulary_size": len(self.index.vocabulary),
            "avg_doc_length": round(self.index.avg_doc_length, 1),
        }

    # ------------------------------------------------------------------
    def get_index_data(self) -> dict:
        # Serializa los 50 términos más frecuentes y las longitudes de todos los
        # documentos — usado por la página de visualización del índice
        top_terms = sorted(
            self.index.index.items(),
            key=lambda kv: len(kv[1]),
            reverse=True,
        )[:50]
        return {
            "top_terms": [
                {"term": t, "df": len(postings), "docs": list(postings.keys())}
                for t, postings in top_terms
            ],
            "doc_lengths": {
                str(k): v for k, v in self.index.doc_lengths.items()
            },
        }
