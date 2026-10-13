from .m1_pesanan import Array, buat_oid, buat_rekaman


class KesalahanEkspresi(Exception):
    pass


# Stack
class Tumpukan:
    def __init__(self):
        self.a = Array(8)

    def push(self, x):
        self.a.append(x)

    def pop(self):
        if self.a.size == 0:
            raise IndexError("tumpukan kosong")
        return self.a.pop_back()

    def peek(self):
        if self.a.size == 0:
            raise IndexError("tumpukan kosong")
        return self.a.data[self.a.size - 1]

    def kosong(self):
        return self.a.size == 0

    def ukuran(self):
        return self.a.size

    def isi_teks(self):
        if self.a.size == 0:
            return "kosong"
        s = ""
        for i in range(self.a.size):
            if i > 0:
                s += " "
            s += _teks(self.a.data[i])
        return s


def _teks(x):
    if isinstance(x, float):
        if x == int(x):
            return str(int(x))
        return "%g" % x
    return str(x)


def _gabung(arr):
    s = ""
    for i in range(arr.size):
        if i > 0:
            s += " "
        s += _teks(arr.data[i])
    return s


#  kasir
def _operator(t):
    return t == "+" or t == "-" or t == "*" or t == "/"


def _prio(op):
    if op == "*" or op == "/":
        return 2
    return 1


def _digit(c):
    return ("0" <= c <= "9") or c == "."


def pecah_token(ekspresi):
    """Angka berdigit banyak = satu token. '-' tepat sebelum angka, bila operand
    sedang diharapkan, dianggap tanda negatif."""
    tok = Array(16)
    harap_operand = True
    i = 0
    n = len(ekspresi)
    while i < n:
        ch = ekspresi[i]
        if ch == " " or ch == "\t":
            i += 1
        elif _digit(ch) or (ch == "-" and harap_operand and i + 1 < n
                            and _digit(ekspresi[i + 1])):
            j = i + 1
            while j < n and _digit(ekspresi[j]):
                j += 1
            angka = ekspresi[i:j]
            titik = 0
            for c in angka:
                if c == ".":
                    titik += 1
            if titik > 1 or angka == "." or angka == "-.":
                raise KesalahanEkspresi("angka tidak valid: " + angka)
            tok.append(angka)
            harap_operand = False
            i = j
        elif _operator(ch):
            tok.append(ch)
            harap_operand = True
            i += 1
        elif ch == "(" or ch == ")":
            tok.append(ch)
            harap_operand = (ch == "(")
            i += 1
        else:
            raise KesalahanEkspresi("karakter tidak dikenal: '" + ch + "'")
    return tok


def ke_postfix(ekspresi):
    """-> (postfix: larik token, jejak: larik tuple (no, token, tindakan, stack, keluaran))."""
    tok = pecah_token(ekspresi)
    if tok.size == 0:
        raise KesalahanEkspresi("ekspresi kosong")
    st = Tumpukan()
    keluar = Array(16)
    jejak = Array(32)
    harap_operand = True
    for k in range(tok.size):
        t = tok.data[k]
        no = "1.%d" % (k + 1)
        if t == "(":
            if not harap_operand:
                raise KesalahanEkspresi("tanda '(' tidak pada tempatnya")
            st.push(t)
            tindakan = "push ( ke stack"
        elif t == ")":
            if harap_operand:
                raise KesalahanEkspresi("tanda ')' tidak pada tempatnya")
            while not st.kosong() and st.peek() != "(":
                keluar.append(st.pop())
            if st.kosong():
                raise KesalahanEkspresi("kurung tidak seimbang: ')' berlebih")
            st.pop()
            tindakan = "pop sampai (, lalu buang ("
            harap_operand = False
        elif _operator(t):
            if harap_operand:
                raise KesalahanEkspresi("operator '" + t + "' tidak pada tempatnya")
            dibuang = ""
            while (not st.kosong() and st.peek() != "(" and
                   _prio(st.peek()) >= _prio(t)):
                op = st.pop()
                keluar.append(op)
                dibuang += op + " "
            if dibuang == "":
                tindakan = "push " + t
            else:
                tindakan = "pop " + dibuang + "(lebih kuat/sama kuat), push " + t
            st.push(t)
            harap_operand = True
        else:
            if not harap_operand:
                raise KesalahanEkspresi("dua angka berurutan tanpa operator")
            keluar.append(t)
            tindakan = "operand, langsung ke output"
            harap_operand = False
        jejak.append((no, t, tindakan, st.isi_teks(), _gabung(keluar)))
    if harap_operand:
        raise KesalahanEkspresi("ekspresi berakhir dengan operator")
    while not st.kosong():
        op = st.pop()
        if op == "(":
            raise KesalahanEkspresi("kurung tidak seimbang: '(' tidak ditutup")
        keluar.append(op)
    jejak.append(("1.akhir", "akhir", "pop sisa stack", "kosong", _gabung(keluar)))
    return keluar.ke_larik(), jejak.ke_larik()


def _ke_angka(t):
    for c in t:
        if c == ".":
            return float(t)
    return int(t)


def hitung(postfix):
    """Evaluasi postfix dengan stack angka. -> (total, jejak)."""
    st = Tumpukan()
    jejak = Array(32)
    for k in range(len(postfix)):
        t = postfix[k]
        no = "2.%d" % (k + 1)
        if _operator(t):
            if st.ukuran() < 2:
                raise KesalahanEkspresi("operand kurang untuk operator " + t)
            b = st.pop()           # operand KANAN keluar lebih dulu
            a = st.pop()
            if t == "+":
                r = a + b
            elif t == "-":
                r = a - b
            elif t == "*":
                r = a * b
            else:
                if b == 0:
                    raise KesalahanEkspresi("pembagian dengan nol")
                r = a / b
            if isinstance(r, float) and r == int(r):
                r = int(r)
            st.push(r)
            tindakan = "pop %s dan %s -> %s %s %s = %s" % (
                _teks(b), _teks(a), _teks(a), t, _teks(b), _teks(r))
        else:
            st.push(_ke_angka(t))
            tindakan = "operand, push " + t
        jejak.append((no, t, tindakan, st.isi_teks(), ""))
    if st.ukuran() != 1:
        raise KesalahanEkspresi("ekspresi tidak valid (sisa stack %d)" % st.ukuran())
    return st.pop(), jejak.ke_larik()


# Queue
class AntreanNaif:
    """Larik biasa; dequeue mengambil indeks 0 lalu menggeser seluruh sisa."""

    def __init__(self):
        self.a = Array(16)
        self.total_geseran = 0

    def __len__(self):
        return self.a.size

    def enqueue(self, x):
        self.a.append(x)

    def dequeue(self):
        if self.a.size == 0:
            return None
        x = self.a.remove_at(0)
        self.total_geseran += self.a.geseran_terakhir
        return x

    def push_front(self, x):
        self.total_geseran += self.a.insert(0, x)

    def pop_back(self):
        return self.a.pop_back()

    def kapasitas(self):
        return self.a.kapasitas

    def isi(self):
        return self.a.ke_larik()


class AntreanMelingkar:
    def __init__(self, kapasitas=16):
        if kapasitas < 1:
            kapasitas = 1
        self.data = [None] * kapasitas
        self.K = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.salinan = 0
        self.total_geseran = 0       # selalu 0: tidak ada elemen yang digeser

    def __len__(self):
        return self.count

    def is_empty(self):
        return self.count == 0

    def _tumbuh(self):
        baru = [None] * (self.K * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.K]
        self.salinan += self.count
        self.data = baru
        self.K *= 2
        self.front = 0
        self.rear = self.count

    def enqueue(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.K
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.K
        self.count -= 1
        return x

    def push_front(self, x):
        if self.count == self.K:
            self._tumbuh()
        self.front = (self.front - 1) % self.K
        self.data[self.front] = x
        self.count += 1

    def pop_back(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.K
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def kapasitas(self):
        return self.K

    def isi(self):
        hasil = [None] * self.count
        for i in range(self.count):
            hasil[i] = self.data[(self.front + i) % self.K]
        return hasil


# undo / redo
class Aksi:
    """Catatan satu aksi. `daftar` menyimpan rekamannya, bukan sekadar hitungan."""

    def __init__(self, jenis, varian, daftar, posisi=0):
        self.jenis = jenis        # ENQUEUE / DEQUEUE / ORDER / HAPUS
        self.varian = varian      # 'naif' | 'circular' | 'kedua' | 'array' | 'linked'
        self.daftar = daftar
        self.posisi = posisi

    def deskripsi(self):
        n = len(self.daftar)
        if self.jenis == "ENQUEUE":
            return "ENQUEUE %s (kedua antrean)" % self.daftar[0][0]
        if self.jenis == "DEQUEUE":
            return "DEQUEUE x%d (%s)" % (n, self.varian)
        if self.jenis == "ORDER":
            return "ORDER %s (%s, posisi %d)" % (self.daftar[0][0], self.varian, self.posisi + 1)
        return "HAPUS %s (%s, posisi %d)" % (self.daftar[0][0], self.varian, self.posisi + 1)


class LayananAntrean:
    """Dua antrean berisi pesanan yang sama + tumpukan undo/redo."""

    def __init__(self, store=None):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar(16)
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        self.store = store           # DataPesanan (M1), untuk undo ORDER/HAPUS
        self.nomor_baru = 1

    def isi(self, larik, nomor_berikut):
        """Isi awal dari pesanan berstatus ANTRE (tidak dicatat di undo)."""
        for rec in larik:
            if rec[8] == "ANTRE":
                self.naif.enqueue(rec)
                self.melingkar.enqueue(rec)
        self.nomor_baru = nomor_berikut

    def _catat(self, aksi):
        self.undo.push(aksi)
        self.redo = Tumpukan()       # aksi baru mengosongkan redo

    def catat_m1(self, jenis, struktur, posisi, rec):
        satu = [None]
        satu[0] = rec
        self._catat(Aksi(jenis, struktur, satu, posisi))

    def enqueue(self, pelanggan, resto="kafe-teknik", menu="roti-bakar", prioritas=3):
        rec = buat_rekaman(buat_oid(self.nomor_baru), pelanggan, prioritas, resto, menu)
        self.nomor_baru += 1
        self.naif.enqueue(rec)
        self.melingkar.enqueue(rec)
        satu = [None]
        satu[0] = rec
        self._catat(Aksi("ENQUEUE", "kedua", satu))
        return rec

    def dequeue(self, varian, n):
        """-> (larik rekaman keluar, jumlah elemen yang digeser)."""
        q = self.naif if varian == "naif" else self.melingkar
        awal = q.total_geseran
        keluar = Array(max(n, 1))
        for _ in range(n):
            x = q.dequeue()
            if x is None:
                break
            keluar.append(x)
        daftar = keluar.ke_larik()
        if len(daftar) > 0:
            self._catat(Aksi("DEQUEUE", varian, daftar))
        return daftar, q.total_geseran - awal

    def _balik(self, a):
        """Jalankan KEBALIKAN aksi."""
        if a.jenis == "ENQUEUE":
            self.naif.pop_back()
            self.melingkar.pop_back()
            return "Pembatalan enqueue: %s dikeluarkan lagi dari belakang." % a.daftar[0][0]
        if a.jenis == "DEQUEUE":
            q = self.naif if a.varian == "naif" else self.melingkar
            for i in range(len(a.daftar) - 1, -1, -1):   # urutan asli kembali ke DEPAN
                q.push_front(a.daftar[i])
            return "%d pesanan dikembalikan ke DEPAN antrean %s." % (len(a.daftar), a.varian)
        if a.jenis == "ORDER":
            self.store.hapus_pada(a.varian, a.posisi)
            return "Pesanan %s dicabut dari %s (posisi %d)." % (a.daftar[0][0], a.varian, a.posisi + 1)
        self.store.sisip_pada(a.varian, a.posisi, a.daftar[0])
        return "Pesanan %s dikembalikan ke %s (posisi %d)." % (a.daftar[0][0], a.varian, a.posisi + 1)

    def _ulang(self, a):
        """Kerjakan lagi AKSI ASLINYA (bukan kebalikannya)."""
        if a.jenis == "ENQUEUE":
            self.naif.enqueue(a.daftar[0])
            self.melingkar.enqueue(a.daftar[0])
            return "Enqueue dikerjakan lagi: %s masuk kembali ke belakang." % a.daftar[0][0]
        if a.jenis == "DEQUEUE":
            q = self.naif if a.varian == "naif" else self.melingkar
            for _ in range(len(a.daftar)):
                q.dequeue()
            return "%d pesanan keluar lagi dari antrean %s." % (len(a.daftar), a.varian)
        if a.jenis == "ORDER":
            self.store.sisip_pada(a.varian, a.posisi, a.daftar[0])
            return "Pesanan %s masuk kembali ke %s (posisi %d)." % (a.daftar[0][0], a.varian, a.posisi + 1)
        self.store.hapus_pada(a.varian, a.posisi)
        return "Pesanan %s dihapus lagi dari %s." % (a.daftar[0][0], a.varian)

    def undo_last(self):
        """-> (aksi, pesan), atau None bila tidak ada yang bisa dibatalkan."""
        if self.undo.kosong():
            return None
        a = self.undo.pop()
        pesan = self._balik(a)
        self.redo.push(a)
        return a, pesan

    def redo_last(self):
        if self.redo.kosong():
            return None
        a = self.redo.pop()
        pesan = self._ulang(a)
        self.undo.push(a)
        return a, pesan

    def history(self):
        """Riwayat aksi (terlama -> terbaru), konsisten dengan tumpukan undo."""
        n = self.undo.ukuran()
        h = [None] * n
        for i in range(n):
            h[i] = self.undo.a.data[i].deskripsi()
        return h

    def stats(self):
        return (("queue_len_naif", len(self.naif)),
                ("queue_len_circular", len(self.melingkar)),
                ("queue_capacity_naif", self.naif.kapasitas()),
                ("queue_capacity_circular", self.melingkar.kapasitas()),
                ("total_geseran_naif", self.naif.total_geseran),
                ("total_geseran_circular", self.melingkar.total_geseran),
                ("undo_depth", self.undo.ukuran()),
                ("redo_depth", self.redo.ukuran()))
