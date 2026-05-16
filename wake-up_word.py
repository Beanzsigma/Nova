import speech_recognition as sr
import sounddevice as sd
import time
import io
import wave
import numpy as np
recognizer = sr.Recognizer()
wakeword = "nova"
cooldown = 3
last_trigger = 0
samplerate= 16000
duration = 1
print("im listening")
while True:
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(samplerate)
            wf.writeframes(recording.tobytes())
        wav_buffer.seek(0)
        with sr.AudioFile(wav_buffer) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio).lower()
        print("heard it", text)
        current = time.time()
        if wakeword in text and current - last_trigger >cooldown:
            last_trigger = current
            print('detected word')
    except sr.UnknownValueError:
        pass
    except Exception as e:
        print(e)