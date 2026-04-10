import logging
import sys

try:
    import dagshub
except Exception:
    dagshub = None

try:
    import mlflow
except Exception:
    # Lightweight dummy mlflow replacement so the code can be imported and run
    class _DummyRunInfo:
        def __init__(self, run_id="dummy"):
            self.run_id = run_id

    class _DummyRun:
        def __init__(self):
            self.info = _DummyRunInfo()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class _DummySklearn:
        @staticmethod
        def log_model(model, name):
            return None

    class _DummyMLflow:
        sklearn = _DummySklearn()

        def start_run(self, run_name=None, nested=False):
            return _DummyRun()

        def set_tag(self, *args, **kwargs):
            return None

        def log_param(self, *args, **kwargs):
            return None

        def log_metric(self, *args, **kwargs):
            return None

    mlflow = _DummyMLflow()
from sklearn.model_selection import RandomizedSearchCV

from MachineLearningModule.Classifiers import Classifiers
from MachineLearningModule.DataAcquisition import ReadDatasetFromCSV
from MachineLearningModule.DataPreProcessing import (
    Conversions,
    DimReduction,
    HandleMissingValues,
    Normalisation,
    NumBalancing,
)
from MachineLearningModule.DataSplittingAndCV import DataSplitAndCVMethods
from MachineLearningModule.ModelEvaluation import ModelEvaluation
import os
import joblib
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the DagsHub repository with MLflow integration if dagshub is available
if dagshub is not None:
    try:
        dagshub.init(repo_owner="vannusingh9", repo_name="AndroidMalwareProject", mlflow=True)  # type: ignore
    except Exception as e:
        logger.warning("dagshub.init failed or is not configured: %s", e)


def machine_learning_flow(dataset_path, ml_algorithm):
    """
    Function containing the flow of the Machine learning module.

    Input:
        dataset_path - path to the dataset's CSV file
        ml_algorithm - acronym of ML algorithm chosen

    Output:
        classifier - the obtained classifier
        most_relevant_features - the most relevant features, obtained after applying RRFS
        evaluation_metrics - all obtained evaluation metrics with the classifier
    """
    with mlflow.start_run(run_name=f"{ml_algorithm}_Experiment") as run:
        run_id = run.info.run_id
        mlflow.set_tag("run_id", run_id)
        mlflow.set_tag("ml_algorithm", ml_algorithm)

        logger.info(f"MLflow Run ID: {run_id}")

        # Log dataset and algorithm
        mlflow.log_param("dataset_path", dataset_path)
        mlflow.log_param("ml_algorithm", ml_algorithm)

        # --------------- Data Acquisition ---------------
        dataset, class_name = ReadDatasetFromCSV.get_dataset_from_csv_file(dataset_path)
        logger.info("Data acquisition completed. Class name: %s", class_name)

        # --------------- Data pre-processing ---------------
        x, y = data_pre_processing(dataset, class_name)
        logger.info("Data pre-processing completed.")

        # Fix for numpy array
        try:
            most_relevant_features = x.columns.values
        except AttributeError:
            most_relevant_features = None

        logger.info("Most relevant features identified: %s", most_relevant_features)

        accuracies, confusion_matrices, precisions, recalls, f1_scores, roc_aucs = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        # --------------- Cross-validation ---------------
        outer_cv = DataSplitAndCVMethods.stratified_ten_fold_cv(x, y)
        logger.info("Cross-validation setup completed.")

        classifier = None
        run_counter = 0

        for i, (train_index, test_index) in outer_cv:
            run_counter += 1
            logger.info("Starting fold %d of cross-validation.", i + 1)

            with mlflow.start_run(
                nested=True, run_name=f"{ml_algorithm}_Run_{run_counter}"
            ):
                mlflow.log_param("fold_number", i + 1)
                mlflow.log_param("run_counter", run_counter)

                # Handle both pandas DataFrame and numpy array
                if hasattr(x, "iloc"):
                    x_train, x_test = x.iloc[train_index], x.iloc[test_index]
                else:
                    x_train, x_test = x[train_index], x[test_index]

                if hasattr(y, "iloc"):
                    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
                else:
                    y_train, y_test = y[train_index], y[test_index]

                # --------------- Train the model ---------------
                classifier = Classifiers.get_classifier(ml_algorithm, x_train, y_train)
                logger.info("Model training completed for fold %d.", i + 1)

                # --------------- Hyperparameter tuning ---------------
                classifier = hyperparameter_tuning(
                    classifier, ml_algorithm, x_train, y_train
                )
                logger.info("Hyperparameter tuning completed for fold %d.", i + 1)

                # --------------- Predict ---------------
                y_pred = classifier.predict(x_test)

                # --------------- Model Evaluation ---------------
                accuracy, confusion_matrix, precision, recall, f1_score, roc_auc = (
                    ModelEvaluation.model_evaluation(y_test, y_pred)
                )
                logger.info("Model evaluation completed for fold %d.", i + 1)

                # Log metrics
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", f1_score)
                if roc_auc:
                    mlflow.log_metric("roc_auc", float(roc_auc))

                accuracies.append(accuracy)
                confusion_matrices.append(confusion_matrix)
                precisions.append(precision)
                recalls.append(recall)
                f1_scores.append(f1_score)
                roc_aucs.append(roc_auc)

        evaluation_metrics = [
            accuracies,
            confusion_matrices,
            precisions,
            recalls,
            f1_scores,
            roc_aucs,
        ]

        if classifier is None:
            logger.error("No ML classifier obtained.")
            sys.exit(1)

        # Persist the final trained classifier and most relevant features to disk
        try:
            os.makedirs("models", exist_ok=True)
            model_path = os.path.join("models", "final_model.joblib")
            features_path = os.path.join("models", "most_relevant_features.pkl")
            joblib.dump(classifier, model_path)
            with open(features_path, "wb") as f:
                pickle.dump(most_relevant_features, f)
            logger.info("Saved model to %s and features to %s", model_path, features_path)
        except Exception as e:
            logger.warning("Failed to persist model/features to disk: %s", e)

        try:
            mlflow.sklearn.log_model(classifier, "final_model")  # type: ignore
        except Exception:
            # If mlflow is a dummy or logging fails, continue
            logger.debug("mlflow model logging skipped or failed")

        logger.info("Machine learning flow completed successfully.")
        return classifier, most_relevant_features, evaluation_metrics


def hyperparameter_tuning(classifier, ml_algorithm, x_val, y_val):
    """
    Function to perform hyperparameter tuning of the classifier.

    Input:
        classifier
        ml_algorithm - acronym of ML algorithm chosen
        x_val - validation set
        y_val - targets of the validation set

    Output:
        tuned_classifier - classifier after the tuning of its hyperparameters
    """
    # Sanitize algorithm name for logging to prevent log injection (e.g., newline forging)
    safe_ml_algorithm = str(ml_algorithm).replace("\r", "").replace("\n", "")
    logger.info("Starting hyperparameter tuning for algorithm: %s", safe_ml_algorithm)

    # Parameters
    if ml_algorithm == "RF":
        parameters = {
            "n_estimators": range(100, 1000, 100),
            "max_depth": [None, 3, 5, 7],
            "criterion": ["gini", "entropy", "log_loss"],
        }
    elif ml_algorithm == "SVM":
        parameters = {
            "kernel": ["rbf", "poly", "linear", "sigmoid"],
            "C": range(1, 20, 1),
            "gamma": ["scale", "auto"],
        }
    elif ml_algorithm == "KNN":
        parameters = {
            "n_neighbors": range(1, 11, 1),
            "metric": ["minkowski", "euclidean", "manhattan"],
            "weights": ["uniform", "distance"],
        }
    else:
        logger.warning("No parameters set for algorithm: %s", safe_ml_algorithm)
        return classifier

    try:
        # tuned_classifier = GridSearchCV(classifier, parameters).fit(x_val, y_val)
        # Use RandomizedSearchCV for faster tuning
        tuned_classifier = RandomizedSearchCV(
            classifier, parameters, n_iter=10, cv=3, n_jobs=-1, random_state=42
        ).fit(x_val, y_val)
        logger.info("Hyperparameter tuning completed successfully.")
        return tuned_classifier

    except Exception as e:
        logger.error("Error during hyperparameter tuning: %s", str(e))
        return classifier


def data_pre_processing(dataset, class_name):
    """
    Function for data pre-processing.

    Input:
        dataset
        class name

    Output:
        x - data matrix
        y - targets
    """
    logger.info("Starting data pre-processing.")

    # Converting categorical features to numerical
    dataset = Conversions.convert_all_cat_features_to_num_via_label_encoding(dataset)

    # Dealing with missing values
    dataset = HandleMissingValues.impute_missing_values_with_feature_mean(dataset)

    # Normalising the data
    dataset = Normalisation.min_max_normalisation(dataset)

    # Separating the features from the class label
    y = dataset[class_name]

    # Dimensionality reduction by Relevance-Redundancy Feature Selection (RRFS)
    x = DimReduction.relevance_redundancy_feature_selection(
        dataset, class_name, "FR", 0.3
    )

    # Numerosity balancing by random oversampling
    x, y = NumBalancing.random_oversampling(x, y)

    logger.info("Data pre-processing completed.")
    return x, y
