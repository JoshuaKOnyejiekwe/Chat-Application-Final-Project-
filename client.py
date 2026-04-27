import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime

# --- Configuration ---
HOST = '127.0.0.1'  # Change to server's IP for cross-machine testing
PORT = 5555

# --- Color Palette ---
BG_DARK      = '#1e1e2e'
BG_PANEL     = '#2a2a3d'
BG_INPUT     = '#313145'
ACCENT       = '#7c6af7'
ACCENT_HOVER = '#9b8cf9'
TEXT_MAIN    = '#cdd6f4'
TEXT_DIM     = '#6c7086'
TEXT_SERVER  = '#f38ba8'  # Server/system messages in soft red
TEXT_SELF    = '#a6e3a1'  # Your own messages in green
BORDER       = '#45475a'

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title('ChatNet')
        self.root.configure(bg=BG_DARK)
        self.root.minsize(500, 600)
        self.root.geometry('680x700')

        self.username = None
        self.client = None
        self.connected = False

        self.build_ui()
        self.prompt_username()

    # -------------------------------------------------------
    # UI CONSTRUCTION
    # -------------------------------------------------------
    def build_ui(self):
        # --- Top bar ---
        top_bar = tk.Frame(self.root, bg=BG_PANEL, pady=12)
        top_bar.pack(fill='x', side='top')

        tk.Label(
            top_bar, text='💬  ChatNet',
            bg=BG_PANEL, fg=TEXT_MAIN,
            font=('Helvetica', 16, 'bold')
        ).pack(side='left', padx=16)

        self.status_label = tk.Label(
            top_bar, text='● Disconnected',
            bg=BG_PANEL, fg=TEXT_DIM,
            font=('Helvetica', 10)
        )
        self.status_label.pack(side='right', padx=16)

        # --- Message display area ---
        self.chat_area = scrolledtext.ScrolledText(
            self.root,
            state='disabled',
            bg=BG_DARK,
            fg=TEXT_MAIN,
            font=('Helvetica', 11),
            relief='flat',
            bd=0,
            padx=12,
            pady=8,
            wrap='word',
            insertbackground=TEXT_MAIN
        )
        self.chat_area.pack(fill='both', expand=True, padx=10, pady=(8, 4))

        # Tag styles for different message types
        self.chat_area.tag_config('server', foreground=TEXT_SERVER, font=('Helvetica', 10, 'italic'))
        self.chat_area.tag_config('self',   foreground=TEXT_SELF,   font=('Helvetica', 11, 'bold'))
        self.chat_area.tag_config('other',  foreground=TEXT_MAIN)
        self.chat_area.tag_config('time',   foreground=TEXT_DIM,    font=('Helvetica', 9))

        # --- Input area ---
        input_frame = tk.Frame(self.root, bg=BG_PANEL, pady=10)
        input_frame.pack(fill='x', side='bottom', padx=10, pady=(4, 10))

        self.msg_entry = tk.Entry(
            input_frame,
            bg=BG_INPUT,
            fg=TEXT_MAIN,
            font=('Helvetica', 12),
            relief='flat',
            insertbackground=TEXT_MAIN,
            bd=8
        )
        self.msg_entry.pack(side='left', fill='x', expand=True, padx=(8, 6), ipady=6)
        self.msg_entry.bind('<Return>', self.send_message)
        self.msg_entry.bind('<KeyPress>', self.on_key_press)

        self.send_btn = tk.Button(
            input_frame,
            text='Send',
            bg=ACCENT,
            fg='white',
            font=('Helvetica', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            padx=18,
            pady=6,
            command=self.send_message,
            activebackground=ACCENT_HOVER,
            activeforeground='white'
        )
        self.send_btn.pack(side='right', padx=(0, 8))

    # -------------------------------------------------------
    # CONNECTION
    # -------------------------------------------------------
    def prompt_username(self):
        name = simpledialog.askstring(
            'Welcome to ChatNet',
            'Enter your username (max 20 characters):',
            parent=self.root
        )
        if not name or not name.strip():
            self.root.destroy()
            return

        self.username = name.strip()[:20]
        self.root.title(f'ChatNet — {self.username}')
        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
            self.connected = True
            self.status_label.config(text=f'● Connected as {self.username}', fg=TEXT_SELF)

            thread = threading.Thread(target=self.receive_messages, daemon=True)
            thread.start()

        except Exception as e:
            messagebox.showerror('Connection Failed', f'Could not connect to server:\n{e}')
            self.root.destroy()

    # -------------------------------------------------------
    # NETWORKING
    # -------------------------------------------------------
    def receive_messages(self):
        while self.connected:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == 'USERNAME':
                    self.client.send(self.username.encode('utf-8'))
                else:
                    self.display_message(message)
            except:
                if self.connected:
                    self.display_message('[Server] Connection lost.', tag='server')
                self.connected = False
                self.status_label.config(text='● Disconnected', fg=TEXT_DIM)
                break

    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if not msg or not self.connected:
            return

        full_msg = f'{self.username}: {msg}'
        try:
            self.client.send(full_msg.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)
        except:
            self.display_message('[Server] Failed to send message.', tag='server')

    # -------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------
    def display_message(self, message, tag=None):
        self.chat_area.config(state='normal')

        timestamp = datetime.now().strftime('%H:%M')
        self.chat_area.insert(tk.END, f'[{timestamp}] ', 'time')

        # Auto-detect tag if not provided
        if tag is None:
            if message.startswith('[Server]'):
                tag = 'server'
            elif message.startswith(f'{self.username}:'):
                tag = 'self'
            else:
                tag = 'other'

        self.chat_area.insert(tk.END, message + '\n', tag)
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)  # Auto-scroll to bottom

    def on_key_press(self, event=None):
        # Could be extended later for "is typing..." feature
        pass

    # -------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------
    def on_close(self):
        self.connected = False
        try:
            self.client.close()
        except:
            pass
        self.root.destroy()


# --- Launch ---
if __name__ == '__main__':
    root = tk.Tk()
    app = ChatClient(root)
    root.protocol('WM_DELETE_WINDOW', app.on_close)
    root.mainloop()
