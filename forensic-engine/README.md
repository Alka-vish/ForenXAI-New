# ForenXAI Python Forensic Analysis Engine

A deterministic image feature and forensic evidence extraction service built with **Python**, **FastAPI**, **OpenCV**, **Pillow**, **NumPy**, and **SciPy**.

This service calculates mathematical, structural, frequency, residual, wavelet, compression, and error-level properties of uploaded images. All computed values are genuine numerical calculations directly extracted from the pixel matrix and format metadata.

> **Important Forensic Notice**: These analyses represent empirical **evidence** only. This service does not output arbitrary real/fake verdicts or unverified classification thresholds.

---

## Forensic Analysis Modules

### 1. Image Information
- Dimensions (`width`, `height`), color mode, format, file size in bytes.

### 2. Spatial Features
- **Brightness**: Mean luminance across pixel values.
- **Contrast**: Standard deviation of pixel intensities.
- **Sharpness**: Variance of the Laplacian operator ($\sigma^2_{\nabla^2}$).
- **Edge Density**: Ratio of detected edge pixels using the Canny edge detector.
- **Image Entropy**: Shannon entropy (in bits) derived from the 8-bit intensity histogram.

### 3. Noise Analysis
- **Gaussian Blur Smoothing**: 5×5 kernel ($\sigma=1.0$).
- **High-Pass Noise Residual**: $I - \text{Blur}(I)$.
- **Noise Level**: Standard deviation of the spatial noise residual.
- **Residual Energy**: Mean squared energy of the residual signal.

### 4. Frequency Analysis (2D FFT)
- **2D Fast Fourier Transform**: Shifted DC component with 2D power spectrum calculation.
- **Radial Frequency Partitioning**: Low-frequency (0–15% radius), mid-frequency (15–50% radius), and high-frequency (>50% radius) energy sums and normalized energy ratios.

### 5. SRM-Style Residual Analysis (Spatial Rich Models)
- Standard linear high-pass filter kernels:
  - 1st order horizontal difference `[-1, 1]`
  - 1st order vertical difference `[[-1], [1]]`
  - 2nd order horizontal residual `[-1, 2, -1]`
  - 2nd order vertical residual `[[-1], [2], [-1]]`
  - 3×3 Laplacian kernel
  - 3×3 Ker-Böhme (KB) square kernel `[[-1, 2, -1], [2, -4, 2], [-1, 2, -1]]`
  - 3×3 Edge detector kernel
- Computes mean, standard deviation, variance, residual energy ($\frac{1}{N}\sum R^2$), min, and max for each filter.
- Generates and persists an SRM residual map (`COLORMAP_TWILIGHT`).

### 6. Wavelet Analysis (Haar 2D Discrete Wavelet Transform)
- Level-1 2D Haar DWT decomposing image into 4 subbands:
  - **LL**: Low-low approximation subband
  - **LH**: Low-high horizontal detail subband
  - **HL**: High-low vertical detail subband
  - **HH**: High-high diagonal detail subband
- Calculates individual subband energies, total high-frequency energy ($LH + HL + HH$), and normalized energy ratios.
- Generates a 2×2 quad-subband collage map with crosshair delineation (`COLORMAP_VIRIDIS`).

### 7. JPEG Compression Analysis
- For JPEG files:
  - Extracts luminance and chrominance quantization tables from the image stream.
  - Inverts the Independent JPEG Group (IJG) 50% luminance table to estimate the image's quality factor.
  - Computes 8×8 DCT grid boundary discontinuities (Blocking Artifact Factor, BAF).
  - Evaluates 8×8 block-level variance uniformity.
- For PNG/WEBP or images without usable quantization tables:
  - Safely returns status `"unavailable"` without failing the request.

### 8. Error Level Analysis (ELA / Recompression Analysis)
- Deterministically recompresses the image in-memory to JPEG at quality 90.
- Calculates pixel-level absolute difference across color channels and luminance.
- Global metrics: average difference, maximum difference, standard deviation.
- Regional difference analysis: 3×3 spatial grid evaluating local mean difference, max difference, and regional variance to detect local compression discrepancies.
- Generates an amplified error difference visualization map (`COLORMAP_MAGMA`).

### 9. AI-Generated Image Detection (Deep Learning Indicator)
- Pretrained Swin Transformer (`umm-maybe/AI-image-detector`) executing image classification inference.
- Outputs probabilistic confidence scores for synthetic (`artificial`) versus natural (`human`) visual features.
- Statistical indicator serving as an empirical data point alongside physical, wavelet, and signal evidence.
- Graceful offline fallback: if PyTorch or Hugging Face weights are inaccessible, reports honest `"unavailable"` status without inventing predictions.

### 10. Structured Forensic Evidence Ledger (`evidence`)
- Converts empirical calculations from all active modules into clear, traceable forensic evidence items.
- Every evidence item follows a standardized schema:
```json
{
  "evidence_id": "E001",
  "category": "noise_analysis",
  "title": "High-Pass Spatial Noise Residual",
  "observation": "Spatial noise residual extracted via Gaussian smoothing (5x5 kernel (sigma=1.0)) exhibits a noise standard deviation of 14.4858 and mean squared residual energy of 209.8373.",
  "measurement": {
    "noise_level": 14.4858,
    "residual_energy": 209.8373,
    "gaussian_blur": "5x5 kernel (sigma=1.0)",
    "noise_map": "/maps/noise_residual_...png"
  },
  "source_module": "noise_analysis",
  "coordinates": null,
  "strength": "informational",
  "alternative_explanations": [
    "Noise level variations are heavily influenced by camera sensor ISO, thermal noise, lossy compression smoothing, or artistic grain overlays.",
    "Bilateral filtering, denoising algorithms, or AI generation smoothing can artificially depress high-pass residual energy."
  ],
  "limitations": [
    "Gaussian blur residual is an approximate spatial noise estimation and does not model camera-specific PRNU (Photo-Response Non-Uniformity) sensor patterns.",
    "Intricate high-frequency image textures can contaminate the estimated noise residual."
  ]
}
```
- **Evidence Integrity Principles**:
  - Uses only real mathematical measurements directly extracted from pixel and bitstream data.
  - Never assigns arbitrary labels (REAL, FAKE, HUMAN, AI-GENERATED) as definitive proof.
  - Coordinates are provided when spatial localization is available (e.g. 3×3 regional ELA discrepancies), otherwise `null`.
  - Always includes domain-specific alternative explanations (compression, resizing, lighting, depth-of-field, sensor noise) and technical limitations.

---

## LangGraph Four-Agent Forensic Debate System

ForenXAI implements a deterministic, multi-agent debate architecture powered by **LangGraph StateGraph** featuring **exactly four agents**:

```
START
  ↓
Validate Initial Evidence
  ↓
Prosecutor Turn 1 (Spatial & Noise)
  ↓
Defence Turn 1 (Rebuttal & Optical Context)
  ↓
Sufficiency Check 1
  ↓
Prosecutor Turn 2 (Frequency & Wavelet)
  ↓
Defence Turn 2 (Rebuttal & Power-Law Decay)
  ↓
Sufficiency Check 2
  ↓
Prosecutor Turn 3 (SRM & Error Level Analysis)
  ↓
Defence Turn 3 (Rebuttal & DCT Edge Contrast)
  ↓
Sufficiency Check 3
  ↓
Prosecutor Turn 4 (AI Classifier & Synthesis)
  ↓
Defence Turn 4 (Rebuttal & Concept Drift)
  ↓
Sufficiency Check 4
  ↓
Expert Agent (Anti-Hallucination Audit & Ledger Verification)
  ↓
Expert Recommendation Gate
  ├── Stop (Violation / Critical Missing Evidence) → END
  └── Proceed → Judge Agent (Synthesis & Final Assessment)
                    ↓
                   END
```

### Agent Roles & Guardrails

1. **Prosecutor Agent** (`agents/prosecutor_agent.py`):
   - Argues points suggesting synthetic generation, splicing, or manipulation.
   - Strictly references existing evidence IDs from the ledger (e.g. `E001`, `E002`).
   - Cites uncertainties and alternative explanations alongside observations.
2. **Defence Agent** (`agents/defence_agent.py`):
   - Directly responds to the preceding Prosecutor turn argument.
   - Introduces benign alternative physical explanations (sensor ISO, optics, lossy compression, scene geometry).
   - Strictly references existing evidence IDs.
3. **Expert Agent** (`agents/expert_agent.py`):
   - Runs only after all 8 debate messages are completed.
   - Cross-checks all cited evidence IDs against the ledger and intercepts hallucinations.
   - Detects unsupported definitive claims, evaluates contradictions, and logs technical reliability concerns.
   - Recommends `"proceed_to_judge"` or `"stop"`.
4. **Judge Agent** (`agents/judge_agent.py`):
   - Runs strictly after Expert verification confirms zero hallucinations and valid evidence.
   - Synthesizes verified claims from both debating agents.
   - Issues an assessment constrained strictly to `"REAL"`, `"FAKE"`, or `"UNCERTAIN"`.
   - Never invents confidence percentages or treats single indicators as definitive proof.

### Early Stopping on Insufficient Evidence
If evidence is missing, below minimum analytical threshold (< 3 items), or corrupted, the system stops execution immediately. Neither the Expert nor Judge Agent is called, no verdict is generated, and a transparent explanation is returned:
```json
{
  "status": "insufficient_evidence",
  "can_proceed": false,
  "debate_completed": false,
  "message": "I cannot proceed with the investigation because the available forensic evidence is insufficient.",
  "completed_iterations": 0,
  "expert_report": null,
  "judge_result": null
}
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- `pip` (Python package manager)

### 1. Create a Virtual Environment (Recommended)

```bash
cd forensic-engine
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Service

Start the FastAPI application with Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or run directly with Python:

```bash
python main.py
```

The service will run on `http://0.0.0.0:8000` (or the port specified by the `PORT` environment variable).

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

## API Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Response**:
```json
{
  "status": "ok"
}
```

### 2. Perform Forensic Analysis
- **Endpoint**: `POST /analyze`
- **Content-Type**: `multipart/form-data`
- **Body**: `image` (binary file: JPG, JPEG, PNG, or WEBP)
- **Response**: Full structured JSON payload containing all evidence metrics and visual map links.

### 3. Retrieve Analysis Map
- **Endpoint**: `GET /maps/{filename}`
- **Response**: Binary PNG stream of the generated forensic visualization.

### 4. Execute 4-Agent LangGraph Debate
- **Endpoint**: `POST /debate`
- **Content-Type**: `multipart/form-data`
- **Body**: `image` (binary file: JPG, JPEG, PNG, or WEBP)
- **Response**: Complete forensic extraction, structured evidence ledger, and the 4-agent LangGraph debate results (Prosecutor & Defence 8-message debate, Expert verification report, and Judge final assessment).

### 5. Execute Debate on Precomputed Evidence
- **Endpoint**: `POST /debate-evidence`
- **Content-Type**: `application/json`
- **Body**: JSON object containing `analysis_result` and `evidence` array.
- **Response**: LangGraph debate execution results based directly on the provided evidence ledger.
