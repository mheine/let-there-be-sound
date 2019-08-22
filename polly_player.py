import boto3
import os
import uuid
from playsound import playsound
from contextlib import closing, redirect_stdout
# Just to get rid of pygames init print
with redirect_stdout(None):
    from pygame import mixer
    mixer.init()

def polly_say(text):
    os.environ["AWS_PROFILE"] = "soundboard-polly"
    client = boto3.client('polly', 'eu-central-1')

    response = client.synthesize_speech(
        OutputFormat='mp3',
        Text=text,
        VoiceId='Brian'
    )

    if "AudioStream" in response:
        file_name="polly_audio_%s.mp3" % uuid.uuid4()
        pf = open(file_name, "wb")
        audiostream = response["AudioStream"]
        with closing(audiostream):
            data = audiostream.read()
            pf.write(data)
            pf.flush()
        pf.close()
        mixer.music.load(file_name)
        mixer.music.play()
        while mixer.get_busy():
            sleep(0.1)
        os.remove(file_name)
