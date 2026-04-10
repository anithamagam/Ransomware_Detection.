import argparse
import logging
import os
import sys
from typing import Optional

import joblib

from FeatureExtractionModule import FeatureExtraction
from MachineLearningModule import MachineLearningFlow
from Util import Util

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main(argv: list[str] | None = None):
    """Run the machine learning flow and optional feature extraction/prediction.

    Defaults are chosen to work from the repository root:
    - dataset: `Datasets/Drebin_v1.csv` (if present)
    - ml algorithm: KNN

    Usage examples:
      python main.py --dataset Datasets/Drebin_v1.csv --algorithm KNN
      python main.py --apk apkfile/sample.apk --algorithm RF
    """

    parser = argparse.ArgumentParser(description="Run Android Malware Detection flow")
    parser.add_argument(
        "--dataset",
        default="Datasets/Drebin_v1.csv",
        help="Path to dataset CSV (default: Datasets/Drebin_v1.csv)",
    )
    parser.add_argument(
        "--algorithm",
        default="KNN",
        help="ML algorithm acronym (RF | SVM | KNN | NB | MLP)",
    )
    parser.add_argument(
        "--apk",
        default=None,
        help="Path to APK file for feature extraction and prediction",
    )

    args = parser.parse_args(argv)

    dataset_path = args.dataset
    ml_algorithm = args.algorithm
    apk_path = args.apk

    if not os.path.exists(dataset_path):
        logging.error("Dataset not found at %s", dataset_path)
        sys.exit(2)

    logging.info("Starting machine learning flow")
    classifier, most_relevant_features, evaluation_metrics = (
        MachineLearningFlow.machine_learning_flow(dataset_path, ml_algorithm)
    )
    logging.info("Machine learning flow completed")

    # If an APK path is provided, attempt feature extraction and prediction
    if apk_path:
        if not os.path.exists(apk_path):
            logging.error("APK file not found at %s", apk_path)
            sys.exit(2)

        logging.info("Starting feature extraction for APK: %s", apk_path)
        extracted_features = FeatureExtraction.feature_extraction(
            apk_path, most_relevant_features
        )
        logging.info("Feature extraction completed")

        try:
            prediction = classifier.predict(extracted_features)
            print("\nPrediction:", prediction)
            logging.info("Prediction: %s", prediction)
        except Exception as e:
            logging.error("Error during prediction: %s", str(e))

    # Printing the evaluation metrics
    Util.print_evaluation_metrics(evaluation_metrics)


def run_prediction(apk_path: str, model_path: Optional[str] = None):
    # Determine model and features path
    if model_path:
        clf = joblib.load(model_path)
        features_path = os.path.join(
            os.path.dirname(model_path), "most_relevant_features.pkl"
        )
    else:
        clf_path = os.path.join("models", "final_model.joblib")
        features_path = os.path.join("models", "most_relevant_features.pkl")
        if not os.path.exists(clf_path):
            logging.error(
                "No trained model found at models/final_model.joblib. Run --train first."
            )
            return
        clf = joblib.load(clf_path)

    # load features list
    try:
        import pickle

        with open(features_path, "rb") as f:
            features = pickle.load(f)
    except Exception as e:
        logging.error(f"Failed to load features file: {e}")
        return

    # extract
    extracted = FeatureExtraction.feature_extraction(apk_path, features)
    pred = clf.predict(extracted)
    print("Prediction:", pred)


if __name__ == "__main__":
    main()
