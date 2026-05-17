import speech_recognition as sr
import sounddevice as sd
from Nova import askgroq, exectuteactions
import time
import io
import wave
import numpy as np
recognizer = sr.Recognizer()
wakeword = "nova"
cooldown = 3
last_trigger = 0
samplerate= 16000
duration = 3
print("im listening")
while True:
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
        sd.wait()
        print(np.max(recording))
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
        if "nova" in text and current - last_trigger >cooldown:
            last_trigger = current
            print('detected word')
            print("Listening for command")
            commandrecording = sd.rec(int(5*samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
            wav_buffer2 = io.BytesIO()
            with wave.open(wav_buffer2, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(commandrecording.tobytes())
            wav_buffer2.seek(0)
            with sr.AudioFile(wav_buffer2) as source2:
                commandaudio = recognizer.record(source2)
            try:
                commandtext = recognizer.recognize_google(commandaudio).lower()
                print("command:", commandtext)
            except Exception as e:
                print("Command STT error:", e)
                continue
            parsed = askgroq(commandtext)
            print('groq:', parsed)
            actions = parsed.get("actions", [{"action": "unknown"}])
            print("actions:", actions)
            if not actions or actions[0].get("action") == "unknown":
                print("not valid")
                continue
            print("exectuing actions")
            exectuteactions(actions)
    except sr.UnknownValueError:
        print("STT: could not understand")
        continue
        print("heard it:", text)
    except Exception as e:
        print("stt erro:", e)