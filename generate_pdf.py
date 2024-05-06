# Library membuat file PDF
from fpdf import FPDF
from datetime import datetime
import time 

# Library memasukkan gambar ke PDF
from os import listdir
from os.path import isfile, join
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Inisialisasi PDF
pdf_filename = "hasil_deteksi_dan_counting.pdf"
pdf = FPDF()
pdf.add_page()
c = canvas.Canvas(pdf_filename, pagesize=letter)

starting_time = time.time() 
start_time1 = datetime.now().strftime("%H:%M:%S")
date = datetime.now().strftime("%d-%m-%Y")


# Fungsi untuk menambahkan gambar ke dalam PDF
def add_images_to_pdf(pdf, classNames, num_images_per_class=5): 
    for class_name in classNames:
        image_files = [f for f in listdir("detected_frames") if isfile(join("detected_frames", f)) and f.startswith(class_name + "_frame_")]
        
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"~{class_name}~", ln=True)  
        
        # Menambahkan deskripsi di bawah nama kelas
        pdf.set_font("Arial", size=10)

        if class_name == "Earworm":
            description = "Earworm (cacing/ulat) adalah ulat yang sering ditemukan di banyak sayuran dan bunga. Earworm memakan daun, tunas, dan bunga pada tanaman sayuran seperti tanaman terung."
        elif class_name == "Flea Beetle-s damage":
            description = "Flea beetle-s damage (kerusakan akibat kumbang kutu) adalah penyakit karena kumbang kutu yang memakan daun tanaman sayur, sehingga daun akan berlubang-lubang."
        elif class_name == "Leaf Spot":
            description = "Leaf spot (bercak daun) adalah penyakit akibat fungi patogen Colletotrichum sp yang mengakibatkan ada bercak pada daun tanaman."
        elif class_name == "Leafhopper":
            description = "Leafhopper (wereng) adalah serangga kecil yang menghisap sari tanaman sehingga daun menjadi pucat dan adanya bintik-bintik daun yang memutih."

        pdf.multi_cell(180, 5, txt=description)
        pdf.ln(2)

        # Memasukkan frame sesuai dengan jumlah yang dientukan
        if image_files:
            num_images_added = 0
            for image_file in image_files[:num_images_per_class]:  
                image_path = join("detected_frames", image_file)
                pdf.image(image_path, x=None, y=None, w=120, h=68)  
                num_images_added += 1
                pdf.ln(0)  

                # Menambahkan keterangan di bawah gambar
                pdf.set_font("Arial", size=10, style="I")
                pdf.cell(200, 10, txt=f"Frame hasil deteksi {class_name}", ln=True)
                pdf.ln(2)

        else:
            pdf.set_font("Arial", size=10, style="I")
            pdf.cell(200, 10, txt=f"{class_name} tidak terdeteksi", ln=True)
            pdf.ln(2)
        
        pdf.ln(5)  


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_right_margin(15)
        self.set_left_margin(15)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        image_path = 'D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\Logo_UNY.png'  
        # Menambahkan persegi di margin atas
        self.set_fill_color(180, 180, 180)  
        self.rect(0, 0, self.w, 11, 'F')  
        self.ln(3)

        if self.page_no() == 1:
            # Menambahkan persegi di margin atas
            self.set_fill_color(180, 180, 180)  
            self.rect(0, 0, self.w, 45, 'F')  
            # Menambahkan logo UNY
            self.image(image_path, 5, 2, 40, 40)  
        
    def footer(self):
        # Menambahkan persegi di margin bawah
        self.set_fill_color(180, 180, 180)  
        self.rect(0, 287, self.w, 11, 'F')  
        # Membuat text footer
        self.set_y(-10)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 10, 'oleh Yohanes Gilang Prasaja Putra - 20507334015', 0, 0, 'R')
        

# Fungsi untuk menambahkan dan mengatur konten PDF
def add_detection_results(pdf, id_counts, class_mapping, classNames, output_folder_id):
    total_detections = sum(id_counts.values())
    class_percentages = {name: (count / total_detections) * 100 if total_detections != 0 else 0 for name, count in id_counts.items()}

    # Waktu selesai dan durasi deteksi
    end_time = time.time() 
    end_time1 = datetime.now().strftime("%H:%M:%S") 
    total_time = end_time - starting_time
    hours, minutes = divmod(total_time, 3600)
    minutes, seconds = divmod(minutes, 60)

    # Judul laporan PDF
    pdf.set_y(10) 
    pdf.set_font("Arial", size=18, style="B")
    pdf.cell(180, 9, txt="HASIL DETEKSI", ln=True, align="C")
    pdf.cell(180, 9, txt="PENYAKIT DAUN TANAMAN TERUNG", ln=True, align="C")
    pdf.ln(3)

    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(180, 5, txt="Tugas Akhir D4 Teknik Elektronika UNY", ln=True, align='C')
    pdf.ln(11)
    
    # Waktu, tanggal, dan durasi deteksi
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 7, f"Waktu Mulai    : {start_time1}           Durasi Deteksi  : {int(hours)} jam {int(minutes)} menit {int(seconds)} detik", ln=True, align="L")
    pdf.cell(200, 7, f"Waktu Selesai : {end_time1}           Tanggal             : {date}", ln=True, align="L")

    # Parameter class, persentase, dan jumlah deteksi
    x_position = 15
    y_position = 73
    column_width = 45

    # Memasukkan class, persentase, dan jumlah deteksi ke dalam PDF
    for i, name in enumerate(classNames):
        count = id_counts[class_mapping[name]]
        percentage = class_percentages[class_mapping[name]]

        text1 = f"{name}"
        text2 = f"{count} deteksi"
        text3 = f"{percentage:.2f}%"
        x = x_position + (i * column_width) 

        pdf.set_font("Arial", size=12, style="B")
        pdf.set_xy(x, y_position)
        pdf.cell(column_width, 10, txt=text1, ln=False, align="C")
        pdf.set_font("Arial", size=18, style="B")
        pdf.set_xy(x, y_position + 8)
        pdf.cell(column_width, 20, txt=text3, ln=False, align="C")
        pdf.set_font("Arial", size=12)
        pdf.set_xy(x, y_position + 16)
        pdf.cell(column_width, 30, txt=text2, ln=False, align="C")
        pdf.ln(30)

    page_width = pdf.w
    page_height = pdf.h

    # Memasukkan link google drive
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, txt="Selengkapnya mengenai hasil deteksi dapat diakses pada tautan Google Drive berikut", ln=True)
    pdf.set_text_color(0, 0, 255)
    pdf.cell(200, 8, txt=f'https://drive.google.com/drive/folders/{output_folder_id}', ln=True, link=f'https://drive.google.com/drive/folders/{output_folder_id}')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Memasukkan sample frame deteksi 
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(200, 10, txt='Frame Hasil Deteksi', ln=True)
    pdf.set_text_color(0, 0, 0) 

    # Memanggil add_images_to_pdf
    add_images_to_pdf(pdf, classNames)
