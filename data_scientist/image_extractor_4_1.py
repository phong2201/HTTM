import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm

# Định nghĩa dataset
class FashionImageDataset(Dataset):
    def __init__(self, csv_data, img_dir, transform=None):
        """
        Dùng trực tiếp DataFrame đã được lọc thay vì đọc file từ đầu.
        """
        self.data = csv_data
        self.img_dir = img_dir
        self.transform = transform


    def __len__(self):
        return len(self.data)


    def __getitem__(self, idx):
        img_id = self.data.iloc[idx]['id']
        img_path = os.path.join(self.img_dir, f"{img_id}.jpg")
        
        try:
            image = Image.open(img_path).convert('RGB')
        except Exception as e:
            image = Image.new('RGB', (224, 224), (0, 0, 0))
            
        if self.transform:
            image = self.transform(image)
            
        return image, str(img_id)


class ImageFeatureExtractor:
    def __init__(self, input_csv=None, image_dir=None, output_dir=None, batch_size=64):
        # 1. Cấu hình đường dẫn mặc định
        default_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_img = r"E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\processed_images"
        default_out = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features"

        self.input_csv = input_csv if input_csv and os.path.exists(input_csv) else default_csv
        self.image_dir = image_dir if image_dir and os.path.exists(image_dir) else default_img
        self.output_dir = output_dir if output_dir else default_out
        self.batch_size = batch_size

        os.makedirs(self.output_dir, exist_ok=True)

        # 2. Thiết lập thiết bị
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"--- Extractor khởi tạo trên thiết bị: {self.device} ---")

        # 3. Định nghĩa Transforms (Chuẩn hóa theo ImageNet)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])


    def _get_model(self):
        """Khởi tạo ResNet-18 và loại bỏ lớp Fully Connected (FC)"""
        print("Đang nạp mô hình ResNet-18...")
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        model.fc = nn.Identity() 
        model = model.to(self.device)
        model.eval()
        return model


    def run_extraction(self):
        """Quy trình trích xuất đặc trưng hàng loạt"""
        # 1. Load và lọc dữ liệu
        raw_df = pd.read_csv(self.input_csv)
        raw_df['id'] = raw_df['id'].astype(str)
        
        existing_files = set([f.split('.')[0] for f in os.listdir(self.image_dir) if f.endswith('.jpg')])
        filtered_df = raw_df[raw_df['id'].isin(existing_files)].copy()
        
        # print(f"Bắt đầu trích xuất cho {len(filtered_df)} sản phẩm hợp lệ.")

        dataset = FashionImageDataset(filtered_df, self.image_dir, transform=self.transform)
        dataloader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False, num_workers=2, pin_memory=True)

        model = self._get_model()
        
        all_features = []
        all_ids = []

        # 2. Thực hiện trích xuất (No Gradient để tiết kiệm VRAM)
        with torch.no_grad():
            for inputs, ids in tqdm(dataloader, desc="Đang trích xuất ảnh"):
                inputs = inputs.to(self.device)
                features = model(inputs)
                
                # Chuyển về CPU để tránh tràn bộ nhớ GPU
                all_features.append(features.cpu().numpy())
                all_ids.extend(ids)

        # 3. Tổng hợp và lưu trữ
        # print("\nĐang đóng gói ma trận đặc trưng...")
        feature_matrix = np.vstack(all_features)
        
        feat_save_path = os.path.join(self.output_dir, "image_features_resnet18.npy")
        id_save_path = os.path.join(self.output_dir, "image_feature_ids.csv")

        np.save(feat_save_path, feature_matrix)
        pd.DataFrame(all_ids, columns=['id']).to_csv(id_save_path, index=False)

        # print("="*50)
        print(f"3_4 Trích xuất đặc trưng ảnh hoàn tất")
        # print(f"- Ma trận đặc trưng: {feature_matrix.shape}")
        # print(f"- File đặc trưng: {feat_save_path}")
        # print(f"- File mapping ID: {id_save_path}")
        # print("="*50)


if __name__ == "__main__":
    extractor = ImageFeatureExtractor(batch_size=64)
    extractor.run_extraction()