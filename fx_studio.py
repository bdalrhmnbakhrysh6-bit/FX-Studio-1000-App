import os, shutil, subprocess, sys, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
EFFECTS_DIR = APP_DIR / "effects"
EXPORT_DIR = APP_DIR / "exports"

CATEGORIES = {
    "العربية": ["الكل", "الجزيئات", "تسريبات الضوء", "الأعراس", "الدخان", "وهج العدسات", "الانتقالات"],
    "English": ["All", "Particles", "Light Leaks", "Wedding", "Smoke", "Lens Flares", "Transitions"]
}
FOLDERS = {
    "الكل":"", "الجزيئات":"Particles", "تسريبات الضوء":"Light_Leaks", "الأعراس":"Wedding",
    "الدخان":"Smoke", "وهج العدسات":"Lens_Flares", "الانتقالات":"Transitions",
    "All":"", "Particles":"Particles", "Light Leaks":"Light_Leaks", "Wedding":"Wedding",
    "Smoke":"Smoke", "Lens Flares":"Lens_Flares", "Transitions":"Transitions"
}

class FXStudio:
    def __init__(self, root):
        self.root = root
        self.lang = "ar"
        self.category = "الكل"
        self.files = []
        self.selected = None
        self.root.title("FX Studio 1000")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.style = ttk.Style()
        try: self.style.theme_use("clam")
        except: pass
        self.build()
        self.refresh()

    def tr(self, ar, en):
        return ar if self.lang == "ar" else en

    def build(self):
        self.root.configure(bg="#11151d")
        top = tk.Frame(self.root, bg="#171e2a", height=76)
        top.pack(fill="x")
        tk.Label(top, text="FX Studio 1000", fg="#f4c76b", bg="#171e2a",
                 font=("Arial", 22, "bold")).pack(side="left", padx=22, pady=18)
        self.subtitle = tk.Label(top, text=self.tr("مكتبة المؤثرات السينمائية","Cinematic Effects Library"),
                                 fg="#d7dfeb", bg="#171e2a", font=("Arial", 11))
        self.subtitle.pack(side="left", padx=10)
        self.lang_btn = tk.Button(top, text="English", command=self.toggle_lang, bg="#293548",
                                  fg="white", relief="flat", padx=14, pady=8)
        self.lang_btn.pack(side="right", padx=20)
        body = tk.Frame(self.root, bg="#11151d")
        body.pack(fill="both", expand=True, padx=18, pady=16)
        sidebar = tk.Frame(body, bg="#171e2a", width=220)
        sidebar.pack(side="left", fill="y", padx=(0,14))
        sidebar.pack_propagate(False)
        self.cat_title = tk.Label(sidebar, text=self.tr("التصنيفات","CATEGORIES"), fg="#f4c76b",
                                  bg="#171e2a", font=("Arial", 12, "bold"))
        self.cat_title.pack(anchor="w", padx=16, pady=(18,10))
        self.cat_buttons = tk.Frame(sidebar, bg="#171e2a")
        self.cat_buttons.pack(fill="x", padx=10)
        self.rebuild_categories()
        self.add_btn = tk.Button(sidebar, text=self.tr("＋ إضافة مؤثرات","＋ Add Effects"),
                                 command=self.add_effects, bg="#b88b3c", fg="#10151d",
                                 font=("Arial", 11, "bold"), relief="flat", pady=10)
        self.add_btn.pack(fill="x", padx=12, pady=(22,8))
        self.open_btn = tk.Button(sidebar, text=self.tr("فتح مجلد المؤثرات","Open Effects Folder"),
                                  command=self.open_effects, bg="#293548", fg="white",
                                  relief="flat", pady=9)
        self.open_btn.pack(fill="x", padx=12)
        main = tk.Frame(body, bg="#11151d")
        main.pack(side="left", fill="both", expand=True)
        bar = tk.Frame(main, bg="#11151d")
        bar.pack(fill="x", pady=(0,12))
        self.heading = tk.Label(bar, text=self.tr("مكتبة المؤثرات","Effects Library"), fg="white",
                                bg="#11151d", font=("Arial", 18, "bold"))
        self.heading.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        self.search = tk.Entry(bar, textvariable=self.search_var, bg="#202a39", fg="white",
                               insertbackground="white", relief="flat", font=("Arial", 11))
        self.search.pack(side="right", ipadx=12, ipady=9, fill="x", expand=True, padx=(20,0))
        self.search.insert(0, "")
        self.listbox = tk.Listbox(main, bg="#171e2a", fg="#e8edf5", selectbackground="#8b672f",
                                  font=("Arial", 12), relief="flat", borderwidth=0,
                                  activestyle="none")
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.select_file)
        bottom = tk.Frame(main, bg="#11151d")
        bottom.pack(fill="x", pady=(12,0))
        self.details = tk.Label(bottom, text=self.tr("اختر مؤثراً لعرض تفاصيله","Select an effect to view details"),
                                fg="#aeb9c9", bg="#11151d", anchor="w")
        self.details.pack(side="left", fill="x", expand=True)
        self.export_btn = tk.Button(bottom, text=self.tr("نسخ إلى مجلد Premiere","Copy to Premiere Folder"),
                                    command=self.export_effect, bg="#293548", fg="white",
                                    relief="flat", padx=12, pady=9)
        self.export_btn.pack(side="right")

    def rebuild_categories(self):
        for w in self.cat_buttons.winfo_children(): w.destroy()
        cats = CATEGORIES["العربية"] if self.lang == "ar" else CATEGORIES["English"]
        for c in cats:
            b = tk.Button(self.cat_buttons, text=c, anchor="w", command=lambda x=c:self.choose_category(x),
                          bg="#202a39" if c != self.category else "#34465e", fg="white",
                          activebackground="#40536c", activeforeground="white", relief="flat",
                          padx=12, pady=9)
            b.pack(fill="x", pady=3)

    def toggle_lang(self):
        self.lang = "en" if self.lang == "ar" else "ar"
        self.lang_btn.config(text="العربية" if self.lang == "en" else "English")
        self.subtitle.config(text=self.tr("مكتبة المؤثرات السينمائية","Cinematic Effects Library"))
        self.cat_title.config(text=self.tr("التصنيفات","CATEGORIES"))
        self.add_btn.config(text=self.tr("＋ إضافة مؤثرات","＋ Add Effects"))
        self.open_btn.config(text=self.tr("فتح مجلد المؤثرات","Open Effects Folder"))
        self.heading.config(text=self.tr("مكتبة المؤثرات","Effects Library"))
        self.export_btn.config(text=self.tr("نسخ إلى مجلد Premiere","Copy to Premiere Folder"))
        self.category = "الكل" if self.lang == "ar" else "All"
        self.rebuild_categories()
        self.refresh()

    def choose_category(self, cat):
        self.category = cat
        self.rebuild_categories()
        self.refresh()

    def refresh(self):
        folder = FOLDERS.get(self.category, "")
        base = EFFECTS_DIR / folder if folder else EFFECTS_DIR
        files = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in
                 [".mov",".mp4",".webm",".png",".jpg",".jpeg",".gif"]]
        query = self.search_var.get().lower().strip()
        if query: files = [p for p in files if query in p.name.lower()]
        self.files = sorted(files)
        self.listbox.delete(0, tk.END)
        for p in self.files:
            self.listbox.insert(tk.END, f"  {p.relative_to(EFFECTS_DIR)}")
        self.details.config(text=self.tr(f"عدد المؤثرات: {len(self.files)}","Effects found: "+str(len(self.files))))
        self.selected = None

    def select_file(self, _=None):
        sel = self.listbox.curselection()
        if not sel: return
        self.selected = self.files[sel[0]]
        self.details.config(text=f"{self.selected.name}  |  {self.selected.suffix.upper()}  |  {self.selected.stat().st_size//1024} KB")

    def add_effects(self):
        paths = filedialog.askopenfilenames(title=self.tr("اختر ملفات المؤثرات","Select effect files"),
            filetypes=[("Media","*.mov *.mp4 *.webm *.png *.jpg *.jpeg *.gif"),("All files","*.*")])
        if not paths: return
        target = EFFECTS_DIR / "Imported"
        target.mkdir(exist_ok=True)
        copied = 0
        for p in paths:
            try:
                dest = target / Path(p).name
                if dest.exists(): dest = target / (Path(p).stem + "_copy" + Path(p).suffix)
                shutil.copy2(p, dest); copied += 1
            except Exception as e: messagebox.showerror("FX Studio", str(e))
        self.refresh()
        messagebox.showinfo("FX Studio", self.tr(f"تمت إضافة {copied} ملف","Imported "+str(copied)+" file(s)"))

    def open_effects(self):
        EFFECTS_DIR.mkdir(exist_ok=True)
        if sys.platform == "win32": os.startfile(EFFECTS_DIR)
        elif sys.platform == "darwin": subprocess.Popen(["open", str(EFFECTS_DIR)])
        else: subprocess.Popen(["xdg-open", str(EFFECTS_DIR)])

    def export_effect(self):
        if not self.selected:
            messagebox.showwarning("FX Studio", self.tr("اختر مؤثراً أولاً","Select an effect first")); return
        dest = filedialog.askdirectory(title=self.tr("اختر مجلد مشروع Premiere أو مجلد التصدير","Choose Premiere project or export folder"))
        if not dest: return
        try:
            shutil.copy2(self.selected, Path(dest)/self.selected.name)
            messagebox.showinfo("FX Studio", self.tr("تم نسخ المؤثر بنجاح","Effect copied successfully"))
        except Exception as e: messagebox.showerror("FX Studio", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    FXStudio(root)
    root.mainloop()
