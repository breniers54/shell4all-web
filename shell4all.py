import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from fpdf import FPDF
import json
import os
import subprocess

class Shell4All:
    def __init__(self, root):
        self.root = root
        self.root.title("Shell4All Pro - Terminal Intégré")
        self.root.geometry("900x800")
        self.db_file = os.path.join(os.path.dirname(__file__), "shell_data.json")
        self.load_data()
        self.setup_ui()

    def load_data(self):
        default_data = {
            "Système": {"uname -a": "Infos système.", "uptime": "Temps de fonctionnement."},
            "Fichiers": {"ls -lh": "Liste les fichiers.", "pwd": "Répertoire courant."}
        }
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = default_data

    def save_data(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def setup_ui(self):
        header = tk.Frame(self.root, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(header, text="SHELL4ALL INTERACTIVE", font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50").pack(pady=10)
        form_frame = tk.LabelFrame(self.root, text=" Ajouter une commande ")
        form_frame.pack(pady=5, padx=20, fill="x")
        self.entries = {}
        for i, (l, k) in enumerate([("Catégorie:", "cat"), ("Commande:", "cmd"), ("Description:", "desc")]):
            tk.Label(form_frame, text=l).grid(row=0, column=i*2, padx=5, sticky="w")
            self.entries[k] = tk.Entry(form_frame)
            self.entries[k].grid(row=0, column=i*2+1, padx=5, sticky="ew")
        tk.Button(form_frame, text="Ajouter", command=self.add_command, bg="#3498db", fg="white").grid(row=0, column=6, padx=10, pady=5)
        form_frame.columnconfigure((1,3,5), weight=1)
        search_frame = tk.Frame(self.root); search_frame.pack(pady=5, padx=20, fill="x")
        self.search_var = tk.StringVar(); self.search_var.trace("w", self.update_list)
        tk.Entry(search_frame, textvariable=self.search_var).pack(fill="x")
        self.tree = ttk.Treeview(self.root, columns=("Description"), show="tree headings")
        self.tree.heading("#0", text="Commande"); self.tree.heading("Description", text="Action")
        self.tree.pack(pady=5, padx=20, fill="both", expand=True)
        self.terminal_output = tk.Text(self.root, height=10, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.terminal_output.pack(pady=5, padx=20, fill="x")
        btn_frame = tk.Frame(self.root); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="▶ EXÉCUTER", command=self.run_command, bg="#e67e22", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Supprimer", command=self.delete_item).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Exporter PDF", command=self.export_to_pdf, bg="#27ae60", fg="white").pack(side="left", padx=10)
        self.update_list()

    def run_command(self):
        selected = self.tree.selection()
        if not selected: return
        cmd_text = self.tree.item(selected[0])['text']
        if not self.tree.parent(selected[0]): return
        self.terminal_output.delete("1.0", tk.END)
        try:
            result = subprocess.run(cmd_text, shell=True, capture_output=True, text=True, timeout=5)
            self.terminal_output.insert(tk.END, result.stdout + result.stderr)
        except Exception as e:
            self.terminal_output.insert(tk.END, f"Erreur : {str(e)}")

    def add_command(self):
        cat, cmd, desc = self.entries['cat'].get().strip(), self.entries['cmd'].get().strip(), self.entries['desc'].get().strip()
        if cat and cmd and desc:
            if cat not in self.data: self.data[cat] = {}
            self.data[cat][cmd] = desc
            self.save_data(); self.update_list()
            for k in self.entries: self.entries[k].delete(0, tk.END)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected: return
        t, p = self.tree.item(selected[0])['text'], self.tree.parent(selected[0])
        if p: del self.data[self.tree.item(p)['text']][t]
        else: del self.data[t]
        self.save_data(); self.update_list()

    def update_list(self, *args):
        s = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for cat, cmds in sorted(self.data.items()):
            parent = self.tree.insert("", "end", text=cat, open=True)
            added = False
            for cmd, desc in sorted(cmds.items()):
                if s in cmd.lower() or s in desc.lower():
                    self.tree.insert(parent, "end", text=cmd, values=(desc,))
                    added = True
            if not added: self.tree.delete(parent)

    def export_to_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path: return
        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Shell4All Library", ln=True, align='C')
        for cat, cmds in sorted(self.data.items()):
            pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, cat, ln=True, fill=True)
            for cmd, desc in cmds.items():
                pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 7, f"{cmd}: {desc}")
        pdf.output(path); messagebox.showinfo("OK", "PDF généré")

if __name__ == "__main__":
    root = tk.Tk()
    app = Shell4All(root)
    root.mainloop()