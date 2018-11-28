import time
from polly_player import polly_say

jokes = []
with open("jokes", "r") as jf:
    for line in jf:
        jokes.append(line.strip())

for joke in jokes:
    polly_say(joke)
    time.sleep(2)