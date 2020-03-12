import socket
import select
import signal
import sys
import traceback
from os import listdir, chdir
from os.path import isfile, join, abspath, dirname
from playsound import playsound
from time import sleep
import polly_player

import contextlib
with contextlib.redirect_stdout(None):
    # Just to get rid of pygames init print
    from pygame import mixer
    mixer.init()

SCRIPT_PATH = dirname(abspath(__file__))
chdir(SCRIPT_PATH)

HOST = "3.121.155.173"
PORT = 80
AUDIO_FOLDER = "audio"

sound_files = [f for f in listdir(AUDIO_FOLDER) if isfile(join(AUDIO_FOLDER, f)) and (f.endswith(".mp3") or f.endswith(".wav"))]

try:
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))
except:
    print("Failed to connect to %s on port %s!" % (HOST, PORT))
    exit()

def signal_handler(sig, frame):
    print("Exiting!")
    message = "GET /client HTTP/1.1\r\n\r\nEOF"
    conn.send(str.encode(message))
    conn.close()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

message = "GET /client HTTP/1.1\r\n\r\n"
conn.send(str.encode(message))

while True:
    try:
        ready_to_read, ready_to_write, in_error = \
            select.select([conn,], [conn,], [], 5)
    except select.error:
        conn.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
        conn.close()
        print('connection error')
        break
    except Exception as e:
        print(e)
        break
    try:
        if len(ready_to_read) > 0:
            recv = conn.recv(2048)
            data = recv.decode("utf-8")
            #rawdata = recv.decode("utf-8").split("\r\n")
            #print(rawdata)
            #data = rawdata[-2]
            if data == "":
                continue
            elif data == "EOF":
                print("EOF received, exiting!")
                break
            elif data in sound_files:
                print("Playing sound: %s" % data)
                mixer.music.load(join(AUDIO_FOLDER, data))
                mixer.music.play()
                while mixer.get_busy():
                    sleep(0.1)
            else:
                print("Polly says: %s" % data)
                polly_player.polly_say(data)
    except Exception:
        traceback.print_exc()
        message = "GET /client HTTP/1.1\r\n\r\nEOF"
        conn.send(str.encode(message))
        conn.close()
        break
