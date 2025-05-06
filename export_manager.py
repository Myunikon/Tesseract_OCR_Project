import os
import pandas as pd
from fpdf import FPDF
import json
import csv
import xml.dom.minidom as md
import xml.etree.ElementTree as ET

class ExportManager:
    """
    Kelas untuk menangani ekspor hasil OCR ke berbagai format
    """
    
    def __init__(self):
        """
        Inisialisasi Export Manager
        """
        pass
    
    def export_text(self, text, output_path):
        """
        Mengekspor teks ke file teks biasa
        
        Args:
            text (str): Teks yang akan diekspor
            output_path (str): Path untuk menyimpan file
            
        Returns:
            bool: True jika berhasil
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor teks: {str(e)}")
    
    def export_excel(self, data, output_path):
        """
        Mengekspor data ke file Excel
        
        Args:
            data (DataFrame): Data yang akan diekspor
            output_path (str): Path untuk menyimpan file
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Pastikan data adalah DataFrame
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Data harus berupa pandas DataFrame")
            
            # Ekspor ke Excel
            data.to_excel(output_path, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor ke Excel: {str(e)}")
    
    def export_csv(self, data, output_path, delimiter=','):
        """
        Mengekspor data ke file CSV
        
        Args:
            data (DataFrame): Data yang akan diekspor
            output_path (str): Path untuk menyimpan file
            delimiter (str): Karakter pemisah (default: ',')
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Pastikan data adalah DataFrame
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Data harus berupa pandas DataFrame")
            
            # Ekspor ke CSV
            data.to_csv(output_path, index=False, sep=delimiter)
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor ke CSV: {str(e)}")
    
    def export_json(self, data, output_path, orient='records'):
        """
        Mengekspor data ke file JSON
        
        Args:
            data (DataFrame): Data yang akan diekspor
            output_path (str): Path untuk menyimpan file
            orient (str): Format JSON (default: 'records')
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Pastikan data adalah DataFrame
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Data harus berupa pandas DataFrame")
            
            # Ekspor ke JSON
            data.to_json(output_path, orient=orient)
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor ke JSON: {str(e)}")
    
    def export_pdf(self, text, output_path, title=None):
        """
        Mengekspor teks ke file PDF
        
        Args:
            text (str): Teks yang akan diekspor
            output_path (str): Path untuk menyimpan file
            title (str, optional): Judul dokumen
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Buat objek PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Atur font
            pdf.set_font("Arial", size=12)
            
            # Tambahkan judul jika ada
            if title:
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt=title, ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
            
            # Tambahkan teks
            # Pisahkan teks menjadi baris-baris
            lines = text.split('\n')
            for line in lines:
                # Pecah baris panjang
                pdf.multi_cell(0, 10, txt=line)
            
            # Simpan PDF
            pdf.output(output_path)
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor ke PDF: {str(e)}")
    
    def export_xml(self, data, output_path, root_name='document'):
        """
        Mengekspor data ke file XML
        
        Args:
            data (DataFrame): Data yang akan diekspor
            output_path (str): Path untuk menyimpan file
            root_name (str): Nama elemen root (default: 'document')
            
        Returns:
            bool: True jika berhasil
        """
        try:
            # Pastikan data adalah DataFrame
            if not isinstance(data, pd.DataFrame):
                raise ValueError("Data harus berupa pandas DataFrame")
            
            # Buat elemen root
            root = ET.Element(root_name)
            
            # Konversi setiap baris ke elemen XML
            for _, row in data.iterrows():
                item = ET.SubElement(root, 'item')
                for col, value in row.items():
                    if pd.notna(value):
                        child = ET.SubElement(item, col)
                        child.text = str(value)
            
            # Buat XML tree
            tree = ET.ElementTree(root)
            
            # Tulis ke file dengan format yang rapi
            xmlstr = md.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xmlstr)
            
            return True
        except Exception as e:
            raise Exception(f"Error saat mengekspor ke XML: {str(e)}")