import json
import os
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
if not API_KEY:
    logger.warning("No GOOGLE_API_KEY in environment; using the hardcoded key fallback (not recommended).")

# You can keep the preview model; if it misbehaves, try the stable alias "gemini-2.5-flash"
MODEL_NAME = "gemini-2.5-flash-preview-05-20"

EVALUATION_INSTRUCTION = """
You are an expert AI image evaluator. Your task is to rate a generated image based on a provided text prompt and any reference images.

Use the following guidelines for your assessment. Provide a rating from 1 to 5 for each criterion. Do NOT include any additional text or explanations in your response. The response MUST be a single JSON object.

# Quality Assessment

## 🌟 Prompt Relevance
Definition: Whether the image accurately reflects or responds to the prompt.
Rating Guide (1–5):
1 – Completely unrelated to the prompt.
2 – Mostly incorrect; some vague connections but many mismatches.
3 – Partially relevant; key ideas are present but with errors or omissions.
4 – Mostly accurate; follows the prompt well with minor issues.
5 – Fully aligned with the prompt; clear, focused, and complete.

## 🎨 Aesthetic Quality / Visual Appeal
Definition: Whether the image is visually appealing, clean, and easy to interpret.
Rating Guide (1–5):
1 – Visually poor; unattractive, hard to read or confusing.
2 – Below average; noticeable design flaws, poor readability.
3 – Decent; generally readable but has minor layout/design issues.
4 – Clean and aesthetically good; professional feel with few flaws.
5 – Beautiful, polished, and visually excellent.

## 🔄 Content Coherence
Definition: Whether the content in the image is logically consistent and fits together meaningfully.
Rating Guide (1–5):
1 – Internally inconsistent or nonsensical; parts contradict each other.
2 – Some logic, but confusing or mismatched components.
3 – Mostly coherent, though there are noticeable mismatches or awkward parts.
4 – Logically sound overall, with only minor inconsistencies.
5 – Completely coherent and internally consistent.

## 🧩 Artifacts / Visual Errors
Definition: Whether the image has visual flaws due to generation errors (e.g., distortions, glitches).
Rating Guide (1–5):
1 – Severe artifacts that ruin the image.
2 – Major flaws that are clearly noticeable.
3 – Some minor artifacts, but the image remains usable.
4 – Mostly clean; only very subtle flaws if any.
5 – Perfectly clean; no visible artifacts at all.

Output ONLY a single JSON object with keys:
{
  "prompt_relevance": <rating>,
  "aesthetic_quality": <rating>,
  "content_coherence": <rating>,
  "artifacts": <rating>
}
"""

def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """Extract the first JSON object from text (handles code fences & extra text)."""
    if not text:
        return None
    # Strip common code fences
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    # Greedy match the first {...} block
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None

def extract_text_from_response(resp) -> str:
    """Be resilient: prefer resp.text; fall back to concatenating parts."""
    # Fast path
    try:
        if getattr(resp, "text", None):
            return resp.text
    except Exception:
        pass
    # Fallback: join all text parts from first candidate
    try:
        if resp and resp.candidates:
            parts = resp.candidates[0].content.parts or []
            collected = []
            for p in parts:
                # p may have 'text' or 'inline_data' etc.; we only want text here
                t = getattr(p, "text", None)
                if t:
                    collected.append(t)
            return "\n".join(collected).strip()
    except Exception:
        return ""
    return ""

def upload_file(client,path: str):
    try:
        return client.files.upload(file=path)
    except Exception as e:
        logger.error(f"⚠️ Failed to upload file {path}: {e}")
        return None

def evaluate_generated_image(client, generated_image_path: str, prompt: str, cond_image_paths: List[str]) -> Optional[Dict[str, Any]]:
    """Call Gemini, force JSON output, and robustly parse the response."""
    gen_file = upload_file(client,generated_image_path)
    print(prompt)
    if not gen_file:
        return None

    cond_files = []
    for p in cond_image_paths:
        if os.path.exists(p):
            f = upload_file(client,p)
            if f:
                cond_files.append(f)

    # Build multimodal contents: files + text together
    contents = []
    contents.append(EVALUATION_INSTRUCTION)
    contents.append(f"Prompt: {prompt}")
    if cond_files:
        contents.append(f"Reference images:")
        contents.extend(cond_files)
    
    contents.append("Output Image to be Evaluated:")
    contents.append(gen_file)
    
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config={
                # Force strict JSON so json.loads won’t fail.
                "response_mime_type": "application/json",
                "temperature": 0.0,
            },
        )

        raw = extract_text_from_response(resp)
        data = parse_json_safely(raw)

        # If still None, log diagnostics for finish/blocked reasons
        if data is None:
            try:
                fr = getattr(resp.candidates[0], "finish_reason", None)
                bs = getattr(resp, "usage_metadata", None)
                logger.error(f"Model did not return valid JSON. finish_reason={fr}, usage={bs}, raw='{raw[:300]}'")
            except Exception:
                logger.error(f"Model did not return valid JSON. raw='{raw[:300]}'")
            return None

        # Basic schema check
        expected_keys = {"prompt_relevance", "aesthetic_quality", "content_coherence", "artifacts"}
        if not expected_keys.issubset(set(data.keys())):
            logger.error(f"JSON missing expected keys: got {list(data.keys())}")
            return None

        return data

    except Exception as e:
        logger.error(f"❌ Gemini API error during evaluation of {generated_image_path}: {e}")
        return None

def process_single_example(entry_path: str):
    results_data = {"gemini": {}}
    result_path = os.path.join(entry_path, "gemini_result.json")
    if os.path.exists(result_path):
        try:
            with open(result_path, "r") as f:
                results_data = json.load(f)
        except Exception:
            logger.warning("gemini_result.json exists but is unreadable; starting fresh.")

    json_path = os.path.join(entry_path, "metadata.json")
    with open(json_path, "r") as f:
        data = json.load(f)

    prompt_to_evaluate = data.get("prompt_refined") or data.get("prompt", "")
    task = data.get("task", "")
    cond_images = data.get("cond_images", [])
    cond_image_paths = [os.path.join(entry_path, img) for img in cond_images]

    model_output_dir = os.path.join(entry_path, "model_output")
    if not os.path.isdir(model_output_dir):
        logger.info(f"No model_output folder in {entry_path}")
        return

    for model_file in sorted(os.listdir(model_output_dir)):
        if not model_file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        model_key = os.path.splitext(model_file)[0]
        if model_key in results_data["gemini"] or ((model_key=='uno') and ("IE" in task)):
            logger.info(f"✨ already calculated scores for {model_key} in '{entry_path}'")
            continue

        image_path = os.path.join(model_output_dir, model_file)
        logger.info(f"✨ Evaluating {model_key} for task '{task}' and dir={entry_path} with prompt: '{prompt_to_evaluate}'")
        scores = evaluate_generated_image(client,image_path, prompt_to_evaluate, cond_image_paths)
        if scores:
            results_data["gemini"][model_key] = scores
            with open(result_path, "w") as f:
                json.dump(results_data, f, indent=2)
            logger.info(f"✅ Saved scores for {model_key}: {scores}")
        else:
            logger.error(f"❌ Failed to obtain scores for {model_key}")

def process_all(root_dir: str):
    for entry in sorted(os.listdir(root_dir)):
        entry_path = os.path.join(root_dir, entry)
        if os.path.isdir(entry_path):
            process_single_example(entry_path)

def main():
    root = "YOUR-DATA-ROOT"
    logger.info("start processing...")
    #process_single_example("/home/samin/ImagenHub2_data/TIG/TIG_A_000001")
    # Uncomment to run full sweep:4
    tasks = ["TIG","TIE","SRIG","SRIE","MRIG","MRIE"]
    for task in tasks:
        logger.info(f"processing {task}")
        process_all(os.path.join(root, task))

if __name__ == "__main__":
    API_KEY = API_KEY 

    client = genai.Client(api_key=API_KEY)
    main()
