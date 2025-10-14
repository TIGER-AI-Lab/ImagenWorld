import imagen_hub
from imagen_hub.utils import save_pil_image
import logging
import os
from PIL import Image
import json

# ==== CONFIGURATION ====
#ROOT_DIR = "."  # or your absolute path
IMAGE_NAME = "ultraedit.png"
JSON_NAME = "metadata.json"
MODEL = "UltraEdit"

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

def load_metadata(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {json_path}: {e}")
        return None

def load_images(image_names, folder_path):
    images = []
    for img_name in image_names:
        img_path = os.path.join(folder_path, img_name)
        if os.path.exists(img_path):
            try:
                images.append(Image.open(img_path).convert("RGB"))
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

def process_entry(entry_path, metadata, task_name,prep=False):
    topic = metadata.get("topic", "General")
    user_prompt = metadata.get("prompt_refined", "")
    cond_images = metadata.get("cond_images", [])
    if(prep):
        final_prompt = build_prompt(task_name, topic, user_prompt)
    else:
        final_prompt = user_prompt
    image_inputs = load_images(cond_images, entry_path)
    print(final_prompt)
    out_dir = os.path.join(entry_path,"model_output")
    os.makedirs(out_dir, exist_ok=True)
    try:
        if image_inputs:
            l = len(image_inputs)
            print(f"multiple {l}")
            if(len(image_inputs) == 1 ):
                image = model.infer_one_image(instruct_prompt=final_prompt,src_image = image_inputs[0])
            elif(MODEL == "OmniGen2"):
                print("here")
                image = model.infer_one_image(prompt=final_prompt,input_images = image_inputs,text_guidance_scale=5.0,image_guidance_scale=2.8,max_sequence_length=4096)
            elif(MODEL == 'BagelGenration'):
               image == model.infer_one_image(prompt=final_prompt,cfg_text_scale=4,cfg_img_scale=1.3)
            else:
                print("uno")
                image = model.infer_one_image(prompt=final_prompt,input_images = image_inputs)
        else:
            if(MODEL == "OmniGen2"):
                image = model.infer_one_image(prompt=final_prompt,text_guidance_scale=4.0,image_guidance_scale=1.0,max_sequence_length=4096)
            else:
                image = model.infer_one_image(prompt=final_prompt)
        save_pil_image(image, out_dir, IMAGE_NAME)
        print(f"Processed: {out_dir}/{IMAGE_NAME}")
    except Exception as e:
        print(f"🚫 Error in {entry_path}: {e}")


def process_single_example(input_path):
    out_path = os.path.join(input_path, "model_output",IMAGE_NAME)
    if os.path.exists(out_path):
        print(f"⏭️ Already processed {out_path}. Skipping.")
        return
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
        process_entry(input_path, metadata, task_name)


def process_all(root_dir):
    #i = 0
    for entry in sorted(os.listdir(root_dir)):
        '''if(i>5):
            break'''
        entry_path = os.path.join(root_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        process_single_example(entry_path)
        #i+=1


def main():
    global model
    
    model = imagen_hub.load(MODEL)
    root = 'YOUR-DATA-ROOT'
    tasks = ['TIE','TIG','SRIG','SRIE','MRIG','MRIE']
    tasks = ["TIE"]
    #process_single_example("/data/samin/ImagenHub2_data/TIE/TIE_A_000001")
    for task in tasks:
        print(f'processing {task}')
        process_all(f"{root}/{task}")
    '''for entry in sorted(os.listdir(root)):
        path = os.path.join(root,entry,"model_output")
        process_single_example(path)'''
        

if __name__ == "__main__":
    main()
