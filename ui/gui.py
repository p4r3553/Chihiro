import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, PhotoImage
import io
import contextlib

from binary_loader import load_binary
from disassembler import disassemble
from string_extractor import extract_ascii_strings
from symbol_extractor import extract_symbols
from binary_info import print_binary_info
from graph.cfg_builder import build_cfg
from graph.cfg_visualizer import visualize_cfg
from ui.gdb_guy import GDBConsole

# ---------------- Contexte global ----------------
current_elf = None
current_file = None
current_path = None
current_code = None
current_addr = None

# ---------------- Thème sombre ----------------
BG_COLOR = "#1e1e1e"
FG_COLOR = "#c8f2c8"
BTN_COLOR = "#333"
HIGHLIGHT_COLOR = "#444"

# ---------------- Fonctions UI ----------------
def open_binary():
    global current_elf, current_file, current_path, current_code, current_addr

    filepath = filedialog.askopenfilename(filetypes=[("ELF files", "*.elf"), ("All files", "*.*")])
    if not filepath:
        return

    try:
        if current_file:
            current_file.close()

        elf, f = load_binary(filepath)
        text_section = elf.get_section_by_name('.text')
        code = text_section.data() if text_section else None
        addr = text_section['sh_addr'] if text_section else None

        current_elf, current_file = elf, f
        current_path, current_code, current_addr = filepath, code, addr

        info_box.delete("1.0", tk.END)
        info_box.insert(tk.END, f"[+] Loaded binary: {filepath}\n\n")

        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf):
                print_binary_info(elf)
            info_box.insert(tk.END, buf.getvalue())

    except Exception as e:
        messagebox.showerror("Error", f"Could not load binary:\n{e}")

def show_symbols():
    if not current_elf:
        return messagebox.showwarning("Warning", "No binary loaded.")
    
    info_box.delete("1.0", tk.END)
    info_box.insert(tk.END, "[+] Symbol Table:\n\n")

    symbols = extract_symbols(current_elf)
    for sym in symbols:
        info_box.insert(tk.END, f"  0x{sym['addr']:08x}  {sym['type']:<7}  {sym['name']}\n")

def show_disasm():
    if not current_code or not current_addr:
        return messagebox.showwarning("Warning", "No .text section loaded.")

    info_box.delete("1.0", tk.END)
    info_box.insert(tk.END, "[+] Disassembly of .text:\n\n")

    for instr in disassemble(current_code, current_addr):
        info_box.insert(tk.END, f"0x{instr['address']:x}: {instr['mnemonic']} {instr['op_str']}\n")

def show_strings():
    if not current_code:
        return messagebox.showwarning("Warning", "No .text section loaded.")

    info_box.delete("1.0", tk.END)
    info_box.insert(tk.END, "[+] ASCII Strings in .text:\n\n")

    for s in extract_ascii_strings(current_code):
        try:
            decoded = s.decode('utf-8', errors='ignore')
            info_box.insert(tk.END, decoded + '\n')
        except Exception:
            continue

def show_cfg():
    if not current_code or not current_addr:
        return messagebox.showwarning("Warning", "No .text section loaded.")

    instrs = disassemble(current_code, current_addr)
    cfg = build_cfg(instrs)
    visualize_cfg(cfg)

def launch_debugger():
    if not current_path:
        return messagebox.showwarning("Warning", "No binary loaded.")
    
    dbg_window = tk.Toplevel(root)
    dbg_window.title("GDB Debugger")

    gdb_ui = GDBConsole(dbg_window, current_path)
    gdb_ui.pack(fill="both", expand=True)

def on_quit():
    if current_file:
        current_file.close()
    root.destroy()

# ---------------- Interface Graphique ----------------
root = tk.Tk()
root.title("Chihiro - Reverse Engineering Toolkit")
root.configure(bg=BG_COLOR)

# Définir l'icône de la fenêtre (dans la barre de titre/dock)
try:
    icon = PhotoImage(file="ui/picture.png")
    root.iconphoto(True, icon)
except Exception as e:
    print(f"[!] Failed to set window icon: {e}")

# Logo principal (visuel dans la fenêtre)
try:
    logo = PhotoImage(file="ui/picture.png")
    logo_label = tk.Label(root, image=logo, bg=BG_COLOR)
    logo_label.image = logo
    logo_label.pack(pady=(10, 0))
except Exception as e:
    print(f"[!] Logo missing or invalid: {e}")

# Boutons
btn_frame = tk.Frame(root, bg=BG_COLOR, padx=10, pady=10)
btn_frame.pack()

buttons = [
    ("📂 Open Binary", open_binary),
    ("📦 Show Symbols", show_symbols),
    ("📜 Disassembly", show_disasm),
    ("🔤 Extract Strings", show_strings),
    ("🧠 Visualize CFG", show_cfg),
    ("🐞 Debug Binary", launch_debugger),
]

for label, command in buttons:
    tk.Button(btn_frame, text=label, width=25, command=command,
              bg=BTN_COLOR, fg=FG_COLOR, activebackground=HIGHLIGHT_COLOR).pack(pady=2)

# Zone d'affichage
info_box = scrolledtext.ScrolledText(root, height=30, width=100, font=("Courier", 10),
                                     bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR,
                                     selectbackground=HIGHLIGHT_COLOR)
info_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.protocol("WM_DELETE_WINDOW", on_quit)
root.mainloop()
