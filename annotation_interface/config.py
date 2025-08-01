# config.py
"""
Configuration file for the annotation interface
WBu3KrMCpbFzqAmt
"""
import os

# Storage Configuration
# Options: 'mongodb', 'local'
STORAGE_TYPE = 'mongodb'

# MongoDB Configuration
def get_mongodb_uri():
    """Construct MongoDB URI from Streamlit secrets only"""
    username = None
    password = None
    cluster_url = 'claim-annotation.eimxn2e.mongodb.net'
    app_name = 'Claim-Annotation'
    source = "unknown"
    
    # Only try to get from Streamlit secrets
    try:
        import streamlit as st
        # print("Streamlit secrets found")
        # print(st.secrets)
        # Try nested structure first
        if hasattr(st.secrets, 'mongodb'):
            username = st.secrets.mongodb.MONGODB_USERNAME
            password = st.secrets.mongodb.MONGODB_PASSWORD
            cluster_url = st.secrets.mongodb.get('MONGODB_CLUSTER_URL', 'claim-annotation.eimxn2e.mongodb.net')
            app_name = st.secrets.mongodb.get('MONGODB_APP_NAME', 'Claim-Annotation')
            source = "streamlit_secrets_nested"
            print(f"✅ Reading MongoDB credentials from: {source}")
        # Try flat structure
        elif hasattr(st.secrets, 'MONGODB_USERNAME'):
            username = st.secrets.MONGODB_USERNAME
            password = st.secrets.MONGODB_PASSWORD
            cluster_url = st.secrets.get('MONGODB_CLUSTER_URL', 'claim-annotation.eimxn2e.mongodb.net')
            app_name = st.secrets.get('MONGODB_APP_NAME', 'Claim-Annotation')
            source = "streamlit_secrets_flat"
            print(f"✅ Reading MongoDB credentials from: {source}")
        else:
            source = "streamlit_secrets_not_found"
            print(f"❌ No MongoDB credentials found in Streamlit secrets")
    except (ImportError, AttributeError) as e:
        print(f"❌ Failed to read from Streamlit secrets: {e}")
        print("   This is normal if running outside of Streamlit")
        source = "streamlit_not_available"
    
    if not username or not password:
        raise ValueError(
            f"MongoDB credentials not found. Source attempted: {source}. "
            "Please set MongoDB credentials in .streamlit/secrets.toml file:\n"
            "[mongodb]\n"
            "MONGODB_USERNAME = \"your_username\"\n"
            "MONGODB_PASSWORD = \"your_password\"\n"
            "MONGODB_CLUSTER_URL = \"your_cluster.mongodb.net\"\n"
            "MONGODB_APP_NAME = \"Claim-Annotation\""
        )
    
    print(f"🔑 Using MongoDB credentials from: {source}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'None'}")
    print(f"   Cluster: {cluster_url}")
    
    # Simplified connection string for MongoDB Atlas
    return f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority&appName={app_name}"

MONGODB_CONFIG = {
    'URI': get_mongodb_uri(),
    'DATABASE': "Claim-Annotation"
    # Collection will be created dynamically based on annotator ID
}

# Valid annotator IDs
VALID_ANNOTATORS = [f"annotator_{i:02d}" for i in range(1, 8)]  # Creates annotator_01 through annotator_07

# Dataset assignment function
def get_dataset_paths(annotator_id):
    """Get the appropriate dataset and images directory based on annotator ID"""
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

# Default file paths (will be overridden based on annotator)
# IMAGES_DIR = "pilot_data_nepali/images"
# DATASET_FILE = "pilot_data_nepali/pilot_data.json"
BASE_DIR = "annotation_interface"
GUIDELINES_FILE = "annotation_interface/guidelines.md"

# Development settings
DEBUG_MODE = False
LIMIT_DATASET_SIZE = 10  # Set to None for production to use full dataset 