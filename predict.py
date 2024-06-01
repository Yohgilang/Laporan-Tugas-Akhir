from ultralytics import YOLO

# import csv

model = YOLO('D:\KULIAH\_Tugas Akhir\Project\Code\deteksi_penyakit _tanaman_terung_TA\eggplant_desease.pt', task='detect') 

results = model(source= "D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\test", show=False, conf=0.3, save=True)
