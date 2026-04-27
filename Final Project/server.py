import socket
import threading

# --- Configuration ---
HOST = '0.0.0.0'   # Listen on all network interfaces
PORT = 5555         # Any port above 1024 works

# These lists track everyone connected
clients = []
usernames = []

# --- Broadcast: send a message to ALL connected clients ---
def broadcast(message):
    for client in clients:
        client.send(message)

# --- Handle one client in its own thread ---
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)   # Wait for a message (up to 1024 bytes)
            broadcast(message)            # Forward it to everyone
        except:
            # Client disconnected
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            usernames.remove(username)
            broadcast(f'{username} has left the chat.'.encode('utf-8'))
            break

# --- Main server loop ---
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))   # Bind to address and port
    server.listen()             # Start listening for connections
    print(f'Server running on port {PORT}...')

    while True:
        client, address = server.accept()         # Wait for a new connection
        print(f'Connected: {address}')

        client.send('USERNAME'.encode('utf-8'))   # Ask for their username
        username = client.recv(1024).decode('utf-8')
        usernames.append(username)
        clients.append(client)

        broadcast(f'{username} joined the chat!'.encode('utf-8'))
        client.send('Connected to the server!'.encode('utf-8'))

        # Each client gets its own thread so they don't block each other
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

start_server()