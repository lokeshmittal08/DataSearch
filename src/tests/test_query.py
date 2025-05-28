def test_query():
    data = [{
        "file_name":  "file1.txt",
        "text": "Its an image file. In the image there are three people, 2 people are smiling.",
        "queries_matching":[
            "three people",
            "smiling",
            "people"
        ]
    }]
    
    for item in data:
        build_or_update_index(item["file_name"], item["text"])
    
    
    
    