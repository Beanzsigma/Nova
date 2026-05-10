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
def clear(canvas, canvas_img):
    for item in canvas.find_all():
        if item != canvas_img:
            canvas.delete(item)
def rounded_rect(canvas, x1, y1, x2, y2, r=20, color="#0F4423", width=2):
    arc_kwargs = {"outline": color, "width": width}
    line_kwargs = {"fill": color, "width": width}
    canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", **arc_kwargs)
    canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", **arc_kwargs)
    canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", **arc_kwargs)          
    canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", **arc_kwargs)
    canvas.create_line(x1+r, y1, x2-r, y1, **line_kwargs)
    canvas.create_line(x1+r, y2, x2-r, y2, **line_kwargs)
    canvas.create_line(x1, y1+r, x1, y2-r, **line_kwargs)
    canvas.create_line(x2, y1+r, x2, y2-r, **line_kwargs)
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
frames = []
gif = Image.open(getpath("Images/GIFS/greenglow.gif"))
for frame in ImageSequence.Iterator(gif):
        frame = frame.copy().convert('RGBA')
        r, g, b, a = frame.split()
        a = a.point(lambda x:x *1)
        frame.putalpha(a)
        frames.append(ImageTk.PhotoImage(frame.resize((700, 500))))
def gifbg():
    global after_id 
    if after_id:
        app.after_cancel(after_id)
    for widget in app.winfo_children():
        widget.destroy()
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
def fadein(canvas):
    overlay = canvas.create_rectangle(0, 0, 700, 500, fill='black', state='normal')
    stipples = ["gray75", "gray50", "gray25", "gray12"]
    step= [0]
    alpha=[1.0]
    def fade():
        if step[0] <len(stipples):
            canvas.itemconfig(overlay, stipple=stipples[step[0]])
            step[0] += 1
            app.after(40, fade)
        else:
            canvas.delete(overlay)
    fade()
def main(canvas, canvas_img):
    clear(canvas, canvas_img)
    normalimg = Image.open(getpath("Images/GIFS/mic2.png")).resize((125, 125))
    newnormalimg = normalimg.point(lambda p:min(255, int(p * 1)))
    hoverimg = newnormalimg.point(lambda p:min (255, int(p*1/1.6)))
    recordingimg = Image.open(getpath("Images/GIFS/mic5.png")).resize((125,125))
    canvas.filepic_img = ImageTk.PhotoImage(newnormalimg)
    canvas.filepic_img_hover = ImageTk.PhotoImage(hoverimg)
    canvas.filepic_img_recording = ImageTk.PhotoImage(recordingimg)
    recording = [False]
    imgitem = canvas.create_image(80, 193, image=canvas.filepic_img, anchor='center')
    rectextshdw = canvas.create_text(86, 266, text="", font=('Necosmic Personal Use', 11), fill="#0a2e18")
    rectext = canvas.create_text(83, 263, text="", font=('Necosmic Personal Use', 11), fill="#319950", anchor="center")
    def togglerec(e):
        if not recording[0]:
            recording[0] = True
            canvas.itemconfig(imgitem, image=canvas.filepic_img_recording)
            canvas.itemconfig(rectext, text="Recording...")
            canvas.itemconfig(rectextshdw, text="Recording...")
        else:
            recording[0] = False
            canvas.itemconfig(imgitem, image=canvas.filepic_img)
            canvas.itemconfig(rectext, text="")
            canvas.itemconfig(rectextshdw, text="")
    canvas.tag_bind(imgitem, "<Button-1>", togglerec)
    canvas.tag_bind(imgitem, "<Enter>", lambda e: canvas.itemconfig(imgitem, image=canvas.filepic_img_hover) if not recording[0] else None)
    canvas.tag_bind(imgitem, "<Leave>", lambda e: canvas.itemconfig(imgitem, image=canvas.filepic_img) if not recording [0] else None)
    canvas.create_text(13, 13, text="Your words", font=('Necosmic Personal Use', 17), fill="#0a2e18", anchor='nw')
    canvas.create_text(10, 10, text="Your words", font=('Necosmic Personal Use', 17), fill="#319950", anchor="nw")
    canvas.create_text(693, 13, text="Your PC", font=('Necosmic Personal Use', 17), fill="#0a2e18", anchor="ne")
    canvas.create_text(690, 10, text="Your PC", font=('Necosmic Personal Use', 17), fill="#319950", anchor="ne")
    canvas.create_text(355, 54, text="Nova", font=('Necosmic Personal Use', 38), fill="#0a2e18", anchor='center')
    canvas.create_text(350, 50, text="Nova", font=('Necosmic Personal Use', 38), fill="#319950", anchor='center')
    canvas.create_text(537, 483, text="Powered by Groq", font=('Necosmic Personal Use', 10), fill="#319950", anchor='nw')
    rounded_rect(canvas, 13, 308, 203, 478, r=9, color="#0a2e18", width=3)
    rounded_rect(canvas, 10, 305, 200, 475, r=9, color="#319950", width=3)
    canvas.create_text(103, 328, text="History", font=('Necosmic Personal Use', 16),fill="#0a2e18", anchor='center' )
    canvas.create_text(100, 325, text="History", font=('Necosmic Personal Use', 16), fill="#319950", anchor="center")
    rounded_rect(canvas, 223, 308, 690, 478, r=9, color="#0a2e18", width=3)
    rounded_rect(canvas, 220, 305, 687, 475, r=9, color="#319950")
    canvas.create_text(453, 328, text="Quick Actions", font=('Necosmic Personal Use', 17), fill="#0a2e18", anchor='center')
    canvas.create_text( 450, 325, text="Quick Actions", font=('Necosmic Personal Use', 17), fill="#319950", anchor='center')
    rounded_rect(canvas, 13, 88, 343, 293, r=9, color="#0a2e18")
    rounded_rect(canvas, 10, 85, 340, 290, r=9, color="#319950")
    rounded_rect(canvas, 353, 88, 693, 293, r=9, color="#0a2e18")
    rounded_rect(canvas, 350, 85, 690, 290, r=9, color="#319950")
    canvas.create_text(178, 103, text="Voice Input", font=('Necosmic Personal Use', 16), fill="#0a2e18", anchor='center')
    canvas.create_text(175, 100, text="Voice Input", font=("Necosmic Personal Use", 16), fill="#319950", anchor='center')
    canvas.create_text(525, 103, text="Text Input", font=('Necosmic Personal Use', 16), fill="#0a2e18", anchor='center')
    canvas.create_text(523, 100, text="Text Input", font=('Necosmic Personal Use', 16), fill="#319950", anchor="center")
    def animate(frame_index=0):
        global after_id
        canvas.itemconfig(canvas_img, image=frames[frame_index])
        after_id = app.after(20, animate, (frame_index+1) % len(frames))
    animate()
    fadein(canvas)
def fademain(canvas, canvasbg):
    global after_id
    if after_id:
        app.after_cancel(after_id)
        after_id= None
    overlay = canvas.create_rectangle(0, 0, 700, 500, fill="black", stipple="gray75", state="hidden")
    items = [i for i in canvas.find_all() if i != canvasbg and i != overlay]
    stipples = ["gray75", "gray50", 'gray25', '']
    alpha = [1.0]
    def step():
        if alpha[0] > 0.2:
            alpha[0] -= 0.1
            for item in items:
                try:
                    current= canvas.itemcget(item, "fill")
                    if current and current !="":
                        r = int(int(current[1:3], 16)  * alpha[0])
                        g = int(int(current[3:5], 16) * alpha[0])
                        b = int(int(current[5:7], 16) * alpha[0])
                        canvas.itemconfig(item, fill=f"#{r:02x}{g:02x}{b:02x}")
                except:
                    pass
            step_num = int((1 - alpha[0]) / 0.25)
            stipple = stipples[min(step_num, 3)]
            canvas.itemconfig(overlay, state='normal', stipple=stipple)
            app.after(20, step)
        else:
            canvas.delete(overlay)
            main(canvas, canvasbg)
    step()
def welcome():
    canvas, canvasbg = gifbg()
    canvas.create_text(355, 184, text="Nova", font=('Necosmic Personal Use', 69), fill="#0a2e18", anchor="center")         #shadow cool ;)
    canvas.create_text(350, 180, text="Nova", font=('Necosmic Personal Use', 69), fill="#319950", anchor='center')
    rounded_rect(canvas, 232, 370, 472, 410, r=9, color="#0F4423", width=3  )
    continuebtn2 = canvas.create_text(353, 394, text="Continue", font=('Necosmic Personal Use', 28), fill="#0a2e18", anchor="center")
    continuebtn = canvas.create_text(350,390, text="Continue", font=('Necosmic Personal Use', 28), fill="#319950", anchor="center")
    canvas.create_text(353, 293, text="Where Natural language", font=('Necosmic Personal Use', 13), fill="#0a2e18", anchor='center')
    canvas.create_text(350, 290, text="Where Natural language", font=('Necosmic Personal Use', 13), fill="#319950", anchor="center")
    canvas.create_text(353, 309, text="meets real control", font=('Necosmic Personal Use', 13), fill="#0a2e18", anchor='center')
    canvas.create_text(350, 306, text="meets real control", font=('Necosmic Personal Use', 13), fill="#319950", anchor='center')
    def enter(e):
        canvas.itemconfig(continuebtn, fill="#0F4423")
        canvas.itemconfig(continuebtn2, fill="#0E0D0D")
    def leave(e):
        canvas.itemconfig(continuebtn, fill="#319950")
        canvas.itemconfig(continuebtn2, fill="#0a2e18")
    canvas.tag_bind(continuebtn, "<Enter>", enter)
    canvas.tag_bind(continuebtn, "<Leave>", leave)
    canvas.tag_bind(continuebtn2, '<Enter>', enter)
    canvas.tag_bind(continuebtn2, "<Leave>", leave)
    canvas.tag_bind(continuebtn, "<Button-1>", lambda e: fademain(canvas, canvasbg))
    canvas.tag_bind(continuebtn2, "<Button-1>", lambda e: fademain(canvas, canvasbg))






welcome()
app.mainloop()