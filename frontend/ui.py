import os
import tkinter as tk
from tkinter import ttk

from .kontrol import Aplikasi
from backend.util import fmt_ms

WARNA_HEADER = "#1f3a5f"
WARNA_AKTIF = "#dbe7f5"
WARNA_CATATAN = "#fdf6e3"
WARNA_GALAT = "#b00020"
FONT_MONO = ("Menlo", 9)


class Jendela:
    def __init__(self, root, folder_data):
        self.root = root
        self.app = Aplikasi(folder_data)
        self.tombol = []             # pasangan (Menu, ttk.Button)
        self.menu_aktif = None
        self.entri = []              # widget variabel untuk parameter menu aktif
        self._bangun()
        self._pilih(self.app.menu[0])

    def _gulir(self, ev):
        self._kanvas.yview_scroll(-1 if ev.delta > 0 else 1, "units")

    # --------------------------------------------------------------- tata letak
    def _bangun(self):
        r = self.root
        r.title("2EZ4U Food Delivery")
        r.geometry("1180x780")
        r.minsize(900, 600)
        r.columnconfigure(1, weight=1)
        r.rowconfigure(1, weight=1)

        tk.Label(r, text="2EZ4U Food Delivery", bg=WARNA_HEADER, fg="white",
                 font=("Helvetica", 14, "bold"), anchor="w", padx=12, pady=8
                 ).grid(row=0, column=0, columnspan=2, sticky="ew")

        self._bangun_kiri()
        self._bangun_kanan()
        self._bangun_bawah()

    def _bangun_kiri(self):
        kiri = tk.Frame(self.root, width=300)
        kiri.grid(row=1, column=0, sticky="ns")
        kiri.rowconfigure(0, weight=1)
        kanvas = tk.Canvas(kiri, width=290, highlightthickness=0)
        bar = ttk.Scrollbar(kiri, orient="vertical", command=kanvas.yview)
        isi = tk.Frame(kanvas)
        isi.bind("<Configure>", lambda e: kanvas.configure(scrollregion=kanvas.bbox("all")))
        kanvas.create_window((0, 0), window=isi, anchor="nw")
        kanvas.configure(yscrollcommand=bar.set)
        kanvas.grid(row=0, column=0, sticky="ns")
        bar.grid(row=0, column=1, sticky="ns")
        kanvas.bind("<Enter>", lambda e: kanvas.bind_all("<MouseWheel>", self._gulir))
        kanvas.bind("<Leave>", lambda e: kanvas.unbind_all("<MouseWheel>"))
        self._kanvas = kanvas

        grup_terakhir = ""
        for m in self.app.menu:
            if m.grup != grup_terakhir:
                grup_terakhir = m.grup
                tk.Label(isi, text=m.grup, font=("Helvetica", 8, "bold"), fg="#556", anchor="w"
                         ).pack(fill="x", padx=6, pady=(10, 1))
            b = tk.Button(isi, text=m.label, anchor="w", relief="groove", padx=6,
                          command=lambda mm=m: self._pilih(mm))
            b.pack(fill="x", padx=6, pady=1)
            self.tombol.append((m, b))

    def _bangun_kanan(self):
        kanan = tk.Frame(self.root, padx=12, pady=8)
        kanan.grid(row=1, column=1, sticky="nsew")
        kanan.columnconfigure(0, weight=1)
        kanan.rowconfigure(4, weight=1)

        self.lbl_judul = tk.Label(kanan, text="", font=("Helvetica", 12, "bold"), anchor="w")
        self.lbl_judul.grid(row=0, column=0, sticky="ew")
        self.lbl_desc = tk.Label(kanan, text="", fg="#555", anchor="w", justify="left", wraplength=760)
        self.lbl_desc.grid(row=1, column=0, sticky="ew")

        self.frm_form = tk.Frame(kanan)
        self.frm_form.grid(row=2, column=0, sticky="ew", pady=6)

        self.lbl_ringkas = tk.Label(kanan, text="", anchor="w", justify="left", wraplength=860,
                                    font=("Helvetica", 10))
        self.lbl_ringkas.grid(row=3, column=0, sticky="ew", pady=(4, 4))

        tabel = tk.Frame(kanan)
        tabel.grid(row=4, column=0, sticky="nsew")
        tabel.columnconfigure(0, weight=1)
        tabel.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(tabel, show="headings")
        sy = ttk.Scrollbar(tabel, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(tabel, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        self.lbl_catatan = tk.Label(kanan, text="", anchor="w", justify="left", bg=WARNA_CATATAN,
                                    wraplength=860, padx=6, pady=4, fg="#444")
        self.lbl_catatan.grid(row=5, column=0, sticky="ew", pady=(6, 0))

    def _bangun_bawah(self):
        bawah = tk.Frame(self.root, padx=12)
        bawah.grid(row=2, column=0, columnspan=2, sticky="ew")
        bawah.columnconfigure(0, weight=1)
        tk.Label(bawah, text="COMMAND", font=("Helvetica", 8, "bold"), anchor="w").grid(row=0, column=0, sticky="w")
        self.txt_log = tk.Text(bawah, height=5, font=FONT_MONO, state="disabled", wrap="none")
        sb = ttk.Scrollbar(bawah, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=sb.set)
        self.txt_log.grid(row=1, column=0, sticky="ew")
        sb.grid(row=1, column=1, sticky="ns")

        bar = tk.Frame(self.root, bg=WARNA_HEADER)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        tk.Button(bar, text="Tutup", command=self.root.destroy, padx=10).pack(side="left", padx=6, pady=4)
        self.lbl_status = tk.Label(bar, text="[siap]", bg=WARNA_HEADER, fg="white",
                                   font=FONT_MONO, anchor="w")
        self.lbl_status.pack(side="left", padx=10)

    # ------------------------------------------------------------------ aksi
    def _pilih(self, menu):
        self.menu_aktif = menu
        for m, b in self.tombol:
            b.configure(bg=WARNA_AKTIF if m is menu else self.root.cget("bg"))
        self.lbl_judul.configure(text=menu.judul)
        self.lbl_desc.configure(text=menu.deskripsi)
        self._bangun_form(menu)
        self._tampil_kosong()

    def _bangun_form(self, menu):
        for w in self.frm_form.winfo_children():
            w.destroy()
        self.entri = []
        kol = 0
        for p in menu.params:
            sel = tk.Frame(self.frm_form)
            sel.grid(row=0, column=kol, sticky="nw", padx=(0, 14))
            tk.Label(sel, text=p.label, font=("Helvetica", 9, "bold"), anchor="w").pack(anchor="w")
            var = tk.StringVar(value=p.default)
            if p.pilihan:
                w = ttk.Combobox(sel, textvariable=var, values=list(p.pilihan), state="readonly", width=14)
            else:
                lebar = 46 if len(p.default) > 18 else 22
                w = tk.Entry(sel, textvariable=var, width=lebar)
                w.bind("<Return>", lambda e: self._jalankan())
            w.pack(anchor="w")
            if p.hint:
                tk.Label(sel, text=p.hint, fg="#888", font=("Helvetica", 8), anchor="w").pack(anchor="w")
            self.entri.append(var)
            kol += 1
        teks = "JALANKAN"
        if menu.kunci == "load":
            teks = "LOAD DATA"
        elif menu.kunci in ("stack_undo",):
            teks = "UNDO"
        elif menu.kunci in ("stack_redo",):
            teks = "REDO"
        tk.Button(self.frm_form, text=teks, bg=WARNA_HEADER, fg="white", padx=18, pady=4,
                  command=self._jalankan).grid(row=0, column=kol, sticky="sw")

    def _tampil_kosong(self):
        self.lbl_ringkas.configure(text="", fg="black")
        self.lbl_catatan.configure(text="")
        self._isi_tabel((), [])

    def _jalankan(self):
        m = self.menu_aktif
        nilai = []
        for v in self.entri:
            nilai.append(v.get())
        self.root.configure(cursor="watch")
        self.lbl_status.configure(text="[%s] berjalan..." % m.label)
        self.root.update_idletasks()
        try:
            h = self.app.jalankan(m.kunci, tuple(nilai))
        finally:
            self.root.configure(cursor="")
        self._tampil(h)

    def _tampil(self, h):
        teks = ""
        for i in range(len(h.ringkasan)):
            teks += ("\n" if i else "") + h.ringkasan[i]
        self.lbl_ringkas.configure(text=teks, fg=WARNA_GALAT if h.galat else "black")
        self.lbl_catatan.configure(text=h.catatan)
        self._isi_tabel(h.kolom, h.baris)
        self.lbl_status.configure(text="[%s] %s" % (h.modul, fmt_ms(h.ms)))
        self._catat(h)

    def _isi_tabel(self, kolom, baris):
        self.tree.delete(*self.tree.get_children())
        self.tree.configure(columns=list(kolom))
        for i in range(len(kolom)):
            lebar = len(kolom[i])
            for r in range(min(len(baris), 60)):
                if len(baris[r][i]) > lebar:
                    lebar = len(baris[r][i])
            px = max(50, min(380, lebar * 8 + 16))
            self.tree.heading(kolom[i], text=kolom[i])
            self.tree.column(kolom[i], width=px, anchor="w", stretch=(i == len(kolom) - 1))
        for b in baris:
            self.tree.insert("", "end", values=list(b))

    def _catat(self, h):
        baris = "%-34s -> %-22s %s\n" % (h.perintah[:34], h.modul, fmt_ms(h.ms))
        self.txt_log.configure(state="normal")
        self.txt_log.insert("1.0", baris)
        self.txt_log.configure(state="disabled")


def jalankan():
    akar = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root = tk.Tk()
    Jendela(root, os.path.join(akar, "data"))
    root.mainloop()
