from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ.get("GCS_BUCKET", "track2-day21-bucket")
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """
    Tải file model.pkl từ GCS về máy khi server khởi động.
    """
    # TODO 1: Tạo storage.Client()
    client = storage.Client()

    # TODO 2: Lấy bucket và blob tương ứng
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_MODEL_KEY)

    # TODO 3: Tải file model xuống máy
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    blob.download_to_filename(MODEL_PATH)

    # TODO 4: In thông báo thành công
    print("Model da duoc tai xuong tu GCS.")


try:
    download_model()
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Chua the tai model ngay luc nay: {e}")
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """
    Endpoint kiểm tra sức khỏe server.
    """
    # TODO 5: Trả về dict {"status": "ok"}
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luận chính.
    """
    global model
    # TODO 6: Kiểm tra số lượng đặc trưng
    if len(req.features) != 12:
        raise HTTPException(
            status_code=400,
            detail="Expected 12 features (wine quality)"
        )

    if model is None:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
        else:
            raise HTTPException(status_code=503, detail="Model not loaded yet")

    # TODO 7: Gọi model.predict([req.features])
    prediction = int(model.predict([req.features])[0])

    # TODO 8: Trả về dict chứa prediction và label
    label_map = {0: "thap", 1: "trung_binh", 2: "cao"}
    label = label_map.get(prediction, "khong_xac_dinh")

    return {"prediction": prediction, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

