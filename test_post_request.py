import requests
from sample import sample

r = requests.post("https://1jwjnlh7r4.execute-api.us-east-2.amazonaws.com/prod/text2test",
                  json={"inputTranscript": sample})
print(r.status_code, r.reason)
print(r.json())
