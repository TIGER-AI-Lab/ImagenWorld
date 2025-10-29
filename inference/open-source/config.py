# Model mapping for different tasks
MODEL_MAPPING = {
    "TIG": ["SDXL", "Infinity", "JanusPro", "UNO", "BagelGeneration", "OmniGen2", "FLUX1Kreadev", "QwenImage"],
    "TIE": ["InstructPix2Pix", "BagelEdit", "Step1XEdit", "ICEdit", "OmniGen2", "FLUX1Kontextdev"],
    "SRIG": ["OmniGen2", "BagelGeneration", "UNO"],
    "SRIE": ["OmniGen2", "BagelEdit"],
    "MRIG": ["OmniGen2", "BagelGeneration", "UNO"],
    "MRIE": ["OmniGen2", "BagelEdit"]
}

# Model-specific parameters
MODEL_PARAMS = {
    "OmniGen2": {
        "text_guidance_scale": 5.0,
        "image_guidance_scale": 2.8,
        "max_sequence_length": 4096,
        "text_guidance_scale_no_image": 4.0,
        "image_guidance_scale_no_image": 1.0
    }
}