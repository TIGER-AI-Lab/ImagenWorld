import argparse
import os
import imagen_hub
from config import MODEL_MAPPING
from utils import validate_model_for_task
from processor import ImageProcessor


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ImagenHub inference script for image generation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py --task TIG --model UNO --task_path /path/to/ImagenHub2_data/TIG
        python main.py --task TIE --model BagelEdit --task_path /path/to/ImagenHub2_data/TIE
        python main.py --task MRIE --model OmniGen2 --task_path /path/to/ImagenHub2_data/MRIE
                """
    )
    
    parser.add_argument(
        "--task", 
        required=True, 
        choices=["TIG", "TIE", "SRIG", "SRIE", "MRIG", "MRIE"],
        help="Task type (TIG, TIE, SRIG, SRIE, MRIG, MRIE)"
    )
    parser.add_argument(
        "--model", 
        required=True, 
        help="Model name to use for inference"
    )
    parser.add_argument(
        "--task_path", 
        required=True,
        help="Direct path to the task directory containing sample folders"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of folders to process within the task; if unset, process all."
    )
    
    return parser.parse_args()


def load_model(model_name: str):
    """Load the specified model."""
    try:
        model = imagen_hub.load(model_name)
        print(f"✅ Loaded model: {model_name}")
        return model
    except Exception as e:
        print(f"❌ Failed to load model {model_name}: {e}")
        raise


def main():
    """Main function."""
    args = parse_arguments()
    
    # Validate model for task
    if not validate_model_for_task(args.model, args.task):
        print(f"⚠️ Warning: {args.model} is not in the recommended models for {args.task}")
        print(f"Recommended models for {args.task}: {MODEL_MAPPING.get(args.task, [])}")
        
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Load the model
    model = load_model(args.model)
    
    # Initialize processor
    processor = ImageProcessor(model)
    
    # Validate task path exists
    if not os.path.exists(args.task_path):
        print(f"❌ Task path does not exist: {args.task_path}")
        return
    
    print(f"🚀 Processing {args.task} with {args.model} from {args.task_path}")
    
    # Process samples with optional limit
    stats = processor.process_all(args.task_path, args.model, limit=args.limit)
    
    # Print summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Task: {args.task}")
    print(f"Model: {args.model}")
    print(f"Processed: {stats['processed']}")
    print(f"Errors: {stats['errors']}")
    print("="*50)


if __name__ == "__main__":
    main()