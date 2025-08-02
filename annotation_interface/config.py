
# config.py
"""
Configuration file for the annotation interface.
"""

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

# Annotation guideline and development settings
BASE_DIR = "annotation_interface"
GUIDELINES_FILE = f"{BASE_DIR}/guidelines.md"

# Development mode
DEBUG_MODE = False
LIMIT_DATASET_SIZE = 10  # Use None in production
