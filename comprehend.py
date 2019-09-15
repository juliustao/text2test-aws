import boto3
import re

MIN_SCORE = 0.85

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|me|edu)"
digits = "([0-9])"
months = "(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[.]"

client = boto3.client('comprehend')


def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(months, "\\1<prd>", text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    if "e.g." in text: text = text.replace("e.g.", "e<prd>g<prd>")
    if "i.e." in text: text = text.replace("i.e.", "i<prd>e<prd>")
    if "..." in text: text = text.replace("...", "<prd><prd><prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences


def lambda_handler(event, context):
    results = []

    input_text = event['inputTranscript']
    list_of_input_sentences = split_into_sentences(input_text)

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
