import json
import os
from io import BytesIO
from PIL import Image
from google import genai
import time
import logging
import re


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
        logger.warning("Oops: Task definition not found.")
    has_images = image_count > 0
    # Build instruction
    instruction = (
        f"You are given a task for image generation or editing.\n\n"
        f"**Task Type:** {id_to_task[task]}\n"
        f"**Definition:** {definition}\n"
        f"**Topic:** {id_to_topic[topic]}\n"
        f"**Original Prompt:** \"{original_prompt}\"\n"
        f"**Conditioning Images:** {image_count}\n\n"
        f"**Your Goal:**\n"
        f"List the **objects, elements, or visual components that must appear in the final output image.**\n\n"
        f"**Guidelines:**\n"
        f"- **Do not** explain how the image is generated or edited.\n"
        f"- **Do not** describe editing steps or transformations.\n"
        f"- **Only output the final visual content.**\n"
        f"- **List at most 10 items**. If more objects could be extracted, include only the 10 most important or visually dominant ones."
        f"- If spatial or positional details are specified (e.g., 'on the left', 'in front of'), retain them in the list.\n"
        f"- **If the prompt says to remove or delete something, list that object as well and write: (should not be present).**\n\n"
    )

    if has_images:
        instruction += "- Consider the content of the provided images or reference images if relevant.\n"

    # Explicit output format instruction without brackets
    instruction += (
        "\n**Output Format:**\n"
        "Return the list exactly like this:\n\n"
        "- red sports car\n"
        "- highway\n"
        "- sunset sky\n\n"
        "**Do not include any explanations, extra text, or headings. Only the bullet list.**\n"
    )

    logger.info(instruction)
    return instruction

def parse_bullet_list(model_output):
    """
    Robustly parses a model's output into a list of objects.

    Supports:
    - "- Object"
    - "• Object"
    - "* Object"
    - "1. Object", "2) Object"
    """
    objects = []
    for line in model_output.strip().split('\n'):
        line = line.strip()
        # Match bullets: -, •, *, or numbers like 1. / 1)
        if re.match(r'^(-|\*|•|\d+[.)])\s+', line):
            # Remove bullet/number prefix
            obj = re.sub(r'^(-|\*|•|\d+[.)])\s+', '', line)
            if obj:
                objects.append(obj)
    return objects
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
def find_objects(task, topic, prompt, image_paths,json_path):
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

    if "objects" in data and data["objects"]:
        logger.info(f"⏭️ Already processed {json_path}. Skipping.")
        return
    
    task = data.get("task", "")
    topic = data.get("topic", "")
    prompt = data.get("prompt_refined", "").strip()
    if not prompt:
        prompt = data.get("prompt", "").strip()
    cond_images = data.get("cond_images", [])
    image_dir = os.path.dirname(json_path)
    image_paths = [os.path.join(image_dir, img) for img in cond_images]

    if not prompt:
        logger.info(f"⚠️ No prompt in {json_path}. Skipping.")
        return

    model_output = find_objects(task, topic, prompt, image_paths,json_path)
    objects = parse_bullet_list(model_output)
    data["objects"] = objects

    output_path = output_path or json_path
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"output: {model_output}")
    logger.info(f"✅ Saved objects to {output_path}")
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
