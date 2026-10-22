import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import sys
from wordcloud import WordCloud

class NormalizedDatasetEDA:
    def __init__(self, standard_csv=None, original_csv=None, output_dir=None):
        """
        Khởi tạo class EDA cho dữ liệu chuẩn hóa.
        Hệ thống sẽ so sánh giữa file Standard (sau xử lý) và Original (trước xử lý).
        """
        # 1. Cấu hình đường dẫn mặc định
        default_standard = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_original = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv"
        default_output = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\eda_results"

        # 2. Fallback logic
        self.standard_csv = standard_csv if standard_csv and os.path.exists(standard_csv) else default_standard
        self.original_csv = original_csv if original_csv and os.path.exists(original_csv) else default_original
        self.output_dir = output_dir if output_dir else default_output

        os.makedirs(self.output_dir, exist_ok=True)

        # 3. Load dữ liệu
        try:
            self.df_clean = pd.read_csv(self.standard_csv)
            self.df_raw = pd.read_csv(self.original_csv)
            # print(f"--- Đã load dữ liệu chuẩn hóa: {len(self.df_clean)} dòng ---")
            # print(f"--- Đã load dữ liệu gốc để so sánh: {len(self.df_raw)} dòng ---")
        except Exception as e:
            print(f"Lỗi load dữ liệu: {e}")
            sys.exit()


    def save_text_report(self, task_name, content):
        """Tiện ích lưu báo cáo văn bản"""
        file_path = os.path.join(self.output_dir, f"{task_name}.txt")
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)


    def verify_zero_null_1(self):
        task_name = "3_3_1_zero_null_check"
        print(f"Đang thực hiện {task_name}...")
        null_summary = self.df_clean.isnull().sum()
        total_null = null_summary.sum()
        
        report = f"Tổng số giá trị Null sau Preprocessing: {total_null}\n"
        report += "-"*30 + "\n" + null_summary.to_string()
        self.save_text_report(task_name, report)


    def check_price_distribution_2(self):
        task_name = "3_3_2_price_distribution"
        print(f"Đang thực hiện {task_name}...")

        # Tìm tên cột giá (linh hoạt camelCase/snake_case)
        price_raw = 'price' if 'price' in self.df_raw.columns else 'Price'
        price_log = 'price_log' if 'price_log' in self.df_clean.columns else 'price'

        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        sns.histplot(self.df_raw[price_raw], kde=True, ax=axes[0], color='red')
        axes[0].set_title('Phân phối Giá gốc (Skewed)')
        
        sns.histplot(self.df_clean[price_log], kde=True, ax=axes[1], color='blue')
        axes[1].set_title('Phân phối Giá sau Log Transformation')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{task_name}_comparison.png"), dpi=300)
        plt.close()

        skew_raw = self.df_raw[price_raw].skew()
        skew_clean = self.df_clean[price_log].skew()
        
        report = f"Skewness gốc (Original): {skew_raw:.2f}\n"
        report += f"Skewness sau Log (Processed): {skew_clean:.2f}\n"
        report += "-" * 50 + "\n"
        report += "Nhận xét: " + ("Thành công giảm độ lệch." if abs(skew_clean) < abs(skew_raw) else "Cần kiểm tra lại.")
        self.save_text_report(task_name, report)


    def analyze_deduplication_impact_3(self):
        task_name = "3_3_3_deduplication_impact"
        print(f"Đang thực hiện {task_name}...")
        
        raw_count = len(self.df_raw)
        clean_count = len(self.df_clean)
        
        # Tìm cột Category
        cat_col_raw = 'masterCategory' if 'masterCategory' in self.df_raw.columns else 'master_category'
        cat_col_clean = 'masterCategory' if 'masterCategory' in self.df_clean.columns else 'master_category'

        raw_cat = self.df_raw[cat_col_raw].value_counts()
        clean_cat = self.df_clean[cat_col_clean].value_counts()
        
        comparison_df = pd.DataFrame({'Before': raw_cat, 'After': clean_cat}).fillna(0)
        comparison_df.plot(kind='bar', figsize=(12, 6), color=['gray', 'orange'])
        plt.title('Tác động lọc trùng lên Category')
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
        plt.close()

        report = f"Số lượng dòng ban đầu: {raw_count:,}\n"
        report += f"Số lượng dòng hiện tại: {clean_count:,}\n"
        report += f"Tỷ lệ cắt giảm: {((raw_count - clean_count)/raw_count)*100:.2f}%\n"
        report += "\nChi tiết:\n" + comparison_df.to_string()
        self.save_text_report(task_name, report)


    def check_label_diversity_4(self):
        task_name = "3_3_4_label_diversity"
        print(f"Đang thực hiện {task_name}...")
        label_cols = [c for c in ['brand_label', 'productName_label', 'articleType_label'] if c in self.df_clean.columns]
        
        diversity = {col: self.df_clean[col].nunique() for col in label_cols}
        
        if 'brand_label' in self.df_clean.columns:
            top_brands = self.df_clean['brand_label'].value_counts().nlargest(20)
            plt.figure(figsize=(12, 6))
            sns.barplot(x=top_brands.index, y=top_brands.values, hue=top_brands.index, palette='magma', legend=False)
            plt.savefig(os.path.join(self.output_dir, f"{task_name}_plot.png"), dpi=300)
            plt.close()

        report = f"Thống kê Cardinality:\n" + "\n".join([f"- {k}: {v} unique" for k,v in diversity.items()])
        self.save_text_report(task_name, report)


    def check_onehot_sparsity_5(self):
        task_name = "3_3_5_onehot_sparsity"
        print(f"Đang thực hiện {task_name}...")
        onehot_cols = [col for col in self.df_clean.columns if col.startswith(('gen_', 'use_', 'sea_'))]
        
        if not onehot_cols: return

        fill_rates = self.df_clean[onehot_cols].mean() * 100
        sparsity_df = pd.DataFrame({'Column': onehot_cols, 'Fill Rate (%)': fill_rates}).sort_values(by='Fill Rate (%)', ascending=False)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(data=sparsity_df, x='Fill Rate (%)', y='Column', hue='Column', palette='viridis', legend=False)
        plt.axvline(x=1, color='r', linestyle='--')
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300, bbox_inches='tight')
        plt.close()
        self.save_text_report(task_name, sparsity_df.to_string(index=False))


    def analyze_text_shrinkage_6(self):
        task_name = "3_3_6_text_shrinkage"
        print(f"Đang thực hiện {task_name}...")
        
        # Check columns description/style_note
        desc_col = 'description' if 'description' in self.df_clean.columns else 'productDescription'
        sn_col = 'style_note' if 'style_note' in self.df_clean.columns else 'styleNote'

        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        if desc_col in self.df_clean.columns:
            desc_len = self.df_clean[self.df_clean[desc_col] != 'not found'][desc_col].astype(str).apply(lambda x: len(x.split()))
            sns.histplot(desc_len, bins=30, kde=True, ax=axes[0], color='purple')
            axes[0].set_title('Description Word Count')

        if sn_col in self.df_clean.columns:
            sn_len = self.df_clean[self.df_clean[sn_col] != 'not found'][sn_col].astype(str).apply(lambda x: len(x.split()))
            sns.histplot(sn_len, bins=30, kde=True, ax=axes[1], color='orange')
            axes[1].set_title('Style Note Word Count')

        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
        plt.close()


    def analyze_correlation_7(self):
        task_name = "3_3_7_feature_correlation"
        print(f"Đang thực hiện {task_name}...")
        num_cols = self.df_clean.select_dtypes(include=[np.number]).columns.tolist()
        important_cols = [c for c in ['price_log', 'rating_norm', 'brand_label', 'articleType_label'] if c in num_cols]
        
        if not important_cols: return

        plt.figure(figsize=(10, 8))
        sns.heatmap(self.df_clean[important_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f")
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
        plt.close()


    def generate_clean_wordcloud_8(self):
        task_name = "3_3_8_clean_wordcloud"
        print(f"Đang thực hiện {task_name}...")
        desc_col = 'description' if 'description' in self.df_clean.columns else 'productDescription'
        
        if desc_col in self.df_clean.columns:
            text = " ".join(self.df_clean[self.df_clean[desc_col] != 'not found'][desc_col].astype(str))
            if text.strip():
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
                wordcloud.to_file(os.path.join(self.output_dir, f"{task_name}.png"))


    def check_post_scaling_outliers_9(self):
        task_name = "3_3_9_post_scaling_boxplot"
        print(f"Đang thực hiện {task_name}...")
        num_cols = [c for c in ['price_log', 'rating_norm'] if c in self.df_clean.columns]
        
        if not num_cols: return
        plt.figure(figsize=(12, 5))
        for i, col in enumerate(num_cols):
            plt.subplot(1, len(num_cols), i+1)
            sns.boxplot(x=self.df_clean[col])
        plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
        plt.close()


    def evaluate_gnn_readiness_10(self):
        """Bước quan trọng nhất: Đánh giá khả năng kết nối đồ thị"""
        task_name = "3_3_10_gnn_readiness"
        print(f"Đang thực hiện {task_name}...")
        
        brand_col = 'brand_label' if 'brand_label' in self.df_clean.columns else 'brand_name'
        if brand_col in self.df_clean.columns:
            brand_counts = self.df_clean[brand_col].value_counts()
            
            plt.figure(figsize=(10, 6))
            sns.histplot(brand_counts, bins=50, log_scale=(True, False), color='salmon')
            plt.title('GNN Connectivity: Products per Brand')
            plt.savefig(os.path.join(self.output_dir, f"{task_name}.png"), dpi=300)
            plt.close()

            report = f"Tổng số Nodes: {len(self.df_clean):,}\n"
            report += f"Số cụm (Brands): {len(brand_counts)}\n"
            report += f"Cụm lớn nhất: {brand_counts.max()} nodes\n"
            report += f"Số node cô lập (1 prod/brand): {sum(brand_counts == 1)}\n"
            self.save_text_report(task_name, report)

    def run_all(self):
        # print("=== BẮT ĐẦU EDA TRÊN NORMALIZED DATASET ===")
        self.verify_zero_null_1()
        self.check_price_distribution_2()
        self.analyze_deduplication_impact_3()
        self.check_label_diversity_4()
        self.check_onehot_sparsity_5()
        self.analyze_text_shrinkage_6()
        self.analyze_correlation_7()
        self.generate_clean_wordcloud_8()
        self.check_post_scaling_outliers_9()
        self.evaluate_gnn_readiness_10()
        # print(f"=== HOÀN TẤT EDA. KẾT QUẢ TẠI: {self.output_dir} ===")

if __name__ == "__main__":
    eda_normalized = NormalizedDatasetEDA()
    eda_normalized.run_all()