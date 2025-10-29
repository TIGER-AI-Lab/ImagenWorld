"""
Configuration for closed-source inference pipeline.
"""

# Task mapping
ID_TO_TASK = {
    "TIG": "Text-guided Image Generation",
    "TIE": "Text-guided Image Editing",
    "SRIG": "Single Reference-guided Image Generation",
    "SRIE": "Single Reference-guided Image Editing",
    "MRIG": "Multiple References-guided Image Generation",
    "MRIE": "Multiple References-guided Image Editing"
}

TASK_DEFINITIONS = {
    "Text-guided Image Generation": (
        "Generate a completely new image based only on a descriptive text prompt. "
        "No source or reference images are provided."
    ),
    "Text-guided Image Editing": (
        "Edit an existing image using a descriptive text prompt. "
        "Decide what to modify in the image based on the prompt. No mask or marked region is given."
    ),
    "Single Reference-guided Image Generation": (
        "Create a new image by combining visual cues from one reference image "
        "with instructions from a descriptive text prompt."
    ),
    "Single Reference-guided Image Editing": (
        "Edit an existing image using both a reference image and a text prompt. "
        "Use the reference image to guide the style or content of the edits."
    ),
    "Multiple References-guided Image Generation": (
        "Generate a new image using several reference images along with a text prompt. "
        "The new image should reflect visual elements from the references and follow the prompt's description."
    ),
    "Multiple References-guided Image Editing": (
        "Modify an existing image using multiple reference images and a descriptive text prompt. "
        "The edits should be guided by both the style or content of the references and the instructions in the prompt."
    )
}

ID_TO_TOPIC = {
    "I": "Information Graphics",
    "A": "Artworks",
    "S": "Screenshots",
    "CG": "Computer Graphics",
    "P": "Photorealistic Images",
    "T": "Textual Graphics"
}

# Model configuration
MODEL_CONFIG = {
    "GPT-Image-1": {
        "provider": "openai",
        "model_name": "gpt-image-1",
        "output_filename": "gpt-image-1.png",
        "tasks": ["TIG", "TIE", "SRIG", "SRIE", "MRIG", "MRIE"]
    },
    "Gemini2Flash": {
        "provider": "google",
        "model_name": "gemini-2.5-flash-image-preview",
        "output_filename": "gemini.png",
        "tasks": ["TIG", "TIE", "SRIG", "SRIE", "MRIG", "MRIE"]
    }
}

# API Key environment variable names
API_KEY_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "google": "GEMINI_API_KEY"
}