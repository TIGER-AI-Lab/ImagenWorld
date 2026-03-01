# 🖼️ ImagenWorld 
ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks

[ICLR Paper](https://openreview.net/forum?id=bld9g6jFh9)


<p align="center">
<img src="https://github.com/TIGER-AI-Lab/ImagenWorld/blob/gh-pages/static/images/psudo_banner.png" width="40%">
</p>


**ImagenWorld** is a large-scale, human-centric benchmark designed to stress-test image generation models in real-world scenarios.  
- **Broad coverage across 6 domains:** Artworks, Photorealistic Images, Information Graphics, Textual Graphics, Computer Graphics, and Screenshots.
- **Rich supervision:** ~3.6K condition sets and ~20K fine-grained human annotations enable comprehensive, reproducible evaluation.
- **Explainable evaluation pipeline:** We decompose generated outputs via object/segment extraction to identify entities (objects, fine-grained regions), supporting both scalar ratings and object-/segment-level failure tags.
- **Diverse model suite:** We evaluate **14 models** in total — **4 unified** (GPT-Image-1, Gemini 2.0 Flash, BAGEL, OmniGen2) and **10 task-specific** baselines (SDXL, Flux.1-Krea-dev, Flux.1-Kontext-dev, Qwen-Image, Infinity, Janus Pro, UNO, Step1X-Edit, IC-Edit, InstructPix2Pix).

<div align="center">
 <a href = "https://tiger-ai-lab.github.io/ImagenWorld/">[🌐 Project Page]</a> <a href = "https://github.com/TIGER-AI-Lab/ImagenWorld/blob/gh-pages/static/preprint.pdf">[📄 Preprint]</a> <a href = "https://huggingface.co/datasets/TIGER-Lab/ImagenWorld-condition-set">[💾 Datasets]</a> <a href = "https://huggingface.co/spaces/TIGER-Lab/ImagenWorld-Visualizer">[🏛️ ImagenWorld-Visualizer]</a>
</div>

## 📰 News
* 2025 Jan 25: Accepted to ICLR 2026!
* 2025 Oct 16: ComfyUI Blog on [https://blog.comfy.org/p/introducing-imagenworld](https://blog.comfy.org/p/introducing-imagenworld)
* 2025 Oct 13: Preprint released on Github.

## 📖 Introduction

This repository contains the code for the paper [ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks]().
In this paper, We introduce **ImagenWorld**, a large-scale, human-centric benchmark designed to stress-test image generation models in real-world scenarios. Unlike prior evaluations that focus on isolated tasks or narrow domains, ImagenWorld is organized into six domains: Artworks, Photorealistic Images, Information Graphics, Textual Graphics, Computer Graphics, and Screenshots, and six tasks: Text-to-Image Generation (TIG), Single-Reference Image Generation (SRIG), Multi-Reference Image Generation (MRIG), Text-to-Image Editing (TIE), Single-Reference Image Editing (SRIE), and Multi-Reference Image Editing (MRIE). The benchmark includes 3.6K condition sets and 20K fine-grained human annotations, providing a comprehensive testbed for generative models. To support explainable evaluation, ImagenWorld applies object- and segment-level extraction to generated outputs, identifying entities such as objects and fine-grained regions. This structured decomposition enables human annotators to provide not only scalar ratings but also detailed tags of object-level and segment-level failures.


<p align="center">
  <img src="https://github.com/TIGER-AI-Lab/ImagenWorld/blob/gh-pages/static/images/overview.PNG" alt="Teaser" width="70%"/>
</p>

## 🚀 Quick Start — Inference

**Tasks:** `TIG` (Text→Image Generation), `TIE` (Text→Image Editing), `SRIG`, `SRIE`, `MRIG`, `MRIE`  
**Datasets:** assumes `ImagenWorld/<TASK>/...` layout (adjust `--task_path` as needed)

---

### Open-Source Models

**Directory:** `inference/open-source/`  
**Entrypoint:** `main.py`  
**Model registry:** `inference/open-source/config.py`  
**Batch helper:** `open_models.sh`  

All open-source and close-source runners follow a unified CLI:
```bash
python main.py   --task <TASK>   --model <MODEL>   --task_path <DATASET_PATH>   --limit <N> --verbose
```

#### 🔹 Example: TIG (Text→Image Generation) with UNO
```bash
cd inference/open-source

python main.py   --task TIG   --model UNO   --task_path /path/to/ImagenWorld/TIG   --limit 5 --verbose
```

**Explanation**
- Loads the **UNO** open-source generator from the registry (`config.py`)  
- Runs the **TIG** (Text→Image Generation) task using samples from `/path/to/ImagenWorld/TIG`  
- Saves results to `model_outputs/model_name.png` 
- Prints per-sample logs if `--verbose` is enabled  

---

### Closed-Source Models

**Directory:** `inference/closed-source/`  
**Entrypoint:** `main.py`  
**Model registry:** `inference/closed-source/config.py`  
**Batch helper:** `closed_models.sh`  

Available closed-source APIs and outputs:
- `GPT-Image-1` → saves `gpt-image-1.png`  
- `Gemini2Flash` → saves `gemini.png`

#### 🔧 Setup Environment
Set your API keys before running:
```bash
export OPENAI_API_KEY="sk-..."     # for GPT-Image-1
export GEMINI_API_KEY="..."        # for Gemini 2.5 Flash Image Preview
```

#### 🔹 Example: TIE (Text→Image Editing) with Gemini 2.5 Flash
```bash
cd inference/closed-source

python main.py   --task TIE   --model Gemini2Flash   --task_path /path/to/ImagenWorld/TIE   --limit 5 --verbose
```

**Explanation**
- Loads the selected **closed-source API model** (via OpenAI or Gemini)  
- Runs the specified task on samples from `/path/to/ImagenWorld/<TASK>`  
- Stores generated images (e.g., `gpt-image-1.png`, `gemini.png`)  

---

### Batch Execution (Optional)

Each inference type includes a shell helper for multi-task runs:

```bash
# open-source batch
cd inference/open-source
bash open_models.sh

# closed-source batch
cd inference/closed-source
bash closed_models.sh
```

In both scripts:
- Set `BASE_PATH` → dataset root (e.g., `/path/to/ImagenWorld`)  
- Define `TASK_MODELS` to map each task to a model  
- Set API keys for closed-source models 

## Citation

If you find our work useful for your research, please consider citing our paper:

```bibtex
@inproceedings{
sani2026imagenworld,
title={ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks},
author={Samin Mahdizadeh Sani and Max Ku and Nima Jamali and Matina Mahdizadeh Sani and Paria Khoshtab and Wei-Chieh Sun and Parnian Fazel and Zhi Rui Tam and Thomas Chong and Edisy Kin Wai Chan and Donald Wai Tong Tsang and Chiao-Wei Hsu and Lam Ting Wai and Ho Yin Sam Ng and Chiafeng Chu and Chak-Wing Mak and Keming Wu and Hiu Tung Wong and Yik Chun Ho and Chi Ruan and Zhuofeng Li and I-Sheng Fang and Shih-Ying Yeh and Ho Kei Cheng and Ping Nie and Wenhu Chen},
booktitle={The Fourteenth International Conference on Learning Representations},
year={2026},
url={https://openreview.net/forum?id=bld9g6jFh9}
}
```

<!--
```bibtex
@misc{imagenworld2025,
  title        = {ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks},
  author       = {Samin Mahdizadeh Sani and Max Ku and Nima Jamali and Matina Mahdizadeh Sani and Paria Khoshtab and Wei-Chieh Sun and Parnian Fazel and Zhi Rui Tam and Thomas Chong and Edisy Kin Wai Chan and Donald Wai Tong Tsang and Chiao-Wei Hsu and Ting Wai Lam and Ho Yin Sam Ng and Chiafeng Chu and Chak-Wing Mak and Keming Wu and Hiu Tung Wong and Yik Chun Ho and Chi Ruan and Zhuofeng Li and I-Sheng Fang and Shih-Ying Yeh and Ho Kei Cheng and Ping Nie and Wenhu Chen},
  year         = {2025},
  doi          = {10.5281/zenodo.17344183},
  url          = {https://zenodo.org/records/17344183},
  projectpage  = {https://tiger-ai-lab.github.io/ImagenWorld/},
  blogpost     = {https://blog.comfy.org/p/introducing-imagenworld},
  note         = {Community-driven dataset and benchmark release, Temporarily archived on Zenodo while arXiv submission is under moderation review.},
}
```

```bibtex
 @article{imagenworld2026,
title={ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks},
url={http://dx.doi.org/10.36227/techrxiv.176800878.82723313/v1},
DOI={10.36227/techrxiv.176800878.82723313/v1},
publisher={Institute of Electrical and Electronics Engineers (IEEE)},
author={Sani, Samin Mahdizadeh and Ku, Max and Jamali, Nima and Sani, Matina Mahdizadeh and Khoshtab, Paria and Sun, Wei-Chieh and Fazel, Parnian and Tam, Zhi Rui and Chong, Thomas and Chan, Edisy Kin Wai and Tsang, Donald Wai Tong and Hsu, Chiao-Wei and Lam, Ting Wai and Ng, Ho Yin Sam and Chu, Chiafeng and Mak, Chak-Wing and Wu, Keming and Wong, Hiu Tung and Ho, Yik Chun and Ruan, Chi and Li, Zhuofeng and Fang, I-Sheng and Yeh, Shih-Ying and Cheng, Ho Kei and Nie, Ping and Chen, Wenhu},
year={2026},
month=jan }
```
-->

