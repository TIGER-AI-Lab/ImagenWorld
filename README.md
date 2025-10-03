# 🖼️ ImagenWorld 
[![arXiv](https://img.shields.io/badge/arXiv-2310.01596-b31b1b.svg)]()

ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks



<p align="center">
<img src="https://github.com/TIGER-AI-Lab/ImagenWorld/blob/gh-pages/static/images/psudo_banner.png" width="40%">
</p>


**ImagenWorld** is a large-scale, human-centric benchmark designed to stress-test image generation models in real-world scenarios.  
- **Broad coverage across 6 domains:** Artworks, Photorealistic Images, Information Graphics, Textual Graphics, Computer Graphics, and Screenshots.
- **Rich supervision:** ~3.6K condition sets and ~20K fine-grained human annotations enable comprehensive, reproducible evaluation.
- **Explainable evaluation pipeline:** We decompose generated outputs via object/segment extraction to identify entities (objects, fine-grained regions), supporting both scalar ratings and object-/segment-level failure tags.
- **Diverse model suite:** We evaluate **14 models** in total — **4 unified** (GPT-Image-1, Gemini 2.0 Flash, BAGEL, OmniGen2) and **10 task-specific** baselines (SDXL, Flux.1-Krea-dev, Flux.1-Kontext-dev, Qwen-Image, Infinity, Janus Pro, UNO, Step1X-Edit, IC-Edit, InstructPix2Pix).

<div align="center">
 <a href = "https://tiger-ai-lab.github.io/ImagenWorld/">[🌐 Project Page]</a> <a href = "">[📄 Arxiv]</a> <a href = "https://huggingface.co/datasets/TIGER-Lab/ImagenWorld">[💾 Datasets]</a> <a href = "">[🏛️ ImagenMuseum]</a>
</div>

## 📖 Introduction

This repository contains the code for the paper [ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation on Open-ended Real-World Tasks]().
In this paper, We introduce **ImagenWorld**, a large-scale, human-centric benchmark designed to stress-test image generation models in real-world scenarios. Unlike prior evaluations that focus on isolated tasks or narrow domains, ImagenWorld is organized into six domains: Artworks, Photorealistic Images, Information Graphics, Textual Graphics, Computer Graphics, and Screenshots, and six tasks: Text-to-Image Generation (TIG), Single-Reference Image Generation (SRIG), Multi-Reference Image Generation (MRIG), Text-to-Image Editing (TIE), Single-Reference Image Editing (SRIE), and Multi-Reference Image Editing (MRIE). The benchmark includes 3.6K condition sets and 20K fine-grained human annotations, providing a comprehensive testbed for generative models. To support explainable evaluation, ImagenWorld applies object- and segment-level extraction to generated outputs, identifying entities such as objects and fine-grained regions. This structured decomposition enables human annotators to provide not only scalar ratings but also detailed tags of object-level and segment-level failures.


<p align="center">
  <img src="https://github.com/TIGER-AI-Lab/ImagenWorld/blob/gh-pages/static/images/overview.PNG" alt="Teaser" width="70%"/>
</p>

## 🚀 Release Plan

We will release the evaluation scripts and annotated masks. 

Stay tuned for updates\!


## Citation

If you find our work useful for your research, please consider citing our paper:

```bibtex
@article{
}
