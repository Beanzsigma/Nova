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
#def clear(canvas, canvas_img):
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
        a = a.point(lambda x:x *1)
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
load_font(getpath('Fonts/Necosmic-PersonalUse.otf'))
def welcome():
    canvas, canvasbg = gifbg()
    canvas.create_text(355, 184, text="Nova", font=('Necosmic Personal Use', 69), fill="#0a2e18", anchor="center")         #shadow cool ;)
    canvas.create_text(350, 180, text="Nova", font=('Necosmic Personal Use', 69), fill="#319950", anchor='center')
    continuebtn2 = canvas.create_text(353, 314, text="Continue", font=('Necosmic Personal Use', 28), fill="#0a2e18", anchor="center")
    continuebtn = canvas.create_text(350,310, text="Continue", font=('Necosmic Personal Use', 28), fill="#319950", anchor="center")
    def enter(e):
        canvas.itemconfig(continuebtn, fill="#0F4423")
        canvas.itemconfig(continuebtn2, fill="#000000")
    def leave(e):
        canvas.itemconfig(continuebtn, fill="#319950")
        canvas.itemconfig(continuebtn2, fill="#0a2e18")
    canvas.tag_bind(continuebtn, "<Enter>", enter)
    canvas.tag_bind(continuebtn, "<Leave>", leave)
    canvas.tag_bind(continuebtn2, '<Enter>', enter)
    canvas.tag_bind(continuebtn2, "<Leave>", leave)
welcome()














app.mainloop()