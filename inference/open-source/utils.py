import os
import json
from PIL import Image
from typing import List, Dict, Any, Optional


def load_metadata(json_path: str) -> Optional[Dict[str, Any]]:
    """Load metadata from JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {json_path}: {e}")
        return None


def load_images(image_names: List[str], folder_path: str) -> List[Image.Image]:
    """Load images from the specified folder."""
    images = []
    for img_name in image_names:
        img_path = os.path.join(folder_path, img_name)
        if os.path.exists(img_path):
            try:
                images.append(Image.open(img_path).convert("RGB"))
            except Exception as e:
                print(f"❌ Failed to load image {img_path}: {e}")
    return images


def infer_task_from_path(input_path: str) -> Optional[str]:
    """Infer task name from input path."""
    # Extract task from path (e.g., "TIG", "TIE", etc.)
    path_parts = input_path.split(os.sep)
    for part in path_parts:
        if part in ["TIG", "TIE", "SRIG", "SRIE", "MRIG", "MRIE"]:
            return part
    return None


def validate_model_for_task(model_name: str, task: str) -> bool:
    """Validate if model is recommended for the task."""
    from config import MODEL_MAPPING
    return model_name in MODEL_MAPPING.get(task, [])