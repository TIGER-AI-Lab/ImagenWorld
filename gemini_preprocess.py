import json
import os
from io import BytesIO
from PIL import Image
from google import genai
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

key = 'YOUR-GEMINI-KEY'
client = genai.Client(api_key=key)
model = "gemini-2.5-flash-preview-05-20"

# --- Task Definitions ---
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
        "The new image should reflect visual elements from the references and follow the prompt’s description."
    ),
    "Multiple References-guided Image Editing": (
        "Modify an existing image using multiple reference images and a descriptive text prompt. "
        "The edits should be guided by both the style or content of the references and the instructions in the prompt."
    )
}


id_to_task = {
    "TIG": "Text-guided Image Generation",
    "TIE": "Text-guided Image Editing",
    "SRIG": "Single Reference-guided Image Generation",
    "SRIE": "Single Reference-guided Image Editing",
    "MRIG": "Multiple References-guided Image Generation",
    "MRIE": "Multiple References-guided Image Editing"
}

id_to_topic = {
    "I": "Information Graphics",
    "A": "Artworks",
    "S": "Screenshots",
    "CG": "Computer Graphics",
    "P": "Photorealistic Images",
    "T": "Textual Graphics"
}
# --- Prompt Builder ---

def build_instruction(task, topic, original_prompt, image_count):
    definition = TASK_DEFINITIONS.get(id_to_task[task], "No formal definition provided.")
    if definition == "No formal definition provided.":
        logger.warning("Oops")
    
    is_editing = "Editing" in id_to_task[task]
    has_images = image_count > 0
    requires_images = task != "TIG"

    instruction = (
        f"Rewrite the following dataset prompt for an image generation/editing task.\n\n"
        f"Task: {id_to_task[task]}\n"
        f"Definition: {definition}\n"
        f"Topic: {id_to_topic[topic]}\n"
        f"Original Prompt: \"{original_prompt}\"\n"
        f"Conditioning Images: {image_count}\n\n"
        f"The revised prompt should:\n"
        f"- Match the task’s intended function (e.g., generate, edit)\n"
        f"- Be clear, specific, and detailed enough for both humans and models to follow\n"
        f"- Avoid vague or generic phrases like 'make it nice' or 'improve this'\n"
        f"- Be concise — neither too short nor overly long\n"
        f"- Include specific positional or spatial details when relevant (e.g., 'on the left', 'in the top-right corner')\n"
    )

    if requires_images and has_images:
        instruction += "- Refer to conditioning images using numbered labels (e.g., image 1, image 2, etc.)\n"
        instruction += "- Consider the content of the provided image(s) to clarify or enhance the description\n"

    if is_editing:
        instruction += "- Clearly specify which image is the source image for editing.\n"

    instruction += "- **Do NOT change the original intent or visual outcome described by the prompt**\n\n"
    instruction += "\nReturn only the rewritten prompt."
    logger.info(instruction)
    return instruction


# --- Weak Prompt Checker ---
def flag_weak_prompt(prompt):
    generic_phrases = ["make it better", "something cool", "nice image"]
    return len(prompt.strip().split()) < 4 or any(p in prompt.lower() for p in generic_phrases)

# --- Image Loader ---
def load_image(path):
    try:
        return client.files.upload(file=path)
    except Exception as e:
        logger.info(f"⚠️ Failed to load image {path}: {e}")
        return None

# --- Gemini Call ---
def clarify_prompt(task, topic, prompt, image_paths,json_path):
    instruction = build_instruction(task, topic, prompt, len(image_paths))
    contents = [instruction]

    for path in image_paths:
        img = load_image(path)
        if img is not None:
            contents.append(img)

    try:
        logger.info(f"model: {model}" )
        response = client.models.generate_content(
            model=model,
            contents=contents,
        )
        return response.text.strip()
        
    except Exception as e:
        logger.info(f"❌ Gemini API error: {e} {json_path}")
        return ""

# --- Process Single JSON ---
def process_json_file(json_path, output_path=None):
    with open(json_path, 'r') as f:
        data = json.load(f)

    if "prompt_refined" in data and data["prompt_refined"].strip():
        logger.info(f"⏭️ Already processed {json_path}. Skipping.")
        return
    
    task = data.get("task", "")
    topic = data.get("topic", "")
    prompt = data.get("prompt", "").strip()
    cond_images = data.get("cond_images", [])
    image_dir = os.path.dirname(json_path)
    image_paths = [os.path.join(image_dir, img) for img in cond_images]

    if not prompt:
        logger.info(f"⚠️ No prompt in {json_path}. Skipping.")
        return

    if flag_weak_prompt(prompt):
        logger.info(f"🔍 Weak prompt in {json_path}: '{prompt}'")

    refined = clarify_prompt(task, topic, prompt, image_paths,json_path)
    data["prompt_refined"] = refined

    output_path = output_path or json_path
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"✅ Saved refined prompt to {output_path}")
    logger.info(f"Modified: { refined}")
    time.sleep(10)

# --- Batch Process Folder ---
def batch_process(folder_path):
    logger.info(f"Start processing {folder_path}")
    for root, dirs, files in sorted(os.walk(folder_path), key=lambda x: x[0]):
        for file in sorted(files):
            if file.endswith("metadata.json"):
                process_json_file(os.path.join(root, file))

# --- Example usage ---
if __name__ == "__main__":
    root = 'YOUR-DATA-ROOT'
    tasks = ['TIE','TIG','SRIG','SRIE','MRIG','MRIE']
    for task in tasks:
        logger.info(f'processing {task}')
        batch_process(f'{root}/{task}')
    #batch_process("/home/samin/ImagenHub2_data/ishengfang")
