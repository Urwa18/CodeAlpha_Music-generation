# AI Music Generation Project

An end-to-end deep learning framework in Python for learning musical patterns from MIDI files and generating new compositions using TensorFlow/Keras.

---

## 📁 Project Directory Architecture & Folder Explanations

```
project/
│── dataset/          # Raw MIDI files dataset storage
│── processed_data/   # Preprocessed numerical tensors, note sequences, and vocabulary mappings
│── models/           # Model definitions, saved weights (.keras/.h5), and checkpoints
│── notebooks/        # Jupyter Notebooks for exploratory data analysis (EDA) and prototyping
│── utils/            # Helper utilities for MIDI parsing, visualization, and audio conversion
│── training/         # Model training scripts, loss evaluation, and training pipelines
│── generation/       # Inference and music generation scripts (sampling, temperature scaling)
│── output/           # Generated MIDI files, audio renders (WAV/MP3), and sheet visualizations
│── api/              # REST API server (FastAPI/Flask) for serving generated music endpoints
│── frontend/         # Web application UI for interactive music creation and playback
│── config/           # Centralized project configuration files (YAML / Python settings)
```

### Detailed Purpose of Each Folder

1. **`dataset/`**:
   Stores raw `.mid` / `.midi` files collected from datasets (e.g., MAESTRO Dataset, Lakh MIDI Dataset, or custom piano compositions). Files in this folder remain untouched as source data.

2. **`processed_data/`**:
   Contains preprocessed numerical arrays, encoded sequence tensors (`.npy`, `.npz`), pitch dictionaries, and serialized mappings (`.pkl`) ready for model feeding.

3. **`models/`**:
   Houses neural network model architecture definitions (e.g., Deep LSTM, Recurrent Neural Networks, Transformer models) and holds saved model weights (`.keras`, `.h5`), checkpoints, and serialized metadata.

4. **`notebooks/`**:
   Dedicated space for interactive research, exploratory data analysis (EDA), sequence distribution analysis, visual piano roll plotting, and prototyping model experiments.

5. **`utils/`**:
   Reusable core utility modules for parsing MIDI files with `mido`/`pretty_midi`/`music21`, pitch conversion, vectorization, and helper functions for rendering audio.

6. **`training/`**:
   Scripts to execute model training, manage training loops, compute loss metrics, handle early stopping, and save checkpoints automatically.

7. **`generation/`**:
   Inference engines that accept seed sequences and sample notes/chords step-by-step using temperature scaling, top-k/top-p sampling, and convert predictions back into playable MIDI tracks.

8. **`output/`**:
   Stores synthesized generated music output files (`.mid`, `.wav`) produced by the generation module for user evaluation and listening.

9. **`api/`**:
   Houses the REST API application (FastAPI / Uvicorn) enabling programmatic generation requests, stream generation, and integration with frontends.

10. **`frontend/`**:
    Web-based graphical interface allowing users to adjust parameters (tempo, temperature, instruments), upload custom seed MIDIs, trigger music generation, and listen to results.

11. **`config/`**:
    Central project settings containing parameters for sequence length, pitch bounds, hyperparameters, batch size, learning rates, and directory paths (`config.yaml` & `config.py`).

---

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **Deep Learning Framework**: TensorFlow / Keras (preferred)
- **MIDI Processing**: `pretty_midi`, `music21`, `mido`
- **Data & Numerical Science**: `numpy`, `pandas`, `scipy`
- **API Framework**: `FastAPI` / `Uvicorn`
- **Configuration**: YAML & Python dataclasses

---

## ⚙️ Setup & Installation

1. **Clone or Navigate to Project Directory**:
   ```bash
   cd "d:/frontend/music generation"
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🗺️ Development Roadmap

- [x] **Phase 1: Project Setup & Structure Initialization**
- [ ] **Phase 2: MIDI Data Ingestion & Preprocessing Pipeline**
- [ ] **Phase 3: Deep Learning Model Design (LSTM / Transformer)**
- [ ] **Phase 4: Model Training & Evaluation Pipeline**
- [ ] **Phase 5: Music Generation & Post-Processing Engine**
- [ ] **Phase 6: REST API & Interactive Web Frontend**
