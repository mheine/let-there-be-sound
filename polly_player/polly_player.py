import boto3

client = boto3.client('polly', 'eu-central-1')

response = client.synthesize_speech(
    OutputFormat='mp3',
    Text='Hello World',
    VoiceId='Carmen'
)

if "AudioStream" in response:
    with closing(response["AudioStream"]) as stream:
        data = stream.read()
        fo = open("pollytest.mp3", "w+")
        fo.write( data )
        fo.close()