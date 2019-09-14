import boto3
import json


def comprehend(text):
    assert(isinstance(text, str))
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')
    print('Calling DetectKeyPhrases')
    result = json.dumps(comprehend.detect_key_phrases(Text=text, LanguageCode='en'), sort_keys=True, indent=4)
    print('End of DetectKeyPhrases\n')
    return result


if __name__ == '__main__':
    text = 'The mitochondria is an organelle that provides energy in the form of ATP for the cell.'
    result = comprehend(text)
    print(result)
