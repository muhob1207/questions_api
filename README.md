# Instructions

1)clone this repository 

2)Open terminal and navigate to the "project" directory of "questions_api" directory

3)Make sure you have docker in your system and it is open

4)To install the necessary libraries write $ pip install -r requirements.txt

5)To create a container for the PostgreSQL database in docker write $ docker-compose up -d

The database connection settings can be found in the docker-compose.yml file. 

6)Start the server using the command: $ uvicorn main:app --host 0.0.0.0 --port 8000 --reload

7)Now you can make a POST request to this server. Example:

```python
import requests

url = "http://localhost:8000/get_questions/"

payload = {
    "questions_num": 5  
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Response Content:")
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")
```

8)Note that making a request to the endpoint will create new records in the database. You can check which records were created using the step below:

-In the terminal write: $ psql -h localhost -U admin -d muhob1207

-This will allow you to write SQL queries. To see all records from the 'questions' table write:

SELECT * FROM public.questions;


 
