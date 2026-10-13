"""Pengontrol: menjembatani menu UI dengan backend M1-M3.

Tidak ada kode Tkinter di sini, jadi seluruh alur bisa diuji dari terminal
(lihat tools/transkrip.py dan tests/). UI hanya menampilkan `Hasil`.
"""
import os

from backend.util import (BELUM, NAMA_PRIORITAS,
                          Pencacah, fmt_int, fmt_jam, fmt_ms,
                          fmt_rp, mulai, selesai_ms)
from backend.m1_pesanan import Array, DataPesanan, muat_pesanan
from backend.m2_antrean import (KesalahanEkspresi, LayananAntrean, hitung,
                                ke_postfix)
from backend.m3_laporan import (binary_search, insertion_sort, linear_search,
                                merge_sort, terurut)

BATAS_INSERTION = 20000
BARIS_TAMPIL = 200

KOLOM_REKAMAN = ("#", "oid", "pelanggan", "resto", "menu", "harga",
                 "prio", "masuk", "selesai", "status")


def kolom_sort(nama):
    if nama == "oid":
        return 0
    if nama == "harga":
        return 4
    return 7


class Hasil:
    def __init__(self, judul=""):
        self.judul = judul
        self.ringkasan = []        # baris teks di atas tabel
        self.kolom = ()
        self.baris = []            # larik tuple string
        self.catatan = ""
        self.modul = ""            # mis. "M2 - queue naif"
        self.ms = 0.0
        self.galat = False
        self.perintah = ""         # teks untuk panel COMMAND


class Param:
    def __init__(self, kode, label, default="", hint="", pilihan=None):
        self.kode = kode
        self.label = label
        self.default = default
        self.hint = hint
        self.pilihan = pilihan


class Menu:
    def __init__(self, grup, label, kunci, judul, deskripsi, params=()):
        self.grup = grup
        self.label = label
        self.kunci = kunci
        self.judul = judul
        self.deskripsi = deskripsi
        self.params = params


P_NAMA = Param("nama", "Nama pelanggan", "Pelanggan Baru", "nama untuk pesanan yang akan dibuat")
P_NOMOR = Param("nomor", "Nomor urut pesanan (mulai 1)", "1", "posisi dalam barisan, bukan oid")


def _ket_jenis(jenis):
    if jenis == "REGULER":
        return "REGULER masuk paling belakang barisan."
    if jenis == "PRIORITAS":
        return "PRIORITAS menyerobot ke tengah barisan."
    return "VIP langsung ke urutan pertama."


def _daftar_menu():
    m = []
    G = "DATA"
    m.append(Menu(G, "Load", "load", "Muat data ke semua struktur",
                  "Membaca pesanan.csv, lalu mengisi array, linked list, dan kedua antrean."))
    for nama, kode in (("ARRAY", "array"), ("LINKEDLIST", "linked")):
        G = "M1 - DATA PESANAN"
        m.append(Menu(G, nama + " - LIHAT PESANAN", "m1_lihat_" + kode,
                      nama.title() + ": lihat pesanan ke-i",
                      "Array membuka langsung lewat indeks, linked list menelusuri simpul satu per satu.",
                      (P_NOMOR, Param("jumlah", "Jumlah baris", "10", "berapa pesanan ditampilkan"))))
        for jenis in ("REGULER", "PRIORITAS", "VIP"):
            m.append(Menu(G, nama + " - TAMBAH PESANAN " + jenis, "m1_tambah_%s_%s" % (kode, jenis),
                          "%s: pesanan %s" % (nama.title(), jenis),
                          _ket_jenis(jenis),
                          (P_NAMA,)))
        m.append(Menu(G, nama + " - HAPUS PESANAN", "m1_hapus_" + kode,
                      nama.title() + ": hapus pesanan ke-i",
                      "Pesanan dicabut dari barisan. Array menggeser sisa, linked list menelusuri lalu menyambung.",
                      (P_NOMOR,)))
    G = "M2 - STACK DAN QUEUE"
    m.append(Menu(G, "STACK - POSTFIX (MESIN KASIR)", "stack_postfix",
                  "Stack: hitung struk lewat postfix",
                  "Struk ditulis infix, lalu dihitung dua tahap dengan stack: tahap 1 infix menjadi postfix, tahap 2 postfix dievaluasi.",
                  (Param("ekspresi", "Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000",
                         "angka, + - * / dan tanda kurung"),)))
    m.append(Menu(G, "STACK - UNDO", "stack_undo", "Stack: batalkan aksi terakhir",
                  "Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya."))
    m.append(Menu(G, "STACK - REDO", "stack_redo", "Stack: kerjakan lagi aksi yang dibatalkan",
                  "Mengambil catatan teratas tumpukan redo, lalu mengerjakan ulang aksi aslinya."))
    m.append(Menu(G, "QUEUE - ENQUEUE", "queue_enqueue", "Queue: pesanan baru masuk ke belakang",
                  "Menambah pesanan di ujung belakang kedua antrean sekaligus.", (P_NAMA,)))
    for nama, kode in (("NAIF", "naif"), ("CIRCULAR", "circular")):
        m.append(Menu(G, "QUEUE - DEQUEUE " + nama, "queue_dequeue_" + kode,
                      "Queue %s: ambil dari depan" % kode,
                      "Versi naif menggeser seluruh isi untuk tiap dequeue." if kode == "naif"
                      else "Versi melingkar hanya memajukan penunjuk front.",
                      (Param("n", "Berapa kali dequeue", "1", "coba 1 lalu 100 untuk melihat bedanya"),)))
    G = "M3 - SORT DAN SEARCH"
    ps = (Param("jumlah", "Jumlah baris diurutkan", "2000", "diambil dari awal data; coba 1.000 lalu 2.000 lalu 4.000"),
          Param("kunci", "Diurutkan menurut", "harga", "oid (teks), harga (angka), selesai (waktu selesai)",
                ("oid", "harga", "selesai")))
    m.append(Menu(G, "SORT - INSERTION SORT", "sort_insertion", "Sort: insertion sort, O(n^2)",
                  "Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik.", ps))
    m.append(Menu(G, "SORT - MERGE SORT", "sort_merge", "Sort: merge sort, O(n log n)",
                  "Larik dibelah dua terus-menerus, lalu potongan yang sudah terurut disatukan kembali.", ps))
    po = (Param("oid", "Nomor pesanan (oid)", "O-137442", "format O-000001 sampai O-200000"),)
    m.append(Menu(G, "SEARCH - LINEAR SEARCH", "search_linear", "Search: linear search, O(n)",
                  "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.", po))
    m.append(Menu(G, "SEARCH - BINARY SEARCH", "search_binary", "Search: binary search, O(log n)",
                  "Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar yang sudah terurut menurut oid.", po))
    return m


def _bulat(teks, nama, minimum=None, maksimum=None):
    t = teks.strip()
    if t == "":
        raise ValueError("%s wajib diisi" % nama)
    n = 0
    negatif = False
    for i in range(len(t)):
        c = t[i]
        if i == 0 and c == "-":
            negatif = True
        elif c == "." and i > 0:
            continue                      # boleh pemisah ribuan: 20.000
        elif "0" <= c <= "9":
            n = n * 10 + (ord(c) - 48)
        else:
            raise ValueError("%s harus berupa bilangan bulat" % nama)
    if negatif:
        n = -n
    if minimum is not None and n < minimum:
        raise ValueError("%s minimal %s" % (nama, fmt_int(minimum)))
    if maksimum is not None and n > maksimum:
        raise ValueError("%s maksimal %s" % (nama, fmt_int(maksimum)))
    return n


def _cek_oid(teks):
    t = teks.strip().upper()
    ok = len(t) == 8 and t[0] == "O" and t[1] == "-"
    if ok:
        for c in t[2:]:
            if not ("0" <= c <= "9"):
                ok = False
    if not ok:
        raise ValueError("format oid harus O-000001 sampai O-200000")
    return t


def _baris_rekaman(no, r):
    return (str(no), r[0], r[1], r[2], r[3], fmt_int(r[4]), str(r[5]),
            fmt_jam(r[6]), fmt_jam(r[7]), r[8])


def _detail(rec):
    return [("oid", rec[0]), ("pelanggan", rec[1]), ("resto", rec[2]), ("menu", rec[3]),
            ("harga", fmt_int(rec[4])), ("prioritas", str(rec[5]) + " (" + NAMA_PRIORITAS[rec[5]] + ")"),
            ("masuk", fmt_jam(rec[6])), ("selesai", fmt_jam(rec[7]) if rec[7] < BELUM else "-"),
            ("status", rec[8])]


class Aplikasi:
    def __init__(self, folder_data):
        self.folder = folder_data
        self.menu = _daftar_menu()
        self.dimuat = False
        self.data = None
        self.antrean = None
        self.versi = 0                 # naik tiap kali M1 berubah (cache dibuang)
        self._snap = None
        self._snap_versi = -1
        self._urut_oid = None
        self._urut_versi = -1
        self.log = []                  # panel COMMAND: tuple (perintah, modul, ms)

    # ------------------------------------------------------------ dasar
    def cari_menu(self, kunci):
        for i in range(len(self.menu)):
            if self.menu[i].kunci == kunci:
                return self.menu[i]
        raise KeyError(kunci)

    def jalankan(self, kunci, nilai):
        """`nilai` = tuple string sesuai urutan Menu.params. -> Hasil."""
        m = self.cari_menu(kunci)
        h = Hasil(m.judul)
        try:
            if kunci != "load" and not self.dimuat:
                raise ValueError("Data belum dimuat. Jalankan menu DATA > Load dulu.")
            fungsi = getattr(self, "_h_" + self._nama_handler(kunci))
            fungsi(h, kunci, nilai)
        except (ValueError, IndexError, KeyError, KesalahanEkspresi) as e:
            h.galat = True
            pesan = e.args[0] if len(e.args) > 0 else "kesalahan"
            h.ringkasan = [str(pesan) if str(pesan)[:7] == "DITOLAK" else "GAGAL: " + str(pesan)]
            h.kolom = ()
            h.baris = []
            if h.modul == "":
                h.modul = "-"
        teks = kunci
        for i in range(len(nilai)):
            teks += "  " + nilai[i]
        h.perintah = teks
        self.log.append((teks, h.modul, h.ms))
        return h

    @staticmethod
    def _nama_handler(kunci):
        if kunci[:8] == "m1_lihat":
            return "m1_lihat"
        if kunci[:9] == "m1_tambah":
            return "m1_tambah"
        if kunci[:8] == "m1_hapus":
            return "m1_hapus"
        if kunci[:14] == "queue_dequeue_":
            return "queue_dequeue"
        return kunci

    def _akhir_m1(self):
        self.versi += 1

    def _snapshot(self):
        """Larik terpadat dari array M1 (tanpa ruang cadangan), di-cache per versi."""
        if self._snap_versi != self.versi or self._snap is None:
            self._snap = self.data.array.ke_larik()
            self._snap_versi = self.versi
        return self._snap

    def _tabel_rekaman(self, h, larik, batas=BARIS_TAMPIL):
        h.kolom = KOLOM_REKAMAN
        n = len(larik)
        tampil = n if n < batas else batas
        baris = []
        for i in range(tampil):
            baris.append(_baris_rekaman(i + 1, larik[i]))
        if n > tampil:
            h.catatan = "Menampilkan %s dari %s baris." % (fmt_int(tampil), fmt_int(n))
        h.baris = baris

    def _panjang_antrean(self):
        return "Panjang antrean sekarang: naif %s, circular %s." % (
            fmt_int(len(self.antrean.naif)), fmt_int(len(self.antrean.melingkar)))

    def _undo_redo_teks(self):
        return "Tumpukan undo %d, redo %d." % (self.antrean.undo.ukuran(), self.antrean.redo.ukuran())

    # ------------------------------------------------------------- DATA
    def _h_load(self, h, kunci, nilai):
        t0 = mulai()
        larik = muat_pesanan(os.path.join(self.folder, "pesanan.csv"))
        t_csv = selesai_ms(t0)
        t1 = mulai()
        self.data = DataPesanan()
        self.data.muat(larik)
        t_m1 = selesai_ms(t1)
        t2 = mulai()
        self.antrean = LayananAntrean(self.data)
        self.antrean.isi(larik, self.data.nomor_array)
        t_q = selesai_ms(t2)
        self._urut_oid = None
        self.versi += 1
        self.dimuat = True
        antre = self.antrean.melingkar.count
        h.modul = "M1 - larik"
        h.ms = selesai_ms(t0)
        h.ringkasan = [
            "%s pesanan dimuat ke array dan linked list; %s berstatus ANTRE masuk ke kedua antrean." % (
                fmt_int(len(larik)), fmt_int(antre))]
        h.kolom = ("tahap", "waktu")
        h.baris = [("baca CSV menjadi larik", fmt_ms(t_csv)),
                   ("isi array + linked list", fmt_ms(t_m1)),
                   ("isi antrean naif + melingkar", fmt_ms(t_q))]
        a = self.data.array
        h.catatan = "Array tumbuh %d kali (kapasitas akhir %s, %s elemen disalin; amortized O(1) per append)." % (
            a.jumlah_tumbuh, fmt_int(a.kapasitas), fmt_int(a.salinan))

    # --------------------------------------------------------------- M1
    def _struktur_dari(self, kunci):
        return "array" if "array" in kunci else "linked"

    def _h_m1_lihat(self, h, kunci, nilai):
        s = self._struktur_dari(kunci)
        n = _bulat(nilai[0], "Nomor pesanan", 1, self.data.struktur(s).size)
        jml = _bulat(nilai[1], "Jumlah baris", 1, 500)
        t0 = mulai()
        arr, biaya = self.data.lihat(s, n - 1, jml)
        h.ms = selesai_ms(t0)
        h.modul = "M1 - " + s
        h.ringkasan = ["Pesanan ke-%s dan %d berikutnya dibuka dari %s (isi %s pesanan)." % (
            fmt_int(n), arr.size - 1, "array" if s == "array" else "linked list",
            fmt_int(self.data.struktur(s).size))]
        if s == "array":
            h.ringkasan.append("Akses langsung lewat indeks: O(1) untuk menuju posisi pertama.")
        else:
            h.ringkasan.append("%s simpul harus dilewati dari head untuk sampai ke posisi %s: O(n)." % (
                fmt_int(biaya), fmt_int(n)))
        h.kolom = KOLOM_REKAMAN
        baris = []
        for i in range(arr.size):
            baris.append(_baris_rekaman(n + i, arr.data[i]))
        h.baris = baris
        h.catatan = "Bandingkan waktu menu ARRAY dan LINKEDLIST pada nomor urut besar, misalnya 150.000."

    def _h_m1_tambah(self, h, kunci, nilai):
        s = self._struktur_dari(kunci)
        jenis = kunci[kunci.rfind("_") + 1:]
        nama = nilai[0].strip()
        if nama == "":
            raise ValueError("Nama pelanggan wajib diisi")
        t0 = mulai()
        rec, pos, biaya = self.data.tambah(s, jenis, nama)
        h.ms = selesai_ms(t0)
        self.antrean.catat_m1("ORDER", s, pos, rec)
        self._akhir_m1()
        h.modul = "M1 - " + s
        total = self.data.struktur(s).size
        h.ringkasan = ["%s masuk sebagai %s di posisi %s dari %s." % (
            rec[0], jenis, fmt_int(pos + 1), fmt_int(total))]
        if s == "array":
            h.ringkasan.append("%s elemen digeser." % fmt_int(biaya))
        else:
            h.ringkasan.append("%s simpul ditelusuri sebelum menyambung." % fmt_int(biaya))
        h.ringkasan.append(self._undo_redo_teks() + " (bisa dibatalkan lewat STACK - UNDO)")
        h.kolom = ("kolom", "isi")
        h.baris = _detail(rec)

    def _h_m1_hapus(self, h, kunci, nilai):
        s = self._struktur_dari(kunci)
        n = _bulat(nilai[0], "Nomor pesanan", 1, self.data.struktur(s).size)
        t0 = mulai()
        rec, biaya = self.data.hapus_pada(s, n - 1)
        h.ms = selesai_ms(t0)
        self.antrean.catat_m1("HAPUS", s, n - 1, rec)
        self._akhir_m1()
        h.modul = "M1 - " + s
        h.ringkasan = ["%s (urutan ke-%s) dicabut dari %s." % (rec[0], fmt_int(n), s),
                       ("%s elemen digeser." if s == "array" else "%s simpul ditelusuri.") % fmt_int(biaya),
                       "Sisa %s pesanan. " % fmt_int(self.data.struktur(s).size) + self._undo_redo_teks()]
        h.kolom = ("kolom", "isi")
        h.baris = _detail(rec)

    # --------------------------------------------------------------- M2
    def _h_stack_postfix(self, h, kunci, nilai):
        teks = nilai[0]
        t0 = mulai()
        pf, jejak1 = ke_postfix(teks)
        total, jejak2 = hitung(pf)
        h.ms = selesai_ms(t0)
        h.modul = "M2 - stack"
        pf_teks = ""
        for i in range(len(pf)):
            pf_teks += (" " if i else "") + pf[i]
        h.ringkasan = ["Struk : " + teks.strip(), "Postfix: " + pf_teks, "TOTAL : " + fmt_rp(total)]
        h.kolom = ("langkah", "token", "tindakan", "stack", "output")
        baris = []
        for r in jejak1:
            baris.append(r)
        for r in jejak2:
            baris.append((r[0], r[1], r[2], r[3], ""))
        h.baris = baris
        h.catatan = ("Baris 1.x tahap konversi, baris 2.x tahap evaluasi. Tanda ( hanya mengatur stack dan "
                     "tidak pernah muncul di output. Operand kanan selalu keluar lebih dulu.")

    def _tampil_aksi(self, h, a, pesan):
        h.ringkasan = [pesan, self._panjang_antrean(), self._undo_redo_teks()]
        h.kolom = ("#", "oid", "pelanggan", "resto", "menu")
        baris = []
        tampil = len(a.daftar) if len(a.daftar) < BARIS_TAMPIL else BARIS_TAMPIL
        for i in range(tampil):
            r = a.daftar[i]
            baris.append((str(i + 1), r[0], r[1], r[2], r[3]))
        h.baris = baris
        if len(a.daftar) > tampil:
            h.catatan = "Menampilkan %d dari %d pesanan." % (tampil, len(a.daftar))

    def _h_stack_undo(self, h, kunci, nilai):
        t0 = mulai()
        r = self.antrean.undo_last()
        h.ms = selesai_ms(t0)
        h.modul = "M2 - stack"
        if r is None:
            h.ringkasan = ["Tidak ada aksi yang bisa dibatalkan.", self._undo_redo_teks()]
            return
        self._akhir_m1()
        self._tampil_aksi(h, r[0], r[1])
        h.catatan = "Kebalikan dari aksi dijalankan; catatan pindah ke tumpukan redo."

    def _h_stack_redo(self, h, kunci, nilai):
        t0 = mulai()
        r = self.antrean.redo_last()
        h.ms = selesai_ms(t0)
        h.modul = "M2 - stack"
        if r is None:
            h.ringkasan = ["Tumpukan redo kosong, tidak ada yang diulang.", self._undo_redo_teks()]
            return
        self._akhir_m1()
        self._tampil_aksi(h, r[0], r[1])
        h.catatan = "Redo mengerjakan ULANG aksi aslinya, bukan kebalikannya. Aksi baru apa pun mengosongkan redo."

    def _h_queue_enqueue(self, h, kunci, nilai):
        nama = nilai[0].strip()
        if nama == "":
            raise ValueError("Nama pelanggan wajib diisi")
        t0 = mulai()
        rec = self.antrean.enqueue(nama)
        h.ms = selesai_ms(t0)
        h.modul = "M2 - queue"
        h.ringkasan = ["%s masuk ke barisan paling belakang pada KEDUA antrean." % rec[0],
                       self._panjang_antrean(), self._undo_redo_teks()]
        h.kolom = ("kolom", "isi")
        h.baris = _detail(rec)
        h.catatan = "enqueue menempel di belakang, jadi O(1) pada kedua versi. Perbedaannya baru muncul saat dequeue."

    def _h_queue_dequeue(self, h, kunci, nilai):
        varian = "naif" if kunci.endswith("naif") else "circular"
        q = self.antrean.naif if varian == "naif" else self.antrean.melingkar
        n = _bulat(nilai[0], "Jumlah dequeue", 1, 100000)
        if len(q) == 0:
            raise ValueError("Antrean kosong")
        t0 = mulai()
        daftar, geser = self.antrean.dequeue(varian, n)
        h.ms = selesai_ms(t0)
        h.modul = "M2 - queue " + varian
        k = len(daftar)
        h.ringkasan = ["%s pesanan keluar dari depan antrean %s." % (fmt_int(k), varian)]
        if varian == "naif":
            rata = geser // k if k else 0
            h.ringkasan.append("Total %s elemen digeser, rata-rata %s geseran per dequeue." % (
                fmt_int(geser), fmt_int(rata)))
            h.catatan = "pop(0) memaksa seluruh sisa isi bergeser satu petak ke kiri, jadi O(n) per dequeue."
        else:
            q2 = self.antrean.melingkar
            h.ringkasan.append("Tidak ada elemen yang digeser. front sekarang %s, rear %s, kapasitas %s." % (
                fmt_int(q2.front), fmt_int(q2.rear), fmt_int(q2.K)))
            h.catatan = "Hanya penunjuk front yang maju; isi larik tidak disentuh, jadi O(1)."
        h.ringkasan.append("Sisa antrean %s: %s. %s" % (varian, fmt_int(len(q)), self._undo_redo_teks()))
        h.kolom = ("#", "oid", "pelanggan", "resto", "menu", "masuk")
        baris = []
        tampil = k if k < BARIS_TAMPIL else BARIS_TAMPIL
        for i in range(tampil):
            r = daftar[i]
            baris.append((str(i + 1), r[0], r[1], r[2], r[3], fmt_jam(r[6])))
        h.baris = baris

    # --------------------------------------------------------------- M3
    def _h_sort(self, h, nilai, algoritma):
        total = self.data.array.size
        n = _bulat(nilai[0], "Jumlah baris", 1, total)
        nama_kunci = nilai[1].strip()
        if nama_kunci not in ("oid", "harga", "selesai"):
            raise ValueError("Kunci harus oid, harga, atau selesai")
        kunci = kolom_sort(nama_kunci)
        if algoritma == "insertion" and n > BATAS_INSERTION:
            h.modul = "M3 - insertion sort"
            raise ValueError("DITOLAK: batasnya %s baris, pakai merge sort untuk data besar." % fmt_int(BATAS_INSERTION))
        sumber = self._snapshot()
        A = [None] * n
        for i in range(n):
            A[i] = sumber[i]
        c = Pencacah()
        t0 = mulai()
        if algoritma == "insertion":
            insertion_sort(A, kunci, c)
        else:
            merge_sort(A, kunci, c)
        h.ms = selesai_ms(t0)
        h.modul = "M3 - " + ("insertion sort" if algoritma == "insertion" else "merge sort")
        h.ringkasan = ["%s pesanan diurutkan menurut %s." % (fmt_int(n), nama_kunci),
                       "%s perbandingan, %s pemindahan." % (fmt_int(c.banding), fmt_int(c.pindah)),
                       "Urutan terverifikasi: " + ("ya" if terurut(A, kunci) else "TIDAK")]
        self._tabel_rekaman(h, A)
        if algoritma == "insertion":
            h.catatan = ("Menggeser hanya bila LEBIH BESAR (>), jadi stabil. Lipatduakan jumlah baris: "
                         "perbandingan naik kira-kira empat kali. Bandingkan dengan SORT - MERGE SORT.")
        else:
            h.catatan = ("Penggabungan memakai <, kiri didahulukan saat kunci sama, jadi stabil. Lipatduakan "
                         "jumlah baris: perbandingan naik sekitar dua kali.")

    def _h_sort_insertion(self, h, kunci, nilai):
        self._h_sort(h, nilai, "insertion")

    def _h_sort_merge(self, h, kunci, nilai):
        self._h_sort(h, nilai, "merge")

    def _h_search_linear(self, h, kunci, nilai):
        oid = _cek_oid(nilai[0])
        A = self._snapshot()
        c = Pencacah()
        t0 = mulai()
        i = linear_search(A, oid, 0, c)
        h.ms = selesai_ms(t0)
        h.modul = "M3 - linear"
        if i < 0:
            h.ringkasan = ["%s tidak ditemukan." % oid,
                           "%s perbandingan: seluruh data diperiksa (kasus terburuk)." % fmt_int(c.banding)]
        else:
            h.ringkasan = ["Ditemukan pada indeks %s." % fmt_int(i),
                           "%s perbandingan." % fmt_int(c.banding)]
            h.kolom = ("kolom", "isi")
            h.baris = _detail(A[i])
        h.catatan = "Data tidak perlu terurut, tetapi setiap pesanan diperiksa satu per satu dari depan."

    def _urut_menurut_oid(self):
        """Daftar terurut oid dibangun sekali (merge sort). -> ms yang terpakai, atau None."""
        if self._urut_oid is not None and self._urut_versi == self.versi:
            return None
        sumber = self._snapshot()
        n = len(sumber)
        B = [None] * n
        for i in range(n):
            B[i] = sumber[i]
        t0 = mulai()
        merge_sort(B, 0)
        ms = selesai_ms(t0)
        self._urut_oid = B
        self._urut_versi = self.versi
        return ms

    def _h_search_binary(self, h, kunci, nilai):
        oid = _cek_oid(nilai[0])
        t0 = mulai()
        ms_bangun = self._urut_menurut_oid()
        t1 = mulai()
        c = Pencacah()
        i = binary_search(self._urut_oid, oid, 0, c)
        h.ms = selesai_ms(t1)
        h.modul = "M3 - binary"
        baris_awal = []
        if ms_bangun is not None:
            baris_awal.append("Daftar terurut oid dibangun sekali dengan merge sort, %s." % fmt_ms(ms_bangun))
        else:
            baris_awal.append("Memakai daftar terurut oid yang sudah dibangun (biaya pembangunan tidak diulang).")
        if i < 0:
            h.ringkasan = baris_awal + ["%s tidak ditemukan, %d perbandingan." % (oid, c.banding)]
        else:
            h.ringkasan = baris_awal + ["Ditemukan pada baris ke-%s dari %s." % (
                fmt_int(i + 1), fmt_int(len(self._urut_oid))),
                "%d perbandingan, bandingkan dengan linear search." % c.banding]
            h.kolom = ("kolom", "isi")
            h.baris = _detail(self._urut_oid[i])
        h.catatan = ("Setiap perbandingan membuang separuh sisa daftar, jadi paling banyak 18 langkah untuk "
                     "200.001 baris. Syaratnya daftar SUDAH terurut menurut kunci yang dicari: di sini terurut menurut oid.")
