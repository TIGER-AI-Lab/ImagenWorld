import os
import sys
import json
from io import BytesIO
from PIL import Image
from openai import OpenAI
import base64

# ==== CONFIGURATION ====
ROOT_DIR = "."  # or your absolute path
JSON_NAME = "metadata.json"
OUTPUT_NAME = "gpt-image-1.png"

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
    return OpenAI(api_key=api_key)

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
                images.append(open(img_path,"rb"))
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
            result = client.images.edit(
                model=model,
                image=image_inputs,
                prompt=final_prompt,
                quality="medium"
            )
        else:
            result = client.images.generate(
                model=model,
                prompt=final_prompt,
                quality="medium"
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(os.path.join(entry_path, OUTPUT_NAME), "wb") as f:
            f.write(image_bytes)
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

def process_all(root_dir, client, model):
    for entry in sorted(os.listdir(root_dir)):
        entry_path = os.path.join(root_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if os.path.exists(os.path.join(entry_path, JSON_NAME)):
            image_path = os.path.join(entry_path, OUTPUT_NAME)
            if os.path.exists(image_path):
                print(f"⏭️ Already processed {image_path}. Skipping.")
            else:
                process_single_example(entry_path, client, model)


def main():
    key = "YOUR-GPT-KEY"
    client = initialize_client(key)
    model = "gpt-image-1"
    root = 'YOUR-DATA-ROOT'
    tasks = ['TIE','TIG','SRIG','SRIE','MRIG','MRIE']
    for task in tasks:
        print(f'processing {task}')
        process_all(f"{root}/{task}", client, model)
        #process_single_example(f"{root}/{task}/{task}_A_000001",client,model)

if __name__ == "__main__":
    main()