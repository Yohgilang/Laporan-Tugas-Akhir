# Library konfigurasi google drive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
import os


# Parameter untuk upload frame ke google drive dan lokal
uploaded_frames = set()
detected_frames = [] 
output_folder = "detected_frames"
folder_id = 'isi bagian ini dengan ID Folder Google Drive'  
upload_frame = []
gauth = GoogleAuth()
drive = GoogleDrive(gauth)


class DriveUploader:
    def __init__(self):
        self.gauth = GoogleAuth()
        self.drive = GoogleDrive(self.gauth)
        self.output_folder = output_folder
        self.folder_id = folder_id
        self.uploaded_frames = set()
        self.upload_frame = []

    # Fungsi untuk konfigurasi autentikasi google drive
    def initialize_auth(self):
        self.gauth.DEFAULT_SETTINGS['client_config_file'] = "D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\client_secrets.json"          
        self.gauth.LoadCredentialsFile("D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\mycreds.txt")
        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
        elif self.gauth.access_token_expired:
            self.gauth.Refresh()
        else:
            self.gauth.Authorize()
        self.gauth.SaveCredentialsFile("D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\mycreds.txt")

    # Fungsi untuk membuat folder di google drive
    def create_folder_gdrive(self, folder_id):
        current_datetime = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
        folder_name = f"output_deteksi_{current_datetime}"
        folder_metadata = {
                'title': folder_name,
                'parents': [{'id': folder_id}],  
                'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive.CreateFile(folder_metadata)
        folder.Upload()
        print(f"Folder {folder_name} berhasil dibuat di Google Drive.")
        return folder['id']

    # Fungsi untuk mengunggah frame deteksi ke google drive
    def upload_frame_to_drive(self, frame_path, output_folder_id):
        try:
            file = self.drive.CreateFile({'parents': [{'id': output_folder_id}]})
            file.SetContentFile(frame_path)
            file['title'] = os.path.basename(frame_path)  
            file.Upload()
            print(f"Frame {frame_path} berhasil diunggah ke Google Drive.")

            # Tambahkan frame_path ke list upload_frame
            upload_frame.append(frame_path)

        except Exception as e:
            print(f"Error saat mengunggah frame {frame_path} ke Google Drive:", e)

    # Fungsi untuk mengatur unggahan frame deteksi agar tidak double
    def upload_detected_frames_to_drive(self, detected_frames, output_folder_id, uploaded_frames):
        for frame_path in detected_frames:
            if frame_path not in uploaded_frames:
                self.upload_frame_to_drive(frame_path, output_folder_id)
                uploaded_frames.add(frame_path) 

        # Memberikan pesan jika semua frame telah terunggah ke google drive
        folder_path = 'D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\detected_frames'
        total_frames = len(os.listdir(folder_path))
        if len(upload_frame) == total_frames:
            print("Seluruh frame deteksi telah selesai terkirim ke Google Drive")
        