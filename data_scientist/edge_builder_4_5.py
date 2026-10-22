import pandas as pd
import numpy as np
import os
import sys
from itertools import combinations
from tqdm import tqdm

class EdgeBuilder:
    def __init__(self, input_csv=None, id_csv=None, output_dir=None):
        """
        Khởi tạo class Xây dựng Cạnh (Edges).
        Tạo liên kết giữa các sản phẩm dựa trên giả thuyết Homophily.
        """
        # 1. Thiết lập đường dẫn mặc định
        default_input = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\standard_dataset\fashion_preprocessed_dataset.csv"
        default_ids = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\image_features\image_feature_ids.csv"
        default_out_dir = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\graph_data"

        # 2. Cơ chế Fallback đường dẫn
        self.input_csv = input_csv if input_csv and os.path.exists(input_csv) else default_input
        self.id_csv = id_csv if id_csv and os.path.exists(id_csv) else default_ids
        self.output_dir = output_dir if output_dir else default_out_dir

        os.makedirs(self.output_dir, exist_ok=True)


    def _load_and_sync(self):
        """Nạp dữ liệu và đồng bộ hóa ID để đảm bảo chỉ số Index chính xác"""
        try:
            df_clean = pd.read_csv(self.input_csv)
            df_ids = pd.read_csv(self.id_csv)
            
            df_clean['id'] = df_clean['id'].astype(str)
            df_ids['id'] = df_ids['id'].astype(str)
            
            # Merge để giữ đúng thứ tự đã trích xuất features
            df_final = pd.merge(df_ids, df_clean, on='id', how='left')
            
            # Tạo mapping từ ID (chuỗi) sang Index (số nguyên 0 -> N-1)
            # Đây là "từ điển" cực kỳ quan trọng cho GNN
            id_to_idx = {str(id_val): i for i, id_val in enumerate(df_final['id'])}
            
            return df_final, id_to_idx
        except Exception as e:
            print(f"Lỗi nạp dữ liệu: {e}")
            sys.exit()


    def run_build(self):
        """Thực thi quy trình xây dựng danh sách cạnh (Edge List)"""
        # print("--- Bắt đầu xây dựng Edges cho Đồ thị ---")
        
        df_final, id_to_idx = self._load_and_sync()
        edge_list = []

        # 1. Tạo cạnh dựa trên Brand (Thương hiệu)
        # Mục đích: Nối các sản phẩm cùng hãng để GNN học phong cách thiết kế chung.
        # print("Đang nối cạnh theo Brand...")
        brand_groups = df_final.groupby('brand_label').indices
        for brand, indices in tqdm(brand_groups.items(), desc="Brand Edges"):
            if len(indices) > 1:
                # Kỹ thuật Sampling cho GPU 4GB: Nếu brand quá lớn, chỉ chọn ngẫu nhiên 5 hàng xóm
                if len(indices) > 100:
                    for u in indices:
                        neighbors = np.random.choice(indices, 5, replace=False)
                        for v in neighbors:
                            if u != v:
                                edge_list.append([u, v])
                else:
                    # Nếu nhóm nhỏ, nối tất cả các cặp (Fully Connected Subgraph)
                    for u, v in combinations(indices, 2):
                        edge_list.append([u, v])
                        edge_list.append([v, u]) # Đồ thị vô hướng

        # 2. Tạo cạnh dựa trên Article Type (Loại sản phẩm)
        # Mục đích: Nối các sản phẩm cùng loại (ví dụ: cùng là Giày) để học tính năng.
        # print("Đang nối cạnh theo Article Type...")
        type_groups = df_final.groupby('articleType_label').indices
        for a_type, indices in tqdm(type_groups.items(), desc="Type Edges"):
            if len(indices) > 1:
                for u in indices:
                    # Mỗi sản phẩm nối với 3 hàng xóm ngẫu nhiên cùng loại
                    num_neighbors = min(3, len(indices) - 1)
                    neighbors = np.random.choice(indices, num_neighbors, replace=False)
                    for v in neighbors:
                        if u != v:
                            edge_list.append([u, v])
                            edge_list.append([v, u])

        # 3. Chuẩn hóa và lưu trữ
        # print("Đang chuẩn hóa Edge Index...")
        # Chuyển thành định dạng COO (Coordinate Format) [2, E] chuẩn PyTorch Geometric
        edge_index = np.array(edge_list).T
        # Loại bỏ các cạnh trùng lặp để tiết kiệm bộ nhớ
        edge_index = np.unique(edge_index, axis=1)
        
        edge_out = os.path.join(self.output_dir, "edge_index.npy")
        mapping_out = os.path.join(self.output_dir, "id_to_idx_mapping.csv")

        np.save(edge_out, edge_index)
        pd.DataFrame(list(id_to_idx.items()), columns=['id', 'idx']).to_csv(mapping_out, index=False)

        # print("="*50)
        print(f"3_8 Xây dựng đồ thị hoàn tất")
        # print(f"- Tổng số Nodes: {len(df_final):,}")
        # print(f"- Tổng số Edges: {edge_index.shape[1]:,}")
        # print(f"- File cạnh lưu tại: {edge_out}")
        # print(f"- File mapping lưu tại: {mapping_out}")
        # print("="*50)
        return edge_out, mapping_out

if __name__ == "__main__":
    builder = EdgeBuilder()
    builder.run_build()