import requests
r = requests.post("https://1jwjnlh7r4.execute-api.us-east-2.amazonaws.com/prod/text2test",
                  json={"inputTranscript": "Joe went to the store. Sarah and Jessie are going swimming. The frog jumped and landed in the pond. Can I have some juice to drink? The pizza smells delicious. There is a fly in the car with us. Look on top of the refrigerator for the key. I am out of paper for the printer. Will you help me with the math homework? The music is too loud for my ears."})
print(r.status_code, r.reason)
print(r.json())
