import sys
import os
from PyQt6.QtWidgets import QApplication
from app.gui import MainWindow

def main():
    """
    Fungsi utama untuk menjalankan aplikasi
    """
    # Pastikan folder output ada
    os.makedirs('output', exist_ok=True)
    
    # Buat aplikasi Qt
    app = QApplication(sys.argv)
    
    # Buat dan tampilkan jendela utama
    window = MainWindow()
    window.show()
    
    # Jalankan event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()