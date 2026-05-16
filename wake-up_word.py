from openwakeword.model import Model
import sounddevice as sd
import numpy as np
model = Model()
samplerate = 16000
chunksize = 1280
lastrigger = 0
cooldown = 4
