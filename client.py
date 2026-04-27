import socket
import threading

HOST = '127.0.0.1'  # Change this to the server's IP when testing across machines
PORT = 5555

username = input('Choose a username: ')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# --- Receive messages from the server (runs in background) ---
def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'USERNAME':
                client.send(username.encode('utf-8'))  # Server is asking for our name
            else:
                print(message)   # Print incoming messages
        except:
            print('Disconnected from server.')
            client.close()
            break

# --- Send messages to the server ---
def send():
    while True:
        message = f'{username}: {input("")}'
        client.send(message.encode('utf-8'))

# Run both receive and send simultaneously using threads
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()