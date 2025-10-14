import os
import sys
import json
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types
import time

# ==== CONFIGURATION ====
ROOT_DIR = "."  # or your absolute path
JSON_NAME = "metadata.json"
OUTPUT_NAME = "gemini.png"

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
        "The new image should reflect visual elements from the references and follow the prompt’s description."
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

def initialize_client(api_key):
    if not api_key:
        raise RuntimeError("❌ GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)

def load_metadata(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {json_path}: {e}")
        return None

def load_images(image_names, folder_path,client):
    images = []
    for img_name in image_names:
        img_path = os.path.join(folder_path, img_name)
        if os.path.exists(img_path):
            try:
                images.append(client.files.upload(file=img_path))
            except Exception as e:
                print(f"❌ Failed to load image {img_path}: {e}")
    return images

def build_prompt(task_name, topic, user_prompt):
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

def process_entry(entry_path, metadata, client, model, task_name):
    topic = metadata.get("topic", "General")
    user_prompt = metadata.get("prompt_refined", "")
    cond_images = metadata.get("cond_images", [])
    final_prompt = build_prompt(task_name, topic, user_prompt)
    image_inputs = load_images(cond_images, entry_path,client)
    print(final_prompt)
    try:
        if image_inputs:
            contents = [final_prompt] +  image_inputs
        else:
            contents = [final_prompt] 
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                image.save(os.path.join(entry_path, OUTPUT_NAME))
                print(f"✅ Saved: {entry_path}/{OUTPUT_NAME}")
                return

    except Exception as e:
        print(f"🚫 Error in {entry_path}: {e}")


def process_single_example(input_path, client, model):
    task_name = None
    for tid, name in ID_TO_TASK.items():
        if tid in input_path:
            task_name = name
            break
    if not task_name:
        print(f"❌ Could not infer task name from path: {input_path}")
        return

    json_path = os.path.join(input_path, JSON_NAME)
    metadata = load_metadata(json_path)
    if metadata:
        process_entry(input_path, metadata, client, model, task_name)
        time.sleep(5)


def process_all(root_dir, client, model):
    for entry in os.listdir(root_dir):
        entry_path = os.path.join(root_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if os.path.exists(os.path.join(entry_path, JSON_NAME)):
            process_single_example(entry_path, client, model)

def main():
    key = "YOUR-GEMINI-KEY"
    client = initialize_client(key)
    model = "gemini-2.5-flash-image-preview"

    root = '.'
    tasks = ['TIE','TIG','SRIG','SRIE','MRIG','MRIE']
    for task in tasks:
        print(f'processing {task}')
        #process_all(f"{root}/{task}", client, model)
        process_single_example(f"{root}/{task}/{task}_A_000001")

if __name__ == "__main__":
    main()



