import os
import traceback
from typing import Dict, Any, Optional
from imagen_hub.utils import save_pil_image
from utils import load_metadata, load_images, infer_task_from_path
from model_handler import ModelHandler


class ImageProcessor:
    """Main processor for handling image generation tasks."""
    
    def __init__(self, model):
        self.model_handler = ModelHandler(model)
    
    def process_entry(self, entry_path: str, metadata: Dict[str, Any], task_name: str, 
                     model_name: str) -> bool:
        """Process a single entry with the specified model."""
        user_prompt = metadata.get("prompt_refined", "")
        cond_images = metadata.get("cond_images", [])
        
        image_inputs = load_images(cond_images, entry_path)
        print(f"Processing with {model_name}: {user_prompt}")
        
        out_dir = os.path.join(entry_path, "model_output")
        os.makedirs(out_dir, exist_ok=True)
        
        # Generate output filename based on model name
        output_filename = f"{model_name.lower()}.png"
        output_path = os.path.join(out_dir, output_filename)
        
        # Skip if already processed
        if os.path.exists(output_path):
            print(f"⏭️ Already processed {output_path}. Skipping.")
            return True
        
        try:
            # Get the appropriate inference function
            inference_func = self.model_handler.get_inference_function(
                model_name, image_inputs, user_prompt
            )
            
            # Generate the image
            image = inference_func()
            
            # Save the image
            save_pil_image(image, out_dir, output_filename)
            print(f"✅ Processed: {output_path}")
            return True
            
        except Exception as e:
            print(f"🚫 Error in {entry_path} with {model_name}: {e}")
            traceback.print_exc()
            return False
    
    def process_single_example(self, input_path: str, model_name: str) -> bool:
        """Process a single example with the specified model."""
        task_name = infer_task_from_path(input_path)
        if not task_name:
            print(f"❌ Could not infer task name from path: {input_path}")
            return False

        json_path = os.path.join(input_path, "metadata.json")
        metadata = load_metadata(json_path)
        if metadata:
            return self.process_entry(input_path, metadata, task_name, model_name)
        return False
    
    def process_all(self, root_dir: str, model_name: str, limit: Optional[int] = None) -> Dict[str, int]:
        """Process all entries in the root directory with the specified model.
        
        Args:
            root_dir: Task directory containing per-sample folders.
            model_name: Model to use.
            limit: If provided, process at most this many folders; otherwise process all.
        """
        stats = {"processed": 0, "skipped": 0, "errors": 0}
        visited = 0
        
        for entry in sorted(os.listdir(root_dir)):
            entry_path = os.path.join(root_dir, entry)
            if not os.path.isdir(entry_path):
                continue
            
            if limit is not None and visited >= limit:
                break
            visited += 1
            
            success = self.process_single_example(entry_path, model_name)
            if success:
                stats["processed"] += 1
            else:
                stats["errors"] += 1
        
        return stats