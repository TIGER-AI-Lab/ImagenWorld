"""
OpenAI GPT-Image-1 inference handler.
"""

import os
import base64
from typing import List, Dict, Any
from openai import OpenAI
from utils import load_metadata, build_prompt


class OpenAIHandler:
    """Handles OpenAI GPT-Image-1 inference."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-image-1"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
    
    def load_images(self, image_names: List[str], folder_path: str) -> List:
        """Load images for OpenAI API."""
        images = []
        for img_name in image_names:
            img_path = os.path.join(folder_path, img_name)
            if os.path.exists(img_path):
                try:
                    images.append(open(img_path, "rb"))
                except Exception as e:
                    print(f"❌ Failed to load image {img_path}: {e}")
        return images
    
    def process_entry(self, entry_path: str, metadata: Dict[str, Any], task_name: str, output_filename: str) -> bool:
        """Process a single entry."""
        topic = metadata.get("topic", "General")
        user_prompt = metadata.get("prompt_refined", "")
        cond_images = metadata.get("cond_images", [])
        
        final_prompt = build_prompt(task_name, topic, user_prompt)
        image_inputs = self.load_images(cond_images, entry_path)
        
        print(final_prompt)
        
        try:
            if image_inputs:
                result = self.client.images.edit(
                    model=self.model_name,
                    image=image_inputs[0],  # OpenAI edit only takes one image
                    prompt=final_prompt,
                    quality="medium"
                )
            else:
                result = self.client.images.generate(
                    model=self.model_name,
                    prompt=final_prompt,
                    quality="medium"
                )
            
            # Save the generated image
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            
            output_path = os.path.join(entry_path, output_filename)
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            
            print(f"✅ Saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"🚫 Error in {entry_path}: {e}")
            return False
    
    def process_single_example(self, input_path: str, task_name: str, output_filename: str) -> bool:
        """Process a single example."""
        json_path = os.path.join(input_path, "metadata.json")
        metadata = load_metadata(json_path)
        if metadata:
            return self.process_entry(input_path, metadata, task_name, output_filename)
        return False
    
    def process_all(self, root_dir: str, task_name: str, output_filename: str, limit: int = None) -> Dict[str, int]:
        """Process all entries in the root directory."""
        stats = {"processed": 0, "skipped": 0, "errors": 0}
        visited = 0
        
        for entry in sorted(os.listdir(root_dir)):
            entry_path = os.path.join(root_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            
            if limit is not None and visited >= limit:
                break
            visited += 1
            
            output_path = os.path.join(entry_path, output_filename)
            if os.path.exists(output_path):
                print(f"⏭️ Already processed {output_path}. Skipping.")
                stats["skipped"] += 1
                continue
            
            success = self.process_single_example(entry_path, task_name, output_filename)
            if success:
                stats["processed"] += 1
            else:
                stats["errors"] += 1
        
        return stats