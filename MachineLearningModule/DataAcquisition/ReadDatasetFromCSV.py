import csv

import pandas
import os

# Define the datasets root directory similarly to backend/api.py
DATASETS_ROOT = os.path.abspath(
    os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Datasets"))
)

# Cache the resolved datasets root to avoid redundant filesystem operations
DATASETS_ROOT_REAL = os.path.realpath(DATASETS_ROOT)


def _resolve_dataset_path(file_path: str) -> str:
    """
    Resolve and validate a dataset path to ensure it stays within DATASETS_ROOT.
    """
    if file_path is None:
        raise ValueError("Dataset path cannot be None")
    candidate = str(file_path).strip()
    if not candidate:
        raise ValueError("Dataset path cannot be empty")

    # If an absolute path is provided (e.g., from backend/api.py), normalize it and
    # ensure that it still lies within DATASETS_ROOT.
    if os.path.isabs(candidate):
        # Resolve completely, following symlinks
        resolved = os.path.realpath(candidate)
        # Check that the resolved path is within the allowed directory
        normalized_root = DATASETS_ROOT_REAL.rstrip(os.sep)
        if not resolved.startswith(normalized_root + os.sep):
            raise ValueError("Invalid dataset path")
        return resolved

    # For relative paths, support both dataset-root-relative names (e.g. "foo.csv")
    # and repo-root-relative paths starting with "Datasets/" (e.g. "Datasets/foo.csv").
    normalized = os.path.normpath(candidate)
    path_parts = normalized.split(os.sep)
    if path_parts and path_parts[0] == "Datasets":
        # Drop the leading "Datasets" segment so we don't end up with Datasets/Datasets/...
        relative_path = os.path.join(*path_parts[1:]) if len(path_parts) > 1 else ""
    else:
        relative_path = normalized

    # Build path under the datasets root and normalize
    joined = os.path.join(DATASETS_ROOT, relative_path)
    # Resolve completely, following symlinks
    resolved = os.path.realpath(joined)
    # Ensure the resolved path is still within DATASETS_ROOT to prevent directory traversal
    normalized_root = DATASETS_ROOT_REAL.rstrip(os.sep)
    if not resolved.startswith(normalized_root + os.sep):
        raise ValueError("Invalid dataset path")
    return resolved


def get_dataset_from_csv_file(file_path):
    """
    Function to read/get dataset from a CSV file.

    Input:
        file_path - Path to the CSV file (relative to the datasets root)

    Output:
        dataset
        class name
    """
    resolved_path = _resolve_dataset_path(file_path)
    delimiter = get_csv_delimiter(file_path)
    dataset = pandas.read_csv(resolved_path, sep=delimiter, low_memory=False)
    class_name = list(dataset.columns)[-1]
    return dataset[:][:], class_name


def get_csv_delimiter(file_path):
    """
    Function to get the delimiter in the CSV file.

    Input:
        file_path - Path to the CSV file (relative to the datasets root)

    Output:
        delimiter in the CSV file
    """
    resolved_path = _resolve_dataset_path(file_path)
    with open(resolved_path, "r") as file:
        first_line = file.readline()
        dialect = csv.Sniffer().sniff(first_line)
        return str(dialect.delimiter)
