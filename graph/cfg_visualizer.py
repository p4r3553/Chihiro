# ------------------------
# CFG Viewer - Chihiro
# ------------------------

import tkinter as tk
from tkinter import Canvas, Entry, Button, messagebox
from textwrap import wrap
import networkx as nx

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

INSTR_COLORS = {
    "jmp": "#d0f0ff",
    "call": "#e0ffe0",
    "ret": "#ffe0e0",
    "nop": "#f5f5f5",
    "default": "#f0f8ff"
}

class CFGViewer:
    def __init__(self, cfg, title="CFG Viewer"):
        self.cfg = cfg
        self.title = title
        self.zoom = 1.0
        self.node_items = {}
        self.edge_items = []

        self.root = tk.Toplevel()
        self.root.title(self.title)

        self.canvas = Canvas(self.root, bg="#fbfbfb", width=1400, height=800)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.search_box = Entry(self.root)
        self.search_box.pack(side=tk.LEFT, padx=5)

        Button(self.root, text="", command=self.search_node).pack(side=tk.LEFT)
        Button(self.root, text=" Export PNG", command=self.export_png).pack(side=tk.LEFT, padx=5)

        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom_linux)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom_linux)  # Linux scroll down

        self._draw_graph()
        self._draw_legend()

    def run(self):
        self.root.mainloop()

    def _draw_graph(self):
        try:
            # Horizontal layout using Graphviz with increased spacing
            pos = nx.nx_agraph.graphviz_layout(self.cfg, prog="dot", args='-Grankdir=LR -Gnodesep=1 -Granksep=1.2')
        except Exception:
            pos = nx.spring_layout(self.cfg, seed=42)

        if not pos:
            return

        y_center = sum(y for _, y in pos.values()) / len(pos)
        pos_scaled = {
            node: (x * 2.8 + 100, (y - y_center) * 2.2 + 400)
            for node, (x, y) in pos.items()
        }

        for node in self.cfg.nodes():
            if node not in pos_scaled:
                continue

            x, y = pos_scaled[node]
            instrs = self.cfg.nodes[node].get("instructions", [])
            if not instrs:
                continue

            lines = [f"{i['mnemonic']} {i['op_str']}".strip() for i in instrs]
            label_text = f"0x{node:x}\n" + "\n".join(wrap("  ".join(lines), 40))
            mnemonic = instrs[-1]["mnemonic"]
            color = next((c for k, c in INSTR_COLORS.items() if mnemonic.startswith(k)), INSTR_COLORS["default"])

            width = max(140, 8 * max(len(line) for line in label_text.splitlines()) + 30)
            height = 14 * len(label_text.splitlines()) + 26

            # Shadow
            self.canvas.create_oval(
                x - width//2 + 2, y - height//2 + 2, x + width//2 + 2, y + height//2 + 2,
                fill="#d0d0d0", outline="", tags=f"shadow_{node}"
            )

            # Main oval
            oval = self.canvas.create_oval(
                x - width//2, y - height//2, x + width//2, y + height//2,
                fill=color, outline="#2c3e50", width=2, tags=f"node_{node}"
            )

            # Text
            text = self.canvas.create_text(
                x, y, text=label_text,
                font=("Courier New", 8), justify="center", tags=f"label_{node}"
            )

            self.node_items[node] = {"oval": oval, "text": text, "coords": (x, y)}

            self.canvas.tag_bind(f"node_{node}", "<Enter>", lambda e, n=node: self._highlight(n))
            self.canvas.tag_bind(f"node_{node}", "<Leave>", lambda e, n=node: self._unhighlight(n))

        # Draw edges
        for src, dst in self.cfg.edges():
            if src not in pos_scaled or dst not in pos_scaled:
                continue
            x1, y1 = pos_scaled[src]
            x2, y2 = pos_scaled[dst]
            line = self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, width=1.2, fill="#777")
            self.edge_items.append((src, dst, line))

        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=bbox)
            self.canvas.xview_moveto(0.3)

    def _draw_legend(self):
        x, y = 20, 20
        self.canvas.create_text(x, y - 10, text="Legend:", anchor="nw", font=("Arial", 9, "bold"))
        for key, color in INSTR_COLORS.items():
            if key == "default":
                continue
            self.canvas.create_rectangle(x, y, x + 20, y + 20, fill=color, outline="#333")
            self.canvas.create_text(x + 30, y + 10, anchor="w", text=key, font=("Arial", 9))
            y += 25

    def search_node(self):
        query = self.search_box.get().strip().lower()
        for node, items in self.node_items.items():
            label = self.canvas.itemcget(items["text"], "text").lower()
            if query in label:
                x, y = items["coords"]
                bbox = self.canvas.bbox("all")
                if bbox:
                    self.canvas.xview_moveto((x - 600) / bbox[2])
                    self.canvas.yview_moveto((y - 400) / bbox[3])
                self.canvas.itemconfig(items["oval"], outline="#ff0000", width=3)
            else:
                self.canvas.itemconfig(items["oval"], outline="#2c3e50", width=2)

    def _highlight(self, node):
        self.canvas.itemconfig(self.node_items[node]["oval"], outline="#ff8800", width=3)

    def _unhighlight(self, node):
        self.canvas.itemconfig(self.node_items[node]["oval"], outline="#2c3e50", width=2)

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def do_pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self._zoom_canvas(event.x, event.y, scale)

    def on_zoom_linux(self, event):
        scale = 1.1 if event.num == 4 else 0.9
        self._zoom_canvas(event.x, event.y, scale)

    def _zoom_canvas(self, x, y, scale):
        self.zoom *= scale
        self.canvas.scale("all", x, y, scale, scale)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def export_png(self):
        if not ImageGrab:
            messagebox.showerror("Error", "Pillow is required for image export.")
            return
        try:
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x1, y1))
            img.save("cfg_export.png")
            messagebox.showinfo("Success", "Graph exported as cfg_export.png")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


def visualize_cfg(cfg, title=" CFG - Chihiro"):
    viewer = CFGViewer(cfg, title)
    viewer.run()
