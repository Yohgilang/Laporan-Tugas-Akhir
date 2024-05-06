
from ultralytics import YOLO

# Load a YOLOv8n PyTorch model
model = YOLO('D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\eggplant_desease.pt')

# Export the model
model.export(format='openvino')  

# Load the exported OpenVINO model
ov_model = YOLO('D:\\KULIAH\\_Tugas Akhir\\Project\\Code\\deteksi_penyakit _tanaman_terung_TA\\eggplant_desease_openvino_model/')





