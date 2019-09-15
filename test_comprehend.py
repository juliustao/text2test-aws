from comprehend import lambda_handler
from sample import sample

input_json = {
    'inputTranscript': sample
}

output_json = lambda_handler(event=input_json, context=None)

print(output_json)
