from __future__ import annotations

import os
import shutil
import tempfile
import pickle
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import joblib
from FeatureExtractionModule import FeatureExtraction
from MachineLearningModule import MachineLearningFlow

app = FastAPI(title="Android Malware Detection API")

DATASETS_ROOT = os.path.abspath(
    os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "Datasets"))
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend if a build exists
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/train")
def train(dataset_path: Optional[str] = None, algorithm: str = "KNN"):
    # Constrain dataset paths to the configured datasets root directory
    if dataset_path is None:
        # Use the default dataset inside the datasets root, with normalization
        resolved_dataset_path = os.path.abspath(
            os.path.normpath(os.path.join(DATASETS_ROOT, "Drebin_v1.csv"))
        )
    else:
        # Treat user-provided value as a path relative to DATASETS_ROOT
        # Strip whitespace and reject empty strings and absolute paths to avoid escaping the datasets root
        dataset_path = dataset_path.strip()
        if not dataset_path:
            raise HTTPException(status_code=400, detail="Dataset path cannot be empty")
        # Reject absolute paths outright
        if os.path.isabs(dataset_path):
            raise HTTPException(
                status_code=400,
                detail="Dataset path must be relative to the datasets root; absolute paths are not allowed",
            )
        # Build path under the datasets root and normalize
        candidate_path = os.path.join(DATASETS_ROOT, dataset_path)
        resolved_dataset_path = os.path.abspath(os.path.normpath(candidate_path))
        # Ensure the normalized path is still within DATASETS_ROOT to prevent directory traversal
        if os.path.commonpath([DATASETS_ROOT, resolved_dataset_path]) != DATASETS_ROOT:
            raise HTTPException(status_code=400, detail="Invalid dataset path")

    if not os.path.exists(resolved_dataset_path):
        raise HTTPException(status_code=400, detail=f"Dataset not found: {resolved_dataset_path}")

    _, _, _ = MachineLearningFlow.machine_learning_flow(
        resolved_dataset_path, algorithm
    )
    return JSONResponse({"status": "trained", "algorithm": algorithm})


@app.post("/predict_apk")
async def predict_apk(file: UploadFile = File(...)):
    # Ensure model files exist
    model_path = os.path.join("models", "final_model.joblib")
    features_path = os.path.join("models", "most_relevant_features.pkl")
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        raise HTTPException(status_code=400, detail="Model not trained. Call /train first.")

    # Save uploaded APK to a temp file
    tmp_dir = tempfile.mkdtemp(prefix="apk_upload_")
    try:
        tmp_path = os.path.join(tmp_dir, file.filename)
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Load model and features
        try:
            clf = joblib.load(model_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {e}")
        try:
            with open(features_path, "rb") as f:
                features = pickle.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load features: {e}")

        # Extract features from APK
        try:
            extracted = FeatureExtraction.feature_extraction(tmp_path, features)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Feature extraction failed: {e}")

        # Predict
        try:
            pred = clf.predict(extracted)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

        return JSONResponse({"prediction": pred.tolist() if hasattr(pred, "tolist") else str(pred)})
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass
