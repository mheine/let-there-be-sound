import boto3
from contextlib import closing
import subprocess
import sys

text=str(sys.argv[1])

client = boto3.client('polly', 'eu-central-1')

response = client.synthesize_speech(
    OutputFormat='mp3',
    Text=text,
    VoiceId='Joanna'
)

file_name="polly_audio.mp3"
padded_file="polly_audio_padded.mp3"

if "AudioStream" in response:
    with closing(response["AudioStream"]) as stream:
        data = stream.read()
        fo = open(file_name, "w+")
        fo.write( data )
        fo.close()
    subprocess.call("sox " + file_name + " -r 44100 -c 2 " + padded_file + " pad 1.0 1.0", shell=True)
    subprocess.call("play " + padded_file, shell=True)
