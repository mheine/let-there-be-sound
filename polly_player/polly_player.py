import boto3

client = boto3.client('polly', 'eu-central-1')

response = client.synthesize_speech(
    OutputFormat='mp3',
    Text='Hello World',
    VoiceId='Carmen'
)

print(response['AudioStream'].read()) 