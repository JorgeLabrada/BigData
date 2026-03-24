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
git clone https://github.com/JorgeLabrada/BigData.git
cd BigData
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
git clone https://github.com/JorgeLabrada/BigData.git
cd BigData
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

---

---

# Documentation

## table

- [aws cli basics](#aws-cli-basics)
- [s3](#s3)
- [glue](#glue)
- [athena](#athena)
- [spark / pyspark](#spark--pyspark)
- [random tips](#random-tips)

---

## aws cli basics

first things first, set up your credentials:

```bash
aws configure
# asks for: access key, secret key, region, output format

# check you're logged in as the right person
aws sts get-caller-identity
```

---

## s3


```bash
# list your buckets
aws s3 ls

# see what's inside a bucket
aws s3 ls s3://my-bucket/

# upload a file
aws s3 cp localfile.csv s3://my-bucket/data/

# upload a whole folder
aws s3 cp ./data/ s3://my-bucket/data/ --recursive

# download something
aws s3 cp s3://my-bucket/data/file.csv ./

# synchron
aws s3 sync ./local-folder s3://my-bucket/folder/

# delete a file
aws s3 rm s3://my-bucket/data/old-file.csv
```

> use `--dryrun` before syncin

---

## glue


```bash
# see your databases
aws glue get-databases

# list tables in a db
aws glue get-tables --database-name my_database

# check your jobs
aws glue get-jobs

# run a job
aws glue start-job-run --job-name my-etl-job

# see if it worked
aws glue get-job-runs --job-name my-etl-job

# crawlers (they scan s3 and figure out the schema automatically)
aws glue get-crawlers
aws glue start-crawler --name my-crawler
```

glue scripts run on spark under the hood, but they use their own "DynamicFrame" thing instead of regular dataframes — you have to convert:

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

datasource = glueContext.create_dynamic_frame.from_catalog(
    database="my_database",
    table_name="my_table"
)

# convert to normal spark df so you can work with it
df = datasource.toDF()
df.show(5)

job.commit()
```

---

## athena

```bash
# run a query
aws athena start-query-execution \
  --query-string "SELECT * FROM my_table LIMIT 10" \
  --query-execution-context Database=my_database \
  --result-configuration OutputLocation=s3://my-bucket/athena-results/

# check if it finished
aws athena get-query-execution --query-execution-id <execution-id>

# get the results
aws athena get-query-results --query-execution-id <execution-id>
```

you can also just use the web console which is way easier honestly.

```sql
-- point a table at an s3 path
CREATE EXTERNAL TABLE IF NOT EXISTS my_database.sales (
  order_id   STRING,
  product    STRING,
  amount     DOUBLE,
  order_date STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://my-bucket/data/sales/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- normal query
SELECT product, SUM(amount) AS total_sales
FROM my_database.sales
GROUP BY product
ORDER BY total_sales DESC;
```

> if your data is partitioned, always filter by partition — athena charges by how much data it scans

---

## spark / pyspark

distributed processing engine. used a lot with glue and emr.

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count

spark = SparkSession.builder.appName("MyApp").getOrCreate()

# read from s3
df = spark.read.csv("s3://my-bucket/data/file.csv", header=True, inferSchema=True)

df.printSchema()
df.show(5)

# filter and select
df.filter(col("amount") > 100).select("order_id", "product", "amount").show()

# groupby
df.groupBy("product").agg(
    count("order_id").alias("num_orders"),
    sum("amount").alias("total")
).show()

# save as parquet (much better than csv for big data)
df.write.mode("overwrite").parquet("s3://my-bucket/output/")
```



```python
df.createOrReplaceTempView("sales")

spark.sql("""
    SELECT product, SUM(amount) as total
    FROM sales
    GROUP BY product
    ORDER BY total DESC
""").show()
```

---

## random-tips

- s3 paths always start with `s3://`

- athena saves query results to s3, clean them up or they accumulate
- glue crawlers don't auto-run, you have to schedule them or trigger manually
- `--output table` makes cli output way more readable than the default json

```bash
aws s3 ls --output table
aws s3api list-buckets --query "Buckets[].Name"
```

---
