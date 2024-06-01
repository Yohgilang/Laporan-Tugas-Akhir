# -------------------------------------------------------------- LIBRARY

# Deteksi, tracking, dan counting
import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
import pandas
import os
from datetime import datetime
from openvino.tools import mo

# Import from differend file .py
from sort import *
from gdrive_set import DriveUploader, GoogleDrive, GoogleAuth 
from generate_pdf import PDF, canvas, FPDF, letter, add_images_to_pdf, add_detection_results
from sender_email import send_email

# Configure telegram bot
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
# --------------------------------------------------------------


# Model dari hasil export openvino
ov_model = YOLO('D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\eggplant_desease_openvino_model/', task='detect')

# Mengakses video atau webcam
cap = cv2.VideoCapture('isi bagian ini dengan alamat IP RTSP') #alamat IP RTSP

# Menyimpan video hasil deteksi
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter('video_deteksi_penyakit_tanaman_terung.mp4', fourcc, 10.0, (640, 360))  

# Parameter menghitung jumlah deteksi untuk setiap penyakit (id)
classNames = ['Earworm', 'Flea Beetle-s damage', 'Leaf Spot', 'Leafhopper']
class_mapping = {"Earworm": "id1", "Flea Beetle-s damage": "id2", "Leaf Spot": "id3", "Leafhopper": "id4"}
detected_id = list(class_mapping.values())
id_counts = {class_name: 0 for class_name in class_mapping.values()}

# Mengonversi class_name menjadi ID
def map_class_name(original_class_name):
    return class_mapping.get(original_class_name, original_class_name)

# Tracking menggunakan SORT (A Simple, Online and Realtime Tracker)
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3) # --------------------------

# Koordinat polygon
line = np.array([(0,0), (640,0), (640,360), (0,360)], np.int32) 

# Inisialisasi variabel counting
totalcount = []
count=0

# Parameter untuk menampilkan FPS
font = cv2.FONT_HERSHEY_PLAIN
starting_time = time.time()
frame_id = 0


# -------------------------------------------------------------- EMAIL DAN TELEGRAM

# Memuat variabel dalam file .env
load_dotenv()

# Konfigurasi telegram 
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

updater = Updater(token=telegram_bot_token, use_context=True, request_kwargs={'connect_timeout': 60, 'read_timeout': 60})
dispatcher = updater.dispatcher

# Command handler untuk menerima input email tujuan
def send_to_email(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Masukkan email tujuan:")
    return "WAITING_EMAIL"

# Callback untuk menyimpan email tujuan dan meminta pengguna untuk mengirim PDF
def handle_email_input(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    email_to = update.message.text
    context.user_data['email_to'] = email_to
    context.bot.send_message(chat_id=chat_id, text=f"Email tujuan: {email_to}\nMengirimkan PDF...")
    send_email(email_to)
    context.bot.send_message(chat_id=chat_id, text="PDF berhasil dikirim ke email tujuan.")

# Command handler untuk menerima input email tujuan
def start_monitoring(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Anda dapat mengirimkan file PDF hasil deteksi dan counting melalui email ke alamat yang dituju dengan menggunakan command /send_to_email")
    
# Menambahkan  commandhandler dan messagehandler ke dispatcher
dispatcher.add_handler(CommandHandler("send_to_email", send_to_email))
dispatcher.add_handler(CommandHandler("start_monitoring", start_monitoring))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_email_input))


# -------------------------------------------------------------- GOOGLE DRIVE DAN LOKAL

# Parameter untuk upload frame ke google drive dan lokal
output_folder = "detected_frames"
folder_id = 'isi bagian ini dengan ID Folder Google Drive'  
detected_frames = [] 
uploaded_frames = set()
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# Membuat folder untuk menyimpan frame hasil deteksi dalam lokal device (laptop)
if not os.path.exists(output_folder):
        os.makedirs(output_folder)

# Hapus semua gambar yang ada di dalam folder sebelum menyimpan gambar baru
files = [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f))]
for f in files:
    os.remove(os.path.join(output_folder, f))

# Membuat objek DriveUploader
uploader = DriveUploader()

# Memanggil initialize_auth
uploader.initialize_auth()

# Memanggil create_folder_gdrive
output_folder_id = uploader.create_folder_gdrive(folder_id)
print(output_folder_id)

upload_frame = []

# Fungsi untuk mengunggah gambar ke dalam folder baru di google drive
def upload_frame_to_drive(frame_path, output_folder_id):
    try:
        file = drive.CreateFile({'parents': [{'id': output_folder_id}]})
        file.SetContentFile(frame_path)
        file['title'] = os.path.basename(frame_path)  
        file.Upload()
        print(f"Frame {frame_path} berhasil diunggah ke Google Drive.")

        # Tambahkan frame_path ke list upload_frame
        upload_frame.append(frame_path)

    except Exception as e:
        print(f"Error saat mengunggah frame {frame_path} ke Google Drive:", e)


# -------------------------------------------------------------- MEMBUAT PDF

# Inisialisasi PDF
pdf_filename = "hasil_deteksi_dan_counting.pdf"
pdf = FPDF()
pdf.add_page()
c = canvas.Canvas(pdf_filename, pagesize=letter)

# Memanggil add_images_to_pdf
add_images_to_pdf(pdf, classNames, num_images_per_class=5)

# Memanggil header dan footer
pdf.header()
pdf.footer()

pdf = PDF()
pdf.add_page()


# -------------------------------------------------------------- KODE LOOP

# Jalankan eksekusi kode loop
try:
    while True:
        success, imag = cap.read()
        frame_id += 1
        if not success:
            print('Video selesai')
            break  
        if count % 5 != 0:
            continue

        # Memeriksa frame apakah ada atau tidak sebelum melakukan resizing frame
        if imag.size != 0:
            img = cv2.resize(imag, (640,360))
            results = ov_model(img, show=False, conf=0.3, save=False) 
            detection = np.empty((0, 5))

            # Membuat box dan parameternya
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    w, h = x2 - x1, y2 - y1
                    conf = math.ceil((box.conf[0] * 100)) / 100  
                    cls = int(box.cls[0])  
                    classfound = classNames[cls]

                    # Mengatur agar penyakit yang terdeteksi sesuai dengan batas minimal confidence  
                    if classfound == 'Earworm' or classfound == 'Flea Beetle-s damage' or classfound == 'Leaf Spot' or classfound == 'Leafhopper' and conf >= 0.3:
                        new_class_name = map_class_name(classfound)    
                        currentArray = np.array([x1, y1, x2, y2, conf])
                        detection = np.vstack((detection, currentArray))
                    else:
                        new_class_name = None

            # Perbaharui tracker SORT
            tracker_results = tracker.update(detection)

            # Membuat polygon dalam video
            cv2.polylines(img, [line], True, (0, 255, 0), 3)

            # Perulangan dengan tracker_result (SORT)
            for res in tracker_results:
                x1, y1, x2, y2, id = res
                x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)
                w, h = x2 - x1, y2 - y1
                cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))
                cvzone.putTextRect(img, f'{classfound} {conf}', (max(0, x1), max(35, y1)), scale=1, thickness=1, offset=10)
                cx, cy = x1 + w // 2, y1 + h // 2
                cv2.circle(img, (cx, cy), 2, (255, 0, 255), cv2.FILLED)

                # OCunting class penyakit yang terdeteksi dalam polygone
                if cv2.pointPolygonTest(line,(cx,cy),False) >= 0:
                    if totalcount.count(id) == 0:
                        totalcount.append(id)
                        if new_class_name in detected_id:
                            id_counts[new_class_name] += 1

                            # Membuat nama frame deteksi dan memasukkan ke folder lokal
                            time_frame = datetime.now().strftime("%H-%M-%S")
                            frame_filename = f"{classfound}_frame_{frame_id}_time_{time_frame}.jpg"
                            frame_path = os.path.join(output_folder, frame_filename)
                            cv2.imwrite(frame_path, img)
                            detected_frames.append(frame_path)

            # Parameter untuk menampilkan text di video
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_size = 0.7
            font_thickness = 2
            font_color = (0, 0, 255)
            y_coordinate = 60

            # Menampilkan text total hasil deteksi di video
            cv2.putText(img, f"Total Count: {len(totalcount)}", (20, 25), font, font_size, font_color, font_thickness, cv2.LINE_AA)

            # Menampilkan text hasil deteksi setiap class di video
            for i, name in enumerate(classNames):
                text = f"{name}: {id_counts[class_mapping[name]]} "
                cv2.putText(img, text, (20, y_coordinate), font, font_size, font_color, font_thickness, cv2.LINE_AA)
                y_coordinate += 20

            # Menampilkan FPS di video
            elapsed_time = time.time() - starting_time
            fps = frame_id / elapsed_time
            cv2.putText(img, "FPS: " + str(round(fps, 2)), (500, 30), font, 0.8, (0, 0, 255), 2)

            out.write(img)
            
            # Menampilkan deteksi di video
            cv2.imshow('DETEKSI PENYAKIT DAUN TANAMAN TERUNG', img)
            if cv2.waitKey(30)&0xFF==27:     
                print("Detection stopped manually.")
                break


# -------------------------------------------------------------- KODE INTERRUPT
            
# Inisialisasi keyboard interrupt
except KeyboardInterrupt:
    print("Deteksi Selesai dan Hasilnya Akan Dikirim ke Email Melalui Telegram Bot")
    

# -------------------------------------------------------------- KODE AKHIR
    
# Menjalankan kode setelah interrupt
finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Memanggil add_detection_results
    add_detection_results(pdf, id_counts, class_mapping, classNames, output_folder_id)
    
    # Membuat file PDF dari parameter yang telah dibuat
    pdf.output(pdf_filename)
    print('PDF Tersimpan')

    # Memanggil upload_detected_frames_to_drive
    uploader.upload_detected_frames_to_drive(detected_frames, output_folder_id, uploaded_frames)

    # Memulai bot telegram
    bot = Bot(token=telegram_bot_token)

    updater.start_polling()
    updater.idle()
    