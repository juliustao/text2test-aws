import boto3

MIN_SCORE = 0.85
DELIMITERS = ['.', '?', '!', '\n']

client = boto3.client('comprehend')


def lambda_handler(event, context):
    results = []

    input_text = event['inputTranscript']
    index_list = [0]
    for i in range(len(input_text)):
        if input_text[i] in DELIMITERS:
            index_list.append(i+1)

    if len(index_list) <= 1:
        return results

    list_of_input_sentences = []
    for i in range(len(index_list) - 1):
        sentence = input_text[index_list[i]:index_list[i+1]].strip(' ”"\')')
        if len(sentence) > 2:
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

        if len(entities_list) == 0:
            continue

        # select the highest confidence entity and use it as our blank
        max_score = 0.0
        max_score_entity = {'Score': max_score}

        # find max confidence entity
        for entity in entities_list:
            if float(entity['Score']) > max_score:
                max_score_entity = entity

        question = ''
        answer = ''
        score = 0.0
        # type(entity): dictionary
        if float(max_score_entity['Score']) >= MIN_SCORE:
            begin_index = int(max_score_entity['BeginOffset'])
            end_index = int(max_score_entity['EndOffset'])

            blank = '_' * (end_index - begin_index)
            question = list_of_input_sentences[i][:begin_index] + blank + list_of_input_sentences[i][end_index:]
            # question is the original sentence with a blank where the highest confidence word is.

            answer = max_score_entity['Text']
            # answer is the text of the entity

            score = max_score_entity['Score']

        if len(question) != 0 and len(answer) != 0 and score > 0.0:
            result = {
                'question': question,
                'answer': answer,
                'score': score,
            }
            results.append(result)

    return results
