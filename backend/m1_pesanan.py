"""M1 - Manajemen data pesanan.

Dua representasi dibangun berdampingan:
  * Array  : larik dinamis dengan kapasitas ganda (amortized O(1) append).
  * LinkedList : senarai bertaut ganda simpul, tanpa larik penampung.

Rekaman pesanan adalah tuple 9 medan:
  (oid, pelanggan, resto, menu, harga, prioritas, masuk, selesai, status)

Modul ini juga menampung util bersama (konstanta, format, waktu) yang dipakai
modul lain dan antarmuka.
"""
import time

# Penanda pesanan yang belum selesai (dipakai sebagai "waktu selesai").
BELUM = 10 ** 9
JUMLAH_DETIK_HARI = 24 * 60 * 60
NAMA_PRIORITAS = ("", "VIP", "PRIORITAS", "REGULER")


def nama_prioritas(prioritas):
    if 1 <= prioritas <= 3:
        return NAMA_PRIORITAS[prioritas]
    return "?"


def jenis_prioritas(nama):
    if nama == "VIP":
        return 1
    if nama == "PRIORITAS":
        return 2
    return 3


def posisi_prioritas(prioritas, size):
    if prioritas == 1:
        return 0
    if prioritas == 2:
        return size // 2
    return size


def jam_sekarang():
    lt = time.localtime()
    return lt.tm_hour * 3600 + lt.tm_min * 60 + lt.tm_sec


def fmt_int(n):
    """Format bilangan bulat dengan pemisah ribuan titik tanpa format bawaan."""
    negatif = n < 0
    if negatif:
        n = -n
    angka = ""
    if n == 0:
        angka = "0"
    while n > 0:
        angka = chr(48 + (n % 10)) + angka
        n //= 10
    keluaran = ""
    panjang = len(angka)
    for i in range(panjang):
        if i > 0 and (panjang - i) % 3 == 0:
            keluaran += "."
        keluaran += angka[i]
    if negatif:
        keluaran = "-" + keluaran
    return keluaran


def fmt_rp(n):
    return "Rp " + fmt_int(n)


def fmt_jam(detik):
    if detik >= BELUM:
        return "-"
    d = detik % JUMLAH_DETIK_HARI
    jam = d // 3600
    menit = (d % 3600) // 60
    return "%02d:%02d" % (jam, menit)


def mulai():
    return time.perf_counter()


def selesai_ms(t0):
    return (time.perf_counter() - t0) * 1000.0


def fmt_ms(ms):
    if ms < 1.0:
        return "%.3f ms" % ms
    if ms < 1000.0:
        return "%.2f ms" % ms
    return "%.3f s" % (ms / 1000.0)


def format_oid(nomor):
    """O-000001 ... (enam digit)."""
    angka = ""
    n = nomor
    for _ in range(6):
        angka = chr(48 + (n % 10)) + angka
        n //= 10
    return "O-" + angka


# --------------------------------------------------------------- dynamic array
class Array:
    """Larik dinamis buatan sendiri: tumbuh dua kali saat kapasitas penuh."""

    def __init__(self, kapasitas_awal=16):
        if kapasitas_awal < 1:
            kapasitas_awal = 1
        self.data = [None] * kapasitas_awal
        self.size = 0
        self.kapasitas = kapasitas_awal
        self.jumlah_tumbuh = 0
        self.salinan = 0

    def _siapkan(self, perlu):
        if perlu <= self.kapasitas:
            return
        kapasitas = self.kapasitas
        while kapasitas < perlu:
            kapasitas *= 2
        baru = [None] * kapasitas
        i = 0
        while i < self.size:
            baru[i] = self.data[i]
            i += 1
        self.salinan += self.size
        self.data = baru
        self.kapasitas = kapasitas
        self.jumlah_tumbuh += 1

    def append(self, nilai):
        self._siapkan(self.size + 1)
        self.data[self.size] = nilai
        self.size += 1

    def get(self, pos):
        return self.data[pos]

    def set(self, pos, nilai):
        self.data[pos] = nilai

    def insert(self, pos, nilai):
        """Menyisipkan pada pos, menggeser elemen setelahnya. -> jumlah geseran."""
        self._siapkan(self.size + 1)
        i = self.size
        geser = 0
        while i > pos:
            self.data[i] = self.data[i - 1]
            i -= 1
            geser += 1
        self.data[pos] = nilai
        self.size += 1
        return geser

    def hapus(self, pos):
        """Menghapus pos, menggeser sisa ke kiri. -> jumlah geseran."""
        geser = 0
        i = pos
        while i < self.size - 1:
            self.data[i] = self.data[i + 1]
            i += 1
            geser += 1
        self.size -= 1
        self.data[self.size] = None
        return geser

    def ke_larik(self):
        """Salinan padat tanpa ruang cadangan."""
        hasil = [None] * self.size
        i = 0
        while i < self.size:
            hasil[i] = self.data[i]
            i += 1
        return hasil


# --------------------------------------------------------------- linked list
class Simpul:
    def __init__(self, nilai):
        self.nilai = nilai
        self.berikut = None
        self.sebelum = None


class LinkedList:
    """Senarai bertaut ganda. Penyisipan/penghapusan butuh penelusuran O(n)."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, nilai):
        simpul = Simpul(nilai)
        if self.tail is None:
            self.head = simpul
            self.tail = simpul
        else:
            simpul.sebelum = self.tail
            self.tail.berikut = simpul
            self.tail = simpul
        self.size += 1
        return 0

    def _simpul_ke(self, pos):
        simpul = self.head
        i = 0
        while i < pos:
            simpul = simpul.berikut
            i += 1
        return simpul

    def get(self, pos):
        return self._simpul_ke(pos).nilai

    def insert(self, pos, nilai):
        """-> jumlah simpul yang ditelusuri."""
        if pos >= self.size:
            return self.append(nilai)
        simpul = Simpul(nilai)
        if pos == 0:
            simpul.berikut = self.head
            self.head.sebelum = simpul
            self.head = simpul
        else:
            tujuan = self._simpul_ke(pos)
            sebelumnya = tujuan.sebelum
            simpul.sebelum = sebelumnya
            simpul.berikut = tujuan
            sebelumnya.berikut = simpul
            tujuan.sebelum = simpul
        self.size += 1
        return pos

    def hapus(self, pos):
        """-> (rekaman, jumlah simpul yang ditelusuri)."""
        tujuan = self._simpul_ke(pos)
        rekaman = tujuan.nilai
        sebelum = tujuan.sebelum
        sesudah = tujuan.berikut
        if sebelum is None:
            self.head = sesudah
        else:
            sebelum.berikut = sesudah
        if sesudah is None:
            self.tail = sebelum
        else:
            sesudah.sebelum = sebelum
        self.size -= 1
        return rekaman, pos

    def ke_larik(self):
        hasil = [None] * self.size
        simpul = self.head
        i = 0
        while simpul is not None:
            hasil[i] = simpul.nilai
            simpul = simpul.berikut
            i += 1
        return hasil


# --------------------------------------------------------------- data pesanan
class DataPesanan:
    def __init__(self):
        self.array = Array()
        self.linked = LinkedList()
        self.nomor_array = 0        # pencacah oid berikutnya

    def struktur(self, nama):
        return self.array if nama == "array" else self.linked

    def muat(self, larik):
        i = 0
        while i < len(larik):
            self.array.append(larik[i])
            self.linked.append(larik[i])
            i += 1
        self.nomor_array = len(larik)

    # ------------------------------------------------------------- pembuatan
    def buat_baru(self, nama, prioritas=3, resto="2EZ4U", menu="Pesanan Baru",
                  harga=0):
        self.nomor_array += 1
        rekaman = (format_oid(self.nomor_array), nama, resto, menu, harga,
                   prioritas, jam_sekarang(), BELUM, "ANTRE")
        return rekaman

    def sisip_pada(self, nama_struktur, pos, rekaman):
        if nama_struktur == "array":
            return self.array.insert(pos, rekaman)
        return self.linked.insert(pos, rekaman)

    # ------------------------------------------------------------- operasi M1
    def tambah(self, nama_struktur, jenis, nama):
        prioritas = jenis_prioritas(jenis)
        rekaman = self.buat_baru(nama, prioritas)
        struktur = self.struktur(nama_struktur)
        pos = posisi_prioritas(prioritas, struktur.size)
        biaya = self.sisip_pada(nama_struktur, pos, rekaman)
        return rekaman, pos, biaya

    def hapus_pada(self, nama_struktur, pos):
        if nama_struktur == "array":
            rekaman = self.array.get(pos)
            biaya = self.array.hapus(pos)
        else:
            rekaman, biaya = self.linked.hapus(pos)
        return rekaman, biaya

    def lihat(self, nama_struktur, awal, jumlah):
        """-> (Array berisi salinan potongan, biaya penelusuran)."""
        potongan = Array()
        if nama_struktur == "array":
            batas = awal + jumlah
            if batas > self.array.size:
                batas = self.array.size
            i = awal
            while i < batas:
                potongan.append(self.array.data[i])
                i += 1
            return potongan, 0
        simpul = self.linked._simpul_ke(awal)
        i = awal
        batas = awal + jumlah
        while simpul is not None and i < batas:
            potongan.append(simpul.nilai)
            simpul = simpul.berikut
            i += 1
        return potongan, awal


# --------------------------------------------------------------- pembacaan CSV
def _pecah(baris):
    """Pemecah koma sederhana (medan tidak mengandung koma)."""
    bagian = []
    mulai = 0
    i = 0
    while i < len(baris):
        if baris[i] == ",":
            bagian.append(baris[mulai:i])
            mulai = i + 1
        i += 1
    bagian.append(baris[mulai:])
    return bagian


def muat_pesanan(path):
    """Membaca pesanan.csv menjadi larik tuple rekaman."""
    berkas = open(path, "r", encoding="utf-8")
    larik = []
    pertama = True
    for baris in berkas:
        panjang = len(baris)
        while panjang > 0 and (baris[panjang - 1] == "\n" or baris[panjang - 1] == "\r"):
            panjang -= 1
        if panjang == 0:
            continue
        baris = baris[:panjang]
        if pertama:
            pertama = False
            continue
        bagian = _pecah(baris)
        larik.append((bagian[0], bagian[1], bagian[2], bagian[3],
                      int(bagian[4]), int(bagian[5]), int(bagian[6]),
                      int(bagian[7]), bagian[8]))
    berkas.close()
    return larik
