# app.py
"""
Nepali Facebook Claim Annotation Interface

Data Storage Structure:
- Local: Use JSONL format with fields: annotator_id, post_id, text, image_id, label
- GitHub: Save directly to GitHub repository using GitHub API
"""
import streamlit as st
import pandas as pd
import json
import os
from PIL import Image
import logging
from pathlib import Path
import time
from datetime import datetime

# Import configuration with error handling
try:
    from config import (
        VALID_ANNOTATORS,
        get_dataset_paths,
        BASE_DIR,
        GUIDELINES_FILE,
        DEBUG_MODE,
        LIMIT_DATASET_SIZE
    )
except ValueError as e:
    # Handle missing environment variables
    import streamlit as st
    st.error(f"Configuration Error: {str(e)}")
    st.error("Please set the required environment variables and restart the application.")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set default level to INFO
logger = logging.getLogger(__name__)

# Disable watchdog debug messages
logging.getLogger('watchdog').setLevel(logging.WARNING)

# Set page config first
st.set_page_config(
    page_title="Nepali Facebook Claim Annotation",
    page_icon="📝",
    layout="wide"
)

def get_storage_config():
    """Get storage configuration dynamically to avoid caching issues"""
    STORAGE_TYPE = st.secrets.get('STORAGE_TYPE', 'local')
    GITHUB_TOKEN = st.secrets.get('GITHUB_TOKEN', None)
    GITHUB_REPO_OWNER = st.secrets.get('GITHUB_REPO_OWNER', 'hewanshrestha')
    GITHUB_REPO_NAME = st.secrets.get('GITHUB_REPO_NAME', 'facebook-claim-annotation')
    GITHUB_ANNOTATIONS_FOLDER = st.secrets.get('GITHUB_ANNOTATIONS_FOLDER', 'annotations')
    
    return STORAGE_TYPE, GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_ANNOTATIONS_FOLDER

def initialize_github_storage():
    """Initialize GitHub storage if configured"""
    STORAGE_TYPE, GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_ANNOTATIONS_FOLDER = get_storage_config()
    
    github_storage = None
    if STORAGE_TYPE == 'github':
        try:
            from github_storage import GitHubStorage
            if GITHUB_TOKEN:
                github_storage = GitHubStorage(
                    token=GITHUB_TOKEN,
                    repo_owner=GITHUB_REPO_OWNER,
                    repo_name=GITHUB_REPO_NAME,
                    folder=GITHUB_ANNOTATIONS_FOLDER
                )
            else:
                st.error("GitHub token not found. Please set GITHUB_TOKEN in secrets.")
                st.stop()
        except ImportError as e:
            st.error(f"Error importing GitHub storage: {str(e)}")
            st.stop()
    
    return github_storage, STORAGE_TYPE

def get_annotator_dirs(annotator_id):
    """Get the annotation and log directories for an annotator"""
    if annotator_id not in VALID_ANNOTATORS:
        raise ValueError(f"Invalid annotator ID. Must be one of: {', '.join(VALID_ANNOTATORS)}")
    
    annotator_dir = os.path.join(BASE_DIR, annotator_id)
    annotations_dir = os.path.join(annotator_dir, "annotations")
    logs_dir = os.path.join(annotator_dir, "logs")
    
    # Create directories if they don't exist
    os.makedirs(annotations_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    return annotations_dir, logs_dir

# Configure logging
def setup_logging(annotator_id):
    """Set up logging for a specific annotator"""
    global logger
    
    # Check if logging is already set up for this session to avoid multiple session start logs
    if 'logging_setup' not in st.session_state:
        st.session_state.logging_setup = True
        
        _, logs_dir = get_annotator_dirs(annotator_id)
        log_file = os.path.join(logs_dir, 'annotation_logs.log')
        
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        logger = logging.getLogger(__name__)
        logger.info(f"Annotation session started for {annotator_id}")
    else:
        logger = logging.getLogger(__name__)
    
    return logger

# Custom CSS (without .stRadio to avoid interference)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 2rem;
    }
    .claim-text-box {
        background-color: #fffbe6;
        border: 2px solid #d4af37;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 1rem;
    }
    .claim-text {
        font-size: 18px;
        line-height: 1.6;
        font-family: 'Noto Sans Devanagari', Arial, sans-serif;
    }
    .step-box, .step-box-2 {
        padding: 10px 15px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    .step-box {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .step-box-2 {
        background-color: #fff3e0;
        border-left: 4px solid #f57c00;
    }
    .step-text, .step-text-2 {
        font-size: 14px;
        font-weight: 500;
        margin: 0;
        line-height: 1.4;
    }
    .step-text { color: #0d47a1; }
    .step-text-2 { color: #e65100; }
    div[data-testid="stButton"] button {
        width: 100%;
        font-size: 16px;
        padding: 10px 0;
    }
    .nav-buttons {
        margin-top: 20px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    div[data-testid="stImage"] img {
        max-width: 80%;
        margin: 0 auto;
        display: block;
    }
    
    /* Responsive Design for smaller screens */
    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 28px !important;
        }
        .note-box {
            font-size: 16px !important;
            padding: 10px !important;
        }
        .claim-text {
            font-size: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_guidelines():
    """Load annotation guidelines from markdown file"""
    try:
        with open(GUIDELINES_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # Replace <br> with actual line breaks
            content = content.replace('<br>', '\n')
            return content
    except FileNotFoundError:
        return "Guidelines file not found."

def load_dataset(annotator_id):
    """Load the dataset of image-text pairs based on annotator ID"""
    try:
        # Get the appropriate dataset path for this annotator
        dataset_paths = get_dataset_paths(annotator_id)
        dataset_file = dataset_paths["dataset_file"]
        
        with open(dataset_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame and add unique IDs
        df = pd.DataFrame(data)
        df['id'] = [f"item_{i}" for i in range(len(df))]
        # Shuffle the DataFrame so codemixed and monolingual samples are mixed
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Limit dataset size if specified in config
        if LIMIT_DATASET_SIZE and LIMIT_DATASET_SIZE > 0:
            df = df.head(LIMIT_DATASET_SIZE)
            if DEBUG_MODE:
                logger.info(f"Dataset limited to {LIMIT_DATASET_SIZE} items for development")
        
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return pd.DataFrame()

def save_annotation(annotator_id, item_id, annotation, current_item):
    """Save annotation to local file or GitHub repository"""
    logger.debug(f"Starting save_annotation for item {item_id}")
    
    # Get the original post ID from the current item (check multiple possible field names)
    original_post_id = current_item.get('postId') or current_item.get('post_id') or current_item.get('id') or item_id
    
    annotation_data = {
        "annotator_id": annotator_id,
        "post_id": original_post_id,
        "text": current_item["text"],
        "image_id": current_item["image_id"],
        "label": annotation,
        "timestamp": datetime.now().isoformat()
    }
    
    github_storage, STORAGE_TYPE = initialize_github_storage()
    
    if STORAGE_TYPE == 'github' and github_storage:
        # Save to GitHub
        logger.debug("GitHub storage is enabled, saving to GitHub")
        success = github_storage.save_single_annotation(annotator_id, annotation_data)
        if success:
            logger.info(f"Annotation saved to GitHub for item {item_id}")
        else:
            logger.error(f"Failed to save annotation to GitHub for item {item_id}")
            # Fallback to local storage if GitHub fails
            logger.info("Falling back to local storage")
            _save_annotation_locally(annotator_id, annotation_data)
    else:
        # Save locally using the unified format
        logger.debug("Local storage is enabled, saving locally")
        _save_annotation_locally(annotator_id, annotation_data)
    
    logger.info(f"Annotation saved for item {item_id}")

def _save_annotation_locally(annotator_id, annotation_data):
    """Helper function to save annotation locally"""
    annotations_dir, _ = get_annotator_dirs(annotator_id)
    jsonl_file = os.path.join(annotations_dir, f"{annotator_id}_annotations.jsonl")
    
    # Convert to JSON string
    json_line = json.dumps(annotation_data, ensure_ascii=False)
    with open(jsonl_file, 'a', encoding='utf-8') as f:
        f.write(json_line + '\n')
    logger.debug(f"Saved annotation locally to {jsonl_file}")

def get_annotation_progress(annotator_id):
    """Get annotation progress for an annotator from local file or GitHub repository"""
    annotations = []
    
    github_storage, STORAGE_TYPE = initialize_github_storage()
    
    if STORAGE_TYPE == 'github' and github_storage:
        # Get from GitHub
        try:
            annotations = github_storage.get_annotations(annotator_id)
            logger.debug(f"Retrieved {len(annotations)} annotations from GitHub for {annotator_id}")
        except Exception as e:
            logger.error(f"Error getting annotations from GitHub: {str(e)}")
            # Fallback to local storage
            annotations = _get_annotations_locally(annotator_id)
    else:
        # Use local file
        annotations = _get_annotations_locally(annotator_id)
    
    return annotations

def _get_annotations_locally(annotator_id):
    """Helper function to get annotations from local storage"""
    annotations = []
    annotations_dir, _ = get_annotator_dirs(annotator_id)
    jsonl_file = os.path.join(annotations_dir, f"{annotator_id}_annotations.jsonl")
    if os.path.exists(jsonl_file):
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    annotations.append(json.loads(line))
    return annotations

def get_annotator_items(df, annotator_id):
    """Get the items assigned to a specific annotator. Now returns all items for all annotators."""
    return df.copy()

def get_next_unannotated_item(annotator_id, df):
    """Get the next unannotated item for the annotator from their assigned items"""
    # Get only the items assigned to this annotator
    assigned_items = get_annotator_items(df, annotator_id)
    
    annotated_items = set()
    
    # Get all existing annotations using unified method
    existing_annotations = get_annotation_progress(annotator_id)
    for data in existing_annotations:
        # Use post_id for matching (support both old and new format)
        post_id = data.get('post_id') or data.get('item_id')
        if post_id:
            annotated_items.add(post_id)
    
    # Also check temporary annotations
    temp_annotated_items = set(st.session_state.temp_annotations.keys())
    all_annotated_items = annotated_items.union(temp_annotated_items)
    
    for idx, row in assigned_items.iterrows():
        # Check if this item's post_id is already annotated
        item_post_id = row.get('post_id') or row.get('postId') or row.get('id')
        if item_post_id not in all_annotated_items:
            return row
    return None

def get_previous_annotations(annotator_id):
    """Get all previous annotations for an annotator"""
    return get_annotation_progress(annotator_id)

def update_annotation(annotator_id, item_id, new_annotation, current_item):
    """Update an existing annotation"""
    # Handle local storage using unified format
    annotations_dir, _ = get_annotator_dirs(annotator_id)
    jsonl_file = os.path.join(annotations_dir, f"{annotator_id}_annotations.jsonl")
    
    # Read all annotations
    annotations = get_previous_annotations(annotator_id)
    
    # Find and update the specific annotation
    updated = False
    for i, ann in enumerate(annotations):
        # Match by post_id (support both old and new format)
        ann_post_id = ann.get('post_id') or ann.get('item_id')
        current_post_id = current_item.get('post_id') or current_item.get('postId') or current_item.get('id')
        
        if ann_post_id == current_post_id:
            # Get the original post ID from the current item
            original_post_id = current_item.get('postId') or current_item.get('post_id') or current_item.get('id') or item_id
            
            annotations[i] = {
                "annotator_id": annotator_id,
                "post_id": original_post_id,
                "text": current_item["text"],
                "image_id": current_item["image_id"],
                "label": new_annotation,
                "timestamp": datetime.now().isoformat()
            }
            updated = True
            break
    
    # Convert annotations back to JSONL format
    updated_content = ""
    for ann in annotations:
        updated_content += json.dumps(ann, ensure_ascii=False) + '\n'
    
    # Update local file
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    logger.info(f"Annotation updated for item {item_id}")
    return updated

def save_all_temporary_annotations(annotator_id):
    """Save all temporary annotations to local file or GitHub repository"""
    try:
        if not st.session_state.temp_annotations:
            st.warning("No temporary annotations to save!")
            return False
        
        logger.info(f"Saving {len(st.session_state.temp_annotations)} temporary annotations")
        
        # Convert temporary annotations to list format
        annotations_to_save = []
        for item_id, annotation_data in st.session_state.temp_annotations.items():
            # Get the original post ID from the stored annotation data
            original_post_id = annotation_data.get('original_post_id') or annotation_data["item_id"]
            
            # Create unified format for storage
            local_annotation_data = {
                "annotator_id": annotation_data["annotator_id"],
                "post_id": original_post_id,
                "text": annotation_data["text"],
                "image_id": annotation_data["image_id"],
                "label": annotation_data["annotation"],
                "timestamp": datetime.now().isoformat()
            }
            annotations_to_save.append(local_annotation_data)
        
        github_storage, STORAGE_TYPE = initialize_github_storage()
        
        if STORAGE_TYPE == 'github' and github_storage:
            # Save to GitHub
            logger.debug("GitHub storage is enabled, saving all annotations to GitHub")
            success = github_storage.append_to_jsonl_file(annotator_id, annotations_to_save)
            if success:
                logger.info(f"Successfully saved {len(st.session_state.temp_annotations)} annotations to GitHub")
                return True
            else:
                logger.error("Failed to save annotations to GitHub")
                # Fallback to local storage if GitHub fails
                logger.info("Falling back to local storage")
                return _save_all_annotations_locally(annotator_id, annotations_to_save)
        else:
            # Save locally
            logger.debug("Local storage is enabled, saving all annotations locally")
            return _save_all_annotations_locally(annotator_id, annotations_to_save)
            
    except Exception as e:
        logger.error(f"Error in save_all_temporary_annotations: {str(e)}", exc_info=True)
        return False

def _save_all_annotations_locally(annotator_id, annotations_to_save):
    """Helper function to save all annotations locally"""
    try:
        annotations_dir, _ = get_annotator_dirs(annotator_id)
        jsonl_file = os.path.join(annotations_dir, f"{annotator_id}_annotations.jsonl")
        
        # Convert annotations to JSONL format
        jsonl_content = ""
        for annotation_data in annotations_to_save:
            jsonl_content += json.dumps(annotation_data, ensure_ascii=False) + '\n'
        
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(jsonl_content)
        logger.info(f"Successfully saved {len(annotations_to_save)} annotations locally")
        return True
    except Exception as e:
        logger.error(f"Error saving annotations locally: {str(e)}")
        return False

def main():
    # Initialize session state with separate tracking variables
    if 'current_item' not in st.session_state:
        st.session_state.current_item = None
    if 'is_previous' not in st.session_state:
        st.session_state.is_previous = False
    if 'prev_annotation_index' not in st.session_state:
        st.session_state.prev_annotation_index = -1
    if 'is_update' not in st.session_state:
        st.session_state.is_update = False
    if 'temp_annotations' not in st.session_state:
        st.session_state.temp_annotations = {}
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'submitted_annotations' not in st.session_state:
        st.session_state.submitted_annotations = 0
    
    # Use separate tracking variables (NOT widget keys)
    if 'display_claim_status' not in st.session_state:
        st.session_state.display_claim_status = "No Claim"
    if 'display_checkworthiness' not in st.session_state:
        st.session_state.display_checkworthiness = "Check-worthy"

    # Sidebar for annotator login and guidelines
    with st.sidebar:
        st.title("Annotation Interface")
        
        # Annotator login
        annotator_id = st.text_input("Enter your annotator ID:")
        if not annotator_id:
            st.warning("Please enter your annotator ID to begin.")
            return
        
        # Validate annotator ID
        if annotator_id not in VALID_ANNOTATORS:
            st.error(f"Invalid annotator ID. Please use one of: {', '.join(VALID_ANNOTATORS)}")
            return
        
        # Set up logging for the selected annotator
        logger = setup_logging(annotator_id)
        
        # Storage Configuration and Status
        st.header("Storage Configuration")
        STORAGE_TYPE, GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, GITHUB_ANNOTATIONS_FOLDER = get_storage_config()
        st.write(f"**Current Storage:** {STORAGE_TYPE.title()}")
        if STORAGE_TYPE == 'local':
            st.info("💾 Using local file storage")
        elif STORAGE_TYPE == 'github':
            st.info("🌐 Using GitHub storage")
            if GITHUB_TOKEN:
                # Test GitHub connection
                try:
                    from github_storage import GitHubStorage
                    github_storage = GitHubStorage(
                        token=GITHUB_TOKEN,
                        repo_owner=GITHUB_REPO_OWNER,
                        repo_name=GITHUB_REPO_NAME,
                        folder=GITHUB_ANNOTATIONS_FOLDER
                    )
                    if github_storage.test_connection():
                        st.success("✅ GitHub connection successful")
                    else:
                        st.error("❌ GitHub connection failed")
                except ImportError:
                    st.error("GitHub storage module not found. Please ensure it's installed.")
                    st.stop()
            else:
                st.error("GitHub token not found in secrets. Please set GITHUB_TOKEN in secrets.")
                st.stop()
        else:
            st.error("Unknown storage type. Please set STORAGE_TYPE in secrets.")
            st.stop()
        
        # Guidelines
        st.header("Guidelines")
        guidelines = load_guidelines()
        st.markdown(guidelines)
        
        # Dataset Assignment Info
        st.header("Your Assignment")
        dataset_paths = get_dataset_paths(annotator_id)
        if "nepali" in dataset_paths["dataset_file"].lower():
            st.info("📚 **Dataset:** Nepali Facebook Claims")
        elif "telugu" in dataset_paths["dataset_file"].lower():
            st.info("📚 **Dataset:** Telugu Facebook Claims")
        elif "bangla" in dataset_paths["dataset_file"].lower():
            st.info("📚 **Dataset:** Bangla Facebook Claims")
        else:
            st.info(f"📚 **Dataset:** {dataset_paths['dataset_file']}")
        
        # Progress tracking
        st.header("Your Progress")
        assigned_items = get_annotator_items(load_dataset(annotator_id), annotator_id)
        
        # Use local storage logic
        temp_annotations_count = len(st.session_state.temp_annotations)
        total_annotations = temp_annotations_count + st.session_state.submitted_annotations
        st.write(f"**Total annotations:** {total_annotations}")
        st.write(f"**Unsaved annotations:** {temp_annotations_count}")
        st.write(f"**Total items assigned:** {len(assigned_items)}")
        st.write(f"**Remaining items:** {len(assigned_items) - total_annotations}")
    
    # Main content area
    st.title("Facebook Claim Annotation")
    
    # Load dataset
    df = load_dataset(annotator_id)
    if df.empty:
        st.error("No data available for annotation.")
        return

    # Get assigned items for this annotator
    assigned_items = get_annotator_items(df, annotator_id)
    
    # Get current item
    if st.session_state.current_index >= len(assigned_items):
        st.markdown("""
            <div style="color: #00a86b; font-weight: bold; font-size: 25px; margin: 15px 0; padding: 10px; border-left: 4px solid #00a86b; background-color: #e6f7f0; display: inline-block; width: fit-content;">
                Congratulations! You have completed all annotations.
            </div>
        """, unsafe_allow_html=True)
        
        # Add Submit All button below congratulations message
        if len(st.session_state.temp_annotations) > 0:
            st.markdown(f"""
                <div style="color: #0066cc; font-weight: bold; font-size: 25px; margin: 15px 0; padding: 10px; border-left: 4px solid #0066cc; background-color: #e6f0ff; display: inline-block; width: fit-content;">
                    You have {len(st.session_state.temp_annotations)} unsaved annotations.
                </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                <style>
                    div[data-testid="stButton"] button {
                        padding: 20px 40px;
                        height: auto;
                    }
                    div[data-testid="stButton"] button p {
                        font-size: 20px !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            if st.button("Submit All Annotations", type="primary"):
                with st.spinner("Submitting all annotations..."):
                    success = save_all_temporary_annotations(annotator_id)
                    if success:
                        st.success(f"Successfully submitted {len(st.session_state.temp_annotations)} annotations!")
                        # Update submitted annotations count and clear temporary storage
                        st.session_state.submitted_annotations += len(st.session_state.temp_annotations)
                        st.session_state.temp_annotations = {}
                        st.rerun()
                    else:
                        st.error("Failed to submit annotations. Please try again.")
        else:
            st.markdown("""
                <div style="color: #00a86b; font-weight: bold; font-size: 25px; margin: 15px 0; padding: 10px; border-left: 4px solid #00a86b; background-color: #e6f7f0; display: inline-block; width: fit-content;">
                    All annotations have been submitted!
                </div>
            """, unsafe_allow_html=True)
        return
    
    # Display important note in red (only when not on congratulations page)
    st.markdown("""
        <div class="note-box" style="color: #ff0000; font-weight: bold; font-size: 22px; margin: 15px 0; padding: 10px; border-left: 4px solid #ff0000; background-color: #fff0f0; display: inline-block; width: fit-content;">
            Note: Consider both the image and text together when making your decision
        </div>
    """, unsafe_allow_html=True)
    
    current_item = assigned_items.iloc[st.session_state.current_index]
    st.session_state.current_item = current_item
    
    # Check if this item has a temporary annotation
    if current_item['id'] in st.session_state.temp_annotations:
        temp_ann = st.session_state.temp_annotations[current_item['id']]
        st.session_state.display_claim_status = temp_ann['annotation']['claim_status']
        if temp_ann['annotation']['claim_status'] == "Claim":
            st.session_state.display_checkworthiness = temp_ann['annotation']['checkworthiness']
    else:
        st.session_state.display_claim_status = "No Claim"
        st.session_state.display_checkworthiness = "Check-worthy"

    # --- Two-Column Layout ---
    col1, col2 = st.columns([3, 2])

    with col1:
        # Display text
        st.markdown('<h5>Claim Text & Image</h5>', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="claim-text-box">
                <div class="claim-text">{current_item["text"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    
        # Display image
        try:
            # Get the appropriate images directory for this annotator
            dataset_paths = get_dataset_paths(annotator_id)
            images_dir = dataset_paths["images_dir"]
            image_path = os.path.join(images_dir, current_item['image_id'])
            image = Image.open(image_path)
            st.image(image, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")

    with col2:
        # Annotation form
        st.markdown('<h5>Label the Claim</h5>', unsafe_allow_html=True)
    
        # Step 1: Claim Detection
        st.markdown('''
            <div class="step-box">
                <p class="step-text"><b>Q1: Claim Detection</b> <br> Does the image-text pair make a factual claim that can be verified?</p>
            </div>
        ''', unsafe_allow_html=True)
    
        claim_options = ["Claim", "No Claim"]
        claim_index = 0 if st.session_state.display_claim_status == "Claim" else 1
        claim_status = st.radio(
            "Is this a claim?",
            claim_options,
            index=claim_index,
            horizontal=True,
            label_visibility="collapsed"
        )

        # Task 2: Checkworthiness Detection
        checkworthiness = None
        if claim_status == "Claim":
            st.markdown('''
                <div class="step-box-2">
                    <p class="step-text-2"><b>Q2: Checkworthiness Detection</b> <br> If "Claim" to Q1, does it present content that is harmful, up-to-date, urgent or breaking news information or likely to mislead the public and therefore worth fact-checking? </p>
                </div>
            ''', unsafe_allow_html=True)
        
            checkworthy_options = ["Check-worthy", "Not Check-worthy"]
            checkworthy_index = 0 if st.session_state.display_checkworthiness == "Check-worthy" else 1
            checkworthiness = st.radio(
                "Is this claim check-worthy?",
                checkworthy_options,
                index=checkworthy_index,
                horizontal=True,
                label_visibility="collapsed"
            )

        # Navigation buttons
        st.markdown("""<div class="nav-buttons">""", unsafe_allow_html=True)
    
        if st.button("Previous", disabled=st.session_state.current_index == 0):
            st.session_state.current_index -= 1
            st.rerun()
    
        if st.button("Next"):
            # Save current annotation to temporary storage
            annotation = {
                "claim_status": claim_status,
                "checkworthiness": checkworthiness if claim_status == "Claim" else None
            }
            
            # Get the original post ID from the current item (check multiple possible field names)
            original_post_id = current_item.get('postId') or current_item.get('post_id') or current_item.get('id') or current_item['id']
            
            st.session_state.temp_annotations[current_item['id']] = {
                "annotator_id": annotator_id,
                "item_id": current_item['id'],
                "original_post_id": original_post_id,  # Store original post ID
                "text": current_item["text"],
                "image_id": current_item["image_id"],
                "annotation": annotation
            }
        
            st.session_state.current_index += 1
            st.rerun()
    
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()