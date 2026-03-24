# 🎵 Vinyl — Music Search Engine

**Student:** Jorge Alfonso Labrada Ramos (vape)  
**Course:** Information Retrieval / Search Engines

---

## Domain & Justification

**Domain: Music** — Album reviews and artist biographies.

Music is a domain rich with descriptive language, named entities (artists, albums, songs), genre terminology, historical context, and emotional vocabulary. This makes it an ideal corpus for testing a BM25 ranking system: queries can be factual ("Miles Davis Kind of Blue"), thematic ("jazz improvisation"), biographical ("Amy Winehouse Grammy"), or critical ("best album 1990s grunge"), all of which benefit from TF-IDF-style relevance weighting over a diverse, text-heavy collection.

The corpus contains **25 documents**: a mix of full-length album reviews and artist biographies spanning jazz, soul, rock, hip-hop, electronic, and pop — sourced from Rolling Stone, Pitchfork, AllMusic, and Biography.com.

---

## Enhancement Implemented

**Enhancement C — Autocomplete**

As the user types in the search bar, term suggestions appear in a dropdown, populated by querying `/api/autocomplete` against a **Trie** built from the engine's vocabulary (all stemmed tokens from the corpus).

Features:
- Debounced API calls (180 ms) to avoid request flooding
- Matches only the **last word** being typed — previous words are preserved
- Suggestions ranked by **document frequency** (most common terms first)
- Full **keyboard navigation**: `↑` `↓` to move, `Enter` to select, `Escape` to dismiss
- Matching prefix is **bolded** inside each suggestion
- Graceful fallback on network error

---

## Project Structure

```
my-search-engine/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── corpus.json              # 25 music documents with sources
├── search_engine.py         # Text processing, Inverted Index, BM25, Autocomplete (Trie)
├── app.py                   # Flask web server
├── templates/
│   ├── base.html
│   ├── index.html           # Homepage with search bar
│   ├── results.html         # Search results with term highlighting
│   └── index_view.html      # Inverted index visualizer
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── autocomplete.js
        └── highlight.js
```

---

## Search Engine Components

| Component | Details |
|---|---|
| **Tokenization** | Lowercase, regex punctuation removal, whitespace split |
| **Stop words** | Custom 80-word list, no external dependencies |
| **Stemming** | Custom suffix-stripping stemmer (no NLTK required) |
| **Inverted Index** | Dictionary of `term → {doc_id → frequency}` + positional index |
| **BM25** | Standard BM25 with k1=1.5, b=0.75 |
| **Autocomplete** | Trie over vocabulary, suggestions sorted by document frequency |

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Homepage |
| `GET /search?q=<query>` | HTML search results |
| `GET /api/search?q=<query>` | JSON search results |
| `GET /api/autocomplete?q=<prefix>` | JSON autocomplete suggestions |
| `GET /index-view` | Inverted index visualization page |

---

## 🐳 Run with Docker (recommended)

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/my-search-engine.git
cd my-search-engine
```

### 2. Build and start the container
```bash
docker-compose up --build
```

### 3. Open in browser
```
http://localhost:5000
```

### 4. Stop the container
```bash
docker-compose down
```

> The `volumes` mount in `docker-compose.yml` maps your local folder into the container, so any edits to the code are reflected immediately without rebuilding.

---

## 🐍 Run Locally (without Docker)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/my-search-engine.git
cd my-search-engine
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
python app.py
```

### 5. Open in browser
```
http://localhost:5000
```

> **No external NLP libraries required.** The engine uses only Python's standard library plus Flask.

---

## Example Queries to Try

- `Radiohead OK Computer`
- `jazz improvisation Miles Davis`
- `Beyoncé Lemonade Black Lives`
- `guitar rock album 1990s`
- `Grammy soul voice`
- `producer synthesizer electronic`

---

## Screenshots

*(Add screenshots of the homepage, search results, and autocomplete dropdown here)*
