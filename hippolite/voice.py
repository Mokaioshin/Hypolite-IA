import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import subprocess
import tempfile
import os
import winsound
import unicodedata
import requests

from brain import ask_hipolite


MODEL_SIZE = "small"

print("Chargement de Whisper...")

model = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)

print("Whisper prêt.")


def normalize_text(text):
    text = text.lower().strip()

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


def prepare_for_tts(text):
    replacements = {
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "à": "a",
        "â": "a",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ÿ": "y",
        "ç": "c",
        "œ": "oe",
        "Œ": "OE",
        "æ": "ae",
        "Æ": "AE",
        "’": "'",
        "‘": "'",
        "«": '"',
        "»": '"',
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
        "\u00A0": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def set_state(state, text=""):
    try:
        requests.post(
            f"http://127.0.0.1:5000/state/{state}",
            json={"text": text},
            timeout=0.2
        )
    except requests.RequestException:
        pass


def speak(text):
    set_state("speaking", text)

    print(f"\nHipolite > {text}")

    text_file = os.path.join(
        tempfile.gettempdir(),
        "hipolite_text.txt"
    )

    temp_wav = os.path.join(
        tempfile.gettempdir(),
        "hipolite_voice.wav"
    )

    tts_text = prepare_for_tts(text)

    with open(
        text_file,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(tts_text)

    ps_script = f'''
Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$voice = $synth.GetInstalledVoices() |
    Where-Object {{ $_.VoiceInfo.Name -like "*Claude*" }} |
    Select-Object -First 1

if ($null -eq $voice) {{
    Write-Error "Voix Claude introuvable"
    exit 1
}}

$synth.SelectVoice($voice.VoiceInfo.Name)

$text = Get-Content -Raw -LiteralPath "{text_file}"

$synth.SetOutputToWaveFile("{temp_wav}")

$synth.Speak($text)

$synth.Dispose()
'''

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            ps_script
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("[TTS ERREUR]")
        print(result.stderr)
        set_state("idle")
        return

    try:
        winsound.PlaySound(
            temp_wav,
            winsound.SND_FILENAME
        )
    except Exception as error:
        print(f"[AUDIO ERREUR] {error}")

    set_state("idle")

    try:
        os.remove(text_file)
    except OSError:
        pass

    try:
        os.remove(temp_wav)
    except OSError:
        pass


def listen(duration=5):
    print("\nParle maintenant...")

    sample_rate = 16000

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    audio = np.squeeze(audio)

    segments, info = model.transcribe(
        audio,
        language="fr"
    )

    text = " ".join(
        segment.text
        for segment in segments
    )

    return text.strip()


def main():
    print("==============================")
    print("       HIPOLITE V0.3")
    print("==============================")
    print("Voix : Claude 🇨🇦")
    print("Whisper : Small")
    print("Parle pendant 5 secondes.")
    print("Dis 'arrête', 'quitte' ou 'stop' pour arrêter.\n")

    while True:
        text = listen()

        if not text:
            print("Je n'ai rien entendu.")
            continue

        print(f"\nToi > {text}")

        normalized_text = normalize_text(text)

        stop_commands = [
            "arrete",
            "arreter",
            "arrete toi",
            "arrete-toi",
            "quitte",
            "quitter",
            "stop",
            "eteins toi",
            "eteins-toi",
            "ferme toi",
            "ferme-toi"
        ]

        should_stop = any(
            command in normalized_text
            for command in stop_commands
        )

        if should_stop:
            speak(
                "Bon, enfin. J'avais presque commencé "
                "à apprécier notre conversation."
            )
            print("\nHipolite arrêté.")
            break

        try:
            set_state("thinking")

            answer = ask_hipolite(text)
            speak(answer)

        except Exception as error:
            print(f"[ERREUR] {error}")
            set_state("idle")


# Lancement
if __name__ == "__main__":
    main()