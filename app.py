def main():
    try:
        from frontend.ui import jalankan
    except ModuleNotFoundError as e:
        if e.name == "tkinter":
            print("Tkinter tidak ditemukan di Python ini.")
            print("Linux : sudo apt install python3-tk")
            return
        raise
    jalankan()


if __name__ == "__main__":
    main()
