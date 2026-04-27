import socket
import threading

# --- Configuration ---
HOST = '0.0.0.0'   # Listen on all network interfaces
PORT = 5555

# Use a dictionary to pair clients with usernames safely
clients = {}  # {client_socket: username}
lock = threading.Lock()  # Prevent race conditions when modifying clients dict

# --- Broadcast: send a message to ALL connected clients ---
def broadcast(message, sender=None):
    with lock:
        disconnected = []
        for client in clients:
            try:
                client.send(message)
            except:
                disconnected.append(client)
        # Clean up any clients that failed
        for client in disconnected:
            remove_client(client)

# --- Remove a client safely ---
def remove_client(client):
    if client in clients:
        username = clients[client]
        del clients[client]
        try:
            client.close()
        except:
            pass
        return username
    return None

# --- Handle one client in its own thread ---
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message)
        except:
            break

    # Client disconnected
    with lock:
        username = remove_client(client)
    if username:
        broadcast(f'[Server] {username} has left the chat.'.encode('utf-8'))
        print(f'{username} disconnected.')

# --- Main server loop ---
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "address in use" errors on restart
    server.bind((HOST, PORT))
    server.listen()
    print(f'[Server] Running on port {PORT}...')

    while True:
        try:
            client, address = server.accept()
            print(f'[Server] New connection from {address}')

            # Ask for username
            client.send('USERNAME'.encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()

            # Validate username
            if not username or len(username) > 20:
                client.send('[Server] Invalid username. Disconnecting.'.encode('utf-8'))
                client.close()
                continue

            with lock:
                clients[client] = username

            print(f'[Server] {username} joined.')
            broadcast(f'[Server] {username} joined the chat!'.encode('utf-8'))
            client.send('[Server] Welcome! You are now connected.\n'.encode('utf-8'))

            thread = threading.Thread(target=handle_client, args=(client,), daemon=True)
            thread.start()

        except KeyboardInterrupt:
            print('\n[Server] Shutting down...')
            broadcast('[Server] Server is shutting down. Goodbye!'.encode('utf-8'))
            break

start_server()
