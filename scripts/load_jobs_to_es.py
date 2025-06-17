from elasticsearch import Elasticsearch
import json

# Connect to local ES (inside Docker network)
es = Elasticsearch("http://localhost:9200")

index_name = "job_postings"

# Define index mapping
mapping = {
    "mappings": {
        "properties": {
            "job_title": {"type": "keyword"},
            "company": {"type": "keyword"},
            "location": {"type": "keyword"},
            "employment_type": {"type": "keyword"},
            "experience_level": {"type": "keyword"},
            "industry": {"type": "keyword"},
            "salary_range": {"type": "keyword"},
            "skills": {"type": "keyword"},
            "remote_option": {"type": "keyword"},
            "posted_date": {"type": "date"}
        }
    }
}

# Create index
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

# Load and index JSON lines
with open("job_postings_1000.json", "r") as file:
    for line in file:
        es.index(index=index_name, document=json.loads(line.strip()))

print("✅ Job data loaded into Elasticsearch.")
