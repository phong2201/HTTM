import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import os
import sys
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv, GAE
from torch_geometric.utils import train_test_split_edges
from tqdm import tqdm

# --- Định nghĩa ENCODER (Kiến trúc GCN 2 lớp) ---
class GCNEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(GCNEncoder, self).__init__()
        # Lớp 1: Học đặc trưng lân cận (Neighborhood aggregation)
        self.conv1 = GCNConv(in_channels, hidden_channels)
        # Lớp 2: Nén thành Embedding cuối cùng (Latent vector)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        # Truyền tin và kích hoạt phi tuyến tính ReLU
        x = self.conv1(x, edge_index).relu()
        # Dropout để chống Overfit khi đồ thị thưa
        x = F.dropout(x, p=0.2, training=self.training)
        return self.conv2(x, edge_index)

class GNNTrainer:
    def __init__(self, node_feat_path=None, edge_index_path=None, output_dir=None, 
                 epochs=100, lr=0.01, hidden_dim=256, out_dim=128):
        """
        Khởi tạo class Huấn luyện GNN.
        Hỗ trợ nén đặc trưng từ 911+ chiều xuống 128 chiều.
        """
        # 1. Thiết lập đường dẫn mặc định
        default_node = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\final_node_features\final_node_features.npy"
        default_edge = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\graph_data\edge_index.npy"
        default_out = r"E:\Hcmut material\AI\Intelligence System\intelligent-system\data-scientist\features\models"

        self.node_feat_path = node_feat_path if node_feat_path and os.path.exists(node_feat_path) else default_node
        self.edge_index_path = edge_index_path if edge_index_path and os.path.exists(edge_index_path) else default_edge
        self.output_dir = output_dir if output_dir else default_out
        
        self.epochs = epochs
        self.lr = lr
        self.hidden_dim = hidden_dim
        self.out_dim = out_dim

        os.makedirs(self.output_dir, exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(f"--- GNN Trainer khởi tạo trên thiết bị: {self.device} ---")

    def _prepare_data(self):
        """Nạp ma trận đặc trưng và danh sách cạnh vào PyTorch Geometric"""
        # print("--- Đang chuẩn bị dữ liệu Đồ thị ---")
        x_np = np.load(self.node_feat_path)
        edge_index_np = np.load(self.edge_index_path)

        x = torch.from_numpy(x_np).to(torch.float32)
        edge_index = torch.from_numpy(edge_index_np).to(torch.long)

        data = Data(x=x, edge_index=edge_index)
        
        # Chia cạnh để học Link Prediction (Dự đoán liên kết)
        # val=5%, test=10% để đánh giá khả năng tổng quát hóa
        data = train_test_split_edges(data, val_ratio=0.05, test_ratio=0.1)
        return data.to(self.device)

    def run_training(self, last_model_path=None):
        """
        Thực hiện quy trình huấn luyện.
        Nếu truyền vào last_model_path, sẽ thực hiện Warm Start (học tiếp).
        """
        data = self._prepare_data()
        in_channels = data.num_features

        # Khởi tạo GAE với Encoder của chúng ta
        model = GAE(GCNEncoder(in_channels, self.hidden_dim, self.out_dim)).to(self.device)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)

        # 1. CƠ CHẾ WARM START: Nạp trọng số cũ nếu có
        if last_model_path and os.path.exists(last_model_path):
            # print(f"Nạp trọng số cũ từ: {last_model_path} (Warm Start)")
            model.load_state_dict(torch.load(last_model_path))
            # Giảm Learning Rate khi học tiếp để tinh chỉnh (Fine-tuning)
            for param_group in optimizer.param_groups:
                param_group['lr'] = self.lr * 0.1

        # print(f"Bắt đầu huấn luyện: Input({in_channels}) -> {self.hidden_dim} -> {self.out_dim}")
        
        model.train()
        for epoch in range(1, self.epochs + 1):
            optimizer.zero_grad()
            
            # Encode node sang không gian ẩn (Z)
            z = model.encode(data.x, data.train_pos_edge_index)
            
            # Tính toán Loss tái tạo cạnh (Reconstruction Loss)
            loss = model.recon_loss(z, data.train_pos_edge_index)
            
            loss.backward()
            optimizer.step()

            # Đánh giá định kỳ mỗi 10 Epoch
            if epoch % 10 == 0:
                model.eval()
                with torch.no_grad():
                    z = model.encode(data.x, data.train_pos_edge_index)
                    # Tính AUC và AP trên tập Validation
                    auc, ap = model.test(z, data.val_pos_edge_index, data.val_neg_edge_index)
                    print(f"Epoch: {epoch:03d} | Loss: {loss:.4f} | Val AUC: {auc:.4f} | Val AP: {ap:.4f}")
                model.train()

        # 2. Lưu kết quả
        # print("\n--- Huấn luyện hoàn tất! Đang đóng gói Version ---")
        
        # Lưu file trọng số (.pth)
        weight_path = os.path.join(self.output_dir, "fashion_gnn_model.pth")
        torch.save(model.state_dict(), weight_path)
        
        # Lưu ma trận Embedding (npy) - Đây là nguyên liệu chính để Predict
        model.eval()
        with torch.no_grad():
            final_z = model.encode(data.x, data.train_pos_edge_index).cpu().numpy()
            emb_path = os.path.join(self.output_dir, "final_gnn_embeddings.npy")
            np.save(emb_path, final_z)

        # print("="*50)
        print(f"3_9 Kết quả huấn luyện")
        # print(f"- Trọng số mô hình: {weight_path}")
        # print(f"- Ma trận Embeddings: {final_z.shape}")
        # print(f"- File Embeddings lưu tại: {emb_path}")
        # print("="*50)
        
        return weight_path, emb_path

if __name__ == "__main__":
    trainer = GNNTrainer(epochs=100)
    trainer.run_training()