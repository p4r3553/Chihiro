import tkinter as tk
from tkinter import scrolledtext
import pty
import os
import threading

class GDBConsole(tk.Frame):
    def __init__(self, master, binary_path):
        super().__init__(master)
        self.master = master
        self.binary_path = binary_path
        self.master.title("GDB Debugger")
        self.pack()
        self.scroll_enabled = True

        self.bg_color = "#1e1e1e"
        self.fg_color = "#c8f2c8"
        self.button_color = "#333"
        self.highlight_color = "#444444"

        self.configure(bg=self.bg_color)
        self.master.configure(bg=self.bg_color)

        self.text_area = scrolledtext.ScrolledText(
            self, height=30, width=100, font=("Courier", 10),
            bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color,
            selectbackground=self.highlight_color
        )
        self.text_area.pack(padx=10, pady=(10, 2), fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self, font=("Courier", 10),
                              bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.entry.bind("<Return>", self.send_command)
        self.entry.pack(fill=tk.X, padx=10, pady=(0, 5))

        btns = tk.Frame(self, bg=self.bg_color)
        btns.pack(pady=5)

        def make_btn(text, cmd):
            if isinstance(cmd, str):
                return tk.Button(btns, text=text, command=lambda: self.run_cmd(cmd),
                                 bg=self.button_color, fg=self.fg_color, activebackground=self.highlight_color)
            else:
                return tk.Button(btns, text=text, command=cmd,
                                 bg=self.button_color, fg=self.fg_color, activebackground=self.highlight_color)

        make_btn(" Break main", "break main").pack(side=tk.LEFT, padx=2)
        make_btn(" Run", "run").pack(side=tk.LEFT, padx=2)
        make_btn(" Continue", "continue").pack(side=tk.LEFT, padx=2)
        make_btn(" Next", "next").pack(side=tk.LEFT, padx=2)
        make_btn("↪ Step", "step").pack(side=tk.LEFT, padx=2)
        make_btn(" Registers", "info registers").pack(side=tk.LEFT, padx=2)
        make_btn(" Breakpoints", "info breakpoints").pack(side=tk.LEFT, padx=2)
        make_btn(" Del BPs", "delete breakpoints").pack(side=tk.LEFT, padx=2)
        make_btn(" x/i $rip", "x/i $rip").pack(side=tk.LEFT, padx=2)
        make_btn(" Layout Src", "layout src").pack(side=tk.LEFT, padx=2)
        make_btn(" Clear", self.clear_output).pack(side=tk.LEFT, padx=2)

        self.scroll_btn = tk.Button(btns, text=" Auto-scroll ON", command=self.toggle_scroll,
                                    bg=self.button_color, fg=self.fg_color, activebackground=self.highlight_color)
        self.scroll_btn.pack(side=tk.LEFT, padx=2)

        # Search bar
        search_frame = tk.Frame(self, bg=self.bg_color)
        search_frame.pack(pady=5, padx=10, fill=tk.X)

        tk.Label(search_frame, text="🔍 Search:", fg=self.fg_color, bg=self.bg_color).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     bg=self.bg_color, fg=self.fg_color, insertbackground=self.fg_color)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Find", command=self.find_text,
                  bg=self.button_color, fg=self.fg_color).pack(side=tk.LEFT)

        # Start GDB
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp("gdb", ["gdb", binary_path])

        self.reader_thread = threading.Thread(target=self.read_from_gdb, daemon=True)
        self.reader_thread.start()

    def send_command(self, event=None):
        cmd = self.entry.get()
        self.entry.delete(0, tk.END)
        self.run_cmd(cmd)

    def run_cmd(self, cmd):
        os.write(self.fd, (cmd + "\n").encode())

    def read_from_gdb(self):
        while True:
            try:
                output = os.read(self.fd, 1024).decode(errors='ignore')
                self.text_area.insert(tk.END, output)
                if self.scroll_enabled:
                    self.text_area.see(tk.END)
            except OSError:
                break

    def toggle_scroll(self):
        self.scroll_enabled = not self.scroll_enabled
        state = "ON" if self.scroll_enabled else "OFF"
        self.scroll_btn.config(text=f" Auto-scroll {state}")

    def clear_output(self):
        self.text_area.delete("1.0", tk.END)

    def find_text(self):
        self.text_area.tag_remove('found', '1.0', tk.END)
        search = self.search_var.get()
        if search:
            idx = '1.0'
            while True:
                idx = self.text_area.search(search, idx, nocase=1, stopindex=tk.END)
                if not idx:
                    break
                lastidx = f"{idx}+{len(search)}c"
                self.text_area.tag_add('found', idx, lastidx)
                idx = lastidx
            self.text_area.tag_config('found', background='yellow', foreground='black')
