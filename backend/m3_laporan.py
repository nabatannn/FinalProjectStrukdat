def insertion_sort(A, kunci, pencacah=None):
    """Di tempat, stabil (geser hanya bila LEBIH BESAR, bukan >=). O(n^2)."""
    banding = 0
    pindah = 0
    for i in range(1, len(A)):
        x = A[i]
        kx = x[kunci]
        j = i - 1
        while j >= 0:
            banding += 1
            if A[j][kunci] > kx:
                A[j + 1] = A[j]
                pindah += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            A[j + 1] = x
            pindah += 1
    if pencacah is not None:
        pencacah.banding += banding
        pencacah.pindah += pindah
    return A


def merge_sort(A, kunci, pencacah=None):
    """Stabil, O(n log n), memakai petak bantu. Mengembalikan A (terurut di tempat)."""
    n = len(A)
    if n < 2:
        return A
    bantu = [None] * n
    hit = [0, 0]                     # [perbandingan, pemindahan]
    _belah(A, bantu, 0, n, kunci, hit)
    if pencacah is not None:
        pencacah.banding += hit[0]
        pencacah.pindah += hit[1]
    return A


def _belah(A, bantu, lo, hi, kunci, hit):
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _belah(A, bantu, lo, mid, kunci, hit)
    _belah(A, bantu, mid, hi, kunci, hit)
    i = lo
    j = mid
    k = lo
    banding = 0
    while i < mid and j < hi:
        banding += 1
        if A[j][kunci] < A[i][kunci]:   # kanan duluan hanya bila STRIKT lebih kecil -> stabil
            bantu[k] = A[j]
            j += 1
        else:
            bantu[k] = A[i]
            i += 1
        k += 1
    while i < mid:                       # sisa bagian kiri
        bantu[k] = A[i]
        i += 1
        k += 1
    while j < hi:                        # sisa bagian kanan
        bantu[k] = A[j]
        j += 1
        k += 1
    for t in range(lo, hi):
        A[t] = bantu[t]
    hit[0] += banding
    hit[1] += 2 * (hi - lo)


def linear_search(A, target, kunci=0, pencacah=None):
    """O(n). Mengembalikan indeks atau -1."""
    banding = 0
    hasil = -1
    for i in range(len(A)):
        banding += 1
        if A[i][kunci] == target:
            hasil = i
            break
    if pencacah is not None:
        pencacah.banding += banding
    return hasil


def binary_search(A, target, kunci=0, pencacah=None):
    """O(log n); A WAJIB terurut menurut `kunci`. Indeks atau -1."""
    lo = 0
    hi = len(A) - 1
    banding = 0
    hasil = -1
    while lo <= hi:                      # <= , bukan <
        mid = (lo + hi) // 2
        banding += 1
        v = A[mid][kunci]
        if v == target:
            hasil = mid
            break
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    if pencacah is not None:
        pencacah.banding += banding
    return hasil


def batas_bawah(A, target, kunci=0, pencacah=None):
    """Indeks pertama dengan A[i][kunci] >= target (len(A) bila tidak ada)."""
    lo = 0
    hi = len(A)
    banding = 0
    while lo < hi:
        mid = (lo + hi) // 2
        banding += 1
        if A[mid][kunci] < target:
            lo = mid + 1
        else:
            hi = mid
    if pencacah is not None:
        pencacah.banding += banding
    return lo


def terurut(A, kunci):
    for i in range(1, len(A)):
        if A[i - 1][kunci] > A[i][kunci]:
            return False
    return True
