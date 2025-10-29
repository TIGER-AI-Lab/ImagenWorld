"""
Google Gemini inference handler.
"""

import os
import time
from io import BytesIO
from typing import List, Dict, Any
from PIL import Image
from google import genai
from google.genai import types
from utils import load_metadata, build_prompt


class GoogleHandler:
    """Handles Google Gemini inference."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash-image-preview"):
        print(f"🔑 Initializing Google handler with key: {api_key[:8]}...{api_key[-4:]}")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    def load_images(self, image_names: List[str], folder_path: str) -> List:
        """Load images for Google Gemini API - matches original working code."""
        images = []
        for img_name in image_names:
            img_path = os.path.join(folder_path, img_name)
            if os.path.exists(img_path):
                try:
                    images.append(self.client.files.upload(file=img_path))
                except Exception as e:
                    print(f"❌ Failed to load image {img_path}: {e}")
        return images
    
    def process_entry(self, entry_path: str, metadata: Dict[str, Any], task_name: str, output_filename: str) -> bool:
        """Process a single entry - matches original working code exactly."""
        topic = metadata.get("topic", "General")
        user_prompt = metadata.get("prompt_refined", "")
        cond_images = metadata.get("cond_images", [])
        
        final_prompt = build_prompt(task_name, topic, user_prompt)
        image_inputs = self.load_images(cond_images, entry_path)
        
        print(final_prompt)
        
        try:
            if image_inputs:
                contents = [final_prompt] + image_inputs
            else:
                contents = [final_prompt]
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            # Save the generated image - matches original exactly
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    output_path = os.path.join(entry_path, output_filename)
                    image.save(output_path)
                    print(f"✅ Saved: {output_path}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"🚫 Error in {entry_path}: {e}")
            return False
    
    def process_single_example(self, input_path: str, task_name: str, output_filename: str) -> bool:
        """Process a single example - matches original working code."""
        json_path = os.path.join(input_path, "metadata.json")
        metadata = load_metadata(json_path)
        if metadata:
            success = self.process_entry(input_path, metadata, task_name, output_filename)
            # Match original timing
            time.sleep(5)
            return success
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