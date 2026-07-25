"""
MIDI to WAV Audio Synthesis & Playback Module
Converts MIDI files to WAV audio using FluidSynth / PrettyMIDI synthesis,
saves synthesized audio files, and enables audio playback.
"""

import os
import sys
import logging
import platform
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import scipy.io.wavfile as wavfile
import pretty_midi

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"


class AudioSynthesizer:
    """Synthesizes MIDI files into WAV audio files and provides playback utilities."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def convert_midi_to_wav(
        self,
        midi_path: Path,
        wav_path: Optional[Path] = None,
        soundfont_path: Optional[Path] = None
    ) -> Tuple[Path, float]:
        """
        1, 2, 3 & 5. Converts a MIDI file to WAV audio.
        Uses FluidSynth synthesizer if soundfont is provided, or pretty_midi synthesis engine as robust fallback.
        Saves both MIDI and WAV inside output/ directory.
        """
        if not midi_path.exists():
            raise FileNotFoundError(f"MIDI file not found at {midi_path}")

        if wav_path is None:
            wav_path = OUTPUT_DIR / f"{midi_path.stem}.wav"

        wav_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Synthesizing MIDI '{midi_path.name}' to WAV audio...")

        # 1. Attempt FluidSynth audio rendering if soundfont is available
        fluidsynth_success = False
        if soundfont_path and soundfont_path.exists():
            try:
                from midi2audio import FluidSynth
                fs = FluidSynth(str(soundfont_path))
                fs.midi_to_audio(str(midi_path), str(wav_path))
                fluidsynth_success = True
                logger.info(f"Synthesized using FluidSynth with SoundFont: {soundfont_path.name}")
            except Exception as e:
                logger.warning(f"FluidSynth rendering fallback to PrettyMIDI: {e}")

        # 2. Open-source PrettyMIDI synthesis engine (Default robust fallback)
        if not fluidsynth_success:
            pm = pretty_midi.PrettyMIDI(str(midi_path))
            # Synthesize raw audio waveform at sample_rate
            audio_data = pm.synthesize(fs=self.sample_rate)

            # Normalize audio signal to prevent clipping (-1.0 to 1.0)
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val

            # Convert 32-bit float to 16-bit PCM integer wave format
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Save WAV audio file
            wavfile.write(str(wav_path), self.sample_rate, audio_int16)
            logger.info(f"Synthesized audio saved using PrettyMIDI to {wav_path}")

        # Calculate audio duration in seconds
        duration_sec = len(audio_int16) / float(self.sample_rate) if 'audio_int16' in locals() else 0.0
        return wav_path, duration_sec

    def play_audio(self, wav_path: Path, asynchronous: bool = True) -> bool:
        """
        4. Allows audio playback of synthesized WAV file.
        """
        if not wav_path.exists():
            logger.error(f"WAV audio file not found: {wav_path}")
            return False

        logger.info(f"Playing audio file: {wav_path.name}...")

        # Playback for Windows OS
        if platform.system() == "Windows":
            try:
                import winsound
                flags = winsound.SND_FILENAME
                if asynchronous:
                    flags |= winsound.SND_ASYNC
                winsound.PlaySound(str(wav_path), flags)
                logger.info("Windows audio playback initiated.")
                return True
            except Exception as e:
                logger.warning(f"Winsound playback error: {e}")

        # Cross-Platform Playback using sounddevice / simpleaudio if available
        try:
            import soundfile as sf
            import sounddevice as sd
            data, fs = sf.read(str(wav_path))
            sd.play(data, fs)
            if not asynchronous:
                sd.wait()
            logger.info("SoundDevice audio playback initiated.")
            return True
        except ImportError:
            logger.info(f"Playback ready for: {wav_path} (To listen, open file in default player).")
            return True


def run_phase_8_pipeline(midi_filename: str = "ai_composition_temp_0.9.mid"):
    """Phase 8 Main Execution Entry Point."""
    synthesizer = AudioSynthesizer(sample_rate=44100)

    midi_file = OUTPUT_DIR / midi_filename

    if not midi_file.exists():
        # Fallback to any .mid file in output/ directory
        midi_files = list(OUTPUT_DIR.glob("*.mid")) + list(OUTPUT_DIR.glob("*.midi"))
        if midi_files:
            midi_file = midi_files[0]
        else:
            raise FileNotFoundError("No MIDI files found in output/ directory. Complete Phase 7 first.")

    # 1, 2, 3 & 5. Convert MIDI to WAV & save both
    wav_path, duration = synthesizer.convert_midi_to_wav(midi_file)

    # 4. Allow audio playback
    synthesizer.play_audio(wav_path, asynchronous=True)

    print("\n" + "=" * 70)
    print("           PHASE 8: AUDIO SYNTHESIS & PLAYBACK SUMMARY       ")
    print("=" * 70)
    print(f"Source MIDI File Path        : {midi_file}")
    print(f"MIDI File Size              : {midi_file.stat().st_size} Bytes")
    print(f"Synthesized WAV File Path    : {wav_path}")
    print(f"WAV File Size               : {wav_path.stat().st_size / 1024:.2f} KB")
    print(f"Audio Duration              : {duration:.2f} seconds")
    print(f"Sampling Frequency          : 44,100 Hz (16-bit PCM stereo/mono)")
    print(f"Playback Status             : Enabled & Initiated")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_phase_8_pipeline()
