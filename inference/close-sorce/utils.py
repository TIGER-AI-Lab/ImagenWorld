"""
Utility functions for closed-source inference.
"""

import os
import json
from typing import Dict, Any, Optional, List
from config import ID_TO_TASK, TASK_DEFINITIONS, ID_TO_TOPIC, MODEL_CONFIG, API_KEY_ENV_VARS


def load_metadata(json_path: str) -> Optional[Dict[str, Any]]:
    """Load metadata from JSON file."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {json_path}: {e}")
        return None


def build_prompt(task_name: str, topic: str, user_prompt: str) -> str:
    """Build a comprehensive prompt for the model."""
    task_definition = TASK_DEFINITIONS.get(task_name, "")
    topic_description = ID_TO_TOPIC.get(topic, topic)
    return (
        f"You are an expert visual generation assistant.\n\n"
        f"Task: {task_name}\n"
        f"Task Definition: {task_definition}\n"
        f"Visual Domain: {topic_description}\n"
        f"User Objective: {user_prompt}\n\n"
        f"Please generate an image that fulfills the user's objective, adheres to the task definition, "
        f"and fits within the specified visual domain."
    )


def infer_task_from_path(input_path: str) -> Optional[str]:
    """Infer task name from input path."""
    for tid, name in ID_TO_TASK.items():
        if tid in input_path:
            return name
    return None


def validate_model_for_task(model_name: str, task: str) -> bool:
    """Validate if model is recommended for the task."""
    return task in MODEL_CONFIG.get(model_name, {}).get("tasks", [])


def get_api_key(provider: str, api_key_arg: Optional[str] = None) -> str:
    """Get API key from argument or environment variable."""
    if api_key_arg:
        return api_key_arg
    
    env_var = API_KEY_ENV_VARS.get(provider)
    if not env_var:
        raise ValueError(f"Unknown provider: {provider}")
    
    api_key = os.getenv(env_var)
    if not api_key:
        raise RuntimeError(f"❌ {env_var} environment variable not set and no API key provided via argument.")
    
    return api_key