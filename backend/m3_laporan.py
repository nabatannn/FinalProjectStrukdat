"""M3 - Pengurutan dan pencarian pada rekaman pesanan.

Rekaman diurutkan menurut salah satu kolom:
  0 -> oid (teks), 4 -> harga (bilangan), 7 -> selesai (waktu).
Semua algoritma menghitung perbandingan lewat objek Pencacah.
"""


class Pencacah:
    """Menghitung jumlah perbandingan dan pemindahan sebuah algoritma."""

    def __init__(self):
        self.banding = 0
        self.pindah = 0

    def bandingkan(self):
        self.banding += 1

    def pindahkan(self):
        self.pindah += 1


def insertion_sort(A, kunci, pencacah=None):
    """Insertion sort in-place dan stabil. O(n^2)."""
    n = len(A)
    i = 1
    while i < n:
        nilai = A[i]
        j = i - 1
        while j >= 0:
            if pencacah is not None:
                pencacah.bandingkan()
            if A[j][kunci] > nilai[kunci]:
                A[j + 1] = A[j]
                if pencacah is not None:
                    pencacah.pindahkan()
                j -= 1
            else:
                break
        if j + 1 != i:
            A[j + 1] = nilai
            if pencacah is not None:
                pencacah.pindahkan()
        i += 1


def selection_sort(A, kunci, pencacah=None):
    """Selection sort in-place, O(n^2), TIDAK stabil."""
    n = len(A)
    i = 0
    while i < n - 1:
        terkecil = i
        j = i + 1
        while j < n:
            if pencacah is not None:
                pencacah.bandingkan()
            if A[j][kunci] < A[terkecil][kunci]:
                terkecil = j
            j += 1
        if terkecil != i:
            A[i], A[terkecil] = A[terkecil], A[i]
            if pencacah is not None:
                pencacah.pindahkan()
        i += 1


def bubble_sort(A, kunci, pencacah=None):
    """Bubble sort in-place, stabil, O(n^2). Berhenti dini bila sudah terurut."""
    n = len(A)
    i = 0
    while i < n - 1:
        tukar = False
        j = 0
        batas = n - 1 - i
        while j < batas:
            if pencacah is not None:
                pencacah.bandingkan()
            if A[j][kunci] > A[j + 1][kunci]:
                A[j], A[j + 1] = A[j + 1], A[j]
                if pencacah is not None:
                    pencacah.pindahkan()
                tukar = True
            j += 1
        if not tukar:
            break
        i += 1


def _median_ke_depan(A, rendah, tinggi, kunci, pencacah):
    """Taruh median dari A[rendah], A[tengah], A[tinggi] ke posisi rendah."""
    tengah = (rendah + tinggi) // 2
    if pencacah is not None:
        pencacah.bandingkan()
    if A[tengah][kunci] < A[rendah][kunci]:
        A[tengah], A[rendah] = A[rendah], A[tengah]
    if pencacah is not None:
        pencacah.bandingkan()
    if A[tinggi][kunci] < A[rendah][kunci]:
        A[tinggi], A[rendah] = A[rendah], A[tinggi]
    if pencacah is not None:
        pencacah.bandingkan()
    if A[tinggi][kunci] < A[tengah][kunci]:
        A[tinggi], A[tengah] = A[tengah], A[tinggi]
    A[tengah], A[rendah] = A[rendah], A[tengah]


def _quick(A, rendah, tinggi, kunci, pencacah):
    """Partisi ala Hoare; rekursi pada sisi lebih kecil agar kedalaman O(log n)."""
    while rendah < tinggi:
        _median_ke_depan(A, rendah, tinggi, kunci, pencacah)
        pivot = A[rendah][kunci]
        i = rendah + 1
        j = tinggi
        while True:
            while i <= j:
                if pencacah is not None:
                    pencacah.bandingkan()
                if A[i][kunci] < pivot:
                    i += 1
                else:
                    break
            while i <= j:
                if pencacah is not None:
                    pencacah.bandingkan()
                if A[j][kunci] > pivot:
                    j -= 1
                else:
                    break
            if i > j:
                break
            A[i], A[j] = A[j], A[i]
            if pencacah is not None:
                pencacah.pindahkan()
            i += 1
            j -= 1
        A[rendah], A[j] = A[j], A[rendah]
        if pencacah is not None:
            pencacah.pindahkan()
        if j - rendah < tinggi - j:
            _quick(A, rendah, j - 1, kunci, pencacah)
            rendah = j + 1
        else:
            _quick(A, j + 1, tinggi, kunci, pencacah)
            tinggi = j - 1


def quick_sort(A, kunci, pencacah=None):
    """Quick sort rata-rata O(n log n); pivot median-of-three, partisi Hoare."""
    if len(A) > 1:
        _quick(A, 0, len(A) - 1, kunci, pencacah)


def _gabung(A, tmp, kiri, tengah, kanan, kunci, pencacah):
    i = kiri
    j = tengah
    k = kiri
    while i < tengah and j < kanan:
        if pencacah is not None:
            pencacah.bandingkan()
        if A[i][kunci] <= A[j][kunci]:
            tmp[k] = A[i]
            i += 1
        else:
            tmp[k] = A[j]
            j += 1
        if pencacah is not None:
            pencacah.pindahkan()
        k += 1
    while i < tengah:
        tmp[k] = A[i]
        i += 1
        k += 1
        if pencacah is not None:
            pencacah.pindahkan()
    while j < kanan:
        tmp[k] = A[j]
        j += 1
        k += 1
        if pencacah is not None:
            pencacah.pindahkan()
    t = kiri
    while t < kanan:
        A[t] = tmp[t]
        t += 1


def _urutkan(A, tmp, kiri, kanan, kunci, pencacah):
    if kanan - kiri < 2:
        return
    tengah = (kiri + kanan) // 2
    _urutkan(A, tmp, kiri, tengah, kunci, pencacah)
    _urutkan(A, tmp, tengah, kanan, kunci, pencacah)
    _gabung(A, tmp, kiri, tengah, kanan, kunci, pencacah)


def merge_sort(A, kunci, pencacah=None):
    """Merge sort divide-and-conquer dan stabil. O(n log n)."""
    n = len(A)
    if n < 2:
        return
    tmp = [None] * n
    _urutkan(A, tmp, 0, n, kunci, pencacah)


def linear_search(A, oid, awal=0, pencacah=None):
    """Pencarian linear dari awal. -> indeks atau -1."""
    i = awal
    n = len(A)
    while i < n:
        if pencacah is not None:
            pencacah.bandingkan()
        if A[i][0] == oid:
            return i
        i += 1
    return -1


def binary_search(A, oid, awal=0, pencacah=None):
    """Pencarian biner pada larik yang sudah terurut menurut oid. -> indeks atau -1."""
    kiri = awal
    kanan = len(A) - 1
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        if pencacah is not None:
            pencacah.bandingkan()
        if A[tengah][0] == oid:
            return tengah
        if pencacah is not None:
            pencacah.bandingkan()
        if A[tengah][0] < oid:
            kiri = tengah + 1
        else:
            kanan = tengah - 1
    return -1


def terurut(A, kunci):
    """Memeriksa apakah A tidak menurun menurut kunci."""
    i = 1
    while i < len(A):
        if A[i - 1][kunci] > A[i][kunci]:
            return False
        i += 1
    return True
