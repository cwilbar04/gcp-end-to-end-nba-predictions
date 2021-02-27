import pandas as pd
from google.cloud import bigquery
from google.cloud import bigquery_storage
from datetime import datetime

def create_model_data:
    project_id = os.environ.get('GCP_PROJECT')
    client = bigquery.Client(project=project_id)


