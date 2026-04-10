from __future__ import annotations

import os
import shutil
import tempfile
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from MachineLearningModule.MachineLearningFlow import machine_learning_flow
from FeatureExtractionModule import FeatureExtraction

app = FastAPI(title="Android Malware Detection API")

# Root directory for datasets; user-provided paths must resolve within this directory
DATASETS_ROOT = os.path.abspath(
    os.path.normpath(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "Datasets")
    )
)

# Cache the resolved datasets root to avoid redundant filesystem operations
DATASETS_ROOT_REAL = os.path.realpath(DATASETS_ROOT)

# Allow frontend dev server origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for trained classifier and feature list
MODEL: dict = {"classifier": None, "features": None}


def get_default_dataset_path() -> str:
    default = os.path.join(DATASETS_ROOT, "Drebin_v1.csv")
    return default


@app.on_event("startup")
def startup_event():
    # If a pre-trained model isn't required, we won't train automatically to avoid heavy startup.
    # This keeps startup fast; call `/train` to train the model on demand.
    pass


def validate_dataset_path(user_path: Optional[str]) -> str:
    """
    Validate and sanitize a user-provided dataset path.

    Returns the absolute, sanitized path if valid.
    Raises HTTPException if the path is invalid or outside the allowed directory.
    """
    if user_path is None:
        # Use the default dataset inside the datasets root
        safe_path = get_default_dataset_path()
    else:
        # Strip whitespace and reject empty strings
        user_path = user_path.strip()
        if not user_path:
            raise HTTPException(status_code=400, detail="Dataset path cannot be empty")

        # Reject absolute paths to prevent directory traversal
        if os.path.isabs(user_path):
            raise HTTPException(
                status_code=400,
                detail="Dataset path must be relative, absolute paths are not allowed",
            )

        # Reject paths containing null bytes
        if "\x00" in user_path:
            raise HTTPException(
                status_code=400, detail="Invalid characters in dataset path"
            )

        # Join with the datasets root and resolve to absolute path
        safe_path = os.path.join(DATASETS_ROOT, user_path)

    # Resolve the path completely, following symlinks
    resolved_path = os.path.realpath(safe_path)

    # Check that the resolved path is within the allowed directory
    # Strip trailing separator to handle consistent behavior across platforms
    normalized_root = DATASETS_ROOT_REAL.rstrip(os.sep)

    # Ensure path is strictly within the directory (not the directory itself)
    if not resolved_path.startswith(normalized_root + os.sep):
        raise HTTPException(status_code=400, detail="Invalid dataset path")

    # Verify the path points to a file, not a directory
    if not os.path.isfile(resolved_path):
        raise HTTPException(status_code=400, detail="Dataset file not found")

    return resolved_path


@app.post("/train")
def train(dataset_path: Optional[str] = None, algorithm: str = "KNN"):
    # Validate and sanitize the dataset path
    resolved_dataset_path = validate_dataset_path(dataset_path)

    classifier, most_relevant_features, evaluation_metrics = (
        MachineLearningFlow.machine_learning_flow(resolved_dataset_path, algorithm)
    )
    MODEL["classifier"] = classifier
    MODEL["features"] = most_relevant_features

    # Return relative path instead of absolute to avoid leaking server structure
    relative_path = os.path.relpath(resolved_dataset_path, DATASETS_ROOT_REAL)
    return JSONResponse(
        {"status": "trained", "algorithm": algorithm, "dataset": relative_path}
    )


@app.post("/predict_apk")
async def predict_apk(file: UploadFile = File(...)):
    if MODEL.get("classifier") is None or MODEL.get("features") is None:
        raise HTTPException(
            status_code=400, detail="Model not trained. Call /train first."
        )

    suffix = ".apk"
    if not file.filename.endswith(suffix):
        raise HTTPException(status_code=400, detail="Uploaded file is not an APK")

    # Save uploaded APK to a temp file
    tmp_dir = tempfile.mkdtemp(prefix="apk_upload_")
    try:
        tmp_path = os.path.join(tmp_dir, file.filename)
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract features and predict
        try:
            extracted = FeatureExtraction.feature_extraction(
                tmp_path, MODEL["features"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Feature extraction failed: {e}"
            )

        try:
            pred = MODEL["classifier"].predict(extracted)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

        return JSONResponse(
            {"prediction": pred.tolist() if hasattr(pred, "tolist") else str(pred)}
        )
    finally:
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass


# Serve static frontend if `frontend/dist` exists
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"
)
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL.get("classifier") is not None}
