from openwakeword.model import Model
import sounddevice as sd
import time
import numpy as np
model = Model()
samplerate = 16000
chunksize = 1280
lastrigger = 0
cooldown = 4
def callback(indata, frames, time_info, status):
    global lastrigger
    audio = indata.flatten().astype(np.int16)
    prediction = model.predict(audio)
    for wakeword, score in prediction.items():
        if score > 0.5:
            current = time.time()
            if current - lastrigger >cooldown:
                lastrigger = current
                print("detect")
stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", blocksize=chunksize, callback=callback)
with stream:
    print('i hear u bru')
    while True:
        sd.sleep(1000)

