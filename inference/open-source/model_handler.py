from typing import List, Callable, Any
from PIL import Image
from config import MODEL_PARAMS


class ModelHandler:
    """Handles model-specific inference logic and parameters."""
    
    def __init__(self, model):
        self.model = model
    
    def get_inference_function(self, model_name: str, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """Get the appropriate inference function based on model name and inputs."""
        
        if model_name == "OmniGen2":
            return self._get_omnigen2_inference(image_inputs, prompt)
        elif model_name in ["BagelGeneration", "BagelEdit"]:
            return self._get_bagel_inference(model_name, image_inputs, prompt)
        elif model_name == "UNO":
            return self._get_uno_inference(image_inputs, prompt)
        elif model_name in ["SDXL", "Infinity", "JanusPro", "QwenImage"]:
            return self._get_text_to_image_inference(prompt)
        elif model_name == "InstructPix2Pix":
            return self._get_instructpix2pix_inference(image_inputs, prompt)
        elif model_name in ["Step1XEdit", "ICEdit"]:
            return self._get_edit_inference(model_name, image_inputs, prompt)
        elif model_name in ["FLUX1Kreadev", "FLUX1Kontextdev"]:
            return self._get_flux_inference(model_name, image_inputs, prompt)
        else:
            return self._get_default_inference(image_inputs, prompt)
    
    def _get_omnigen2_inference(self, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """OmniGen2 specific inference."""
        params = MODEL_PARAMS["OmniGen2"]
        if image_inputs:
            return lambda: self.model.infer_one_image(
                prompt=prompt,
                input_images=image_inputs,
                text_guidance_scale=params["text_guidance_scale"],
                image_guidance_scale=params["image_guidance_scale"],
                max_sequence_length=params["max_sequence_length"]
            )
        else:
            return lambda: self.model.infer_one_image(
                prompt=prompt,
                text_guidance_scale=params["text_guidance_scale_no_image"],
                image_guidance_scale=params["image_guidance_scale_no_image"],
                max_sequence_length=params["max_sequence_length"]
            )
    
    def _get_bagel_inference(self, model_name: str, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """Bagel specific inference."""
        # Bagel only accepts prompt, input_images, think, and seed parameters
        return lambda: self.model.infer_one_image(
            prompt=prompt,
            input_images=image_inputs,
            think=False,
            seed=42
        )
    
    def _get_uno_inference(self, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """UNO specific inference."""
        if image_inputs:
            return lambda: self.model.infer_one_image(
                prompt=prompt,
                input_images=image_inputs
            )
        else:
            return lambda: self.model.infer_one_image(prompt=prompt)
    
    def _get_text_to_image_inference(self, prompt: str) -> Callable:
        """Text-to-image models inference."""
        return lambda: self.model.infer_one_image(prompt=prompt)
    
    def _get_instructpix2pix_inference(self, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """InstructPix2Pix specific inference."""
        if image_inputs:
            return lambda: self.model.infer_one_image(
                instruct_prompt=prompt,
                src_image=image_inputs[0]
            )
        else:
            return lambda: self.model.infer_one_image(instruct_prompt=prompt)
    
    def _get_edit_inference(self, model_name: str, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """Generic edit models inference."""
        if image_inputs:
            return lambda: self.model.infer_one_image(
                prompt=prompt,
                src_image=image_inputs[0]
            )
        else:
            return lambda: self.model.infer_one_image(prompt=prompt)
    
    def _get_flux_inference(self, model_name: str, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """Flux models specific inference."""
        if model_name == "FLUX1Kontextdev" and image_inputs:
            return lambda: self.model.infer_one_image(
                prompt=prompt,
                src_image=image_inputs[0]
            )
        else:
            return lambda: self.model.infer_one_image(prompt=prompt)
    
    def _get_default_inference(self, image_inputs: List[Image.Image], prompt: str) -> Callable:
        """Default inference for unknown models."""
        if image_inputs:
            if len(image_inputs) == 1:
                return lambda: self.model.infer_one_image(
                    instruct_prompt=prompt,
                    src_image=image_inputs[0]
                )
            else:
                return lambda: self.model.infer_one_image(
                    prompt=prompt,
                    input_images=image_inputs
                )
        else:
            return lambda: self.model.infer_one_image(prompt=prompt)