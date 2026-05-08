import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from main_engine import MainEngine


# ── Color palette ─────────────────────────────────────────────────────────────
BG       = "#0d1117"
PANEL    = "#161b22"
BORDER   = "#30363d"
ACCENT   = "#58a6ff"
GREEN    = "#3fb950"
YELLOW   = "#d29922"
RED      = "#f85149"
TEXT     = "#e6edf3"
MUTED    = "#8b949e"
HEADER   = "#1f2937"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Courier New", 10)
FONT_BIG  = ("Courier New", 14, "bold")
FONT_MED  = ("Courier New", 11, "bold")


class RouterSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Routing Simulator")
        self.root.configure(bg=BG)
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.engine = MainEngine(None)
        self.routers = {}
        self.config_path = None

        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        title_bar = tk.Frame(self.root, bg=PANEL, pady=10)
        title_bar.pack(fill="x", side="top")

        tk.Label(title_bar, text="◈  DYNAMIC ROUTING SIMULATOR",
                 font=FONT_BIG, fg=ACCENT, bg=PANEL).pack(side="left", padx=20)
        tk.Label(title_bar, text="Distance Vector Protocol",
                 font=FONT_UI, fg=MUTED, bg=PANEL).pack(side="left", padx=5)

        self.status_label = tk.Label(title_bar, text="● NO CONFIG LOADED",
                                     font=FONT_UI, fg=RED, bg=PANEL)
        self.status_label.pack(side="right", padx=20)

        # Main body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        # Left panel: controls
        left = tk.Frame(body, bg=PANEL, width=280, bd=1, relief="flat",
                        highlightthickness=1, highlightbackground=BORDER)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Right panel: routing tables + log
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True)
        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        def section(text):
            tk.Label(parent, text=text, font=("Courier New", 9, "bold"),
                     fg=MUTED, bg=PANEL, anchor="w", pady=4).pack(fill="x", padx=14)

        tk.Label(parent, text="CONTROLS", font=FONT_MED,
                 fg=ACCENT, bg=PANEL, anchor="w").pack(fill="x", padx=14, pady=(14, 4))

        # Load config
        section("── CONFIG FILE")
        self.config_var = tk.StringVar(value="No file selected")
        tk.Label(parent, textvariable=self.config_var, font=("Courier New", 8),
                 fg=YELLOW, bg=PANEL, anchor="w", wraplength=240).pack(fill="x", padx=14)

        btn_frame = tk.Frame(parent, bg=PANEL)
        btn_frame.pack(fill="x", padx=14, pady=6)
        self._btn(btn_frame, "Browse Config", self._browse_config).pack(side="left")
        self._btn(btn_frame, "Run", self._run_simulation, color=GREEN).pack(side="left", padx=6)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # Router selector
        section("── VIEW ROUTER TABLE")
        self.router_var = tk.StringVar()
        self.router_combo = ttk.Combobox(parent, textvariable=self.router_var,
                                         state="readonly", font=FONT_UI)
        self.router_combo.pack(fill="x", padx=14, pady=4)
        self.router_combo.bind("<<ComboboxSelected>>", lambda e: self._show_table())
        self._btn(parent, "Show All Tables", self._show_all_tables).pack(padx=14, fill="x", pady=2)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=14, pady=8)

        # Change cost
        section("── CHANGE_COST SIMULATOR")

        tk.Label(parent, text="Router:", font=FONT_UI, fg=TEXT, bg=PANEL, anchor="w").pack(fill="x", padx=14)
        self.cc_router_var = tk.StringVar()
        self.cc_router_combo = ttk.Combobox(parent, textvariable=self.cc_router_var,
                                             state="readonly", font=FONT_UI)
        self.cc_router_combo.pack(fill="x", padx=14, pady=2)

        tk.Label(parent, text="Neighbor Index (1-based):", font=FONT_UI, fg=TEXT, bg=PANEL, anchor="w").pack(fill="x", padx=14, pady=(6,0))
        self.cc_idx_var = tk.StringVar(value="1")
        tk.Entry(parent, textvariable=self.cc_idx_var, font=FONT_UI,
                 bg=HEADER, fg=TEXT, insertbackground=TEXT, bd=0,
                 highlightthickness=1, highlightbackground=BORDER).pack(fill="x", padx=14, pady=2)

        tk.Label(parent, text="New Cost (ms):", font=FONT_UI, fg=TEXT, bg=PANEL, anchor="w").pack(fill="x", padx=14, pady=(6,0))
        self.cc_cost_var = tk.StringVar(value="500")
        tk.Entry(parent, textvariable=self.cc_cost_var, font=FONT_UI,
                 bg=HEADER, fg=TEXT, insertbackground=TEXT, bd=0,
                 highlightthickness=1, highlightbackground=BORDER).pack(fill="x", padx=14, pady=2)

        self._btn(parent, "Apply change_cost()", self._apply_change_cost, color=YELLOW).pack(fill="x", padx=14, pady=8)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=14, pady=4)

        self._btn(parent, "Reset", self._reset, color=RED).pack(fill="x", padx=14, pady=4)

    def _build_right_panel(self, parent):
        # Top: routing table display
        table_frame = tk.Frame(parent, bg=PANEL, bd=1, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER)
        table_frame.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(table_frame, text="ROUTING TABLES", font=FONT_MED,
                 fg=ACCENT, bg=PANEL, anchor="w").pack(fill="x", padx=12, pady=(10, 4))

        # Treeview for tables
        tree_wrap = tk.Frame(table_frame, bg=PANEL)
        tree_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Routing.Treeview",
                         background=BG, foreground=TEXT,
                         fieldbackground=BG, rowheight=24,
                         font=FONT_MONO, borderwidth=0)
        style.configure("Routing.Treeview.Heading",
                         background=HEADER, foreground=ACCENT,
                         font=("Courier New", 10, "bold"), relief="flat")
        style.map("Routing.Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", BG)])

        cols = ("Router", "Destination", "Next Hop", "Cost (ms)")
        self.tree = ttk.Treeview(tree_wrap, columns=cols, show="headings",
                                  style="Routing.Treeview")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        vsb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Tags for coloring
        self.tree.tag_configure("direct",      background="#0d2818", foreground=GREEN)
        self.tree.tag_configure("unreachable", background="#1a0d0d", foreground=RED)
        self.tree.tag_configure("self",        background="#0d1a2a", foreground=MUTED)
        self.tree.tag_configure("routed",      background=BG,        foreground=TEXT)
        self.tree.tag_configure("sep",         background=BORDER,    foreground=BORDER)

        # Bottom: log
        log_frame = tk.Frame(parent, bg=PANEL, height=140, bd=1, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER)
        log_frame.pack(fill="x")
        log_frame.pack_propagate(False)

        tk.Label(log_frame, text="SIMULATION LOG", font=FONT_MED,
                 fg=ACCENT, bg=PANEL, anchor="w").pack(fill="x", padx=12, pady=(8, 2))

        self.log_text = tk.Text(log_frame, bg=BG, fg=GREEN, font=("Courier New", 9),
                                bd=0, wrap="word", state="disabled",
                                insertbackground=GREEN)
        self.log_text.tag_configure("info",  foreground=GREEN)
        self.log_text.tag_configure("error", foreground=RED)
        self.log_text.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    def _btn(self, parent, text, cmd, color=ACCENT):
        return tk.Button(parent, text=text, command=cmd, font=FONT_UI,
                         bg=HEADER, fg=color, activebackground=BORDER,
                         activeforeground=color, bd=0, pady=5, padx=8,
                         cursor="hand2", relief="flat",
                         highlightthickness=1, highlightbackground=BORDER)

    # ── Actions ────────────────────────────────────────────────────────────────

    def _browse_config(self):
        path = filedialog.askopenfilename(
            title="Select Config File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.config_path = path
            self.config_var.set(os.path.basename(path))
            self._log(f"Config selected: {path}")

    def _run_simulation(self):
        if not self.config_path:
            messagebox.showerror("Error", "Please select a config file first.")
            return
        try:
            self.engine = MainEngine(self.config_path)
            self.routers = self.engine.load()
            iters = self.engine.run_convergence()
            self._log(f"Loaded {len(self.routers)} routers. Converged in {iters} iteration(s).")
            self._update_combos()
            self._show_all_tables()
            self.status_label.config(text=f"● {len(self.routers)} ROUTERS LOADED", fg=GREEN)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            self._log(f"ERROR: {e}", error=True)

    def _show_table(self):
        name = self.router_var.get()
        if not name or name not in self.routers:
            return
        self._render_tables([self.routers[name]])

    def _show_all_tables(self):
        if not self.routers:
            return
        self._render_tables(list(self.routers.values()))

    def _render_tables(self, router_list):
        self.tree.delete(*self.tree.get_children())
        for router in router_list:
            table = router.get_table_snapshot()
            for dest, info in sorted(table.items()):
                cost = info["cost"]
                line = info["line"]
                cost_str = str(cost) if cost != -1 else "unreachable"

                if dest == router.name:
                    tag = "self"
                elif cost == -1:
                    tag = "unreachable"
                elif line == dest:
                    tag = "direct"
                else:
                    tag = "routed"

                self.tree.insert("", "end",
                                 values=(router.name, dest, line, cost_str),
                                 tags=(tag,))
            # separator row
            self.tree.insert("", "end", values=("", "", "", ""), tags=("sep",))

    def _apply_change_cost(self):
        router_name = self.cc_router_var.get()
        if not router_name:
            messagebox.showerror("Error", "Select a router first.")
            return
        try:
            idx = int(self.cc_idx_var.get())
            new_cost = int(self.cc_cost_var.get())
        except ValueError:
            messagebox.showerror("Error", "Index and cost must be integers.")
            return

        routers, msg = self.engine.apply_change_cost(router_name, idx, new_cost)
        if routers is None:
            messagebox.showerror("Error", msg)
            self._log(f"ERROR: {msg}", error=True)
        else:
            self.routers = routers
            self._log(f"change_cost applied — {msg}")
            self._show_all_tables()

    def _update_combos(self):
        names = sorted(self.routers.keys())
        self.router_combo["values"] = names
        self.cc_router_combo["values"] = names
        if names:
            self.router_var.set(names[0])
            self.cc_router_var.set(names[0])

    def _reset(self):
        self.routers = {}
        self.engine = MainEngine(None)
        self.config_path = None
        self.config_var.set("No file selected")
        self.tree.delete(*self.tree.get_children())
        self.router_combo["values"] = []
        self.cc_router_combo["values"] = []
        self.status_label.config(text="● NO CONFIG LOADED", fg=RED)
        self._log("Simulator reset.")

    def _log(self, msg, error=False):
        self.log_text.config(state="normal")
        tag = "error" if error else "info"
        self.log_text.insert("end", f"▶  {msg}\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import subprocess, os
    pid = os.getpid()
    subprocess.Popen([
        "osascript", "-e",
        f'delay 0.3\ntell application "System Events"\n'
        f'  set frontmost of (first process whose unix id is {pid}) to true\n'
        f'end tell'
    ])
    root = tk.Tk()
    app = RouterSimGUI(root)
    root.lift()
    root.attributes("-topmost", True)
    root.after(400, lambda: root.attributes("-topmost", False))
    root.focus_force()
    root.mainloop()
