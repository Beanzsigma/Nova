import customtkinter as ctk
import threading 
import queue
after_id = None
from groq import Groq
import json 
import speech_recognition as sr
import subprocess
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pydantic import BaseModel
from typing import Optional
from tkinter import Canvas, Text
from PIL import Image, ImageSequence, ImageTk
import os
import sys
ctk.set_appearance_mode('dark')
app=ctk.CTk()
app.resizable(False, False)
app.title("Nova")
app.geometry('700x500')
def getpath(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
FR_PRIVATE = 0x10
def load_font(font_path):
    windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
app.iconbitmap(getpath("Images/GIFS/logo.ico"))
def gifbg():
    global after_id 
    if after_id:
        app.after_cancel(after_id)
    for widget in app.winfo_children():
        widget.destroy()
    frames  = []
    gif = Image.open(getpath('Images/GIFS/greenglow.gif'))
    for frame in ImageSequence.Iterator(gif):
        frame = frame.copy().convert('RGBA')
        r, g, b, a = frame.split()
        a = a.point(lambda x:x *4)
        frame.putalpha(a)
        frames.append(ImageTk.PhotoImage(frame.resize((700, 500))))
    canvas = Canvas(app, width=700, height=500, highlightthickness=0, bd=0, bg="black")
    canvas.place(x=0, y=0)
    canvasbg = canvas.create_image(0, 0, anchor="nw")
    def animate(frame_index=0):
        global after_id
        canvas.itemconfig(canvasbg, image=frames[frame_index])
        canvas._frames = frames
        after_id = app.after(20, animate, (frame_index+1) % len(frames))
    animate()
    return canvas, canvasbg
def welcome():
    canvas, canvasbg = gifbg()
    canvas.create_text(350, 180, text="Nova", font=('Arial', 38), fill="#2e412d", anchor='center')
welcome()














app.mainloop()