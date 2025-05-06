import os
import pytesseract
import pandas as pd
from PIL import Image

class OCREngine:
    """
    Kelas untuk menangani operasi OCR menggunakan Tesseract
    """
    
    def __init__(self, tesseract_cmd=None):
        """
        Inisialisasi OCR Engine
        
        Args:
            tesseract_cmd (str, optional): Path ke executable tesseract.
                                          Default None akan menggunakan path sistem.
        """
        # Konfigurasi path Tesseract jika disediakan
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        # Coba deteksi Tesseract
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Peringatan: Tesseract tidak terdeteksi. Error: {str(e)}")
            print("Pastikan Tesseract OCR terinstal dan tersedia di PATH sistem.")
    
    def image_to_text(self, image_path, lang='eng', config=''):
        """
        Mengkonversi gambar ke teks menggunakan Tesseract OCR
        
        Args:
            image_path (str): Path ke file gambar
            lang (str): Kode bahasa untuk OCR (default: 'eng')
            config (str): Konfigurasi tambahan untuk Tesseract
            
        Returns:
            str: Teks hasil OCR
        """
        try:
            # Buka gambar dengan PIL
            image = Image.open(image_path)
            
            # Jalankan OCR
            text = pytesseract.image_to_string(image, lang=lang, config=config)
            
            return text
        except Exception as e:
            raise Exception(f"Error saat menjalankan OCR: {str(e)}")
    
    def image_to_data(self, image_path, lang='eng', config=''):
        """
        Mengekstrak data terstruktur dari gambar
        
        Args:
            image_path (str): Path ke file gambar
            lang (str): Kode bahasa untuk OCR (default: 'eng')
            config (str): Konfigurasi tambahan untuk Tesseract
            
        Returns:
            DataFrame: Data terstruktur hasil OCR
        """
        try:
            # Buka gambar dengan PIL
            image = Image.open(image_path)
            
            # Jalankan OCR dengan output data
            data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DATAFRAME)
            
            # Filter baris yang memiliki teks
            if not data.empty:
                data = data.dropna(subset=['text']).reset_index(drop=True)
            
            return data
        except Exception as e:
            raise Exception(f"Error saat mengekstrak data: {str(e)}")
    
    def image_to_boxes(self, image_path, lang='eng', config=''):
        """
        Mendapatkan kotak pembatas karakter dari gambar
        
        Args:
            image_path (str): Path ke file gambar
            lang (str): Kode bahasa untuk OCR (default: 'eng')
            config (str): Konfigurasi tambahan untuk Tesseract
            
        Returns:
            DataFrame: Data kotak pembatas karakter
        """
        try:
            # Buka gambar dengan PIL
            image = Image.open(image_path)
            
            # Jalankan OCR dengan output boxes
            boxes = pytesseract.image_to_boxes(image, lang=lang, config=config)
            
            # Konversi hasil ke DataFrame
            box_data = []
            for box in boxes.splitlines():
                parts = box.split()
                if len(parts) >= 6:
                    char, x1, y1, x2, y2, page = parts[:6]
                    box_data.append({
                        'char': char,
                        'x1': int(x1),
                        'y1': int(y1),
                        'x2': int(x2),
                        'y2': int(y2),
                        'page': int(page) if page.isdigit() else page
                    })
            
            return pd.DataFrame(box_data)
        except Exception as e:
            raise Exception(f"Error saat mengekstrak boxes: {str(e)}")
    
    def get_available_languages(self):
        """
        Mendapatkan daftar bahasa yang tersedia di Tesseract
        
        Returns:
            list: Daftar kode bahasa yang tersedia
        """
        try:
            # Dapatkan daftar bahasa dari Tesseract
            langs = pytesseract.get_languages()
            return langs
        except Exception as e:
            print(f"Error saat mendapatkan daftar bahasa: {str(e)}")
            return ["eng"]  # Default ke bahasa Inggris jika gagal