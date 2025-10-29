#!/bin/bash

# ===== API KEYS - SET YOUR KEYS HERE =====
OPENAI_API_KEY="your_openai_api_key_here"
GEMINI_API_KEY=AIzaSyCzGwTpnkJJ_P7TsHabQKJhX5jJ_wORzA0
# =========================================

# Base paths
BASE_PATH="/home/samin/ImagenWorld-data/ImagenWorld"
SCRIPT_PATH="main.py"

# Define tasks and their models
declare -A TASK_MODELS
TASK_MODELS[TIG]="Gemini2Flash"
TASK_MODELS[TIE]="Gemini2Flash"
TASK_MODELS[SRIG]="Gemini2Flash"
TASK_MODELS[SRIE]="Gemini2Flash"
TASK_MODELS[MRIG]="Gemini2Flash"
TASK_MODELS[MRIE]="Gemini2Flash"

# Function to run inference
run_inference() {
    local task=$1
    local model=$2
    local task_path="${BASE_PATH}/${task}"
    
    echo "=========================================="
    echo "Testing: ${task} with ${model}"
    echo "=========================================="
    
    # Set API key argument based on model
    local api_key_arg=""
    if [[ "$model" == "GPT-Image-1" ]]; then
        if [[ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]]; then
            echo "❌ Please set your OpenAI API key in the script"
            return 1
        fi
        api_key_arg="--api_key ${OPENAI_API_KEY}"
    elif [[ "$model" == "Gemini2Flash" ]]; then
        if [[ "$GEMINI_API_KEY" == "your_gemini_api_key_here" ]]; then
            echo "❌ Please set your Gemini API key in the script"
            return 1
        fi
        api_key_arg="--api_key ${GEMINI_API_KEY}"
    fi
    
    python "${SCRIPT_PATH}" \
        --task "${task}" \
        --model "${model}" \
        --task_path "${task_path}" \
        --limit 1 \
        --verbose \
        ${api_key_arg}
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ SUCCESS: ${task} with ${model}"
    else
        echo "❌ FAILED: ${task} with ${model} (exit code: ${exit_code})"
    fi
    echo ""
}

# Main execution
echo "Starting comprehensive closed-source model testing..."
echo "Base path: ${BASE_PATH}"
echo "Script path: ${SCRIPT_PATH}"
echo "Limit: 1 sample per task"
echo ""

# Check if API keys are set
if [[ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]]; then
    echo "⚠️  Warning: OpenAI API key not set in script"
fi
if [[ "$GEMINI_API_KEY" == "your_gemini_api_key_here" ]]; then
    echo "⚠️  Warning: Gemini API key not set in script"
fi
echo ""

# Track results
total_tests=0
successful_tests=0
failed_tests=0

# Loop through all tasks and their models
for task in "${!TASK_MODELS[@]}"; do
    echo "Processing task: ${task}"
    
    # Check if task directory exists
    task_path="${BASE_PATH}/${task}"
    if [ ! -d "${task_path}" ]; then
        echo "⚠️  Warning: Task directory does not exist: ${task_path}"
        echo ""
        continue
    fi
    
    # Get models for this task
    models=(${TASK_MODELS[$task]})
    
    for model in "${models[@]}"; do
        total_tests=$((total_tests + 1))
        run_inference "${task}" "${model}"
        
        if [ $? -eq 0 ]; then
            successful_tests=$((successful_tests + 1))
        else
            failed_tests=$((failed_tests + 1))
        fi
    done
done

# Print final summary
echo "=========================================="
echo "FINAL SUMMARY"
echo "=========================================="
echo "Total tests: ${total_tests}"
echo "Successful: ${successful_tests}"
echo "Failed: ${failed_tests}"
if [ $total_tests -gt 0 ]; then
    echo "Success rate: $(( (successful_tests * 100) / total_tests ))%"
else
    echo "Success rate: N/A (no tests run)"
fi
echo "=========================================="

# Exit with error code if any tests failed
if [ $failed_tests -gt 0 ]; then
    exit 1
else
    exit 0
fi