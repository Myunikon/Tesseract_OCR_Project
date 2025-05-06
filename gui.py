import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFileDialog, QTabWidget, QTextEdit, 
                            QComboBox, QSpinBox, QCheckBox, QMessageBox, QProgressBar,
                            QStatusBar, QToolBar, QMenu, QMenuBar, QSplitter)
from PyQt6.QtGui import QPixmap, QImage, QAction, QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize

from .ocr_engine import OCREngine
from .image_processor import ImageProcessor
from .pdf_handler import PDFHandler
from .webcam_capture import WebcamCapture
from .export_manager import ExportManager

class OCRWorker(QThread):
    """Thread terpisah untuk menjalankan OCR agar UI tetap responsif"""
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, ocr_engine, image_path, lang, config):
        super().__init__()
        self.ocr_engine = ocr_engine
        self.image_path = image_path
        self.lang = lang
        self.config = config
        
    def run(self):
        try:
            # Simulasi progress
            self.progress.emit(10)
            
            # Jalankan OCR
            result = self.ocr_engine.image_to_text(self.image_path, self.lang, self.config)
            
            self.progress.emit(100)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Inisialisasi komponen utama
        self.ocr_engine = OCREngine()
        self.image_processor = ImageProcessor()
        self.pdf_handler = PDFHandler(self.ocr_engine)
        self.webcam = WebcamCapture()
        self.export_manager = ExportManager()
        
        # Variabel untuk menyimpan path gambar saat ini
        self.current_image_path = None
        self.processed_image = None
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        # Setup window
        self.setWindowTitle("Tesseract OCR Application")
        self.setGeometry(100, 100, 1200, 800)
        
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Main widget dan layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Splitter untuk membagi area gambar dan hasil
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel kiri - gambar dan kontrol
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Area gambar
        self.image_label = QLabel("Tidak ada gambar yang dimuat")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("border: 1px solid #cccccc; background-color: #f5f5f5;")
        left_layout.addWidget(self.image_label)
        
        # Kontrol gambar
        image_controls = QHBoxLayout()
        
        self.load_image_btn = QPushButton("Muat Gambar")
        self.load_image_btn.clicked.connect(self.load_image)
        image_controls.addWidget(self.load_image_btn)
        
        self.load_pdf_btn = QPushButton("Muat PDF")
        self.load_pdf_btn.clicked.connect(self.load_pdf)
        image_controls.addWidget(self.load_pdf_btn)
        
        self.webcam_btn = QPushButton("Webcam")
        self.webcam_btn.clicked.connect(self.toggle_webcam)
        image_controls.addWidget(self.webcam_btn)
        
        left_layout.addLayout(image_controls)
        
        # Pengaturan OCR
        ocr_settings = QHBoxLayout()
        
        ocr_settings.addWidget(QLabel("Bahasa:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["eng", "ind", "eng+ind"])
        ocr_settings.addWidget(self.lang_combo)
        
        ocr_settings.addWidget(QLabel("Mode:"))
        self.psm_combo = QComboBox()
        self.psm_combo.addItems([
            "0 - Orientasi dan deteksi skrip otomatis",
            "1 - Segmentasi otomatis dengan OSD",
            "3 - Segmentasi penuh otomatis tanpa OSD (default)",
            "4 - Satu kolom teks dengan ukuran variabel",
            "6 - Blok teks seragam",
            "7 - Satu baris teks",
            "8 - Satu kata",
            "10 - Satu karakter",
            "11 - Teks mentah",
            "12 - Teks mentah + OSD",
            "13 - Teks mentah tanpa rotasi"
        ])
        self.psm_combo.setCurrentIndex(2)  # Default ke PSM 3
        ocr_settings.addWidget(self.psm_combo)
        
        left_layout.addLayout(ocr_settings)
        
        # Pengaturan pemrosesan gambar
        img_proc_settings = QHBoxLayout()
        
        self.grayscale_cb = QCheckBox("Grayscale")
        self.grayscale_cb.setChecked(True)
        img_proc_settings.addWidget(self.grayscale_cb)
        
        self.denoise_cb = QCheckBox("Denoise")
        self.denoise_cb.setChecked(True)
        img_proc_settings.addWidget(self.denoise_cb)
        
        self.threshold_cb = QCheckBox("Threshold")
        self.threshold_cb.setChecked(True)
        img_proc_settings.addWidget(self.threshold_cb)
        
        self.deskew_cb = QCheckBox("Deskew")
        self.deskew_cb.setChecked(True)
        img_proc_settings.addWidget(self.deskew_cb)
        
        left_layout.addLayout(img_proc_settings)
        
        # Tombol OCR
        self.ocr_btn = QPushButton("Jalankan OCR")
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.ocr_btn.setEnabled(False)
        left_layout.addWidget(self.ocr_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)
        
        # Panel kanan - hasil OCR
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tab untuk hasil yang berbeda
        self.result_tabs = QTabWidget()
        
        # Tab teks
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.result_tabs.addTab(self.text_result, "Teks")
        
        # Tab data
        self.data_result = QTextEdit()
        self.data_result.setReadOnly(True)
        self.result_tabs.addTab(self.data_result, "Data")
        
        right_layout.addWidget(self.result_tabs)
        
        # Kontrol ekspor
        export_controls = QHBoxLayout()
        
        self.export_text_btn = QPushButton("Ekspor Teks")
        self.export_text_btn.clicked.connect(lambda: self.export_result("text"))
        self.export_text_btn.setEnabled(False)
        export_controls.addWidget(self.export_text_btn)
        
        self.export_excel_btn = QPushButton("Ekspor Excel")
        self.export_excel_btn.clicked.connect(lambda: self.export_result("excel"))
        self.export_excel_btn.setEnabled(False)
        export_controls.addWidget(self.export_excel_btn)
        
        self.export_pdf_btn = QPushButton("Ekspor PDF")
        self.export_pdf_btn.clicked.connect(lambda: self.export_result("pdf"))
        self.export_pdf_btn.setEnabled(False)
        export_controls.addWidget(self.export_pdf_btn)
        
        right_layout.addLayout(export_controls)
        
        # Tambahkan panel ke splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 700])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Siap")
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Menu File
        file_menu = menu_bar.addMenu("File")
        
        open_image_action = QAction("Buka Gambar", self)
        open_image_action.triggered.connect(self.load_image)
        file_menu.addAction(open_image_action)
        
        open_pdf_action = QAction("Buka PDF", self)
        open_pdf_action.triggered.connect(self.load_pdf)
        file_menu.addAction(open_pdf_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Keluar", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Edit
        edit_menu = menu_bar.addMenu("Edit")
        
        process_action = QAction("Proses Gambar", self)
        process_action.triggered.connect(self.process_image)
        edit_menu.addAction(process_action)
        
        # Menu Tools
        tools_menu = menu_bar.addMenu("Tools")
        
        webcam_action = QAction("Webcam", self)
        webcam_action.triggered.connect(self.toggle_webcam)
        tools_menu.addAction(webcam_action)
        
        # Menu Help
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("Tentang", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Tambahkan aksi ke toolbar
        open_image_action = QAction("Buka Gambar", self)
        open_image_action.triggered.connect(self.load_image)
        toolbar.addAction(open_image_action)
        
        process_action = QAction("Proses Gambar", self)
        process_action.triggered.connect(self.process_image)
        toolbar.addAction(process_action)
        
        ocr_action = QAction("OCR", self)
        ocr_action.triggered.connect(self.run_ocr)
        toolbar.addAction(ocr_action)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Buka Gambar", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
            self.ocr_btn.setEnabled(True)
            self.status_bar.showMessage(f"Gambar dimuat: {os.path.basename(file_path)}")
    
    def load_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Buka PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                # Konversi halaman pertama PDF ke gambar
                with tempfile.TemporaryDirectory() as temp_dir:
                    image_paths = self.pdf_handler.convert_pdf_to_images(
                        file_path, output_folder=temp_dir, output_format='png'
                    )
                    
                    if image_paths and len(image_paths) > 0:
                        self.current_image_path = image_paths[0]
                        self.display_image(image_paths[0])
                        self.ocr_btn.setEnabled(True)
                        self.status_bar.showMessage(f"PDF dimuat: {os.path.basename(file_path)} (halaman 1)")
                    else:
                        QMessageBox.warning(self, "Error", "Gagal mengkonversi PDF ke gambar")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saat memuat PDF: {str(e)}")
    
    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        
        # Skala gambar agar sesuai dengan label
        pixmap = pixmap.scaled(
            self.image_label.width(), self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(pixmap)
    
    def process_image(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang dimuat")
            return
        
        # Muat gambar
        image = self.image_processor.load_image(self.current_image_path)
        
        # Terapkan pemrosesan berdasarkan checkbox
        if self.grayscale_cb.isChecked():
            image = self.image_processor.grayscale(image)
        
        if self.denoise_cb.isChecked():
            image = self.image_processor.denoise(image)
        
        if self.threshold_cb.isChecked():
            image = self.image_processor.adaptive_threshold(image)
        
        if self.deskew_cb.isChecked():
            image = self.image_processor.deskew(image)
        
        # Simpan gambar yang diproses ke file sementara
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        cv2.imwrite(temp_path, image)
        self.processed_image = temp_path
        
        # Tampilkan gambar yang diproses
        self.display_image(temp_path)
        self.status_bar.showMessage("Gambar telah diproses")
    
    def run_ocr(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "Peringatan", "Tidak ada gambar yang dimuat")
            return
        
        # Gunakan gambar yang diproses jika ada
        image_path = self.processed_image if self.processed_image else self.current_image_path
        
        # Dapatkan pengaturan OCR
        lang = self.lang_combo.currentText()
        psm = self.psm_combo.currentIndex()
        if psm == 0: psm = 0
        elif psm == 1: psm = 1
        else: psm = psm + 1  # Karena indeks combo box tidak termasuk PSM 2
        
        config = f"--psm {psm}"
        
        # Nonaktifkan tombol OCR selama pemrosesan
        self.ocr_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Menjalankan OCR...")
        
        # Jalankan OCR di thread terpisah
        self.ocr_worker = OCRWorker(self.ocr_engine, image_path, lang, config)
        self.ocr_worker.finished.connect(self.ocr_finished)
        self.ocr_worker.progress.connect(self.progress_bar.setValue)
        self.ocr_worker.error.connect(self.ocr_error)
        self.ocr_worker.start()
    
    def ocr_finished(self, result):
        # Tampilkan hasil OCR
        self.text_result.setText(result)
        
        # Coba dapatkan data terstruktur
        try:
            if self.current_image_path:
                data = self.ocr_engine.image_to_data(self.current_image_path)
                if data is not None:
                    self.data_result.setText(str(data))
        except Exception as e:
            self.data_result.setText(f"Error mendapatkan data terstruktur: {str(e)}")
        
        # Aktifkan kembali tombol OCR dan ekspor
        self.ocr_btn.setEnabled(True)
        self.export_text_btn.setEnabled(True)
        self.export_excel_btn.setEnabled(True)
        self.export_pdf_btn.setEnabled(True)
        
        self.status_bar.showMessage("OCR selesai")
    
    def ocr_error(self, error_msg):
        QMessageBox.warning(self, "Error OCR", f"Error saat menjalankan OCR: {error_msg}")
        self.ocr_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("OCR gagal")
    
    def toggle_webcam(self):
        # Implementasi untuk mengaktifkan/menonaktifkan webcam
        pass
    
    def export_result(self, format_type):
        if format_type == "text":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Simpan Teks", "", "Text Files (*.txt)"
            )
            if file_path:
                self.export_manager.export_text(self.text_result.toPlainText(), file_path)
                self.status_bar.showMessage(f"Teks diekspor ke {file_path}")
        
        elif format_type == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Simpan Excel", "", "Excel Files (*.xlsx)"
            )
            if file_path:
                try:
                    data = self.ocr_engine.image_to_data(self.current_image_path)
                    if data is not None:
                        self.export_manager.export_excel(data, file_path)
                        self.status_bar.showMessage(f"Data diekspor ke {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Error Ekspor", f"Error saat mengekspor ke Excel: {str(e)}")
        
        elif format_type == "pdf":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Simpan PDF", "", "PDF Files (*.pdf)"
            )
            if file_path:
                try:
                    self.export_manager.export_pdf(self.text_result.toPlainText(), file_path)
                    self.status_bar.showMessage(f"PDF diekspor ke {file_path}")
                except Exception as e:
                    QMessageBox.warning(self, "Error Ekspor", f"Error saat mengekspor ke PDF: {str(e)}")
    
    def show_about(self):
        QMessageBox.about(
            self, 
            "Tentang Aplikasi OCR",
            "Aplikasi OCR dengan Tesseract\n\n"
            "Aplikasi ini menggunakan Tesseract OCR Engine untuk mengenali teks dari gambar.\n\n"
            "Fitur:\n"
            "- Pengenalan teks dari gambar\n"
            "- Pemrosesan gambar untuk meningkatkan akurasi OCR\n"
            "- Dukungan untuk berbagai bahasa\n"
            "- Ekspor hasil ke berbagai format\n\n"
            "© 2023 Tesseract OCR Project"
        )