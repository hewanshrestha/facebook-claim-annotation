
# config.py
"""
Configuration file for the annotation interface.
"""

# Storage Configuration
# Options: 'mongodb', 'local'
STORAGE_TYPE = 'mongodb'

# Valid annotator IDs
VALID_ANNOTATORS = [f"annotator_{i:02d}" for i in range(1, 8)]

# Dataset assignment
def get_dataset_paths(annotator_id):
    """Return dataset paths based on annotator ID"""
    if annotator_id in ["annotator_01", "annotator_02", "annotator_03", "annotator_04"]:
        return {
            "images_dir": "pilot_data_nepali/images",
            "dataset_file": "pilot_data_nepali/pilot_data.json"
        }
    elif annotator_id in ["annotator_05", "annotator_06", "annotator_07"]:
        return {
            "images_dir": "pilot_data_telugu/images", 
            "dataset_file": "pilot_data_telugu/pilot_data.json"
        }
    else:
        raise ValueError(f"Invalid annotator ID: {annotator_id}")

# MongoDB Configuration
def get_mongodb_uri():
    """Construct MongoDB URI from Streamlit secrets"""
    try:
        import streamlit as st
        creds = st.secrets["mongodb"]
        username = creds["MONGODB_USERNAME"]
        password = creds["MONGODB_PASSWORD"]
        cluster_url = creds.get("MONGODB_CLUSTER_URL", "claim-annotation.eimxn2e.mongodb.net")
        app_name = creds.get("MONGODB_APP_NAME", "Claim-Annotation")
    except Exception as e:
        raise RuntimeError(
            "❌ MongoDB credentials not found in Streamlit secrets.\n"
            "Ensure you have the following in `.streamlit/secrets.toml` or in Streamlit Cloud Secrets:\n\n"
            "[mongodb]\n"
            "MONGODB_USERNAME = \"your_username\"\n"
            "MONGODB_PASSWORD = \"your_password\"\n"
            "MONGODB_CLUSTER_URL = \"your_cluster.mongodb.net\"\n"
            "MONGODB_APP_NAME = \"Claim-Annotation\"\n"
        ) from e

    return (
        f"mongodb+srv://{username}:{password}@{cluster_url}/"
        f"?retryWrites=true&w=majority&appName={app_name}"
        f"&maxPoolSize=10&serverSelectionTimeoutMS=30000"
    )

# MongoDB connection settings
MONGODB_CONFIG = {
    "URI": get_mongodb_uri(),
    "DATABASE": "Claim-Annotation"
}

# Annotation guideline and development settings
BASE_DIR = "annotation_interface"
GUIDELINES_FILE = f"{BASE_DIR}/guidelines.md"

# Development mode
DEBUG_MODE = False
LIMIT_DATASET_SIZE = 10  # Use None in production
