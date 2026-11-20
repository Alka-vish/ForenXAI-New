# ForenXAI: Real vs. AI-Manipulated Facial Image Dataset

**ForenXAI** is a research-oriented facial image dataset developed for AI-manipulated image detection, synthetic media analysis, and digital image forensics.

The dataset contains authentic facial photographs and AI-manipulated facial images, with an emphasis on image-level provenance, metadata preservation, and reproducibility.

## 1. Dataset Overview

ForenXAI consists of two primary classes:

| Class | Number of Images | Description |
|---|---:|---|
| Real | 788 | Authentic facial photographs |
| Fake | 677 | AI-manipulated facial photographs |
| **Total** | **1,465** | **Complete dataset** |

The dataset is designed to support research into identifying visual and forensic differences between authentic facial photographs and AI-manipulated images.

### Dataset Highlights

- 1,465 facial images across two classes.
- Authentic images collected from Wikimedia Commons and Smithsonian Open Access.
- AI-manipulated images derived from FFHQ source images.
- Stable Diffusion-based image manipulation.
- Image-level metadata and provenance information.
- Technical image properties and SHA-256 integrity information.
- Designed for digital image forensics and synthetic image detection research.

## 2. Dataset Directory Structure

The dataset is organized as follows:

```text
Forex_AI_Dataset1/
│
├── fake/
│   ├── fake_001.jpg
│   └── ...
│
├── metadata/
│   ├── metadata.json
│   └── ...
│
├── Real/
│   ├── real_001.jpg
│   └── ...
│
└── Smithsonian_Real/
    ├── real_001.jpg
    └── ...
```

### Folder Description

| Folder | Description |
|---|---|
| `fake/` | AI-manipulated facial images derived from FFHQ source images |
| `metadata/` | Image-level metadata, provenance, and generation information |
| `Real/` | Authentic facial images collected from Wikimedia Commons |
| `Smithsonian_Real/` | Authentic facial images collected from Smithsonian Open Access |

The two authentic image folders together contain 788 images.

## 3. Dataset Collection Methodology

### 3.1 Real Image Collection

Authentic facial images were collected from publicly accessible image repositories:

**Wikimedia Commons**
- Website: https://commons.wikimedia.org/
- API: https://commons.wikimedia.org/w/api.php
- Provides photographs and associated metadata, including creator information, source URLs, descriptions, and licensing details.

**Smithsonian Open Access**
- Website: https://www.si.edu/openaccess
- Provides publicly accessible images and collection metadata through its Open Access initiative.

The collection workflow uses Python-based data extraction and image downloading.

Technologies used in the collection workflow include:

- Python for automation and dataset processing.
- BeautifulSoup4 for HTML parsing and web data extraction.
- Requests for downloading images and retrieving web resources.
- Wikimedia Commons API and Smithsonian Open Access API for structured metadata retrieval.

Available source information, including creator, credit, description, original URL, attribution, and licensing details, is preserved in the accompanying metadata.

### 3.2 AI-Manipulated Image Generation

The Fake class contains 677 AI-manipulated facial images derived from the **Flickr-Faces-HQ (FFHQ)** dataset.

FFHQ provides the original facial images used as source material for the manipulation pipeline.

AI-based image manipulation is performed using Stable Diffusion-based techniques, including:

- **Image-to-Image (img2img):** Transforming an existing facial image while retaining aspects of its original visual structure.
- **Inpainting:** Modifying selected image regions while preserving surrounding image content.

The recommended lightweight generation configuration uses Stable Diffusion 1.5 with Hugging Face Diffusers and PyTorch.

Generation metadata is retained wherever available to support traceability and reproducibility.

**Note:** The generated samples are classified as AI-manipulated images. They should not be interpreted as face swaps or identity replacements unless those specific operations have been performed.

## 4. Source Datasets and Data Sources

| Source | Purpose | Reference |
|---|---|---|
| Wikimedia Commons | Authentic facial photographs | https://commons.wikimedia.org/ |
| Smithsonian Open Access | Authentic facial photographs | https://www.si.edu/openaccess |
| FFHQ | Source facial images for manipulation | https://github.com/NVlabs/ffhq-dataset |

### FFHQ Reference

Karras, T., Laine, S., and Aila, T. (2019).

*A Style-Based Generator Architecture for Generative Adversarial Networks.*

Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR).

Dataset repository: https://github.com/NVlabs/ffhq-dataset

## 5. Tools and Technologies

| Technology | Application |
|---|---|
| Python | Dataset collection and automation |
| BeautifulSoup4 | HTML parsing |
| Requests | Image downloading |
| Wikimedia Commons API | Real image collection |
| Smithsonian Open Access API | Real image collection |
| FFHQ | Source facial image dataset |
| Stable Diffusion 1.5 | AI-based image manipulation |
| Hugging Face Diffusers | Diffusion model integration |
| PyTorch | Deep learning and model execution |
| CUDA | GPU acceleration |
| OpenCV | Image processing and face detection |
| Pillow | Image loading and processing |
| NumPy | Numerical image analysis |
| hashlib | SHA-256 integrity verification |
| JSON | Metadata storage |

## 6. Metadata Configuration

ForenXAI maintains structured metadata to preserve image-level provenance, classification, technical characteristics, and generation history.

The metadata includes the following information wherever available.

### General Information

- Filename
- Classification label
- Source repository
- Original source URL
- Image URL
- Creator
- Credit
- Description
- Original date
- License
- License URL
- Attribution
- Collection timestamp
- Human review status

### Image Properties

- Width and height
- Aspect ratio
- Image format
- SHA-256 hash
- Brightness
- Contrast
- Sharpness
- Face detection status
- Face count

### Generation Information

For AI-manipulated images, additional information includes:

- Original source image reference
- Generation framework
- Model name and version
- Manipulation technique
- Random seed
- Generation parameters
- Prompts, where available

Generation fields are not applicable to original authentic photographs.

The metadata is intended to provide transparency and help researchers trace individual images to their respective sources.

## 7. Forensic Characteristics

ForenXAI is intended to support research into multiple forensic representations that can help distinguish authentic photographs from AI-manipulated images.

The broader ForenXAI research framework investigates:

| Representation | Purpose |
|---|---|
| Spatial | Pixel-level structures, textures, and visual inconsistencies |
| Noise | Image noise distributions and inconsistencies |
| FFT | Frequency-domain and spectral characteristics |
| ELA | Error Level Analysis and compression-related differences |
| JPEG | JPEG compression and encoding artifacts |
| SRM | Spatial Rich Model-based residual representations |
| Wavelet | Multi-scale frequency and texture characteristics |

These representations provide complementary information for image authenticity analysis and can be used in forensic classification and explainability research.

## 8. Intended Applications

The dataset is intended for academic and experimental research in:

1. Real-versus-AI-manipulated facial image classification.
2. AI-generated and synthetic media detection.
3. Digital image forensics.
4. Image manipulation identification.
5. Forensic feature extraction and analysis.
6. Explainable AI-based image authenticity assessment.
7. Research into generative AI and synthetic media.

## 9. Rights, Licensing, and Attribution

ForenXAI incorporates images from multiple external sources. Copyright ownership and licensing conditions may differ between individual images. Therefore, no single licence should be assumed to apply to the entire dataset.

### 9.1 Wikimedia Commons

Wikimedia Commons contains images released under different Creative Commons licences and public-domain designations.

- **Source:** https://commons.wikimedia.org/
- **Licensing information:** https://commons.wikimedia.org/wiki/Commons:Licensing
- **Reuse guidelines:** https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia

Each image must be checked individually for its original licence, creator, attribution requirements, and source file page.

### 9.2 Smithsonian Open Access

Smithsonian Open Access makes designated digital collection assets available under Creative Commons Zero (CC0).

- **Source:** https://www.si.edu/openaccess
- **Official licensing information:** https://www.si.edu/openaccess/faq
- **CC0 1.0 Universal:** https://creativecommons.org/publicdomain/zero/1.0/

Only images explicitly designated as CC0 should be treated as Smithsonian Open Access assets available under CC0. Other items may have different usage conditions.

### 9.3 Flickr-Faces-HQ (FFHQ)

The Fake class uses facial images derived from the Flickr-Faces-HQ (FFHQ) dataset.

- **Dataset repository:** https://github.com/NVlabs/ffhq-dataset
- **Dataset licence (CC BY-NC-SA 4.0):** https://creativecommons.org/licenses/by-nc-sa/4.0/

The FFHQ documentation specifies that its individual source photographs were originally published under different licences:

| Original image licence | Licence URL |
|---|---|
| Creative Commons Attribution 2.0 (CC BY 2.0) | https://creativecommons.org/licenses/by/2.0/ |
| Creative Commons Attribution-NonCommercial 2.0 (CC BY-NC 2.0) | https://creativecommons.org/licenses/by-nc/2.0/ |
| Public Domain Mark 1.0 | https://creativecommons.org/publicdomain/mark/1.0/ |
| Creative Commons Zero 1.0 (CC0 1.0) | https://creativecommons.org/publicdomain/zero/1.0/ |
| U.S. Government Works | https://www.usa.gov/copyright |

The FFHQ dataset documentation, including its metadata, download script, and documentation, is separately released under CC BY-NC-SA 4.0 by NVIDIA.

The original image licence and creator information should be checked using the FFHQ metadata. The dataset-level licence should not be assumed to replace the licences of individual photographs.

### 9.4 AI-Manipulated Images

The AI-manipulated images are derived from FFHQ source photographs using Stable Diffusion-based image manipulation.

The original source-image references and available generation information should be preserved.

The licensing conditions applicable to each original image must be considered when determining whether its manipulated derivative can be redistributed. Modifications do not automatically eliminate the original image's copyright or licensing restrictions.

### 9.5 Attribution and Reuse Requirements

Users accessing or reusing ForenXAI should:

- Preserve original creator and source information wherever available.
- Consult the image-level licence recorded in `metadata.json`.
- Provide appropriate attribution and licence links where required.
- Indicate modifications to source images where required.
- Respect NonCommercial and ShareAlike conditions where applicable.
- Verify third-party rights and restrictions before redistribution or commercial use.

**Important:** ForenXAI is a publicly accessible research dataset with mixed source-level licensing. Public access does not imply unrestricted commercial use or redistribution rights for every image.

## 10. Research and Usage Considerations

ForenXAI is intended to facilitate research and experimentation in AI-manipulated image detection and digital image forensics.

Researchers are encouraged to:

- Preserve the original metadata when using the dataset.
- Maintain source-image references for manipulated samples.
- Avoid train-test leakage between original images and their derivatives.
- Evaluate models using appropriate classification metrics.
- Document preprocessing and experimental configurations.
- Consider image quality, source diversity, and potential dataset biases when interpreting results.

The dataset should not be treated as a guarantee that an image is authentic or manipulated. Model predictions require appropriate validation and interpretation.

## 11. Credits and Acknowledgements

We acknowledge the original photographers, creators, institutions, dataset authors, and open-source developers whose resources and technologies contributed to the development of ForenXAI.

### Real Image Sources

- **Wikimedia Commons:** https://commons.wikimedia.org/
- **Smithsonian Open Access:** https://www.si.edu/openaccess

### Source Dataset

- **Flickr-Faces-HQ (FFHQ):** https://github.com/NVlabs/ffhq-dataset

### Image Generation Framework

- **Stable Diffusion 1.5:** https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5
- **Hugging Face Diffusers:** https://huggingface.co/docs/diffusers

### Supporting Technologies

We also acknowledge the developers and maintainers of Python, PyTorch, CUDA, OpenCV, Pillow, NumPy, Requests, BeautifulSoup4, and other open-source technologies used in the dataset collection, processing, and analysis workflows.

ForenXAI is an independently developed research dataset and is not affiliated with, endorsed by, or officially distributed by the above-mentioned organizations.

## 12. Dataset Summary

| Property | Details |
|---|---|
| Dataset Name | ForenXAI |
| Full Name | Real vs. AI-Manipulated Facial Image Dataset |
| Total Images | 1,465 |
| Real Images | 788 |
| Fake Images | 677 |
| Dataset Classes | Real and Fake |
| Real Image Sources | Wikimedia Commons and Smithsonian Open Access |
| Fake Image Source | FFHQ-derived facial images |
| Manipulation Framework | Stable Diffusion |
| Metadata Format | JSON |
| Primary Research Domain | AI-Based Image Detection and Digital Image Forensics |
| Intended Usage | Academic and Research Purposes |

---

**ForenXAI Research Team**

Developed for research into synthetic facial image detection, AI-based image manipulation analysis, and digital media forensics.
