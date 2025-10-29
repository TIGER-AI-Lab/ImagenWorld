export CUDA_VISIBLE_DEVICES=7

#!/bin/bash

# Base paths
BASE_PATH="/home/samin/ImagenWorld-data/ImagenWorld"
SCRIPT_PATH="main.py"

# Define tasks and their models
declare -A TASK_MODELS
TASK_MODELS[TIG]="SDXL Infinity JanusPro UNO BagelGeneration OmniGen2 FLUX1Kreadev QwenImage"
TASK_MODELS[TIE]="InstructPix2Pix BagelEdit Step1XEdit ICEdit OmniGen2 FLUX1Kontextdev"
TASK_MODELS[SRIG]="OmniGen2 BagelGeneration UNO"
TASK_MODELS[SRIE]="OmniGen2 BagelEdit"
TASK_MODELS[MRIG]="OmniGen2 BagelGeneration UNO"
TASK_MODELS[MRIE]="OmniGen2 BagelEdit"

# Function to run inference
run_inference() {
    local task=$1
    local model=$2
    local task_path="${BASE_PATH}/${task}"
    
    echo "=========================================="
    echo "Testing: ${task} with ${model}"
    echo "=========================================="
    
    python "${SCRIPT_PATH}" \
        --task "${task}" \
        --model "${model}" \
        --task_path "${task_path}" \
        --limit 1 \
        --verbose
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ SUCCESS: ${task} with ${model}"
    else
        echo "❌ FAILED: ${task} with ${model} (exit code: ${exit_code})"
    fi
    echo ""
}

# Main execution
echo "Starting comprehensive model testing..."
echo "Base path: ${BASE_PATH}"
echo "Script path: ${SCRIPT_PATH}"
echo "Limit: 1 sample per task"
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
echo "Success rate: $(( (successful_tests * 100) / total_tests ))%"
echo "=========================================="

# Exit with error code if any tests failed
if [ $failed_tests -gt 0 ]; then
    exit 1
else
    exit 0
fi