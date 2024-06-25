#!/usr/bin/env python
# coding: utf-8

# In[1]:


import torch
import os
from csv import DictWriter
import pandas as pd
#import ray
#ray.shutdown()
#import modin.pandas as pd
from pydub import AudioSegment
import shutil


# In[8]:


def audio_splitter(data_frame,speaker,datadir,name,audio_file):
    
    #print('LENGTH:')
    #print(len(data_frame['start']))
    
    
    for i in range(len(data_frame['start'])):
        
        spkr='spkr'+ str(speaker)
        
        #if speaker==1:
        #    spkr='spkr1'
        #else:
        #    spkr='spkr2'
        
        #print(i)
        t1 = data_frame['start'][i] * 1000 #Works in milliseconds
        #print(t1)
        t2 = data_frame['end'][i] * 1000
        #print(t2)
        
        
        newAudio = AudioSegment.from_wav(audio_file)
        newAudio = newAudio[t1:t2]  
        file_name = datadir + '/' + str(spkr) + '_stage' + '/' + name + '_' + str(spkr) + '_' + str(i) + '.wav'
        newAudio.export(file_name, format="wav") 
        
def audio_combiner(df,datadir,name,speaker):
    
    for i in range(len(df['start'])):
        
        
        spkr='spkr'+ str(speaker)
        
        
        #if speaker==1:
        #    spkr='spkr1'
        #else:
        #    spkr='spkr2'
        
        file1=datadir + '/' + str(spkr) + '_stage' + '/' + name + '_' + str(spkr) + '_' + str(i) + '.wav'
        file2=datadir + '/' + str(spkr) + '_stage' + '/' + name + '_' + str(spkr) + '_' + str(i+1) + '.wav'
        
        #print(file1)
        
        output_file=datadir + '/' + str(spkr) + '_final' + '/' + name + '_' + str(spkr)  + '.wav'
        
        root_dir='.'
        
        finaldir = root_dir +'/diarized_output'
        
        final_dest = finaldir + '/' + name + '_' + str(spkr)  + '.wav'
        
        
        sound1 = AudioSegment.from_file(file1, format="wav")
        
        if i+1 < len(df['start']):
            sound2 = AudioSegment.from_file(file2, format="wav")
            combined = sound1 + sound2
            file_handle = combined.export(file2, format="wav")
        
        
        
    #os.copyfile(file1,output_file)
    shutil.copyfile(file1, output_file)
    shutil.copyfile(file1, final_dest)
        
def diarizer(audio_file,datadir_root):
    
    print('Entered Diarizer Component')
    
    print('AUDIO FILE NAME:')
    print(audio_file)
    
    name=audio_file.split('.')[0]
    ext=audio_file.split('.')[1]
    
    fqp = datadir_root + '/wav/' 
    
    fqp_name = fqp + name
    
    audio_file = fqp + audio_file
    
    DEMO_FILE = {'uri': fqp, 'audio': audio_file}
    
    
    pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia')
    diarization = pipeline(DEMO_FILE)
    
    print('DIARIZATION LABELS:')
    print(len(diarization.labels()))
    
    for i in range(1,len(diarization.labels())+1):
        print(i)
    
    print(datadir_root)
    
    os.mkdir(datadir_root + '/' + 'diarized')
    
    datadir= datadir_root + '/' + 'diarized/' + name
    
    os.mkdir(datadir)
    
    root_dir='.'
    
    os.mkdir(datadir + '/csv')
    
    
    for label in range(1,len(diarization.labels())+1):
        print(label)
        os.mkdir(datadir + '/spkr' + str(label) +'_stage')
        os.mkdir(datadir + '/spkr' + str(label) +'_final')
    
    #os.mkdir(datadir + '/spkr1_stage')
    #os.mkdir(datadir + '/spkr2_stage')
    #os.mkdir(datadir +'/spkr1_final')
    #os.mkdir(datadir + '/spkr2_final')
    
    dia_file = open(datadir + '/csv' + '/' + name +'.csv', 'a+', newline='')
    dia_dict={}
    fieldnames = ['start', 'end' , 'label']
    
    # Add dictionary as wor in the csv
    dict_writer = DictWriter(dia_file, fieldnames=fieldnames)
    dict_writer.writeheader()
    
    for i,_,j in diarization.itertracks(yield_label=True):
        dict_writer = DictWriter(dia_file, fieldnames=fieldnames)
        dia_dict['start']=i.start
        dia_dict['end']=i.end
        dia_dict['label']=j
        print(dia_dict)
        # Add dictionary as wor in the csv
        dict_writer.writerow(dia_dict)
        
    dia_file.close()
    
    dia_df = pd.read_csv(datadir + '/csv' + '/' + name +'.csv')
    
    lab_dict={}
    x=1
    for label in diarization.labels():
        lab_dict[x]=label
        x=x+1
    
    for idx,label in lab_dict.items():
        print(idx)
        print(label)
        dia_df_idx = dia_df[dia_df['label']==label].sort_values('start').reset_index(drop=True)
        audio_splitter(dia_df_idx,idx,datadir,name,audio_file)
        audio_combiner(dia_df_idx,datadir,name,idx)
        del dia_df_idx
    
    
    #dia_df_A = dia_df[dia_df['label']=='A'].sort_values('start').reset_index(drop=True)
    #dia_df_B = dia_df[dia_df['label']=='B'].sort_values('start').reset_index(drop=True)
    
    #audio_splitter(dia_df_A,1,datadir,name,audio_file)
    #audio_splitter(dia_df_B,2,datadir,name,audio_file)
        
    #audio_combiner(dia_df_A,datadir,name,1)
    #audio_combiner(dia_df_B,datadir,name,2)
    
def diarize(root):
    
    wavdir = root + '/' + 'wav'

    file_lst=[x.split('.')[0] for x in os.listdir(wavdir)]
    
    diadir = root + '/' + 'diarized'

    dia_lst=os.listdir(diadir)
    
    dia_lst
    
    final_lst = list(set(file_lst) - set(dia_lst))
    
    wav_lst=[x + '.wav' for x in final_lst]
    
    print(wav_lst)

    [diarizer(i,root) for i in wav_lst]
