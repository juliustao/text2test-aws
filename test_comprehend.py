from comprehend import lambda_handler
import json

with open('test.json', 'r') as f:
    input_json = json.load(f)

output_json = lambda_handler(event=input_json, context=None)

print(output_json)
