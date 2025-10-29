"""
Main entry point for closed-source inference pipeline.
"""

import argparse
import os
from config import MODEL_CONFIG
from utils import validate_model_for_task, get_api_key, infer_task_from_path
from openai_handler import OpenAIHandler
from google_handler import GoogleHandler


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Closed-source inference script for image generation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py --task TIG --model GPT-Image-1 --task_path /path/to/TIG --api_key your_key
        python main.py --task TIE --model Gemini2Flash --task_path /path/to/TIE
        python main.py --task MRIE --model GPT-Image-1 --task_path /path/to/MRIE --limit 5
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
        choices=list(MODEL_CONFIG.keys()),
        help="Model name to use for inference"
    )
    parser.add_argument(
        "--task_path", 
        required=True,
        help="Direct path to the task directory containing sample folders"
    )
    parser.add_argument(
        "--api_key",
        help="API key for the model provider (optional if set in environment)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of folders to process within the task; if unset, process all."
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def get_handler(model_name: str, api_key: str):
    """Get the appropriate handler for the model."""
    model_config = MODEL_CONFIG[model_name]
    provider = model_config["provider"]
    
    if provider == "openai":
        return OpenAIHandler(api_key, model_config["model_name"])
    elif provider == "google":
        return GoogleHandler(api_key, model_config["model_name"])
    else:
        raise ValueError(f"Unknown provider: {provider}")


def main():
    """Main function."""
    args = parse_arguments()
    
    # Validate model for task
    if not validate_model_for_task(args.model, args.task):
        print(f"⚠️ Warning: {args.model} is not recommended for {args.task}")
        print(f"Recommended tasks for {args.model}: {MODEL_CONFIG[args.model]['tasks']}")
        
        response = input("Do you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Get API key
    model_config = MODEL_CONFIG[args.model]
    provider = model_config["provider"]
    
    try:
        api_key = get_api_key(provider, args.api_key)
    except (ValueError, RuntimeError) as e:
        print(f"❌ {e}")
        return
    
    # Validate task path exists
    if not os.path.exists(args.task_path):
        print(f"❌ Task path does not exist: {args.task_path}")
        return
    
    # Initialize handler
    handler = get_handler(args.model, api_key)
    output_filename = model_config["output_filename"]
    
    print(f"🚀 Processing {args.task} with {args.model} from {args.task_path}")
    
    # Process samples with optional limit
    stats = handler.process_all(args.task_path, args.task, output_filename, limit=args.limit)
    
    # Print summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Task: {args.task}")
    print(f"Model: {args.model}")
    print(f"Processed: {stats['processed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print("="*50)


if __name__ == "__main__":
    main()