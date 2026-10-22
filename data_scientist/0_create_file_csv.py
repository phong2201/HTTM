import os
import json
import pandas as pd
from tqdm import tqdm

json_dir = r"E:\Hcmut material\AI\Intelligence System\archive\fashion-dataset\styles"
output_csv = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data_scientist\orignal_dataset\fashion_master_dataset.csv"

def extract_product_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
        
    item = content.get('data', {})
    if not item:
        return None

    attrs = item.get('articleAttributes', {})
    
    descriptors = item.get('productDescriptors', {})
    desc_val = descriptors.get('description', {}).get('value', None)
    style_val = descriptors.get('style_note', {}).get('value', None)

    links = item.get('crossLinks', [])
    links_str = "|".join([l.get('value', '') for l in links]) if links else None

    data_row = {
        "id": item.get('id'),
        "brandName": item.get('brandName'),
        "gender": item.get('gender'),
        "masterCategory": item.get('masterCategory', {}).get('typeName'),
        "subCategory": item.get('subCategory', {}).get('typeName'),
        "articleType": item.get('articleType', {}).get('typeName'),
        "baseColour": item.get('baseColour'),
        "season": item.get('season'),
        "usage": item.get('usage'),
        "productDisplayName": item.get('productDisplayName'),
        "price": item.get('price'),
        "discountedPrice": item.get('discountedPrice'),
        "myntraRating": item.get('myntraRating'),
        
        "Fabric": attrs.get('Fabric'),
        "Fit": attrs.get('Fit'),
        "Neck": attrs.get('Neck'),
        "Occasion": attrs.get('Occasion'),
        
        "style_note": style_val,
        "description": desc_val,
        
        "crossLinks": links_str
    }
    return data_row

all_data = []

json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

print(f"Đang xử lý {len(json_files)} file JSON...")
for filename in tqdm(json_files):
    file_path = os.path.join(json_dir, filename)
    try:
        row = extract_product_data(file_path)
        if row:
            all_data.append(row)
    except Exception as e:
        print(f"Lỗi tại file {filename}: {e}")

df = pd.DataFrame(all_data)
df.to_csv(output_csv, index=False, encoding='utf-8-sig')

print(f"\n-Hoàn thành! Đã lưu {len(df)} sản phẩm vào file: {output_csv}")