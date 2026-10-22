import os
import sys
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import BackgroundTasks, HTTPException, status

base_dir = Path(__file__).resolve().parent.parent.parent
ai_code_path = base_dir / "data_scientist"

if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

from data_scientist.eda_original_1 import OriginalDatasetEDA
from data_scientist.preprocessing_2 import FashionPreprocessor
from data_scientist.eda_normalized_3 import NormalizedDatasetEDA
from data_scientist.image_extractor_4_1 import ImageFeatureExtractor
from data_scientist.metadata_extractor_4_2 import MetadataFeatureExtractor
from data_scientist.text_extractor_4_3 import TextFeatureExtractor
from data_scientist.feature_fusion_4_4 import FeatureFusion
from data_scientist.edge_builder_4_5 import EdgeBuilder
from data_scientist.train_GNN_4_6 import GNNTrainer

from repositories import product_repository
from models.model_ai_model import ModelVersion, EDAReport

class AIPipelineService:
    def __init__(self, db: Session):
        self.db = db
        
        self.original_data_dir = ai_code_path / "orignal_dataset"
        self.standard_data_dir = ai_code_path / "standard_dataset"
        self.features_dir = ai_code_path / "features"
        self.reports_dir = ai_code_path / "reports"
        self.raw_images_dir = ai_code_path / "images" 
        self.models_dir = ai_code_path / "models"
        
        # Thư mục ảnh gốc
        self.source_images_dir = Path(r"E:\Hcmut material\AI\Intelligence System\fashion-dataset\images")

        # Tạo thư mục nếu chưa tồn tại
        for folder in [self.original_data_dir, self.standard_data_dir, 
                       self.features_dir, self.reports_dir, 
                       self.raw_images_dir, self.models_dir]:
            folder.mkdir(parents=True, exist_ok=True)


    def _get_relative_path(self, absolute_path: Path) -> str:
        """Chuyển đổi Path tuyệt đối thành string tương đối so với BASE_DIR"""
        try:
            return str(absolute_path.relative_to(base_dir))
        except ValueError:
            return str(absolute_path)


    def sync_db_to_ai_input(self):
        print("1. Đồng bộ hóa dữ liệu Database sang CSV")
        products = product_repository.get_all_products(self.db, limit=100000)
        data = [{
            "id": str(p.id), 
            "brandName": p.brand_name, 
            "productDisplayName": p.product_display_name,
            "description": p.description, 
            "style_note": p.style_note, 
            "price": p.price,
            "discountedPrice": p.discounted_price, 
            "articleType": p.article_type, 
            "gender": p.gender,
            "masterCategory": p.master_category, 
            "subCategory": p.sub_category, 
            "season": p.season,
            "usage": p.usage, 
            "myntraRating": p.myntra_rating or 0.0, 
            "baseColour": p.base_colour,
            "fabric": p.fabric, 
            "fit": p.fit, 
            "neck": p.neck, 
            "occasion": p.occasion
        } for p in products]

        csv_path = self.original_data_dir / "fashion_original_dataset.csv"
        pd.DataFrame(data).to_csv(csv_path, index=False)
        return len(data), products


    def download_product_images(self, products):
        print(f"2. Đang đồng bộ ảnh từ thư mục nguồn: {self.source_images_dir.name}")
        for p in products:
            if not p.image_url: 
                continue

            source_file = self.source_images_dir / f"{p.image_url}.jpg"
            save_path = self.raw_images_dir / f"{p.id}.jpg"
            
            if not save_path.exists() and source_file.exists():
                try:
                    shutil.copy(str(source_file), str(save_path))
                except Exception: 
                    pass


    def check_incremental(self, current_count):
        """Kiểm tra xem có cần train lại không"""
        last_version = self.db.query(ModelVersion).filter(ModelVersion.is_active == True).order_by(desc(ModelVersion.created_at)).first()
        
        if not last_version:
            return True
        
        return current_count > last_version.product_count


    def execute_ai_domino(self, version_tag, db_model_id):
        """Thực thi chuỗi Class AI xử lý dữ liệu và huấn luyện"""
        print(f"3. Thực thi việc train model AI: {version_tag} ---")
        
        # EDA Original
        out_orig = self.reports_dir / version_tag / "original"
        OriginalDatasetEDA(input_path=str(self.original_data_dir / "fashion_original_dataset.csv"),
                           output_dir=str(out_orig), image_dir=str(self.raw_images_dir)).run_all()
        self._save_eda_to_db(db_model_id, "original", out_orig)

        # Preprocessing
        FashionPreprocessor(input_csv=str(self.original_data_dir / "fashion_original_dataset.csv"),
                            output_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                            image_dir=str(self.raw_images_dir)).run_all()

        # EDA Normalized
        out_norm = self.reports_dir / version_tag / "normalized"
        NormalizedDatasetEDA(standard_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                             original_csv=str(self.original_data_dir / "fashion_original_dataset.csv"),
                             output_dir=str(out_norm)).run_all()
        self._save_eda_to_db(db_model_id, "normalized", out_norm)

        # Trích xuất đặc trưng (Feature Extraction)
        ImageFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                              output_dir=str(self.features_dir / "image_features"),
                              image_dir=str(self.raw_images_dir)).run_extraction()
        
        MetadataFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                                 id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                                 output_dir=str(self.features_dir / "metadata_features")).run_extraction()

        TextFeatureExtractor(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                             id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                             output_dir=str(self.features_dir / "text_features")).run_extraction()

        # Fusion & Build Graph
        FeatureFusion(visual_path=str(self.features_dir / "image_features" / "image_features_resnet18.npy"),
                      text_path=str(self.features_dir / "text_features" / "text_features.npy"),
                      meta_path=str(self.features_dir / "metadata_features" / "metadata_features.npy"),
                      output_dir=str(self.features_dir / "final_node_features")).run_fusion()

        EdgeBuilder(input_csv=str(self.standard_data_dir / "fashion_preprocessed_dataset.csv"),
                    id_csv=str(self.features_dir / "image_features" / "image_feature_ids.csv"),
                    output_dir=str(self.features_dir / "graph_data")).run_build()

        # GNN Training
        last_ver = self.db.query(ModelVersion).order_by(desc(ModelVersion.created_at)).first()
        trainer = GNNTrainer(node_feat_path=str(self.features_dir / "final_node_features" / "final_node_features.npy"),
                             edge_index_path=str(self.features_dir / "graph_data" / "edge_index.npy"),
                             output_dir=str(self.features_dir / "models"))
        trainer.run_training(last_model_path=last_ver.model_weights_path if last_ver else None)


    def _save_eda_to_db(self, model_id, eda_type, report_dir: Path):
        files_dict = {}
        
        if report_dir.exists():
            for file_path in report_dir.glob("*"):
                if file_path.is_file():
                    relative_path = self._get_relative_path(file_path)
                    files_dict[file_path.name] = relative_path

        report = EDAReport(
            version_id=model_id,
            eda_type=eda_type,
            report_files=files_dict
        )
        self.db.add(report)
        self.db.commit()


    def finalize_version_archive(self, v_tag, version_obj):
        """Đóng gói file npy/pth vào thư mục version và cập nhật DB"""
        v_dir = self.models_dir / v_tag
        v_dir.mkdir(parents=True, exist_ok=True)

        files_map = {
            "image_feat.npy": self.features_dir / "image_features" / "image_features_resnet18.npy",
            "text_feat.npy": self.features_dir / "text_features" / "text_features.npy",
            "meta_feat.npy": self.features_dir / "metadata_features" / "metadata_features.npy",
            "final_emb.npy": self.features_dir / "models" / "final_gnn_embeddings.npy",
            "gnn_weights.pth": self.features_dir / "models" / "fashion_gnn_model.pth"
        }

        for name, src in files_map.items():
            if src.exists():
                shutil.copy(str(src), str(v_dir / name))

        # Cập nhật thông tin vào DB
        version_obj.image_feat_path = self._get_relative_path(v_dir / "image_feat.npy")
        version_obj.gnn_emb_path = self._get_relative_path(v_dir / "final_emb.npy")
        version_obj.model_weights_path = self._get_relative_path(v_dir / "gnn_weights.pth")
        version_obj.text_feat_path = self._get_relative_path(v_dir / "text_feat.npy")
        version_obj.meta_feat_path = self._get_relative_path(v_dir / "meta_feat.npy")
        version_obj.is_active = True 

        # Tắt các bản cũ
        self.db.query(ModelVersion).filter(ModelVersion.id != version_obj.id).update({ModelVersion.is_active: False})
        self.db.commit()


    async def run_full_process_background(self):
        """
        Hàm thực thi pipeline AI chạy ngầm. 
        Lưu ý: Lỗi ở đây sẽ được ghi nhận vào log hệ thống.
        """
        try:
            # 1. Đồng bộ dữ liệu & Kiểm tra số lượng
            actual_count, products = self.sync_db_to_ai_input()
            if not products:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy sản phẩm nào trong cơ sở dữ liệu để đồng bộ."
                )

            # 2. Kiểm tra thư mục ảnh nguồn (Check tồn tại của ổ E hoặc folder)
            if not self.source_images_dir.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Thư mục ảnh nguồn không tồn tại: {self.source_images_dir}"
                )
                
            self.download_product_images(products)

            # 3. Tạo bản ghi Version tạm thời
            v_tag = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            new_version = ModelVersion(
                version_tag=v_tag,
                product_count=actual_count,
                is_active=False
            )
            self.db.add(new_version)
            self.db.commit()
            self.db.refresh(new_version)

            # 4. Chạy Domino (EDA, Extractors, Training), nếu các hàm bên trong execute_ai_domino lỗi, nó sẽ văng vào khối except
            self.execute_ai_domino(v_tag, new_version.id)

            # 5. Archive & Kích hoạt mô hình
            self.finalize_version_archive(v_tag, new_version)
            
        except HTTPException as http_exc:
            self.db.rollback()
            raise http_exc
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pipeline sụp đổ do lỗi hệ thống: {str(e)}"
            )
        
    async def get_latest_eda_report_service(self, eda_type: str):
        """
        Logic tìm version active mới nhất và trả về báo cáo EDA tương ứng.
        eda_type: 'original' hoặc 'normalized'
        """
        # 1. Tìm phiên bản mô hình đang hoạt động mới nhất
        latest_version = self.db.query(ModelVersion)\
            .filter(ModelVersion.is_active == True)\
            .order_by(desc(ModelVersion.created_at))\
            .first()

        if not latest_version:
            return None, "Không tìm thấy phiên bản mô hình nào đang hoạt động."

        # 2. Lấy báo cáo EDA dựa trên version_id và loại (original/normalized)
        report = self.db.query(EDAReport)\
            .filter(EDAReport.version_id == latest_version.id)\
            .filter(EDAReport.eda_type == eda_type)\
            .first()

        if not report:
            return None, f"Không tìm thấy báo cáo {eda_type} cho phiên bản {latest_version.version_tag}."

        # 3. Trả về thông tin version và dữ liệu báo cáo
        return {
            "version_tag": latest_version.version_tag,
            "product_count": latest_version.product_count,
            "created_at": latest_version.created_at,
            "report_details": report # Đối tượng này chứa các path file
        }, None


async def trigger_training_service(db: Session, background_tasks: BackgroundTasks):
    """
    Hàm cầu nối điều phối kích hoạt huấn luyện.
    """
    service = AIPipelineService(db)
    
    # 1. Đồng bộ dữ liệu & Kiểm tra sản phẩm
    actual_count, products = service.sync_db_to_ai_input()
    
    if actual_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cơ sở dữ liệu trống. Vui lòng thêm sản phẩm trước khi huấn luyện."
        )
    
    # 2. Kiểm tra điều kiện tăng trưởng
    is_needed = service.check_incremental(actual_count)
    
    if not is_needed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dữ liệu hiện tại ({actual_count} sản phẩm) đã được huấn luyện ở phiên bản mới nhất."
        )
    
    # 3. Kích hoạt chạy ngầm
    background_tasks.add_task(service.run_full_process_background)
    
    return {
        "status": "accepted",
        "message": f"Pipeline AI ({actual_count} sản phẩm) đã bắt đầu chạy dưới nền.",
        "version_tag": datetime.now().strftime('v_%Y%m%d_%H%M%S')
    }