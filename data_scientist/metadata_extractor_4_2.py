import pandas as pd
import numpy as np
import os
import sys

class MetadataFeatureExtractor:
    def __init__(self, input_csv=None, id_csv=None, output_dir=None):
        """
        Khởi tạo class trích xuất Metadata.
        Đảm bảo dữ liệu Metadata khớp 100% với danh sách ID đã trích xuất ảnh.
        """
        # 1. Thiết lập đường dẫn mặc định
        default_input = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_ids = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
        default_out = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\metadata_features"

        # 2. Cơ chế Fallback đường dẫn
        self.input_csv = input_csv if input_csv and os.path.exists(input_csv) else default_input
        self.id_csv = id_csv if id_csv and os.path.exists(id_csv) else default_ids
        self.output_dir = output_dir if output_dir else default_out

        os.makedirs(self.output_dir, exist_ok=True)


    def run_extraction(self):
        """Thực hiện quy trình lọc và trích xuất vector Metadata"""
        print("--- Bắt đầu trích xuất Metadata Features ---")
        
        # 1. Nạp dữ liệu
        try:
            df_clean = pd.read_csv(self.input_csv)
            df_ids = pd.read_csv(self.id_csv)
            
            # Ép kiểu ID sang string để tránh lỗi merge
            df_clean['id'] = df_clean['id'].astype(str)
            df_ids['id'] = df_ids['id'].astype(str)
        except Exception as e:
            print(f"Lỗi nạp dữ liệu: {e}")
            return

        # 2. ĐỒNG BỘ HÓA (Crucial Step)
        # Chỉ lấy những sản phẩm đã trích xuất ảnh thành công để đảm bảo ma trận đồng nhất
        df_final = pd.merge(df_ids, df_clean, on='id', how='left')
        
        print(f"Tổng số sản phẩm khớp với dữ liệu ảnh: {len(df_final)}")

        # 3. Lựa chọn đặc trưng (Feature Selection)
        # Nhóm 1: Số (Numerical) - Đã được log/norm ở bước 2
        num_features = ['price_log', 'rating_norm']
        
        # Nhóm 2: One-hot (Categorical)
        one_hot_features = [col for col in df_final.columns if col.startswith(('gen_', 'use_', 'sea_'))]
        
        # Nhóm 3: Nhãn (Label)
        label_features = ['brand_label', 'articleType_label']

        # Tổng hợp danh sách cột
        selected_cols = num_features + one_hot_features + label_features
        print(f"Các cột được chọn ({len(selected_cols)} chiều): {selected_cols}")
        
        # 4. Trích xuất ma trận NumPy
        # Dùng float32 để tiết kiệm bộ nhớ và tương thích với PyTorch
        metadata_matrix = df_final[selected_cols].values.astype(np.float32)
        
        # 5. Lưu trữ
        save_path = os.path.join(self.output_dir, "metadata_features.npy")
        np.save(save_path, metadata_matrix)
        
        # print("="*50)
        print(f"3_5 Trích xuất đặc trưng metadata hoàn tất")
        # print(f"- Kích thước ma trận: {metadata_matrix.shape}")
        # print(f"- File lưu tại: {save_path}")
        # print("="*50)
        return save_path


if __name__ == "__main__":
    extractor = MetadataFeatureExtractor()
    extractor.run_extraction()