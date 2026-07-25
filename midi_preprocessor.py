"""
MIDI Preprocessing & Feature Extraction Module for AI Music Generation
Uses music21 to parse MIDI compositions, extract notes, chords, durations, and tempo,
build sliding-window sequences, encode tokens numerically, and save output tensors.
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"


class MIDIExtractor:
    """Extracts musical components (notes, chords, durations, tempo) from MIDI files using music21."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.notes: List[str] = []
        self.durations: List[float] = []
        self.combined_events: List[str] = []
        self.tempos: List[float] = []

    def parse(self) -> bool:
        """
        Parses the MIDI file safely with music21.
        Returns True if successful, False if corrupted or unparseable.
        """
        import music21

        try:
            # Parse MIDI file into music21 Score stream
            midi_stream = music21.converter.parse(str(self.filepath))
            
            # 1. Extract Tempo (BPM)
            metro_marks = midi_stream.flatten().getElementsByClass(music21.tempo.MetronomeMark)
            if metro_marks:
                self.tempos = [float(mm.getQuarterBPM()) for mm in metro_marks]
            else:
                self.tempos = [120.0]  # Fallback standard BPM

            # Flatten stream to isolate instrument parts / notes
            parts = music21.instrument.partitionByInstrument(midi_stream)
            notes_to_parse = parts.parts[0].recurse() if parts else midi_stream.flat.notes

            for element in notes_to_parse:
                # 2. Extract Single Notes
                if isinstance(element, music21.note.Note):
                    pitch_str = str(element.pitch)
                    duration_val = float(element.duration.quarterLength)

                    self.notes.append(pitch_str)
                    self.durations.append(duration_val)
                    # Combined token representation pitch_duration
                    self.combined_events.append(f"{pitch_str}_{duration_val}")

                # 3. Extract Chords (Multiple simultaneous pitches)
                elif isinstance(element, music21.chord.Chord):
                    chord_str = ".".join(str(n) for n in element.normalOrder)
                    duration_val = float(element.duration.quarterLength)

                    self.notes.append(chord_str)
                    self.durations.append(duration_val)
                    self.combined_events.append(f"CHORD_{chord_str}_{duration_val}")

            return len(self.combined_events) > 0

        except Exception as e:
            logger.warning(f"Safely skipped corrupted/unparseable MIDI file: {self.filepath.name} (Error: {e})")
            return False


class MIDIPreprocessor:
    """Preprocesses a directory of MIDI files into numeric sequences for AI training."""

    def __init__(self, sequence_length: int = 100):
        self.sequence_length = sequence_length
        self.token_to_int: Dict[str, int] = {}
        self.int_to_token: Dict[int, str] = {}
        self.vocab_size: int = 0

    def process_dataset(self, dataset_dir: Path = DATASET_DIR) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Iterates over dataset folder, parses all valid MIDIs, builds vocabulary,
        creates sliding window sequences (X, Y), and saves processed data.
        """
        midi_files = list(dataset_dir.glob("**/*.mid")) + list(dataset_dir.glob("**/*.midi"))
        total_files = len(midi_files)

        if total_files == 0:
            raise FileNotFoundError(f"No MIDI files found in {dataset_dir}")

        logger.info(f"Starting MIDI preprocessing on {total_files} files...")
        all_events: List[str] = []
        parsed_count = 0
        skipped_count = 0

        # Progress display
        for idx, file in enumerate(midi_files, 1):
            progress_pct = (idx / total_files) * 100
            print(f"[{idx}/{total_files}] ({progress_pct:.1f}%) Processing: {file.name}...", end="\r")

            extractor = MIDIExtractor(file)
            if extractor.parse():
                all_events.extend(extractor.combined_events)
                parsed_count += 1
            else:
                skipped_count += 1

        print("\n" + "-" * 60)
        logger.info(f"Preprocessing completed. Parsed: {parsed_count} files, Skipped/Corrupted: {skipped_count} files.")
        logger.info(f"Total musical events extracted: {len(all_events)}")

        if len(all_events) <= self.sequence_length:
            raise ValueError(f"Extracted events ({len(all_events)}) must be greater than sequence length ({self.sequence_length}).")

        # 4. Build Vocabulary & Numeric Encoding
        pitchnames = sorted(list(set(all_events)))
        self.vocab_size = len(pitchnames)
        self.token_to_int = {token: number for number, token in enumerate(pitchnames)}
        self.int_to_token = {number: token for number, token in enumerate(pitchnames)}

        logger.info(f"Unique Token Vocabulary Size: {self.vocab_size}")

        # 5. Create Input (X) and Output (Y) Sliding Window Sequences
        network_input = []
        network_output = []

        for i in range(0, len(all_events) - self.sequence_length, 1):
            sequence_in = all_events[i : i + self.sequence_length]
            sequence_out = all_events[i + self.sequence_length]

            network_input.append([self.token_to_int[char] for char in sequence_in])
            network_output.append(self.token_to_int[sequence_out])

        n_patterns = len(network_input)
        logger.info(f"Generated {n_patterns} sliding-window training sequences.")

        # Reshape & Normalize Inputs for Model Preparation
        X = np.reshape(network_input, (n_patterns, self.sequence_length))
        Y = np.array(network_output)

        # 6. Save Processed Data Tensors & Vocabulary Metadata
        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

        np.save(PROCESSED_DATA_DIR / "X.npy", X)
        np.save(PROCESSED_DATA_DIR / "Y.npy", Y)

        vocab_data = {
            "token_to_int": self.token_to_int,
            "int_to_token": {str(k): v for k, v in self.int_to_token.items()},
            "vocab_size": self.vocab_size,
            "sequence_length": self.sequence_length,
            "total_sequences": n_patterns,
            "parsed_files": parsed_count,
            "skipped_files": skipped_count
        }

        with open(PROCESSED_DATA_DIR / "vocab_metadata.json", "w", encoding="utf-8") as f:
            json.dump(vocab_data, f, indent=4)

        logger.info(f"Saved processed arrays and vocabulary to {PROCESSED_DATA_DIR}/")
        return X, Y, vocab_data


def run_preprocessing():
    """Main execution entry point for Phase 3."""
    preprocessor = MIDIPreprocessor(sequence_length=10)
    X, Y, metadata = preprocessor.process_dataset()

    print("\n" + "=" * 65)
    print("           PHASE 3: MIDI PREPROCESSING SUMMARY               ")
    print("=" * 70)
    print(f"Total Input Sequences (X shape) : {X.shape}")
    print(f"Total Target Labels (Y shape)  : {Y.shape}")
    print(f"Vocabulary Size (Unique Events) : {metadata['vocab_size']}")
    print(f"Sequence Window Length         : {metadata['sequence_length']}")
    print(f"Saved Arrays Location          : {PROCESSED_DATA_DIR}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_preprocessing()
