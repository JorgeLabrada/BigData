

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
