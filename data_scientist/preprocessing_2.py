import pandas as pd
import numpy as np
import os
import re
import cv2
import sys
from sklearn.preprocessing import LabelEncoder
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

class FashionPreprocessor:
    def __init__(self, input_csv=None, output_csv=None, image_dir=None, processed_img_dir=None):
        """
        Khởi tạo class Preprocessing.
        Nếu đường dẫn truyền vào không hợp lệ, sẽ sử dụng đường dẫn mặc định của Khải.
        """
        # 1. Cấu hình đường dẫn mặc định
        default_input = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv"
        default_output = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_img = r"E:\Hcmut material\AI\Intelligence System\fashion-dataset\images"
        default_processed_img = r"E:\Hcmut material\AI\Intelligence System\fashion-dataset\processed_images"

        # 2. Kiểm tra và gán giá trị (Fallback)
        self.input_csv = input_csv if input_csv and os.path.exists(input_csv) else default_input
        self.output_csv = output_csv if output_csv else default_output
        self.image_dir = image_dir if image_dir and os.path.exists(image_dir) else default_img
        self.processed_img_dir = processed_img_dir if processed_img_dir else default_processed_img

        # Tạo thư mục đầu ra nếu chưa có
        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)
        os.makedirs(self.processed_img_dir, exist_ok=True)

        # 3. Chuẩn bị NLTK
        try:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()

        # 4. Load dữ liệu
        try:
            self.df = pd.read_csv(self.input_csv)
            # print(f"--- Đã nạp dữ liệu từ: {self.input_csv} ---")
        except Exception as e:
            print(f"Lỗi: Không thể nạp file CSV. {e}")
            sys.exit()

    def clean_text(self, text):
        """Hàm dọn dẹp văn bản chuyên sâu"""
        if pd.isna(text) or str(text).lower() == 'nan' or text == "":
            return "not found"
        
        try:
            text = text.encode('latin1').decode('utf-8')
        except:
            pass

        # Xóa HTML tags, ký tự non-ASCII và chuẩn hóa
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        words = text.lower().split()
        words = [w for w in words if w not in self.stop_words and len(w) > 1]
        
        result = " ".join(words)
        return result if result != "" else "not found"


    def filter_missing_images(self):
        """Bước 1: Lọc bỏ những sản phẩm không có file ảnh vật lý"""
        if not os.path.exists(self.image_dir):
            print("Cảnh báo: Thư mục ảnh không tồn tại. Bỏ qua bước lọc ảnh.")
            return

        image_files = set([f.split('.')[0] for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))])
        self.df['id_str'] = self.df['id'].astype(str)
        initial_len = len(self.df)
        self.df = self.df[self.df['id_str'].isin(image_files)]
        print(f"3_2_1. Đã lọc ảnh. Còn lại: {len(self.df)}/{initial_len} dòng.")


    def handle_missing_values(self):
        """Bước 2: Xử lý giá trị Null dựa trên logic của Khải"""
        # Áp dụng cho cả tên cột CamelCase và snake_case
        name_cols = ['brandName', 'brand_name', 'productDisplayName', 'product_display_name']
        for col in name_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("not found")

        high_null = ['Neck', 'neck', 'Fit', 'fit', 'Occasion', 'occasion', 'Fabric', 'fabric']
        for col in high_null:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna("Unknown")

        low_null = ['usage', 'season', 'baseColour', 'base_colour']
        for col in low_null:
            if col in self.df.columns:
                mode_val = self.df[col].mode()
                self.df[col] = self.df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")
        print("3_2_2. Đã xử lý giá trị thiếu.")


    def deduplicate(self):
        """Bước 3: Lọc trùng lặp dựa trên thuộc tính và độ dài mô tả"""
        desc_col = 'description' if 'description' in self.df.columns else 'productDescription'
        brand_col = 'brandName' if 'brandName' in self.df.columns else 'brand_name'
        name_col = 'productDisplayName' if 'productDisplayName' in self.df.columns else 'product_display_name'
        color_col = 'baseColour' if 'baseColour' in self.df.columns else 'base_colour'

        if desc_col in self.df.columns:
            self.df['desc_len'] = self.df[desc_col].astype(str).str.len()
            self.df = self.df.sort_values(by='desc_len', ascending=False)
            
            subset_cols = [name_col, brand_col, color_col, 'gender']
            subset_cols = [c for c in subset_cols if c in self.df.columns]
            
            self.df = self.df.drop_duplicates(subset=subset_cols, keep='first')
            self.df = self.df.drop(columns=['desc_len'])
            print(f"3_2_3. Đã lọc trùng lặp. Còn lại: {len(self.df)} dòng.")


    def clean_text_columns(self):
        """Bước 4: Tiền xử lý các cột văn bản"""
        text_cols = ['description', 'style_note', 'styleNote', 'productDescription']
        for col in text_cols:
            if col in self.df.columns:
                print(f"--- Đang làm sạch cột: {col}")
                self.df[col] = self.df[col].apply(self.clean_text)


    def encode_features(self):
        """Bước 5: Mã hóa nhãn và One-hot"""
        # Label Encoding cho các cột phân loại cao
        for col, label in [('brandName', 'brand_label'), ('brand_name', 'brand_label'), 
                           ('productDisplayName', 'productName_label'), ('product_display_name', 'productName_label'),
                           ('articleType', 'articleType_label')]:
            if col in self.df.columns:
                le = LabelEncoder()
                self.df[label] = le.fit_transform(self.df[col].astype(str))

        # One-hot cho các trường định danh thấp (Gender, Usage, Season)
        cat_cols = ['gender', 'usage', 'season']
        cat_cols = [c for c in cat_cols if c in self.df.columns]
        if cat_cols:
            self.df = pd.get_dummies(self.df, columns=cat_cols, prefix=[c[:3] for c in cat_cols], dtype=int)
        print("3_2_4. Đã mã hóa các đặc trưng phân loại.")


    def scale_numerical(self):
        """Bước 6: Chuẩn hóa dữ liệu số (Price log & Rating norm)"""
        if 'price' in self.df.columns:
            self.df['price_log'] = np.log1p(self.df['price'])
        
        rating_col = 'myntraRating' if 'myntraRating' in self.df.columns else 'myntra_rating'
        if rating_col in self.df.columns:
            self.df['rating_norm'] = self.df[rating_col] / 5.0
        print("3_2_5. Đã chuẩn hóa dữ liệu số.")


    def process_images(self, resize_dim=(224, 224)):
        """Bước 7: Resize ảnh vật lý (Optional - mặc định tắt để tiết kiệm thời gian)"""
        # Nếu muốn chạy, hãy gọi hàm này thủ công
        print(f"6. Bắt đầu Resize ảnh sang {resize_dim}...")
        count = 0
        for idx, row in self.df.iterrows():
            img_id = row['id_str']
            img_path = os.path.join(self.image_dir, f"{img_id}.jpg")
            if os.path.exists(img_path):
                img = cv2.imread(img_path)
                if img is not None:
                    img_resized = cv2.resize(img, resize_dim)
                    cv2.imwrite(os.path.join(self.processed_img_dir, f"{img_id}.jpg"), img_resized)
                    count += 1
            if count % 5000 == 0 and count > 0: print(f"   > Đã xử lý {count} ảnh...")
        # print(f"--- Hoàn tất xử lý {count} ảnh.")


    def run_all(self, process_imgs=False):
        """Thực thi toàn bộ quy trình Pipeline"""
        # print("=== Bắt đầu quy trình tiền xử lý (PREPROCESSING) ===")
        self.filter_missing_images()
        self.handle_missing_values()
        self.deduplicate()
        self.clean_text_columns()
        self.encode_features()
        self.scale_numerical()
        
        if process_imgs:
            self.process_images()

        # Lưu file cuối cùng
        if 'id_str' in self.df.columns:
            self.df = self.df.drop(columns=['id_str'])
            
        self.df.to_csv(self.output_csv, index=False, encoding='utf-8-sig')
        # print(f"=== Tiền xử lí hoàn tất. File lưu tại: {self.output_csv} ===")

if __name__ == "__main__":
    preprocessor = FashionPreprocessor()
    preprocessor.run_all(process_imgs=False)