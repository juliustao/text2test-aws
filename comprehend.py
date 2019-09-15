import boto3

client = boto3.client('comprehend')


def lambda_handler(event, context):
    results = []

    input_text = event['inputTranscript']
    index_list = [0]
    for i in range(len(input_text)):
        if input_text[i] in ['.', '?', '!', '\n']:
            index_list.append(i+1)

    if len(index_list) <= 1:
        return results

    list_of_input_sentences = []
    for i in range(len(index_list) - 1):
        sentence = input_text[index_list[i]:index_list[i+1]]
        if len(sentence) > 0:
            list_of_input_sentences.append(sentence)
    # splits up input text into sentences

    if len(list_of_input_sentences) <= 0:
        return results

    list_of_entities_in_sentences = client.batch_detect_entities(TextList=list_of_input_sentences, LanguageCode='en')['ResultList']
    # type(sentence_entities_list): list of dictionaries

    if len(list_of_input_sentences) != len(list_of_entities_in_sentences):
        return results

    for i in range(len(list_of_entities_in_sentences)):
        # type(sentence_entities): dictionary

        entities_list = list_of_entities_in_sentences[i]['Entities']
        # type(entities_list): list of dictionaries

        # select the highest confidence entity and use it as our blank
        max_confidence = 0.0
        max_conf_entity = ''

        # find max confidence entity
        for entity in entities_list:
            if float(entity['Score']) > max_confidence:
                max_conf_entity = entity

        question = ''
        answer = ''
        # type(entity): dictionary
        if float(max_conf_entity['Score']) >= 0.95:
            begin_index = int(max_conf_entity['BeginOffset'])
            end_index = int(max_conf_entity['EndOffset'])

            blank = '_' * (end_index - begin_index)
            question = input_text[:begin_index] + blank + input_text[end_index:]
            # question is the original sentence with a blank where the highest confidence word is.

            answer = max_conf_entity['Text']
            # answer is the text of the entity

        if len(question) != 0 and len(answer) != 0:
            result = {
                'question': question,
                'answer': answer,
            }
            results.append(result)

    return results
