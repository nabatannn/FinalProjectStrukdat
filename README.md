2EZ4U Food Delivery Engine (M1 - M3)

Deskripsi Proyek
2EZ4U APP adalah backend engine dan simulasi antarmuka (frontend) untuk aplikasi layanan pesan-antar makanan berbasis Python. Proyek ini dikembangkan secara murni tanpa pustaka/struktur data bawaan seperti dict, set, list.sort(), collections, dll guna menganalisis karakteristik kinerja, kompleksitas waktu, dan memori dari berbagai struktur data dan algoritma dasar. Proyek ini mencakup pengembangan Milestone 1 (M1) hingga Milestone 3 (M3) dari total 6 milestone satu semester.

Arsitektur & Struktur Repositori
- Aplikasi dibangun dengan arsitektur 3-Layer :
1. Data Layer (data/) 
Menampung dataset CSV hingga 200.000 baris

2. Backend Layer (backend/)
Berisi struktur data kustom dan algoritma mandiri

3. Frontend Layer (frontend/ / app.py) 
Antarmuka Tkinter visual untuk eksekusi, benchmark waktu, dan jumlah operasi.2ez4u/


├── README.md
├── app.py                   # Aplikasi Utama 
├── data/
│   ├── pesanan.csv          # Dataset 200.000 data pesanan
│   └── peta.csv             # Data peta lokasi
├── backend/
│   ├── m1_pesanan.py        # M1: Larik Dynamic Array vs Doubly/Singly Linked List
│   ├── m2_antrean.py        # M2: Circular Queue, Naive Queue, Stack Evaluator & Undo/Redo
│   └── m3_laporan.py        # M3: Insertion Sort, Merge Sort, Linear & Binary Search
└── frontend/
    └── ui.py                # Layout & Komponen UI Tkinter


- Fitur & Implementasi Milestone (M1 - M3)
Milestone 1 : Dynamic Array vs. Linked List (m1_pesanan.py)
Mengelola data pesanan yang masuk dengan 3 tingkat prioritas
a. VIP (Prioritas 1): Disisipkan di paling depan.
b. PRIORITAS (Prioritas 2): Disisipkan di tengah barisan.
c. REGULER (Prioritas 3): Disisipkan di paling belakang

Milestone 2 : Stack & Queue System (m2_antrean.py)
1. Mesin Kasir Struk (Infix to Postfix Evaluation)
- Mengubah ekspresi aritmatika infix (misal: (3*12000)+(2*8500)-5000) menjadi Postfix (RPN) menggunakan Stack Operator
- Evaluasi Postfix menggunakan Stack Operand untuk menghasilkan total harga secara tepat.

2. Sistem Undo & Redo (Stack)
- Menerapkan dua tumpukan (Stack Undo dan Stack Redo)
- Setiap aksi pemrosesan (enqueue/dequeue) mendorong aksi ke Undo Stack dan mengosongkan Redo Stack
- Membatal aksi mengembalikan keadaan secara presisi (termasuk urutan pesanan multi-item saat dequeue).

3. Antrean Layanan : Naive Queue vs Circular Queue
- Naive Queue : Dequeue menggunakan pop(0) / penggeseran indeks yang memicu penggeseran elemen sebanyak O(n).
- Circular Queue : Menggunakan dua pointer (front, rear) dan operasi modulo (% K). Memindahkan front tanpa menggeser elemen (O(1)).
- Penanganan Overflow/Underflow : Memanfaatkan variabel pencacah count untuk membedakan kondisi Antrean Kosong (count == 0) dan Antrean Penuh (count == K) saat front == rear.

Milestone 3: Sorting & Searching (m3_laporan.py)
1. Algoritma Pengurutan (Sorting) - berbagai macam jenis sort
- Insertion Sort (O(n^2)): In-place dan stabil. Optimal untuk data kecil atau hampir terurut.
- Selection Sort (O(n^2)): Memilih elemen terkecil tiap putaran. Perbandingan selalu n(n-1)/2 dan tidak stabil.
- Bubble Sort (O(n^2)): Menukar pasangan bersebelahan, stabil, dan berhenti dini saat data sudah rapi.
- Merge Sort (O(n log n)): Divide and conquer, stabil, mampu menangani hingga 200.000 data.
- Quick Sort (rata-rata O(n log n)): Partisi tiga arah dengan pivot median-of-three, tahan terhadap data berduplikat.
- Algoritma kuadratik (insertion/selection/bubble) menolak dataset > 20.000 baris untuk mencegah sistem freeze; gunakan Merge/Quick Sort untuk data besar.

2. Algoritma Pencarian (Searching)
- Linear Search (O(n)) : Menelusuri seluruh data satu per satu tanpa syarat urutan.
- Binary Search (O(\log n)) : Mengharuskan data terurut terlebih dahulu berdasarkan kunci pencarian (oid).


Aturan Main & Kepatuhan Kode
- Tidak menggunakan fungsi instan/built-in: dict, set, .sort(), sorted(), heapq, bisect, collections
- Tidak menggunakan comprehension dict/set
- Struktur data backend murni menggunakan representasi array primitif / class kustom.
- Menampilkan jumlah perbandingan (bukan hanya durasi waktu) pada algoritma sort dan search.

Cara Menjalankan Aplikasi
1. Pastikan Python 3.11+ telah terinstal dalam sistem
2. Clone repository ke dalam komputer
3. Navigasi menuju folder root directory 2EZ4U pada terminal/command prompt
4. Jalankan aplikasi utama melalui terminal/command prompt menggunakan perintah: python3 app.py


Navigasi UI
- Klik tombol LOAD untuk memuat dataset CSV
- Gunakan menu navigasi di panel kiri untuk menguji fitur M1, M2, dan M3
- Amati hasil operasi, jumlah geseran/perbandingan, dan waktu eksekusi pada log command di bagian bawah