import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
import queue
import os
import pty

class GDBDebugger:
    def __init__(self, binary_path):
        self.binary_path = binary_path
        self.process = None
        self.master_fd = None
        self.q = queue.Queue()

        self.root = tk.Toplevel()
        self.root.title("🐞 Chihiro Debugger")

        self.output_box = scrolledtext.ScrolledText(self.root, height=25, width=100, font=("Courier", 10))
        self.output_box.pack(padx=10, pady=10)

        self.input_field = tk.Entry(self.root, font=("Courier", 10))
        self.input_field.pack(fill=tk.X, padx=10)
        self.input_field.bind("<Return>", self.send_command)

        self.start_gdb()

        self.reader_thread = threading.Thread(target=self.read_output, daemon=True)
        self.reader_thread.start()
        self.update_output()

    def start_gdb(self):
        try:
            self.master_fd, slave_fd = pty.openpty()
            self.process = subprocess.Popen(
                ["gdb", self.binary_path],
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                universal_newlines=True
            )
        except FileNotFoundError:
            messagebox.showerror("Error", "GDB is not installed or not found.")
            self.root.destroy()

    def read_output(self):
        while True:
            try:
                data = os.read(self.master_fd, 1024).decode(errors='ignore')
                self.q.put(data)
            except OSError:
                break

    def update_output(self):
        while not self.q.empty():
            data = self.q.get_nowait()
            self.output_box.insert(tk.END, data)
            self.output_box.see(tk.END)
        self.root.after(100, self.update_output)

    def send_command(self, event=None):
        cmd = self.input_field.get().strip()
        if cmd and self.master_fd:
            os.write(self.master_fd, (cmd + "\n").encode())
            self.input_field.delete(0, tk.END)
