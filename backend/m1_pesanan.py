import csv
import time

# Array
class Array:
    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self.data = [None] * kapasitas
        self.kapasitas = kapasitas
        self.size = 0
        self.salinan = 0             
        self.jumlah_tumbuh = 0
        self.geseran_terakhir = 0

    def __len__(self):
        return self.size

    def _tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.size):
            baru[i] = self.data[i]
        self.salinan += self.size
        self.jumlah_tumbuh += 1
        self.data = baru
        self.kapasitas *= 2

    def append(self, v):
        if self.size == self.kapasitas:
            self._tumbuh()
        self.data[self.size] = v
        self.size += 1
        self.geseran_terakhir = 0

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("indeks sisip di luar jangkauan")
        if self.size == self.kapasitas:
            self._tumbuh()
        d = self.data
        for j in range(self.size, i, -1):
            d[j] = d[j - 1]
        d[i] = v
        self.geseran_terakhir = self.size - i
        self.size += 1
        return self.geseran_terakhir

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        return self.data[i]

    def set(self, i, v):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        self.data[i] = v

    def remove_at(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        d = self.data
        v = d[i]
        for j in range(i, self.size - 1):
            d[j] = d[j + 1]
        self.size -= 1
        d[self.size] = None
        self.geseran_terakhir = self.size - i
        return v

    def pop_back(self):
        if self.size == 0:
            return None
        self.size -= 1
        v = self.data[self.size]
        self.data[self.size] = None
        self.geseran_terakhir = 0
        return v

    def ke_larik(self):
        """Salinan petak berukuran pas (tanpa ruang cadangan)."""
        hasil = [None] * self.size
        for i in range(self.size):
            hasil[i] = self.data[i]
        return hasil


#  LinkList
class Simpul:
    __slots__ = ("nilai", "next")

    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
        self.langkah_terakhir = 0     

    def __len__(self):
        return self.size

    def append(self, v):
        s = Simpul(v)
        if self.tail is None:
            self.head = s
        else:
            self.tail.next = s
        self.tail = s
        self.size += 1
        self.langkah_terakhir = 0

    def prepend(self, v):
        s = Simpul(v)
        s.next = self.head
        self.head = s
        if self.tail is None:
            self.tail = s
        self.size += 1
        self.langkah_terakhir = 0

    def _simpul_ke(self, i):
        cur = self.head
        for _ in range(i):
            cur = cur.next
        return cur

    def insert_at(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("indeks sisip di luar jangkauan")
        if i == 0:
            self.prepend(v)
        elif i == self.size:
            self.append(v)
        else:
            prev = self._simpul_ke(i - 1)
            s = Simpul(v)
            s.next = prev.next
            prev.next = s
            self.size += 1
            self.langkah_terakhir = i - 1
        return self.langkah_terakhir

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        self.langkah_terakhir = i
        return self._simpul_ke(i).nilai

    def ambil(self, mulai, jumlah):
        """Ambil `jumlah` elemen mulai indeks `mulai` -> Array."""
        if mulai < 0 or mulai >= self.size:
            raise IndexError("indeks di luar jangkauan")
        hasil = Array(max(jumlah, 1))
        cur = self._simpul_ke(mulai)
        k = 0
        while cur is not None and k < jumlah:
            hasil.append(cur.nilai)
            cur = cur.next
            k += 1
        self.langkah_terakhir = mulai
        return hasil

    def remove_at(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        if i == 0:
            s = self.head
            self.head = s.next
            if self.head is None:
                self.tail = None
            self.langkah_terakhir = 0
        else:
            prev = self._simpul_ke(i - 1)
            s = prev.next
            prev.next = s.next
            if s is self.tail:
                self.tail = prev
            self.langkah_terakhir = i - 1
        self.size -= 1
        return s.nilai


# muat dari CSV
def muat_pesanan(path):
    """Baca pesanan.csv -> larik primitif berisi tuple 9 kolom."""
    arr = Array(1024)
    with open(path, newline="", encoding="utf-8") as f:
        pembaca = csv.reader(f)
        pertama = True
        for r in pembaca:
            if pertama:
                pertama = False
                continue
            if len(r) < 9:
                continue
            sel = int(float(r[7])) if r[7] != "" else BELUM
            arr.append((r[0], r[1], r[2], r[3], int(r[4]), int(r[5]),
                        int(r[6]), sel, r[8]))
    return arr.ke_larik()


# fasad M1
class DataPesanan:
    """Menyimpan pesanan yang sama pada Array DAN LinkList sekaligus."""

    def __init__(self):
        self.array = Array(1024)
        self.linked = LinkList()
        self.nomor_array = 1
        self.nomor_linked = 1

    def muat(self, larik):
        for rec in larik:
            self.array.append(rec)
            self.linked.append(rec)
        akhir = 0
        if len(larik) > 0:
            akhir = nomor_dari_oid(larik[len(larik) - 1][0])
        self.nomor_array = akhir + 1
        self.nomor_linked = akhir + 1

    def struktur(self, nama):
        if nama == "array":
            return self.array
        if nama == "linked":
            return self.linked
        raise ValueError("struktur harus 'array' atau 'linked'")

    @staticmethod
    def posisi_sisip(jenis, n):
        if jenis == "VIP":
            return 0
        if jenis == "PRIORITAS":
            return n // 2
        if jenis == "REGULER":
            return n
        raise ValueError("jenis harus VIP / PRIORITAS / REGULER")

    def _sisip(self, nama, pos, rec):
        s = self.struktur(nama)
        n = s.size
        if nama == "array":
            if pos == n:
                s.append(rec)
                return 0
            return s.insert(pos, rec)
        if pos == n:
            s.append(rec)
        elif pos == 0:
            s.prepend(rec)
        else:
            s.insert_at(pos, rec)
        return s.langkah_terakhir

    def tambah(self, nama, jenis, pelanggan, resto="kafe-teknik", menu="roti-bakar"):
        """Tambah pesanan baru. -> (rekaman, posisi, biaya)."""
        s = self.struktur(nama)
        pos = self.posisi_sisip(jenis, s.size)
        if nama == "array":
            nomor = self.nomor_array
            self.nomor_array += 1
        else:
            nomor = self.nomor_linked
            self.nomor_linked += 1
        prioritas = 3
        if jenis == "VIP":
            prioritas = 1
        elif jenis == "PRIORITAS":
            prioritas = 2
        rec = buat_rekaman(buat_oid(nomor), pelanggan, prioritas, resto, menu)
        biaya = self._sisip(nama, pos, rec)
        return rec, pos, biaya

    def sisip_pada(self, nama, pos, rec):
        """Dipakai undo/redo."""
        return self._sisip(nama, pos, rec)

    def hapus_pada(self, nama, pos):
        """Hapus pesanan pada indeks `pos` (0-based). -> (rekaman, biaya)."""
        s = self.struktur(nama)
        rec = s.remove_at(pos)
        if nama == "array":
            return rec, s.geseran_terakhir
        return rec, s.langkah_terakhir

    def lihat(self, nama, mulai, jumlah):
        """-> (Array rekaman, biaya)."""
        s = self.struktur(nama)
        if mulai < 0 or mulai >= s.size:
            raise IndexError("nomor pesanan di luar jangkauan")
        if mulai + jumlah > s.size:
            jumlah = s.size - mulai
        if nama == "array":
            hasil = Array(max(jumlah, 1))
            for i in range(mulai, mulai + jumlah):
                hasil.append(s.get(i))
            return hasil, jumlah
        hasil = s.ambil(mulai, jumlah)
        return hasil, s.langkah_terakhir


# utilitas
BELUM = 10 ** 9

# Posisi kolom pada satu rekaman pesanan (tuple 9 elemen)
KOL_OID = 0
KOL_PELANGGAN = 1
KOL_RESTO = 2
KOL_MENU = 3
KOL_HARGA = 4
KOL_PRIORITAS = 5
KOL_MASUK = 6
KOL_SELESAI = 7
KOL_STATUS = 8

NAMA_KUNCI = ("oid", "pelanggan", "resto", "menu", "harga",
              "prioritas", "masuk", "selesai", "status")

NAMA_PRIORITAS = ("", "VIP", "PRIORITAS", "REGULER")

MENU_HARGA = (
    ("air-mineral", 4000), ("es-teh", 5000), ("gorengan", 6000),
    ("teh-tarik", 9000), ("bubur-ayam", 11000), ("roti-bakar", 12000),
    ("es-campur", 12000), ("mie-ayam", 13000), ("mie-goreng", 13000),
    ("kentang-goreng", 14000), ("soto-ayam", 14000), ("gado-gado", 15000),
    ("nasi-goreng", 15000), ("bakso", 16000), ("juice-alpukat", 17000),
    ("kopi-susu", 18000), ("pecel-lele", 18000), ("ayam-geprek", 19000),
    ("nasi-campur", 20000), ("burger-kampus", 21000), ("ayam-bakar", 22000),
    ("sate-ayam", 24000), ("nasi-padang", 25000), ("iga-penyet", 27000),
)

DAFTAR_RESTO = ("kafe-teknik", "kedai-kopi", "warung-bu-ida",
                "bakso-pak-yon", "kantin-asrama", "kantin-pusat")


class Pencacah:
    """Pencacah sederhana yang dititipkan ke algoritma."""

    def __init__(self):
        self.banding = 0
        self.pindah = 0

    def reset(self):
        self.banding = 0
        self.pindah = 0


# waktu
def mulai():
    return time.perf_counter()


def selesai_ms(t0):
    return (time.perf_counter() - t0) * 1000.0


# format
def fmt_int(n):
    """12345 -> '12.345' (pemisah ribuan gaya Indonesia)."""
    n = int(n)
    s = str(abs(n))
    keluar = ""
    hitung = 0
    for i in range(len(s) - 1, -1, -1):
        keluar = s[i] + keluar
        hitung += 1
        if hitung % 3 == 0 and i != 0:
            keluar = "." + keluar
    if n < 0:
        keluar = "-" + keluar
    return keluar


def fmt_desimal(x, d=2):
    return ("%.*f" % (d, x)).replace(".", ",")


def fmt_ms(ms):
    if ms >= 1000.0:
        return fmt_desimal(ms / 1000.0) + " s"
    return fmt_desimal(ms) + " ms"


def fmt_rp(n):
    if n == int(n):
        return "Rp " + fmt_int(n)
    bulat = int(n)
    pecahan = int(round(abs(n - bulat) * 100))
    return "Rp " + fmt_int(bulat) + "," + ("%02d" % pecahan)


def fmt_jam(detik):
    if detik >= BELUM:
        return "-"
    h = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return "%02d:%02d:%02d" % (h, m, s)


def parse_jam(teks):
    """'08:30' atau '08:30:15' -> detik. ValueError bila format salah."""
    bagian = [0, 0, 0]
    n_bagian = 0
    sedang = 0
    ada_digit = False
    for ch in teks.strip() + ":":
        if "0" <= ch <= "9":
            sedang = sedang * 10 + (ord(ch) - 48)
            ada_digit = True
        elif ch == ":":
            if not ada_digit or n_bagian >= 3:
                raise ValueError("format jam harus HH:MM atau HH:MM:SS")
            bagian[n_bagian] = sedang
            n_bagian += 1
            sedang = 0
            ada_digit = False
        else:
            raise ValueError("format jam harus HH:MM atau HH:MM:SS")
    if n_bagian < 2:
        raise ValueError("format jam harus HH:MM atau HH:MM:SS")
    if bagian[1] > 59 or bagian[2] > 59:
        raise ValueError("menit/detik harus 0-59")
    return bagian[0] * 3600 + bagian[1] * 60 + bagian[2]


# pesanan
def buat_oid(nomor):
    return "O-%06d" % nomor


def nomor_dari_oid(oid):
    return int(oid[2:])


def cari_harga(menu):
    for i in range(len(MENU_HARGA)):
        if MENU_HARGA[i][0] == menu:
            return MENU_HARGA[i][1]
    return 10000


def buat_rekaman(oid, pelanggan, prioritas=3, resto="kafe-teknik", menu="roti-bakar"):
    """Rekaman pesanan baru berstatus ANTRE, masuk pada jam dinding saat ini."""
    t = time.localtime()
    masuk = t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec
    return (oid, pelanggan, resto, menu, cari_harga(menu), prioritas,
            masuk, BELUM, "ANTRE")