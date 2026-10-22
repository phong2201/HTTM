import pandas as pd
import numpy as np
import os
import torch
import sys
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class TextFeatureExtractor:
    def __init__(self, input_csv=None, id_csv=None, output_dir=None, model_name='all-MiniLM-L6-v2', batch_size=128):
        """
        Khởi tạo class trích xuất Text Embeddings.
        Sử dụng MiniLM để cân bằng giữa độ chính xác và tốc độ trên GPU 4GB.
        """
        # 1. Thiết lập đường dẫn mặc định
        default_input = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_ids = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
        default_out = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\text_features"

        # 2. Cơ chế Fallback đường dẫn
        self.input_csv = input_csv if input_csv and os.path.exists(input_csv) else default_input
        self.id_csv = id_csv if id_csv and os.path.exists(id_csv) else default_ids
        self.output_dir = output_dir if output_dir else default_out
        self.batch_size = batch_size
        self.model_name = model_name

        os.makedirs(self.output_dir, exist_ok=True)

        # 3. Thiết lập thiết bị
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(f"--- Text Extractor khởi tạo trên thiết bị: {self.device} ---")


    def _combine_text_context(self, row):
        """Gộp các trường văn bản để tạo ngữ cảnh phong phú nhất cho SBERT"""
        # Xử lý linh hoạt CamelCase và snake_case từ DB
        name = str(row.get('productDisplayName', row.get('product_display_name', '')))
        brand = str(row.get('brandName', row.get('brand_name', '')))
        desc = str(row.get('description', ''))
        style = str(row.get('style_note', row.get('styleNote', '')))
        
        # Loại bỏ các từ khóa "not found" để không làm nhiễu vector
        components = [name, brand, desc, style]
        clean_components = [c for c in components if c.lower() != 'not found' and c.strip() != ""]
        
        return " ".join(clean_components).strip()


    def run_extraction(self):
        """Quy trình nạp model và trích xuất vector văn bản hàng loạt"""
        # print(f"--- Bắt đầu trích xuất Text Embeddings ({self.model_name}) ---")
        
        # 1. Nạp dữ liệu và Đồng bộ hóa ID
        try:
            df_clean = pd.read_csv(self.input_csv)
            df_ids = pd.read_csv(self.id_csv)
            
            df_clean['id'] = df_clean['id'].astype(str)
            df_ids['id'] = df_ids['id'].astype(str)
            
            # Chỉ lấy những sản phẩm đã có ảnh để đảm bảo tính nhất quán của ma trận
            df_final = pd.merge(df_ids, df_clean, on='id', how='left')
        except Exception as e:
            print(f"Lỗi nạp dữ liệu: {e}")
            return

        # 2. Chuẩn bị danh sách câu (Context Building)
        print("Đang xây dựng ngữ cảnh văn bản...")
        sentences = df_final.apply(self._combine_text_context, axis=1).tolist()
        
        # 3. Nạp model Sentence-Transformer
        # print(f"Đang nạp model {self.model_name}...")
        model = SentenceTransformer(self.model_name, device=self.device)
        
        # 4. Trích xuất Embeddings theo Batch
        # print(f"Bắt đầu trích xuất cho {len(sentences)} bản ghi...")
        text_embeddings = model.encode(
            sentences, 
            batch_size=self.batch_size, 
            show_progress_bar=True, 
            convert_to_numpy=True
        )

        # 5. Lưu trữ kết quả
        save_path = os.path.join(self.output_dir, "text_features.npy")
        np.save(save_path, text_embeddings)
        
        # print("="*50)
        print(f"3_6 Trích xuất văn bản hoàn tất")
        # print(f"- Kích thước ma trận: {text_embeddings.shape}")
        # print(f"- File lưu tại: {save_path}")
        # print("="*50)
        return save_path

if __name__ == "__main__":
    extractor = TextFeatureExtractor(batch_size=128)
    extractor.run_extraction()