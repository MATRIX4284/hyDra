from flask import Flask, flash, request, redirect, url_for,Response
import shutil
import os
#from local import prediction
import hydra as ev
import sys
#import requests

#sys.path.insert(0, '/data/KAUSTAV/BOT-CLASSIFIER/botInference/SpoofVoiceDetector')

app = Flask(__name__)

@app.route('/hello')
def hello_world():
    print('Hello')
    return 'Hello, hyDra!'


@app.route('/diarization',methods=['GET', 'POST'])
def getDiar():
    print('diarizer')
    val=0
    root_dir='/data/hyDra'
    
    
    audio_dir=root_dir +'/' + 'audio_input'
    
    output_dir=root_dir +'/' + 'diarized_output'
    
    wav_dir=audio_dir +'/' + 'wav'
    
    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
        
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    if os.path.exists('./temp.zip'):
        os.remove('./temp.zip')
    
    print('Clean up complete')
    
    os.mkdir(audio_dir)
    
    os.mkdir(wav_dir)
    
    os.mkdir(output_dir)
    
    print('Directory Preparation Complete')
    
    save_path = os.path.join(wav_dir,"temp.wav")
    
    request.files['file'].save(save_path)
    
    print('input file saved')
    
    ev.diarizer('temp.wav',audio_dir)
    
    print('diarization complete')
    
    output_path = os.path.join(output_dir,"temp.zip")
   
    shutil.make_archive("temp","zip",root_dir=root_dir,base_dir=output_dir)
    
    print('Zip complete.')
    
    def generate():
        with open('./temp.zip', "rb") as fwav:
            data = fwav.read(8192)
            while data:
                yield data
                #print('sending file')
                #print('..')
                data = fwav.read(8192)
                
    print('diarized zip file sent')
    
    #return val
    #return Response(generate(), mimetype="audio/x-wav")
    return Response(generate(), mimetype="application/zip")
