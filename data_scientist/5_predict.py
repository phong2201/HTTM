import numpy as np
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity

path_embeddings = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\models\final_gnn_embeddings\final_gnn_embeddings.npy"
path_mapping = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\edge_matrix_features\id_to_idx_mapping.csv"
path_metadata = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\orignal_dataset\fashion_original_dataset.csv"

def load_inference_data():
    embeddings = np.load(path_embeddings)
    mapping = pd.read_csv(path_mapping)
    metadata = pd.read_csv(path_metadata)
    mapping['id'] = mapping['id'].astype(str)
    metadata['id'] = metadata['id'].astype(str)
    return embeddings, mapping, metadata

def recommend_from_list(input_id_list, embeddings, mapping, metadata, top_k=10):
    # 1. Chuyển ID sang Index và lấy các vector tương ứng
    valid_indices = []
    input_ids_str = [str(i) for i in input_id_list]
    
    for rid in input_ids_str:
        if rid in mapping['id'].values:
            idx = mapping[mapping['id'] == rid]['idx'].values[0]
            valid_indices.append(idx)
        else:
            print(f"Cảnh báo: ID {rid} không tìm thấy trong dữ liệu training.")

    if not valid_indices:
        return "Lỗi: Không có sản phẩm hợp lệ nào trong danh sách."

    # 2. Tính Vector trung bình (User Interest Centroid)
    interest_vectors = embeddings[valid_indices]
    user_profile_vector = np.mean(interest_vectors, axis=0).reshape(1, -1)
    similarities = cosine_similarity(user_profile_vector, embeddings).flatten()

    # 4. Sắp xếp và lấy kết quả
    related_indices = similarities.argsort()[::-1]
    
    results = []
    for idx in related_indices:
        res_id = mapping[mapping['idx'] == idx]['id'].values[0]
        
        if res_id in input_ids_str:
            continue
            
        info = metadata[metadata['id'] == res_id].iloc[0]
        results.append({
            'ID': res_id,
            'Name': info['productDisplayName'],
            'Brand': info['brandName'],
            'Category': info['articleType'],
            'Score': round(similarities[idx], 4)
        })
        
        if len(results) >= top_k:
            break
            
    return pd.DataFrame(results)

if __name__ == "__main__":
    embeddings, mapping, metadata = load_inference_data()
    
    # Ví dụ: Một cái áo thun, một đôi giày và một cái kính
    my_wishlist = ['1597', '39186', '12383'] 
    
    print(f"\n{'='*60}")
    print(f"DỰ ĐOÁN DỰA TRÊN GIỎ HÀNG / WISHLIST")
    print(f"{'='*60}")
    print(f"Sản phẩm đang có trong danh sách: {my_wishlist}")
    
    current_items = metadata[metadata['id'].isin(my_wishlist)][['id', 'productDisplayName']]
    print("\nChi tiết giỏ hàng hiện tại:")
    print(current_items)
    
    top_k_recommendations = recommend_from_list(my_wishlist, embeddings, mapping, metadata, top_k=10)
    
    print("\n" + "*"*20 + " TOP 10 SẢN PHẨM GỢI Ý CHO BẠN " + "*"*20)
    print(top_k_recommendations)