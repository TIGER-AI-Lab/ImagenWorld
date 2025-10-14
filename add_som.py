import imagen_hub
from imagen_hub.utils import save_pil_image
import logging
import os
from PIL import Image
from imagen_hub.SoM import SoM

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(imagen_hub.__version__)


# Task mapping
ID_TO_TASK = {
    "TIG": "Text-guided Image Generation",
    "TIE": "Text-guided Image Editing",
    "SRIG": "Single Reference-guided Image Generation",
    "SRIE": "Single Reference-guided Image Editing",
    "MRIG": "Multiple References-guided Image Generation",
    "MRIE": "Multiple References-guided Image Editing"
}

ID_TO_TOPIC = {
    "I": "Information Graphics",
    "A": "Artworks",
    "S": "Screenshots",
    "CG": "Computer Graphics",
    "P": "Photorealistic Images",
    "T": "Textual Graphics"
}



def process_image(entry_path,filename):
    full_path = os.path.join(entry_path, filename)
    model_name = filename.split(".")[0]
    dest_path = full_path.replace("model_output", "SoM")
    som_dir = os.path.dirname(dest_path)
    som_dir = os.path.join(som_dir, model_name)
    image_path = os.path.join(som_dir, filename)
    if os.path.exists(image_path):
        print(f"⏭️ Already processed {image_path}. Skipping.")
        return
    os.makedirs(som_dir, exist_ok=True)
    try:
        preview, npz_file = som.add_marks(
                                slider=1.8,
                                anno_mode=["Mask", "Mark"], 
                                alpha=0.6 , 
                                image_path=full_path,
                                save_dir=som_dir,
                                method='semantic-sam',
                                text_size=800
                            )
        #result = som.add_marks(image_path=full_path, slider=1.8,method='semantic-sam',text_size=800,alpha=0.6)
        save_pil_image(preview, som_dir, filename)
        logging.info(f"Processed: {full_path} -> {dest_path}")
    except Exception as e:
        logging.warning(f"Failed to process {full_path}: {e}. Saving original instead.")
        # Save original image instead
        #original = Image.open(full_path)
        #save_pil_image(original, som_dir, filename)

def process_single_example(input_path):
    task_name = None
    IMAGE_EXTS = {'jpg', 'jpeg', 'png'}
    for tid, name in ID_TO_TASK.items():
        if tid in input_path:
            task_name = name
            break
    if not task_name:
        print(f"❌ Could not infer task name from path: {input_path}")
        return
    for filename in os.listdir(input_path):
        if(filename.split(".")[1].lower() in IMAGE_EXTS):
            process_image(input_path,filename)


def process_all(root_dir):
    for entry in sorted(os.listdir(root_dir)):
        entry_path = os.path.join(root_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        entry_path = os.path.join(entry_path, "model_output")
        process_single_example(entry_path)

def main():
    global som 
    som = SoM()
    root = 'YOUR-DATA-ROOT'
    tasks = ['TIG','TIE','SRIG','SRIE','MRIG','MRIE']
    #task = "TIG"
    #process_single_example("/home/samin/ImagenHub2_data/TIG/TIG_A_000002/model_output")
    for task in tasks:
        print(f'processing {task}')
        process_all(f"{root}/{task}")

        

if __name__ == "__main__":
    main()
