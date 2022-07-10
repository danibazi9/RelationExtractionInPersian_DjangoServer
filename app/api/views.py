import json
import os
import subprocess

import stanza
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from predpatt import PredPatt, load_conllu


@api_view(['POST'])
def seraji_output_view(request):
    if 'input_text' in request.data:
        text = request.data['input_text']

        with open('file.txt', 'w', encoding='utf-8') as f:
            f.write(text.replace('\r', '').strip())
            f.close()

        bash_command = """curl -F data=@file.txt -F model=persian -F tokenizer=normalized_spaces -F tagger= -F 
        parser= http://lindat.mff.cuni.cz/services/udpipe/api/process """
        try:
            send_order = subprocess.check_output(bash_command.split(), shell=True)
        except subprocess.CalledProcessError as e:
            os.remove("file.txt")
            return Response("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output),
                            status=status.HTTP_424_FAILED_DEPENDENCY)

        os.remove("file.txt")
        conll = json.loads(send_order)['result']
        conll_example = [ud_parse for sent_id, ud_parse in load_conllu(conll)][0]
        ppatt = PredPatt(conll_example)
        return Response({'conll_text': conll, 'output_text': ppatt.pprint()}, status=status.HTTP_200_OK)
    else:
        return Response('text: None, BAD REQUEST!', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def perdt_output_view(request):
    if 'input_text' in request.data:
        text = request.data['input_text']

        stanza.download('fa')  # This downloads the English models for the neural pipeline
        nlp = stanza.Pipeline('fa')  # This sets up a default neural pipeline in English
        doc = nlp(text)
        doc.sentences[0].print_dependencies()
        for sentence in doc.sentences:
            res = "# text = " + text.strip()
            res = res.strip() + '\n'
            for word in sentence.words:
                res = res + str(word.id) + "\t" + str(word.text) + "\t" + str(word.lemma) + "\t" + \
                      str(word.pos) + "\t" + str(word.xpos) + "\t" + str(word.feats) + "\t" + \
                      str(word.head) + "\t" + str(word.deprel) + "\t" + str(word.start_char) + "\t" + \
                      str(word.end_char)
                res = res + '\n'

        conll_example = res
        conll_example = [ud_parse for sent_id, ud_parse in load_conllu(conll_example)][0]
        ppatt = PredPatt(conll_example)
        return Response({'conll_text': res, 'output_text': ppatt.pprint()}, status=status.HTTP_200_OK)
    else:
        return Response('text: None, BAD REQUEST!', status=status.HTTP_400_BAD_REQUEST)
