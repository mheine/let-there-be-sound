import socket
import threading
import traceback
import random
from urllib import parse
from os import listdir
from os.path import isfile, join, splitext
from slackclient import SlackClient

HOST = "0.0.0.0"
PORT = 80
AUDIO_FOLDER = "audio"
CHANNEL_NAME="@per.hellstrom"

token_file = "slack_api_token"

if not isfile(token_file):
    print("File \"slack_api_token\" doesn't exist!")
    print("Copy \"slack_api_token.example\", rename, then place your token in the file")
    exit(1)
else:
    with open(token_file) as sf:
        SLACK_API_TOKEN = sf.readline().strip()

if not SLACK_API_TOKEN:
    print("No SLACK_API_TOKEN available!")
    exit(1)

sc = SlackClient(SLACK_API_TOKEN)

clients = []
sounds = [[splitext(f)[0], f] for f in listdir(AUDIO_FOLDER) if isfile(join(AUDIO_FOLDER, f)) and f.endswith(".mp3")]

jokes = []
with open("jokes", "r") as jf:
    for line in jf:
        jokes.append(line.strip())

T = None
print("Available sounds:")
for sound in sounds:
    print(" - %s" % sound[0])

class ThreadedServer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))

    def listen(self):
        self.sock.listen(5)
        while True:
            try:
                client, address = self.sock.accept()
                client_thread = threading.Thread(target = self.listenToClient, args = (client,address), kwargs={})
                client_thread.start()
            except KeyboardInterrupt:
                self.broadcast(None, "EOF", "Server")
                exit()
            except Exception as e:
                print(e)
                traceback.print_exc()
                exit()

    def get_command(self, value):
        for command in sounds:
            if command[0] == value:
                return command[1]
        return None

    def get_joke(self):
        if jokes:
            i = random.randint(0, len(jokes) - 1)
            return jokes[i]
        else:
            return "No jokes available"

    def broadcast(self, source, message, username):
        print("Broadcasting: %s (Requested by %s)" % (message, username))
        for client in clients:
            if client == source:
                continue
            client.send(str.encode(message))

    def listenToClient(self, client, address):
        addr = address[0]
        size = 1024
        while True:
            try:
                recv = client.recv(size)
                recvtext = recv.decode('utf-8')
                data = recvtext.split("\r\n")
                if data[0] == "":
                    return
                path = data[0].split()[1]
                body = data[-1]
                if path == "/slack":
                    try:
                        parameters = body.split("&")
                        params = {}
                        for param in parameters:
                            key, value = param.split("=")
                            params[key] = value
                        if "text" in params:
                            value = params["text"]
                            username = params["user_name"]
                            if self.get_command(value):
                                sc.api_call(
                                    "chat.postMessage",
                                    link_names=1,
                                    channel=CHANNEL_NAME,
                                    text="Playing sound: %s (Requested by @%s)" % (value, username)
                                )
                                client.send(str.encode("Playing your requested sound: %s" % (value)))
                                self.broadcast(client, self.get_command(value), username)
                                client.close()
                                return
                            elif value == "help":
                                print("Sending help info to: %s" % addr)
                                message = "Help for Soundboard:\r\n"
                                message += "Usage: `/soundboard [command or phrase]`\r\n"
                                message += "Available commands:\r\n"
                                message += "`joke`\r\n"
                                for command in sounds:
                                    message += "`%s`\r\n" % command[0]
                                client.send(str.encode(message))
                                client.close()
                                return
                            elif value == "joke":
                                phrase = self.get_joke()
                                sc.api_call(
                                    "chat.postMessage",
                                    link_names=1,
                                    channel=CHANNEL_NAME,
                                    text="Joke requested by @%s" % username
                                )
                                client.send(str.encode("Joke incoming!"))
                                self.broadcast(client, phrase, username)
                                client.close()
                                return
                            else:
                                phrase = parse.unquote_plus(value)
                                sc.api_call(
                                    "chat.postMessage",
                                    link_names=1,
                                    channel=CHANNEL_NAME,
                                    text="Polly says: %s (Requested by @%s)" % (phrase, username)
                                )
                                client.send(str.encode("Polly is saying your requested phrase: %s" % (phrase)))
                                self.broadcast(client, phrase, username)
                                client.close()
                                return
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
                        client.close()
                        return False
                elif path == "/client":
                    if body == "EOF":
                        client.close()
                        clients.remove(client)
                        print("Client disconnected: %s (%s connected)" % (addr, len(clients)))
                        return
                    else:
                        client.send(str.encode("Connected to soundboard"))
                        clients.append(client)
                        print("New client: %s (%s connected)" % (addr, len(clients)))
                else:
                    print("Invalid path for : %s (%s)" % (addr, path))
                    client.close()
                    return
            except Exception as e:
                print(e)
                traceback.print_exc()
                client.close()
                clients.remove(client)
                return

if __name__ == "__main__":
    T = ThreadedServer()
    T.listen()