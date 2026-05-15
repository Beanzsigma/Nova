import customtkinter as ctk
import sounddevice as sd
import numpy as np
import threading 
import pytesseract
import queue
import pythoncom
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
from dotenv import load_dotenv
load_dotenv()
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
GROQkey = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQkey)
SYSTEM_PROMPT = """You are Nova, an AI desktop assistant for Windows.
The user will give you a natural language command.
Respond ONLY with a JSON object, no explanation, no markdown, nothing else.
Format:
{"actions": [{"action": "action_name", "value": "optional_value"}, ...]}
Available actions:
- set_volume (value: 0-100)
- mute_volume
- unmute_volume
- screenshot
- open_app (value: app name e.g. "spotify", "discord", "notepad")
- close_app (value: app name)
- open_url (value: full url e.g. "https://youtube.com")
- set_brightness (value: 0-100)
- type_text (value: text to type)
- press_key (value: key e.g. "ctrl+c", "alt+f4", "win+d")
- sleep_pc
- lock_pc
-speak_response (value: the response to say out loud, for questions and answers that don't need typing)
- unknown
-read_screen
You can chain multiple actions for complex tasks.
Example: "focus mode" → {"actions": [{"action": "mute_volume"}, {"action": "close_app", "value": "discord"}, {"action": "open_app", "value": "spotify"}]}
Example: "screenshot and open chrome" → {"actions": [{"action": "screenshot"}, {"action": "open_app", "value": "chrome"}]}
Example: "volume 50" → {"actions": [{"action": "set_volume", "value": 50}]}
Example: "what is the capital of France" → {"actions": [{"action": "speak_response", "value": "The capital of France is Paris"}]}
If the user asks a question, always use speak_response, never type_text
If the user says"write", "type", "draft", "compose" etc... use type_text
If it is a system command, use the correct action
unknow only if completely unrealted to everything above
When using speak_response, keep answers shor and direct. Just the answer, nothing else. But repeat the question asked, like when someone asks what 55 + 35 is, 
you have to say the answer to 55 + 35 is 90. Answer like that. You can give responses up to 10 WORDS -- HARD CAP. shorten thing if u need to, but it still needs to make sense. 
For any action that has visible effect(open_app, open_url, close_app) , include a speak_response action about that app. Like for youtube.com, you would just say "Opening Youtube" or something like that
Another thing. When announcing the read screen thing, don't say everything on the screen, just say the main things. Like if I ask what the answer to this problem is on my screen, just answer it. If I ask
what my screen is about, give a brief description.
WHEN USING read_screen:
describe only what is on the screen
max 10 words hard cap
no explanations, or thing like that. exeption for questions about screen like solving a problem
If OCR text is missing or incomplete, infer from context instead of saying unclear.
"""
def askgroq(user_text):
    try: 
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": SYSTEM_PROMPT}, {'role': "user", "content": user_text}], max_tokens=350)
        raw = response.choices[0].message.content.strip()
        raw=raw.replace("```json","").replace("```", "").strip()
        print(f"Groq: {raw}")
        parsed = json.loads(raw)
        return parsed
    except Exception as e:
        print(f"Groq sold bruuu: {e}")
        return {"actions": [{"action": 'unknown'}]}
import pyttsx3
def speak(text):
    def run():
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        pythoncom.CoUninitialize()
    threading.Thread(target=run, daemon=True).start()
def exectuteactions(actions, update_ui=None, user_text=""):
    hasreadscreen = any(a.get(""))
    pythoncom.CoInitialize()
    def announce(text):
        speak(text)
        if update_ui:
            app.after(0, lambda: update_ui(text))
    for a in actions:
        action = a.get("action")
        value = a.get("value")
        try:
            if action == "set_volume":
                vol = int(int(value) * 65535/100)
                subprocess.Popen([getpath("nir/nircmd.exe"), "setsysvolume", str(vol)])
            elif action == "mute_volume":
                subprocess.Popen([getpath("nir/nircmd.exe"), "mutesysvolume", "1"])
            elif action == "unmute_volume":
                subprocess.Popen([getpath("nir/nircmd.exe"), "mutesysvolume", "0"])
            elif action == "screenshot":
                import time
                picturefider = os.path.join(os.environ["USERPROFILE"], "Pictures")
                filename = f"screenshot_{int(time.time())}.png"
                fullpath = os.path.join(picturefider, filename)
                ss = pyautogui.screenshot()
                ss.save(fullpath)
                print(f"Ss here: {fullpath}")
                os.startfile(fullpath)
            elif action == "read_screen":
                import re
                ss = pyautogui.screenshot()
                ss = ss.convert("L")
                ss = ss.resize((ss.width*2, ss.height*2))
                text = pytesseract.image_to_string(ss, config="--oem 3 --psm 6 -c preserve_interword_spaces=1")
                text= text.strip()
                if not text.strip():
                    text = "No readable text found on screen"
                def summarizescreen():
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "You are given OCR text from a screen and a user question. Answer the question based on the screen content. Max 10 words."},
                                {"role": "user", "content": f"Screen text:\n{text[:1000]}\n\nUser question:\n{user_text}"}
                            ],
                            max_tokens=50
                        )
                        summary = response.choices[0].message.content.strip()
                        announce(summary)
                    except Exception as e:
                        announce(text[:60])
                threading.Thread(target=summarizescreen, daemon=True).start()
            elif action == "speak_response":
                speak(value)
                if update_ui:
                    update_ui(value)
            elif action =="open_app":
                subprocess.Popen(["start", value], shell=True)
                announce(f"Opening {value}")
            elif action == "close_app":
                subprocess.Popen(["taskkill", "/f", "/im", f"{value}.exe"], shell=True)
                announce(f"Closing {value}")
            elif action == "open_url":
                subprocess.Popen(["start", value], shell=True)
                announce("Opening website")
            elif action == "type_text":
                speak(value)
                pyautogui.write(value, interval=0.05)
            elif action == "press_key":
                pyautogui.hotkey(*value.split("+"))
            elif action == "lock_pc":
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif action == "sleep_pc":
                subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        except Exception as e:
            print(f"errorr {action}: {e}")
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
voiceque = queue.Queue()
recordingactive  = [False]
def listenvoice(q):
    samplerate = 16000
    chunks = []
    def callback(indata, frames, time, status):
        if recordingactive[0]:
            chunks.append(indata.copy())
    with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback):
        while recordingactive[0]:
            sd.sleep(100)
    if chunks:
        audiodata = np.concatenate(chunks, axis=0)
        r = sr.Recognizer()
        audio = sr.AudioData(audiodata.tobytes(), samplerate, 2)
        try:
            text= r.recognize_google(audio)
            q.put(text)
        except sr.UnknownValueError:
            q.put("__unclear__")
        except Exception as e:
            q.put(f"__error__{e}")
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
load_font(getpath("Fonts/PressStart2P-Regular.ttf"))
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
def showaigif(canvas, on_done, canvas_img, textinput_window):
    global after_id
    if after_id:
        app.after_cancel(after_id)
        after_id= None
    proc_frames = []
    proc_gif = Image.open(getpath("Images/GIFS/AI movement.gif"))
    from PIL import ImageDraw
    for frame in ImageSequence.Iterator(proc_gif):
        frame = frame.copy().convert("RGBA").resize((300, 300))
        mask = Image.new("L", (300, 300), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, 299, 299], radius=150, fill=255)
        frame.putalpha(mask)
        proc_frames.append(ImageTk.PhotoImage(frame))
    overlay1 = canvas.create_rectangle(0, 0, 700, 500, fill='black', stipple="gray50")
    overlay2 = canvas.create_rectangle(0, 0, 700, 500, fill='black', stipple='gray50')
    overlay3 = canvas.create_rectangle(0, 0, 700, 500, fill='black', stipple='gray50')
    procimg = canvas.create_image(350, 210, anchor='center')
    canvas._proc_frames = proc_frames
    proctextshdw = canvas.create_text(353, 390, text="Processing...", font=('Necosmic Personal Use', 18), fill="#666666", anchor='center')
    proctext = canvas.create_text(350, 387, text="Processing...", font=('Necosmic Personal Use', 18), fill="#FFFFFF", anchor='center')
    canvas.tag_raise(overlay1)
    canvas.tag_raise(overlay2)
    canvas.tag_raise(overlay3)
    canvas.tag_raise(procimg)
    canvas.tag_raise(proctextshdw)
    canvas.tag_raise(proctext)
    canvas.itemconfigure(textinput_window, state='hidden')
    procafter = [None]
    canvas._overlay_items = [overlay1, overlay2, overlay3, procimg, proctextshdw, proctext]
    def animate_proc(frame_index=0):
        canvas.itemconfig(procimg, image=proc_frames[frame_index])
        procafter[0] = canvas.after(50, animate_proc, (frame_index + 1) % len(proc_frames))
    animate_proc()
    def done():
        if procafter[0]:
            canvas.after_cancel(procafter[0])
        canvas.delete(overlay1)
        canvas.delete(overlay2)
        canvas.delete(overlay3)
        canvas.delete(procimg)
        canvas.delete(proctext)
        canvas.delete(proctextshdw)
        def animate(frame_index=0):
            global after_id
            canvas.itemconfig(canvas_img, image=frames[frame_index])
            after_id = app.after(20, animate, (frame_index+1) % len(frames))
        animate()
        canvas.itemconfigure(textinput_window, state="normal")
        on_done()
    canvas.after(5000, done)
def main(canvas, canvas_img):
    clear(canvas, canvas_img)
    lastfullresponse = [None]
    voiceresult = [None]
    textresult = [None]
    fullanswerready = [False]
    def getfullanswer(result):
        def run():
            response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": "Give me a full detailed answer to the user's question. Speak naturally, no lists or markdown"},
                                                       {"role": "user", "content": result} ], max_tokens=350)
            full = response.choices[0].message.content.strip()
            speak(full)
        threading.Thread(target=run, daemon=True).start()
    normalimg = Image.open(getpath("Images/GIFS/mic2.png")).resize((125, 125))
    newnormalimg = normalimg.point(lambda p:min(255, int(p * 1)))
    hoverimg = newnormalimg.point(lambda p:min (255, int(p*1/1.6)))
    recordingimg = Image.open(getpath("Images/GIFS/mic5.png")).resize((125,125))
    canvas.filepic_img = ImageTk.PhotoImage(newnormalimg)
    canvas.filepic_img_hover = ImageTk.PhotoImage(hoverimg)
    canvas.filepic_img_recording = ImageTk.PhotoImage(recordingimg)
    imgitem = canvas.create_image(80, 193, image=canvas.filepic_img, anchor='center')
    normalimg2 = Image.open(getpath('Images/GIFS/check.png')).resize((40, 40))
    newnormalimg2 = normalimg2.point(lambda p:min(255, int(p *1)))
    hoverimg2 = newnormalimg2.point(lambda p:min (255, int(p*1/1.6)))
    canvas.filepic_img2 = ImageTk.PhotoImage(newnormalimg2)
    canvas.filepic_img_hover2 = ImageTk.PhotoImage(hoverimg2)
    imgitem2 = canvas.create_image(654, 148, image=canvas.filepic_img2, anchor='center')
    recording = [False]
    rectextshdw = canvas.create_text(86, 266, text="", font=('Necosmic Personal Use', 11), fill="#0a2e18")
    rectext = canvas.create_text(83, 263, text="", font=('Necosmic Personal Use', 11), fill="#319950", anchor="center")
    textinput = ctk.CTkEntry(app, width=252, height=35, fg_color="black", border_color="#319950", font=('Press Start 2P', 13))
    textinput_window = canvas.create_window(495, 150, window=textinput, anchor='center')
    responsetext_shdw = canvas.create_text(523, 175, text="", font=("Press Start 2P", 13), fill="#0a2e18", anchor="n", width=290)
    responsetext= canvas.create_text(520, 172, text="", font=("Press Start 2P", 13), fill="#319950", anchor="n", width=290)
    leftresponseshdw = canvas.create_text(237, 128, text="", font=('Press Start 2P', 13), fill="#0a2e18", anchor='n', width=220)
    lefresponse = canvas.create_text(234, 125, text="", font=("Press Start 2P", 13), fill="#319950", anchor='n', width=220)
    fullresbutton1shdw = canvas.create_text(244, 259, text="Full Answer", font=('Necosmic Personal use', 12), fill="#0a2e18")
    fullresbutton1 = canvas.create_text(241, 256, text="Full Answer", font=("Necosmic Personal use", 12), fill="#319950")
    fullresbutton2shdw = canvas.create_text(524, 269, text="Full Answer", font=("Necosmic Personal use", 12), fill="#0a2e18")
    fullresbutton2 = canvas.create_text(521, 266, text="Full Answer", font=("Necosmic Personal use", 12), fill="#319950")
    rounded_rect(canvas, 448, 255, 593, 280, r=9, color="#319950", width=3)
    rounded_rect(canvas, 165, 244, 315, 270, r=9, color="#319950", width=3)
    def enter1(e):
        canvas.itemconfig(fullresbutton1,fill="#0F4423" )
        canvas.itemconfig(fullresbutton1shdw, fill="#0E0D0D")
    def leave1(e):
        canvas.itemconfig(fullresbutton1, fill="#319950")
        canvas.itemconfig(fullresbutton1shdw, fill='#0a2e18')
    canvas.tag_bind(fullresbutton1, "<Enter>", enter1)
    canvas.tag_bind(fullresbutton1shdw, "<Enter>", enter1)
    canvas.tag_bind(fullresbutton1shdw, "<Leave>", leave1)
    canvas.tag_bind(fullresbutton1, "<Leave>", leave1)
    def enter2(e):
        canvas.itemconfig(fullresbutton2, fill="#0F4423")
        canvas.itemconfig(fullresbutton2shdw, fill="#0E0D0D")
    def leave2(e):
        canvas.itemconfig(fullresbutton2, fill="#319950")
        canvas.itemconfig(fullresbutton2shdw, fill="#0a2e18")
    def fullanswerclickvoice(e):
        if not voiceresult[0]:
            return
        result = voiceresult[0]
        def on_done():
            def run():
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{'role': 'system', "content": "Give me a full natural answer, no lists or markdown. Also, do NOT talk for too long, or get off track. Give a good answer, that's it."},
                                                                                                     {'role': "user", 'content': result}], max_tokens=350) 
                full = response.choices[0].message.content.strip()
                speak(full)
            threading.Thread(target=run, daemon=True).start()
        showaigif(canvas, on_done, canvas_img, textinput_window)
    def fullanswerclicktext(e):
        if not textresult[0]:
            return
        result = textresult[0]
        def on_done():
            def run():
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{'role': 'system', "content": "Give me a full natural answer, no lists or markdown. Also, do NOT talk for too long, or get off track. Give a good answer, that's it."},
                                                                                                     {'role': "user", 'content': result}], max_tokens=350) 
                full = response.choices[0].message.content.strip()
                speak(full)
            threading.Thread(target=run, daemon=True).start()
        showaigif(canvas, on_done, canvas_img, textinput_window)
    canvas.tag_bind(fullresbutton2, "<Enter>", enter2)
    canvas.tag_bind(fullresbutton2shdw, "<Enter>", enter2)
    canvas.tag_bind(fullresbutton2, "<Leave>", leave2)
    canvas.tag_bind(fullresbutton2shdw, "<Leave>", leave2)
    canvas.tag_bind(fullresbutton1, "<Button-1>", fullanswerclickvoice)
    canvas.tag_bind(fullresbutton1shdw, "<Button-1>", fullanswerclickvoice)
    canvas.tag_bind(fullresbutton2, "<Button-1>", fullanswerclicktext)
    canvas.tag_bind(fullresbutton2shdw, "<Button-1>", fullanswerclicktext)
    def checkvoice(canvas, rectext, rectextshdw, imgitem, recording):
        try:
            result = voiceque.get_nowait()
            voiceresult[0] = result 
            fullanswerready[0] = True
            recording[0] = False
            canvas.itemconfig(imgitem, image=canvas.filepic_img)
            def on_done():
                canvas.itemconfig(rectext, text="Processed")
                canvas.itemconfig(rectextshdw, text="Processed")
                def run_groq():
                    parsed = askgroq(result)
                    actions = parsed.get("actions", [])
                    if actions and actions[0].get("action") == "unknown":
                        app.after(0, lambda: canvas.itemconfig(lefresponse, text="I don't understand"))
                        app.after(0, lambda: canvas.itemconfig(leftresponseshdw, text="I don't understand"))
                    def update_ui (text):
                        app.after(0, lambda: canvas.itemconfig(leftresponseshdw, text=text))
                        app.after(0, lambda: canvas.itemconfig(lefresponse, text=text))
                    exectuteactions(actions, update_ui, result)
                threading.Thread(target=run_groq, daemon=True).start()
            showaigif(canvas, on_done, canvas_img, textinput_window)
        except queue.Empty:
            canvas.after(100, lambda: checkvoice(canvas, rectext, rectextshdw, imgitem, recording))
    def togglerec(e):
        if not recording[0]:
            recording[0] = True
            recordingactive[0] = True
            canvas.itemconfig(imgitem, image=canvas.filepic_img_recording)
            canvas.itemconfig(rectext, text="Recording...")
            canvas.itemconfig(rectextshdw, text="Recording...")
            t = threading.Thread(target=listenvoice, args=(voiceque, ),  daemon=True)
            t.start()
            canvas.after(100, lambda: checkvoice(canvas, rectext, rectextshdw, imgitem, recording))
        else:
            recording[0] = False
            recordingactive[0] = False
            canvas.itemconfig(rectext, text="Processing...")
            canvas.itemconfig(rectextshdw, text="Processing...")
    def submittext(e):
        text = textinput.get().strip()
        if text:
            textresult[0] = text
            textinput.delete(0, 'end')
            def on_done():
                def run_groq():
                    parsed = askgroq(text)
                    actions = parsed.get("actions", [])
                    if actions and actions[0].get("action") == "unknown":
                        msg = "I don't understand"
                        app.after(0, lambda: canvas.itemconfig(responsetext, text=msg))
                        app.after(0, lambda: canvas.itemconfig(responsetext_shdw, text=msg))
                    def update_ui(t):
                        app.after(0, lambda: canvas.itemconfig(responsetext, text=t))
                        app.after(0, lambda: canvas.itemconfig(responsetext_shdw, text=t))
                    exectuteactions(actions, update_ui, text)
                threading.Thread(target=run_groq, daemon=True).start()
            showaigif(canvas, on_done, canvas_img, textinput_window)
    canvas.tag_bind(imgitem, "<Button-1>", togglerec)
    canvas.tag_bind(imgitem, "<Enter>", lambda e: canvas.itemconfig(imgitem, image=canvas.filepic_img_hover) if not recording[0] else None)
    canvas.tag_bind(imgitem, "<Leave>", lambda e: canvas.itemconfig(imgitem, image=canvas.filepic_img) if not recording [0] else None)
    canvas.tag_bind(imgitem2, "<Button-1>", submittext)
    canvas.tag_bind(imgitem2, "<Enter>", lambda e: canvas.itemconfig(imgitem2, image=canvas.filepic_img_hover2))
    canvas.tag_bind(imgitem2,"<Leave>", lambda e: canvas.itemconfig(imgitem2, image=canvas.filepic_img2) )
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
        if hasattr(canvas, '_overlay_items'):
            for item in canvas._overlay_items:
                canvas.tag_raise(item)
        after_id = app.after(20, animate, (frame_index + 1) % len(frames))
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