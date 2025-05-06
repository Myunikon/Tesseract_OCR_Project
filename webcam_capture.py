import cv2
import numpy as np
import os
import tempfile
from datetime import datetime

class WebcamCapture:
    """
    Kelas untuk menangani pengambilan gambar dari webcam
    """
    
    def __init__(self, camera_id=0):
        """
        Inisialisasi WebcamCapture
        
        Args:
            camera_id (int): ID kamera (default: 0)
        """
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
    
    def start(self):
        """
        Memulai webcam
        
        Returns:
            bool: True jika berhasil
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise Exception("Tidak dapat membuka webcam")
            
            self.is_running = True
            return True
        except Exception as e:
            print(f"Error saat memulai webcam: {str(e)}")
            return False
    
    def stop(self):
        """
        Menghentikan webcam
        """
        if self.cap is not None:
            self.cap.release()
            self.is_running = False
    
    def get_frame(self):
        """
        Mendapatkan frame dari webcam
        
        Returns:
            numpy.ndarray: Frame gambar
        """
        if not self.is_running:
            self.start()
        
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Tidak dapat membaca frame dari webcam")
        
        return frame
    
    def capture_image(self, output_path=None):
        """
        Mengambil gambar dari webcam dan menyimpannya
        
        Args:
            output_path (str, optional): Path untuk menyimpan gambar.
                                        Jika None, akan dibuat file sementara.
            
        Returns:
            str: Path ke file gambar yang disimpan
        """
        if not self.is_running:
            self.start()
        
        # Ambil frame
        frame = self.get_frame()
        
        # Tentukan path output
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with tempfile.NamedTemporaryFile(suffix=f'_{timestamp}.jpg', delete=False) as temp_file:
                output_path = temp_file.name
        
        # Simpan gambar
        cv2.imwrite(output_path, frame)
        
        return output_path
    
    def preview(self, window_name="Webcam Preview", process_func=None):
        """
        Menampilkan preview webcam
        
        Args:
            window_name (str): Nama jendela preview
            process_func (callable, optional): Fungsi untuk memproses frame
            
        Returns:
            str: Path ke file gambar yang diambil, atau None jika dibatalkan
        """
        if not self.is_running:
            self.start()
        
        cv2.namedWindow(window_name)
        print("Tekan SPACE untuk mengambil gambar atau ESC untuk membatalkan")
        
        captured_image_path = None
        
        while True:
            # Ambil frame
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Proses frame jika ada fungsi pemrosesan
            if process_func is not None:
                display_frame = process_func(frame)
            else:
                display_frame = frame
            
            # Tampilkan frame
            cv2.imshow(window_name, display_frame)
            
            # Tangkap input keyboard
            key = cv2.waitKey(1)
            
            # ESC untuk keluar
            if key == 27:
                break
            
            # SPACE untuk mengambil gambar
            elif key == 32:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = os.path.join(tempfile.gettempdir(), "webcam_capture")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"capture_{timestamp}.jpg")
                
                cv2.imwrite(output_path, frame)
                captured_image_path = output_path
                print(f"Gambar disimpan ke: {output_path}")
                break
        
        # Tutup jendela preview
        cv2.destroyWindow(window_name)
        
        return captured_image_path