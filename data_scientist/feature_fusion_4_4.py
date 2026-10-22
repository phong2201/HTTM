import numpy as np
import os
import sys

class FeatureFusion:
    def __init__(self, visual_path=None, text_path=None, meta_path=None, output_dir=None):
        """
        Khởi tạo class Hợp nhất đặc trưng.
        Gộp các vector từ 3 nguồn: Image, Text, và Metadata thành một Node Feature duy nhất.
        """
        # 1. Cấu hình đường dẫn mặc định
        default_visual = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_features_resnet18.npy"
        default_text = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\text_features\text_features.npy"
        default_meta = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\metadata_features\metadata_features.npy"
        default_out_dir = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\final_node_features"

        # 2. Cơ chế Fallback
        self.visual_path = visual_path if visual_path and os.path.exists(visual_path) else default_visual
        self.text_path = text_path if text_path and os.path.exists(text_path) else default_text
        self.meta_path = meta_path if meta_path and os.path.exists(meta_path) else default_meta
        self.output_dir = output_dir if output_dir else default_out_dir

        os.makedirs(self.output_dir, exist_ok=True)


    def run_fusion(self):
        """Thực hiện quy trình hợp nhất và chuẩn hóa vector đa phương thức"""
        # print("--- Đang bắt đầu quy trình Feature Fusion ---")
        
        # 1. Nạp các ma trận đặc trưng
        try:
            visual_feat = np.load(self.visual_path) # 512 chiều từ ResNet-18
            text_feat = np.load(self.text_path)     # 384 chiều từ MiniLM
            meta_feat = np.load(self.meta_path)     # ~15 chiều từ Metadata
        except Exception as e:
            print(f"Lỗi nạp file .npy: {e}")
            return

        # Kiểm tra tính đồng bộ của số lượng hàng
        if not (visual_feat.shape[0] == text_feat.shape[0] == meta_feat.shape[0]):
            print(f"Cảnh báo: Số lượng bản ghi không khớp! V: {visual_feat.shape[0]}, T: {text_feat.shape[0]}, M: {meta_feat.shape[0]}")
            print("Vui lòng kiểm tra lại bước đồng bộ ID ở các script Extractor trước đó.")
            return

        # print(f"Kích thước Visual: {visual_feat.shape}")
        # print(f"Kích thước Text:   {text_feat.shape}")
        # print(f"Kích thước Meta:   {meta_feat.shape}")

        # 2. Hợp nhất (Concatenation)
        # Nối theo chiều ngang (axis=1) để tạo một vector dài khoảng 911+ chiều
        final_features = np.concatenate([visual_feat, text_feat, meta_feat], axis=1)

        # 3. Chuẩn hóa L2 (L2 Normalization)
        # Giúp đưa tất cả vector về cùng một thang đo (độ dài bằng 1)
        # Điều này cực kỳ quan trọng cho Cosine Similarity và sự ổn định của GNN sau này.
        # print("Đang thực hiện chuẩn hóa L2...")
        norms = np.linalg.norm(final_features, axis=1, keepdims=True)
        norms[norms == 0] = 1
        final_features = final_features / norms

        # 4. Lưu ma trận cuối cùng
        save_path = os.path.join(self.output_dir, "final_node_features.npy")
        np.save(save_path, final_features.astype(np.float32))

        # print("="*50)
        print(f"3_7 Hoàn thành Feature Fusion")
        # print(f"- Ma trận Node Features: {final_features.shape}")
        # print(f"- Mỗi sản phẩm là 1 vector {final_features.shape[1]} chiều.")
        # print(f"- File lưu tại: {save_path}")
        # print("="*50)
        return save_path


if __name__ == "__main__":
    fuser = FeatureFusion()
    fuser.run_fusion()