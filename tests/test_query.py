import os
from pathlib import Path
from shlex import join
from libs.VectorStore import VectorStore
from libs.Api import Api
from libs.Client import Client
from libs.util import dd
import mimetypes
from libs.util import list_files
from app.config import SIMILARITY_THRESHOLD
import pandas as pd
script_dir = os.path.dirname(os.path.abspath(__file__))

cases = {
    "somebody who know how to manage customer database and information" : ["34131484.pdf"] ,
    "experience in sales of cable TV and internet services" : ["34131484.pdf"],
    "High School Diploma or equivalent" : ["34131484.pdf"],
    
    "expert in culinary arts" : ["30311202.pdf"],
    "must know how to sanitize kitchen and food preparation areas" : ["30311202.pdf"],
    "must know how to operate fryers, grills, ovens, and other kitchen equipment" : ["30311202.pdf"],

    "knowledge of wireless networks, lan wan, and internet protocols" : ["engineer.pdf"],
    "microsoft certified" : ["engineer.pdf"],
    "PC mac deployment and support" : ["engineer.pdf"],
    
    "engineering management" : ["37335325.pdf"],
    "phone application development" : ["37335325.pdf"],
    "android ios development" : ["37335325.pdf"],
    "working knowledge of SCRUM and AGILE methodology" : ["37335325.pdf"],
    
    
    "experience in teaching assitant" : ["70892619.pdf"],
    
       
    "table" : ["70892619.pdf"],
    "uae" : ["70892619.pdf"],
    "gulf country" : ["70892619.pdf"],
    "red" : ["70892619.pdf"],
    
}


def ingest(api=Api()):
    client = Client()
    files = list_files(f"{script_dir}/data")
    
    for file in files:
        response = api.ingest(
            local_file_path=file['path'],
            meta={
                "filename": file['name']
            })
        print(f"Ingested {file['name']} successfully with ID: {response}")

def query(question: str, top_k: int = 5, api=Api()):
    response = api.query(question= question, top_k= top_k)
    return response
    

def metrices(results, true_results):
    true_positives = 0
    false_positives = 0
    for result in results:
        if Path(result['meta']['filename']).name in true_results:
            true_positives += 1
        else:
            # If the result is not in true results, it's a false positive
            false_positives += 1
    
    return true_positives, false_positives

def precision(results, true_results):
    true_positive, false_positive = metrices(results, true_results)
    
    precision_value = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    return precision_value
    

def success_rate(results, true_results):
    for result in results:
        if Path(result['meta']['filename']).name in true_results:
            return True
    return False

def test_ingest():
    vector_store = VectorStore()
    vector_store.reset()
    ingest()
    
    
    precision_values = []
    questions = cases.items()
    result_files = []
    actual_files = []
    success_rate_values = []
    
    for question, expected_files in questions:
        response = query(question)
        result_files.append(', '. join(list(map(lambda x: x['meta']['filename'], response ))))
        actual_files.append(', '.join(expected_files))
        precision_values.append(precision(response, expected_files))
        success_rate_values.append(success_rate(response, expected_files))
    # create a dataframe with questions and precision values
    df = pd.DataFrame({
        "questions": list(cases.keys()),
        "actual": result_files,
        "expected": actual_files,
        "precision": precision_values,
        "success": success_rate_values
    })
    print(df)
    print("Average precision: "+ str(sum(precision_values) / len(precision_values)))
    print("Average success rate: "+ str(sum(success_rate_values) / len(success_rate_values)))
