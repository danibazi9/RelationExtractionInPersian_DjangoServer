import os
import json

import stanza
import subprocess

from predpatt import PredPatt, load_conllu

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def result(request):
    if request.method == "POST":
        ud_type, text = request.POST.get("ud_type"), request.POST.get("input_text")

        if ud_type == 'seraji':
            with open('file.txt', 'w', encoding='utf-8') as f:
                f.write(text.replace('\r', '').strip())
                f.close()

            bash_command = """curl -F data=@file.txt -F model=persian -F tokenizer=normalized_spaces -F tagger= -F 
            parser= http://lindat.mff.cuni.cz/services/udpipe/api/process """
            try:
                send_order = subprocess.check_output(bash_command.split(), shell=True)
            except subprocess.CalledProcessError as e:
                os.remove("file.txt")
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

            os.remove("file.txt")
            conll = json.loads(send_order)['result']
            ppatt = PredPatt([ud_parse for sent_id, ud_parse in load_conllu(conll)][0])
            return render(request, 'service.html',
                          {'input_text': text, 'ud_type': ud_type, 'conll_text': conll, 'output_text': ppatt.pprint()})

        elif ud_type == "perdt":
            stanza.download('fa')  # This downloads the Persian models for the neural pipeline
            nlp = stanza.Pipeline('fa')  # This sets up a default neural pipeline in Persian
            doc = nlp(text)
            for sentence in doc.sentences:
                res = "# text = " + text.strip()
                res = res.strip() + '\n'
                for word in sentence.words:
                    res = res + str(word.id) + "\t" + str(word.text) + "\t" + str(word.lemma) + "\t" + \
                          str(word.pos) + "\t" + str(word.xpos) + "\t" + str(word.feats) + "\t" + \
                          str(word.head) + "\t" + str(word.deprel) + "\t" + str(word.start_char) + "\t" +\
                          str(word.end_char)
                    res = res + '\n'

            ppatt = PredPatt([ud_parse for sent_id, ud_parse in load_conllu(res)][0])
            return render(request, 'service.html',
                          {'input_text': text, 'ud_type': ud_type, 'conll_text': res, 'output_text': ppatt.pprint()})
    else:
        return render(request, 'service.html', {'input_text': '', 'ud_type': 'seraji', 'output_text': ''})
