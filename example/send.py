import requests

#url = "http://hydra.560938c6e46842a9a392.eastus.aksapp.io/diarization"
url = "http://0.0.0.0:9000/diarization"
fin = open('/Users/kmukher1/Desktop/OPTUM/DIARIZATION/DEMO_OUTPUT/ASTHMA/asthma_1_1.wav', 'rb')
files = {'file': fin}
r = requests.post(url, files=files)
with open('bandana_diarized_files.zip', 'wb') as f:
    f.write(r.content)
print(r)
