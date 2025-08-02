# github_storage.py
"""
GitHub storage module for saving annotations to GitHub repository
"""
import base64
import json
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubStorage:
    def __init__(self, token: str, repo_owner: str, repo_name: str, folder: str = 'annotations'):
        """
        Initialize GitHub storage client
        
        Args:
            token: GitHub Personal Access Token
            repo_owner: GitHub repository owner (username/organization)
            repo_name: Repository name
            folder: Folder in the repo to save annotations
        """
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.folder = folder
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def _get_file_content(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get existing file content from GitHub"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None  # File doesn't exist
            else:
                logger.error(f"Error getting file content: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception getting file content: {str(e)}")
            return None
    
    def _create_or_update_file(self, file_path: str, content: str, message: str) -> bool:
        """Create or update a file in GitHub repository"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        # Get existing file to get SHA (required for updates)
        existing_file = self._get_file_content(file_path)
        
        # Encode content to base64
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": message,
            "content": content_encoded
        }
        
        # If file exists, include SHA for update
        if existing_file:
            data["sha"] = existing_file["sha"]
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                logger.info(f"Successfully {'updated' if existing_file else 'created'} file: {file_path}")
                return True
            else:
                logger.error(f"Error saving file: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception saving file: {str(e)}")
            return False
    
    def append_to_jsonl_file(self, annotator_id: str, new_annotations: list) -> bool:
        """
        Append new annotations to annotator's JSONL file
        
        Args:
            annotator_id: ID of the annotator
            new_annotations: List of annotation dictionaries to append
            
        Returns:
            bool: True if successful, False otherwise
        """
        file_path = f"{self.folder}/{annotator_id}_annotations.jsonl"
        
        try:
            # Get existing content
            existing_file = self._get_file_content(file_path)
            existing_content = ""
            
            if existing_file:
                # Decode existing content
                existing_content = base64.b64decode(existing_file["content"]).decode('utf-8')
            
            # Append new annotations
            new_lines = []
            for annotation in new_annotations:
                json_line = json.dumps(annotation, ensure_ascii=False)
                new_lines.append(json_line)
            
            # Combine existing and new content
            if existing_content and not existing_content.endswith('\n'):
                existing_content += '\n'
            
            updated_content = existing_content + '\n'.join(new_lines) + '\n'
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            message = f"Add {len(new_annotations)} annotations from {annotator_id} - {timestamp}"
            
            return self._create_or_update_file(file_path, updated_content, message)
            
        except Exception as e:
            logger.error(f"Error appending to JSONL file: {str(e)}")
            return False
    
    def save_single_annotation(self, annotator_id: str, annotation_data: Dict[str, Any]) -> bool:
        """
        Save a single annotation to GitHub
        
        Args:
            annotator_id: ID of the annotator
            annotation_data: Single annotation dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.append_to_jsonl_file(annotator_id, [annotation_data])
    
    def get_annotations(self, annotator_id: str) -> list:
        """
        Get all annotations for an annotator from GitHub
        
        Args:
            annotator_id: ID of the annotator
            
        Returns:
            list: List of annotation dictionaries
        """
        file_path = f"{self.folder}/{annotator_id}_annotations.jsonl"
        
        try:
            existing_file = self._get_file_content(file_path)
            if not existing_file:
                return []
            
            # Decode content
            content = base64.b64decode(existing_file["content"]).decode('utf-8')
            
            # Parse JSONL
            annotations = []
            for line in content.strip().split('\n'):
                if line.strip():
                    annotations.append(json.loads(line))
            
            return annotations
            
        except Exception as e:
            logger.error(f"Error getting annotations: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """Test GitHub API connection and permissions"""
        url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                logger.info("GitHub connection test successful")
                return True
            else:
                logger.error(f"GitHub connection test failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"GitHub connection test exception: {str(e)}")
            return False 