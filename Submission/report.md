# BÁO CÁO THỰC HÀNH MLOPS PIPELINE: CONTINUOUS TRAINING & DEPLOYMENT

**Học viên:** Nguyễn Văn Phong  
**Khoá / Buổi:** K3 - Track 2 - Day 21 (CI/CD cho AI Systems)  
**Mô hình:** Phân loại chất lượng rượu vang (Wine Quality Classification)  

---

### 1. Bộ siêu tham số đã chọn và lý do (dựa trên kết quả so sánh trong MLflow)

Qua quá trình thực nghiệm và theo dõi trên MLflow với mô hình **RandomForestClassifier**, bộ siêu tham số tối ưu được lựa chọn trong `params.yaml` là:
- `n_estimators`: `500`
- `max_depth`: `40`
- `min_samples_split`: `5`

**Lý do lựa chọn:**
- Trong các lần thực nghiệm so sánh trên MLflow với các cấu hình khác nhau (tùy biến `n_estimators` từ 50 đến 500, `max_depth` từ 10 đến 40), cấu hình này mang lại hiệu suất tốt nhất trên tập đánh giá held-out (`eval.csv`).
- Số lượng cây lớn (`n_estimators=500`) cùng độ sâu vừa đủ (`max_depth=40`) giúp mô hình học được các tương tác phi tuyến tính phức tạp giữa 12 đặc trưng hóa học của mẫu rượu, đồng thời `min_samples_split=5` giúp hạn chế tối đa hiện tượng overfitting.

---

### 2. So sánh `accuracy` và `f1_score` giữa 2 lần chạy dữ liệu

| Giai đoạn | Số lượng mẫu huấn luyện | Accuracy | F1-score (Weighted) | Đánh giá Gate (>= 0.70) | Trạng thái Deploy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Giai đoạn 1 (Bước 2)** | 2.998 mẫu | **0.6800** | **0.6786** | ❌ Không đạt (< 0.70) | Dừng pipeline (Không deploy) |
| **Giai đoạn 2 (Bước 3)** | 5.996 mẫu | **0.7500** | **0.7486** | ✅ Đạt (0.75 >= 0.70) | Tự động Deploy lên Cloud VM |
| **Mức cải thiện** | **+2.998 mẫu (+100%)** | **+7.0%** | **+0.0700** | — | — |

**Nhận xét:**
- Khi bổ sung 2.998 mẫu mới từ `train_phase2.csv` (nâng tổng số mẫu lên 5.996), hiệu năng mô hình tăng vượt bậc (+7% Accuracy và +0.07 F1-score).
- Mô hình đạt chuẩn chất lượng của bước kiểm duyệt tự động (`Evaluation Gate >= 0.70`), từ đó kích hoạt job deploy tự động, restart service FastAPI và phục vụ mô hình mới nhất trên Cloud VM mà không cần can thiệp thủ công.

---

### 3. Khó khăn gặp phải và cách giải quyết

1. **Thứ tự đồng bộ dữ liệu (`dvc push` vs `git push`):**
   - *Khó khăn:* Nếu thực hiện `git push` trước khi `dvc push` dữ liệu mới lên Cloud Storage (GCS/S3), CI runner trên GitHub Actions sẽ bị lỗi `dvc pull` do dữ liệu chưa có trên remote storage.
   - *Giải pháp:* Tuân thủ quy trình chuẩn: `dvc add` -> `git add *.dvc` & `git commit` -> `dvc push` dữ liệu lên cloud -> sau đó mới `git push origin main` để kích hoạt workflow CI/CD.

2. **Xác thực và phân quyền giữa CI/CD Runner và Cloud VM:**
   - *Khó khăn:* Runner và Cloud VM cần quyền truy cập an toàn vào Cloud Storage cũng như kết nối SSH để restart service.
   - *Giải pháp:* Sử dụng Service Account Key (`GCP_SA_KEY`) và `SSH_PRIVATE_KEY` lưu trữ bảo mật trong **GitHub Actions Secrets**, đồng thời cấu hình biến môi trường `GOOGLE_APPLICATION_CREDENTIALS` để server FastAPI tự động pull model mới nhất khi khởi động.

3. **Cú pháp gửi POST Request trên Windows PowerShell:**
   - *Khó khăn:* Lệnh `curl` trên PowerShell gặp lỗi parse dấu nháy kép `"` trong payload JSON, dẫn đến lỗi `JSON decode error`.
   - *Giải pháp:* Sử dụng lệnh `Invoke-RestMethod` của PowerShell hoặc thêm cờ `--%` cho `curl.exe` để gửi payload JSON hợp lệ.
