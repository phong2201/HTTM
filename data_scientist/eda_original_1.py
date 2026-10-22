import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
import os
import io
import sys

class OriginalDatasetEDA:
    def __init__(self, input_path=None, output_dir=None, image_dir=None):
        """
        Khởi tạo class EDA. 
        Nếu không truyền path, sẽ sử dụng đường dẫn mặc định của Khải.
        """
        # 1. Thiết lập các đường dẫn mặc định
        default_input = r'E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv'
        default_output = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\eda_results"
        default_images = r"E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\images"

        # 2. Kiểm tra và gán giá trị (Nếu lỗi/không tồn tại thì lấy mặc định)
        self.input_path = input_path if input_path and os.path.exists(input_path) else default_input
        self.output_dir = output_dir if output_dir else default_output
        self.image_dir = image_dir if image_dir and os.path.exists(image_dir) else default_images

        # Tạo thư mục output nếu chưa có
        os.makedirs(self.output_dir, exist_ok=True)

        # 3. Load dữ liệu
        try:
            self.df = pd.read_csv(self.input_path)
            # print(f"--- Dữ liệu đã được load từ: {self.input_path} ---")
        except Exception as e:
            print(f"Lỗi: Không thể load file CSV. {e}")
            sys.exit()


    def save_text_report(self, task_name, content):
        """Hỗ trợ lưu nội dung văn bản vào file .txt"""
        file_path = os.path.join(self.output_dir, f"{task_name}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


    def data_profiling_1(self):
        task_name = "3_1_1_data_profiling"
        print(f"Đang thực hiện {task_name}...")
        
        buffer = io.StringIO()
        self.df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        report = [
            "="*50 + "\n1. DATA PROFILING\n" + "="*50,
            "\n[INFO]\n" + info_str,
            "\n[DESCRIBE]\n" + self.df.describe().to_string(),
            "\n[UNIQUE VALUES]"
        ]
        
        categorical_cols = ['gender', 'masterCategory', 'subCategory', 'season', 'usage']
        for col in categorical_cols:
            if col in self.df.columns:
                report.append(f"- {col}: {self.df[col].nunique()} giá trị")
                
        self.save_text_report(task_name, "\n".join(report))


    def missing_value_analysis_2(self):
        task_name = "3_1_2_missing_value_analysis"
        print(f"Đang thực hiện {task_name}...")
        
        null_counts = self.df.isnull().sum()
        null_percentages = (self.df.isnull().sum() / len(self.df)) * 100
        missing_data = pd.DataFrame({
            'Total Null': null_counts,
            'Percentage (%)': null_percentages
        }).sort_values(by='Percentage (%)', ascending=False)

        self.save_text_report(task_name, missing_data.to_string())

        plt.figure(figsize=(12, 6))
        sns.barplot(x=missing_data.index, y=missing_data['Percentage (%)'], hue=missing_data.index, palette='viridis', legend=False)
        plt.xticks(rotation=45, ha='right')
        plt.title('Tỷ lệ % dữ liệu bị thiếu')
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
        plt.close()


    def category_distribution_3(self):
        task_name = "3_1_3_category_distribution"
        print(f"Đang thực hiện {task_name}...")
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        sns.countplot(data=self.df, y='masterCategory', hue='masterCategory', ax=axes[0], palette='magma', legend=False, order=self.df['masterCategory'].value_counts().index)
        
        top_sub = self.df['subCategory'].value_counts().nlargest(10).index
        sns.countplot(data=self.df, y='subCategory', hue='subCategory', ax=axes[1], palette='viridis', legend=False, order=top_sub)
        
        sns.countplot(data=self.df, x='gender', hue='gender', ax=axes[2], palette='coolwarm', legend=False)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{task_name}_counts.png"), dpi=300)
        plt.close()

        plt.figure(figsize=(10, 6))
        usage_season = pd.crosstab(self.df['usage'], self.df['season'])
        sns.heatmap(usage_season, annot=True, fmt='d', cmap='YlGnBu')
        plt.savefig(os.path.join(self.output_dir, f"{task_name}_heatmap.png"), dpi=300)
        plt.close()


    def attribute_variance_4(self):
        task_name = "3_1_4_attribute_variance"
        print(f"Đang thực hiện {task_name}...")
        
        deep_attrs = ['fabric', 'fit', 'neck', 'occasion']
        # Chuyển đổi sang lowercase để khớp với metadata mới của Khải
        deep_attrs_lower = [c.lower() for c in deep_attrs]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for i, col in enumerate(deep_attrs):
            # Kiểm tra cả hoa lẫn thường cho linh hoạt
            target_col = col if col in self.df.columns else col.lower()
            if target_col in self.df.columns:
                top_vals = self.df[target_col].value_counts().nlargest(10)
                sns.barplot(x=top_vals.values, y=top_vals.index, hue=top_vals.index, ax=axes[i], palette='rocket', legend=False)
                axes[i].set_title(f'Top 10: {col}')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
        plt.close()


    def price_discount_analysis_5(self):
        task_name = "3_1_5_price_analysis"
        print(f"Đang thực hiện {task_name}...")
        
        # Xử lý tên cột linh hoạt cho discountedPrice hoặc discounted_price
        d_price_col = 'discountedPrice' if 'discountedPrice' in self.df.columns else 'discounted_price'
        
        if d_price_col in self.df.columns:
            self.df['discount_pct'] = ((self.df['price'] - self.df[d_price_col]) / (self.df['price'] + 0.001)) * 100

            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            sns.histplot(self.df['price'], bins=50, kde=True, ax=axes[0], color='blue')
            sns.histplot(self.df['discount_pct'], bins=30, kde=True, ax=axes[1], color='green')
            plt.savefig(os.path.join(self.output_dir, f"{task_name}_dist.png"), dpi=300)
            plt.close()

        plt.figure(figsize=(10, 5))
        sns.boxplot(x=self.df['price'], color='cyan')
        plt.savefig(os.path.join(self.output_dir, f"{task_name}_boxplot.png"), dpi=300)
        plt.close()


    def rating_insights_6(self):
        task_name = "3_1_6_rating_insights"
        print(f"Đang thực hiện {task_name}...")
        
        # Xử lý tên cột myntraRating hoặc myntra_rating
        rating_col = 'myntraRating' if 'myntraRating' in self.df.columns else 'myntra_rating'
        
        if rating_col in self.df.columns:
            plt.figure(figsize=(8, 5))
            sns.countplot(x=rating_col, data=self.df, hue=rating_col, palette='viridis', legend=False)
            plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
            plt.close()

            zero_rating_pct = (self.df[rating_col] == 0).sum() / len(self.df) * 100
            self.save_text_report(task_name, f"Tỷ lệ sản phẩm có Rating = 0: {zero_rating_pct:.2f}%")


    def text_semantic_eda_7(self):
        task_name = "3_1_7_text_semantic"
        print(f"Đang thực hiện {task_name}...")
        
        # Style Note
        sn_col = 'style_note' if 'style_note' in self.df.columns else 'styleNote'
        # Description
        desc_col = 'description' if 'description' in self.df.columns else 'productDescription'

        plt.figure(figsize=(16, 6))
        if sn_col in self.df.columns:
            self.df['style_note_len'] = self.df[sn_col].str.split().str.len().fillna(0).astype(int)
            plt.subplot(1, 2, 1)
            sns.histplot(self.df['style_note_len'], bins=30, color='purple')
            plt.title('Độ dài Style Note')

        if desc_col in self.df.columns:
            self.df['desc_len'] = self.df[desc_col].str.split().str.len().fillna(0).astype(int)
            plt.subplot(1, 2, 2)
            sns.histplot(self.df['desc_len'], bins=30, color='orange')
            plt.title('Độ dài Description')

        plt.savefig(os.path.join(self.output_dir, f"{task_name}_len.png"), dpi=300)
        plt.close()

        all_names = " ".join(self.df['productDisplayName'].dropna().astype(str).tolist())
        if all_names.strip():
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_names)
            wordcloud.to_file(os.path.join(self.output_dir, f"{task_name}_wordcloud.png"))


    def brand_dominance_8(self):
        task_name = "3_1_8_brand_dominance"
        print(f"Đang thực hiện {task_name}...")
        
        brand_col = 'brandName' if 'brandName' in self.df.columns else 'brand_name'
        if brand_col in self.df.columns:
            top_brands = self.df[brand_col].value_counts().nlargest(20)
            plt.figure(figsize=(12, 8))
            sns.barplot(x=top_brands.values, y=top_brands.index, hue=top_brands.index, palette='Spectral', legend=False)
            plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
            plt.close()

            report = [
                f"Tổng số thương hiệu: {self.df[brand_col].nunique()}",
                f"Thương hiệu 1 sản phẩm: {(self.df[brand_col].value_counts() == 1).sum()}"
            ]
            self.save_text_report(task_name, "\n".join(report))


    def consistency_check_9(self):
        task_name = "3_1_9_consistency_check"
        print(f"Đang thực hiện {task_name}...")
        
        if not os.path.exists(self.image_dir):
            self.save_text_report(task_name, f"Lỗi: Thư mục ảnh không tồn tại tại {self.image_dir}")
            return

        image_files = set([f.split('.')[0] for f in os.listdir(self.image_dir) if f.endswith(('.jpg', '.png'))])
        csv_ids = set(self.df['id'].astype(str))

        report = [
            f"Số sản phẩm trong CSV: {len(csv_ids)}",
            f"Số file ảnh: {len(image_files)}",
            f"Thiếu ảnh: {len(csv_ids - image_files)}",
            f"Ảnh dư (Orphan): {len(image_files - csv_ids)}"
        ]
        self.save_text_report(task_name, "\n".join(report))


    def duplicate_check_10(self):
        task_name = "3_1_10_duplicate_check"
        print(f"Đang thực hiện {task_name}...")
        
        soft_duplicates = self.df[self.df.duplicated(subset=['productDisplayName', 'gender', 'baseColour'], keep=False)]
        
        report = [
            f"Nghi ngờ trùng lặp mềm: {len(soft_duplicates)}",
            f"Trùng lặp ID tuyệt đối: {self.df.duplicated(subset=['id']).sum()}"
        ]
        self.save_text_report(task_name, "\n".join(report))

    def run_all(self):
        """Kích hoạt toàn bộ Pipeline EDA"""
        # print("=== Bắt đầu chạy EDA trên Original Dataset ===")
        self.data_profiling_1()
        self.missing_value_analysis_2()
        self.category_distribution_3()
        self.attribute_variance_4()
        self.price_discount_analysis_5()
        self.rating_insights_6()
        self.text_semantic_eda_7()
        self.brand_dominance_8()
        self.consistency_check_9()
        self.duplicate_check_10()
        # print(f"=== EDA hoàn tất. Kết quả được lưu tại: {self.output_dir} ===")

if __name__ == "__main__":
    eda_tool = OriginalDatasetEDA()
    eda_tool.run_all()