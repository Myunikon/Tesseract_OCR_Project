import cv2
import numpy as np
from PIL import Image
import math

class ImageProcessor:
    """
    Kelas untuk memproses gambar sebelum OCR untuk meningkatkan akurasi
    """
    
    def __init__(self):
        """
        Inisialisasi Image Processor
        """
        pass
    
    def load_image(self, image_path):
        """
        Memuat gambar dari file
        
        Args:
            image_path (str): Path ke file gambar
            
        Returns:
            numpy.ndarray: Gambar dalam format OpenCV
        """
        try:
            # Baca gambar dengan OpenCV
            image = cv2.imread(image_path)
            
            if image is None:
                # Jika OpenCV gagal, coba dengan PIL
                pil_image = Image.open(image_path)
                image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            return image
        except Exception as e:
            raise Exception(f"Error saat memuat gambar: {str(e)}")
    
    def save_image(self, image, output_path):
        """
        Menyimpan gambar ke file
        
        Args:
            image (numpy.ndarray): Gambar dalam format OpenCV
            output_path (str): Path untuk menyimpan gambar
            
        Returns:
            bool: True jika berhasil
        """
        try:
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            raise Exception(f"Error saat menyimpan gambar: {str(e)}")
    
    def resize(self, image, width=None, height=None, scale=None):
        """
        Mengubah ukuran gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            width (int, optional): Lebar target
            height (int, optional): Tinggi target
            scale (float, optional): Faktor skala
            
        Returns:
            numpy.ndarray: Gambar yang diubah ukurannya
        """
        if scale is not None:
            return cv2.resize(image, None, fx=scale, fy=scale)
        
        if width is not None and height is not None:
            return cv2.resize(image, (width, height))
        
        if width is not None:
            ratio = width / image.shape[1]
            height = int(image.shape[0] * ratio)
            return cv2.resize(image, (width, height))
        
        if height is not None:
            ratio = height / image.shape[0]
            width = int(image.shape[1] * ratio)
            return cv2.resize(image, (width, height))
        
        return image
    
    def grayscale(self, image):
        """
        Mengkonversi gambar ke grayscale
        
        Args:
            image (numpy.ndarray): Gambar input
            
        Returns:
            numpy.ndarray: Gambar grayscale
        """
        if len(image.shape) == 2:
            return image  # Sudah grayscale
        
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def denoise(self, image):
        """
        Mengurangi noise pada gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            
        Returns:
            numpy.ndarray: Gambar yang telah dikurangi noise-nya
        """
        # Pastikan gambar dalam grayscale
        gray = self.grayscale(image)
        
        # Terapkan filter bilateral untuk mengurangi noise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        return denoised
    
    def threshold(self, image, method='binary', block_size=11, c=2):
        """
        Menerapkan thresholding pada gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            method (str): Metode threshold ('binary', 'adaptive', 'otsu')
            block_size (int): Ukuran blok untuk adaptive threshold
            c (int): Konstanta untuk adaptive threshold
            
        Returns:
            numpy.ndarray: Gambar hasil threshold
        """
        # Pastikan gambar dalam grayscale
        gray = self.grayscale(image)
        
        if method == 'binary':
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        elif method == 'adaptive':
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, block_size, c)
        elif method == 'otsu':
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            raise ValueError(f"Metode threshold tidak dikenal: {method}")
        
        return thresh
    
    def adaptive_threshold(self, image, block_size=11, c=2):
        """
        Menerapkan adaptive thresholding pada gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            block_size (int): Ukuran blok
            c (int): Konstanta
            
        Returns:
            numpy.ndarray: Gambar hasil threshold
        """
        # Pastikan gambar dalam grayscale
        gray = self.grayscale(image)
        
        # Terapkan adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, block_size, c)
        
        return thresh
    
    def deskew(self, image):
        """
        Memperbaiki kemiringan gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            
        Returns:
            numpy.ndarray: Gambar yang telah diperbaiki kemiringannya
        """
        # Pastikan gambar dalam grayscale
        gray = self.grayscale(image)
        
        # Deteksi tepi
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Deteksi garis dengan transformasi Hough
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        # Jika tidak ada garis yang terdeteksi, kembalikan gambar asli
        if lines is None or len(lines) == 0:
            return image
        
        # Hitung sudut kemiringan
        angles = []
        for line in lines:
            rho, theta = line[0]
            if theta < np.pi/4 or theta > 3*np.pi/4:
                angles.append(theta)
        
        if not angles:
            return image
        
        # Hitung sudut rata-rata
        median_angle = np.median(angles)
        
        # Konversi ke derajat dan hitung sudut koreksi
        angle_degrees = np.degrees(median_angle - np.pi/2)
        
        # Batasi sudut koreksi
        if abs(angle_degrees) > 45:
            return image
        
        # Rotasi gambar
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return rotated
    
    def remove_borders(self, image, margin=10):
        """
        Menghapus border hitam dari gambar
        
        Args:
            image (numpy.ndarray): Gambar input
            margin (int): Margin tambahan
            
        Returns:
            numpy.ndarray: Gambar tanpa border
        """
        # Pastikan gambar dalam grayscale
        gray = self.grayscale(image)
        
        # Threshold untuk mendapatkan gambar biner
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Temukan kontur
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Jika tidak ada kontur, kembalikan gambar asli
        if not contours:
            return image
        
        # Temukan kontur terbesar
        max_contour = max(contours, key=cv2.contourArea)
        
        # Dapatkan bounding box
        x, y, w, h = cv2.boundingRect(max_contour)
        
        # Tambahkan margin
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(image.shape[1] - x, w + 2 * margin)
        h = min(image.shape[0] - y, h + 2 * margin)
        
        # Crop gambar
        cropped = image[y:y+h, x:x+w]
        
        return cropped