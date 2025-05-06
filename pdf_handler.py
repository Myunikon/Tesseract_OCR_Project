import os
import tempfile
import fitz  # PyMuPDF
from PIL import Image
import io
import numpy as np
import cv2

class PDFHandler:
    """
    Kelas untuk menangani operasi terkait PDF
    """
    
    def __init__(self, ocr_engine=None):
        """
        Inisialisasi PDF Handler
        
        Args:
            ocr_engine (OCREngine, optional): Instance dari OCREngine untuk OCR
        """
        self.ocr_engine = ocr_engine
    
    def convert_pdf_to_images(self, pdf_path, output_folder=None, output_format='png', dpi=300):
        """
        Mengkonversi PDF ke gambar
        
        Args:
            pdf_path (str): Path ke file PDF
            output_folder (str, optional): Folder untuk menyimpan gambar hasil
            output_format (str): Format output gambar (default: 'png')
            dpi (int): DPI untuk rendering (default: 300)
            
        Returns:
            list: Daftar path ke gambar hasil konversi
        """
        try:
            # Buka dokumen PDF
            pdf_document = fitz.open(pdf_path)
            
            # Buat folder output jika belum ada
            if output_folder is None:
                output_folder = tempfile.mkdtemp()
            elif not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            image_paths = []
            
            # Konversi setiap halaman ke gambar
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Render halaman ke gambar
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                
                # Simpan gambar
                image_path = os.path.join(output_folder, f"page_{page_num + 1}.{output_format}")
                pix.save(image_path)
                
                image_paths.append(image_path)
            
            return image_paths
        except Exception as e:
            raise Exception(f"Error saat mengkonversi PDF ke gambar: {str(e)}")
    
    def ocr_pdf(self, pdf_path, lang='eng', config=''):
        """
        Melakukan OCR pada PDF
        
        Args:
            pdf_path (str): Path ke file PDF
            lang (str): Kode bahasa untuk OCR (default: 'eng')
            config (str): Konfigurasi tambahan untuk Tesseract
            
        Returns:
            list: Daftar teks hasil OCR untuk setiap halaman
        """
        if self.ocr_engine is None:
            raise Exception("OCR Engine tidak tersedia")
        
        try:
            # Konversi PDF ke gambar
            with tempfile.TemporaryDirectory() as temp_dir:
                image_paths = self.convert_pdf_to_images(pdf_path, output_folder=temp_dir)
                
                # Lakukan OCR pada setiap gambar
                results = []
                for image_path in image_paths:
                    text = self.ocr_engine.image_to_text(image_path, lang, config)
                    results.append(text)
                
                return results
        except Exception as e:
            raise Exception(f"Error saat melakukan OCR pada PDF: {str(e)}")
    
    def create_searchable_pdf(self, pdf_path, output_path, lang='eng', config=''):
        """
        Membuat PDF yang dapat dicari (searchable PDF)
        
        Args:
            pdf_path (str): Path ke file PDF input
            output_path (str): Path untuk menyimpan PDF hasil
            lang (str): Kode bahasa untuk OCR (default: 'eng')
            config (str): Konfigurasi tambahan untuk Tesseract
            
        Returns:
            bool: True jika berhasil
        """
        if self.ocr_engine is None:
            raise Exception("OCR Engine tidak tersedia")
        
        try:
            # Buka dokumen PDF
            pdf_document = fitz.open(pdf_path)
            
            # Proses setiap halaman
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Render halaman ke gambar
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Konversi ke format yang dapat diproses oleh OCR
                img = Image.open(io.BytesIO(img_data))
                
                # Simpan gambar sementara
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_path = temp_file.name
                    img.save(temp_path)
                
                # Lakukan OCR
                text = self.ocr_engine.image_to_text(temp_path, lang, config)
                
                # Hapus file sementara
                os.unlink(temp_path)
                
                # Tambahkan layer teks ke halaman
                page.insert_text(
                    fitz.Point(0, 0),  # Posisi
                    text,              # Teks
                    fontsize=0,        # Ukuran font 0 = tidak terlihat
                    overlay=True       # Overlay di atas konten yang ada
                )
            
            # Simpan PDF yang dapat dicari
            pdf_document.save(output_path)
            pdf_document.close()
            
            return True
        except Exception as e:
            raise Exception(f"Error saat membuat searchable PDF: {str(e)}")