import customtkinter as ctk
import sounddevice as sd
import numpy as np
import threading 
import pytesseract
import time
import base64
from io import BytesIO
from difflib import SequenceMatcher
import queue
import time
import easyocr
import pythoncom
voiceenabled = [True]
wakewordenabled = [True]
tts_rate = [50]
after_id =None
active_ui = {"canvas": None,"canvas_img": None,"textinput_window": None}
from openai import OpenAI
import base64
from io import BytesIO
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
import cv2
import os
import sys
from dotenv import load_dotenv
load_dotenv()
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)
reader = easyocr.Reader(['en'])
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
AIkey = os.environ.get("HACKCLUB_AI_KEY")
client = OpenAI(api_key=AIkey,base_url="https://ai.hackclub.com/proxy/v1")
COMMAND_MODEL = "openai/gpt-4.1"
VISION_MODEL = "openai/gpt-4.1"
SYSTEM_PROMPT = """You are Nova, an AI desktop assistant for Windows.
Respond ONLY with a valid JSON object.
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
- wait (value: seconds to pause before next action)
-read_screen
- move_mouse (value: {"x": number, "y": number, "duration": optional seconds})
- move_mouse_relative (value: {"x": number, "y": number, "duration": optional seconds})
- click_mouse (value: "left", "right", "middle", or optional)
- double_click_mouse
- scroll_mouse (value: positive scrolls up, negative scrolls down)
- screen_move (value: description of thing on screen)
- screen_click (value: description of thing on screen)
- screen_double_click (value: description of thing on screen)
- screen_right_click (value: description of thing on screen)
You can chain multiple actions for complex tasks.
Example: "focus mode" → {"actions": [{"action": "mute_volume"}, {"action": "close_app", "value": "discord"}, {"action": "open_app", "value": "spotify"}]}
Example: "screenshot and open chrome" → {"actions": [{"action": "screenshot"}, {"action": "open_app", "value": "chrome"}]}
Example: "volume 50" → {"actions": [{"action": "set_volume", "value": 50}]}
Example: "what is the capital of France" → {"actions": [{"action": "speak_response", "value": "The capital of France is Paris"}]}
If the user asks a question, always use speak_response, never type_text
If the user says"write", "type", "draft", "compose" etc... use type_text
If it is a system command, use the correct action
For mouse movement:
- "move mouse to 500 300" do {"actions": [{"action": "move_mouse", "value": {"x": 500, "y": 300}}]}
- "move mouse right 100" do {"actions": [{"action": "move_mouse_relative", "value": {"x": 100, "y": 0}}]}
- "move mouse left 100" do {"actions": [{"action": "move_mouse_relative", "value": {"x": -100, "y": 0}}]}
-  "click" do {"actions": [{"action": "click_mouse", "value": "left"}]}
- "right_click" do {"actions": [{"action": "click_mouse", "value": "right"}]}
- "scroll down" do {"actions": [{"action": "scroll_mouse", "value": -5}]}
For screen vision:
- "click the search bar" do {"actions": [{"action": "screen_click", "value": "search bar"}]}
- "move to the blue button" do {"actions": [{"action": "screen_move", "value": "blue button"}]}
- "double click the Chrome icon" do {"actions": [{"action": "screen_double_click", "value": "Chrome icon"}]}
- "right click the file named Nova.py" do {"actions": [{"action": "screen_right_click", "value": "file named Nova.py"}]}
If the user describes something visible on screen and wants mouse interaction, use screen actions, not coordinate actions.
unknow only if completely unrealted to everything above
When using speak_response, keep answers shor and direct. Just the answer, nothing else. But repeat the question asked, like when someone asks what 55 + 35 is, 
you have to say the answer to 55 + 35 is 90. Answer like that. You can give responses up to 8 WORDS -- HARD CAP. shorten thing if u need to, but it still needs to make sense.  IF USER ASKS FOR A FORMULA OR SOMETHING, SAY ANSWER TOO LONG, AND PUT THE TEXT ANSWER TOO LONG. SAY ANSWER TOO LONG, PRESS FULL ANSWER.
Only use speak_response when the user explicitly asks for spoken output.
CRITICAL: Never use speak_response to narrate what you are doing. 
speak_response is ONLY for answering direct questions from the user.
If the user says "open youtube and play a video", do NOT add speak_response saying "Opening YouTube" or "Playing a video". Just do it silently.
speak_response = answering questions ONLY. Nothing else.
Another thing. When announcing the read screen thing, don't say everything on the screen, just say the main things. Like if I ask what the answer to this problem is on my screen, just answer it. If I ask
what my screen is about, give a brief description.
WHEN USING read_screen:
If user asks WHAT IS ON SCREEN → max 8 words
If user asks QUESTION ABOUT SCREEN → normal answer allowed
no explanations, or thing like that. exeption for questions about screen like solving a problem
If OCR text is missing or incomplete, infer from context instead of saying unclear.
ALSO, when using open_app, make sure the start of the app name is capitalized and everything. 
Another thing, u can do multiple commands, for example the user asks to go to google, use the mouse to go to settings, press it, and scroll down to whatever. 
Additionally, when pressing thing like moving ur mouse to a specific point, make sure it is accurate, and exact.
Return:
{
 "found": true/false,
 "confidence": 0-1,
 "x": number,
 "y": number
}
Only return coordinates if confidence > 0.75.
When doing multi step tasks, make sure to wait to load and stuff, just take that into account, and make sure to follow user's commands.
IMPORTANT: Only use read_screen when the user EXPLICITLY asks "what is on my screen", "what can I do", "what do I see", etc. 
DO NOT use read_screen for action sequences. For example, if user says "open youtube and play a random video", just:
1. open youtube
2. wait a bit
3. click a likely video location (use screen_click to find a thumbnail or video title)
Do NOT add read_screen unless the user asks about the screen content.
Sometimes the user's input isn't describing text, like actually get the meaning of what the user's trying to say, and run commands. Like the youtube video thing, dont click the youtube text, but actually understand.
If the user says "click", "select", "open", or "choose", ALWAYS use screen_click or click_mouse.
Never respond with screen description or speak_response unless explicitly asked.
ALSO WHEN SEARCHING STUFF AND THINGS LIKE THAT WHERE THE USER ASKS YOU TO SEARCH SOMETHING UP BY CLICKING THE SEARCH BAR, MAKE SURE TO PRESS ENTER WHEN YOUR DONE.
- GOOGLE SEARCH BAR IS Ask Google or Type a URL and Opera GX search bar is Enter search or web address. So use this when the user asks to click the search bar or something.
NEVER GO OVER 8 WORDS, AND IF YOU THINK IT'S NOT POSSIBLE TO FIT THE ANSWER IN 8 WORDS, SAY ANSWER TOO LONG, PRESS FULL ANSWER. DON"T COMBINE WORDS WITH SLASHES AND STUFF LIKE THAT, IF YOU HAVE TO, JUST SAY ANSWER TOO LONG, PRESS FULL ANSWER.
"""
SETTINGSFILE = "nova_settings.json"
def savesettings():
    data = {"voiceenabled": voiceenabled[0],"wakewordenabled": wakewordenabled[0],"tts_rate": tts_rate[0]}
    with open(SETTINGSFILE, "w") as f:
        json.dump(data, f, indent=4)
def loadsettings():
    try:
        with open(SETTINGSFILE, "r") as f:
            data = json.load(f)
        voiceenabled[0] = data.get("voiceenabled", True)
        wakewordenabled[0] = data.get("wakewordenabled", True)
        tts_rate[0] = max(1, min(100, int(data.get("tts_rate", 50))))
    except:
        savesettings()
loadsettings()
def askgroq(user_text):
    try:
        response = client.chat.completions.create(model= COMMAND_MODEL, messages=[{"role": "system", "content": SYSTEM_PROMPT},{"role": "user", "content": user_text}], response_format=
                                                  {"type": "json_object"}, max_tokens=450)
        raw = response.choices[0].message.content.strip()
        print(f"AI: {raw}")
        parsed = json.loads(raw)
        return parsed
    except Exception as e:
        print(f"Ai erurrrrrrrrr: {e}")
        return {"actions": [{"action": "unknown"}]}
def findtextscreen(target_text):
    ss = pyautogui.screenshot()
    ss = ss.convert("RGB")
    img = np.array(ss)
    results = reader.readtext(img)
    from difflib import SequenceMatcher
    best = None
    best_score = 0
    for (bbox, text, prob) in results:
        target_lower = target_text.lower()
        ocr_lower = text.lower()

        if target_lower in ocr_lower or ocr_lower in target_lower:
            score = 1.0
        else:
            score = SequenceMatcher(None, target_lower, ocr_lower).ratio()
        print(f"Comparing '{target_text}' with '{text}' = {score}")
        if score > best_score:
            best_score = score
            best = (bbox, text)
    if best and best_score > 0.9:
        bbox, found_text = best
        top_left = bbox[0]
        bottom_right = bbox[2]
        x = int((top_left[0] + bottom_right[0]) / 2)
        y = int((top_left[1] + bottom_right[1]) / 2)
        print(f"Matched: {found_text} ({best_score}) at {x}, {y}")
        return x, y
    return None
import pyttsx3
def find_all_text(target_text):
    ss = pyautogui.screenshot()
    img = np.array(ss)
    results = reader.readtext(img)
    matches = []
    for (bbox, text, prob) in results:
        score = SequenceMatcher(None, target_text.lower(), text.lower()).ratio()
        if score > 0.6:
            top_left = bbox[0]
            bottom_right = bbox[2]
            x = int((top_left[0] + bottom_right[0]) / 2)
            y = int((top_left[1] + bottom_right[1]) / 2)
            matches.append((score, x, y, text))
    matches.sort(key=lambda x: x[2])
    return matches
def parse_index(value):
    words = value.lower()
    if 'first' in words or '1st' in words:
        return 0
    if "second" in words or "2nd" in words:
        return 1
    if "third" in words or "3rd" in words:
        return 2
    return 0
def speak(text):
    if not voiceenabled[0]:
        return
    def run():
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        engine.setProperty('rate', 75 + int(tts_rate[0] * 2))
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        pythoncom.CoUninitialize()
    threading.Thread(target=run, daemon=True).start()
def open_app(value, announce):
    app_name = str(value).strip().lower()
    discord_update = os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe")
    app_map = {  "steam": "steam://open/main", "discord": ["discord://", discord_update], "notepad": "notepad.exe", "calculator": "calc.exe", "chrome": "chrome","spotify": "spotify",}
    target = app_map.get(app_name, value)
    try:
        if app_name == "discord":
            try:
                os.startfile(target[0])
            except:
                subprocess.Popen([target[1], "--processStart", "Discord.exe"])
        elif isinstance(target, str) and "://" in target:
            os.startfile(target)
        elif isinstance(target, str) and target.endswith(".exe"):
            subprocess.Popen([target])
        else:
            subprocess.Popen(f'start "" "{target}"', shell=True)
        announce(f"Opening {app_name}")
    except Exception as e:
        print(f"open_app error for {app_name}: {e}")
        announce(f"Could not open {app_name}")
def clamp_mouse_position(x, y):
    screen_w, screen_h = pyautogui.size()
    x = max(0, min(int(x), screen_w - 1))
    y= max(0, min(int(y), screen_h-1))
    return x, y
def get_dpi_scale():
    try:
        from ctypes import windll
        dc = windll.user32.GetDC(0)
        dpi = windll.gdi32.GetDeviceCaps(dc, 88)
        windll.user32.ReleaseDC(0, dc)
        return dpi/ 96.0
    except:
        return 1.0
def get_primary_monitor_bounds():
    """Get the bounds of the primary monitor using Windows API"""
    try:
        from ctypes import windll
        hdc = windll.user32.GetDC(0)
        screen_w = windll.gdi32.GetDeviceCaps(hdc, 8)  
        screen_h = windll.gdi32.GetDeviceCaps(hdc, 10)  
        windll.user32.ReleaseDC(0, hdc)
        return 0, 0, screen_w, screen_h
    except:
        w, h = pyautogui.size()
        return 0, 0, w, h
def filter_button_from_matches(matches, target_text, ss):
    """Given multiple text matches, ask AI which one is the clickable button"""
    if len(matches) <= 1:
        return matches
    buffer = BytesIO()
    ss.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    matches_str = "\n".join([f"Match {i}: coordinates ({x}, {y}) - text: '{text}'" 
                            for i, (_, x, y, text) in enumerate(matches)])
    prompt = f"""
I found multiple instances of "{target_text}" on the screen:
{matches_str}
Which one is the CLICKABLE BUTTON (not just a text label or heading)?
Answer with ONLY the number (0, 1, 2, etc) of the clickable button match.
If multiple look like buttons, pick the most obvious/prominent one.
Return ONLY a single number, nothing else.
"""
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
 "content": [ {"type": "text", "text": prompt},{ "type": "image_url", "image_url": {    "url": f"data:image/png;base64,{base64_image}" } }]}],max_tokens=350)
    try:
        index = int(response.choices[0].message.content.strip())
        index = max(0, min(index, len(matches) - 1))
        print(f"AI selected match #{index} as the button")
        return [matches[index]]  
    except:
        print("Could not parse AI response, using first match")
        return [matches[0]]
def findscreentarget(target_description):
    screen_w, screen_h = pyautogui.size()
    ss = pyautogui.screenshot()
    original_w, original_h = ss.size
    print(f"Screenshot size: {original_w}x{original_h}")
    print(f"Screen size: {screen_w}x{screen_h}")
    buffer = BytesIO()
    ss.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    prompt = f"""
TARGET OBJECT:
"{target_description}"
When clicking login or those types of buttons, make sure to click that, not like the login box, unless otherwise stated by the user.
IMPORTANT: If there are multiple instances of this text on screen:
- Identify the one that is a CLICKABLE BUTTON or UI element
- NOT just plain text or labels
- Look for visual indicators: borders, distinct background, padding, shadow effects
- Buttons typically have:
  * Distinct background color (darker/lighter than text)
  * Visible borders or outlines
  * Padding around text
  * Hover/focus state indicators
Return the exact pixel coordinate of the CENTER of the target object in the ORIGINAL IMAGE.
Do not scale, do not approximate.
Return coordinates in ORIGINAL IMAGE PIXEL SPACE ONLY.
- GOOGLE SEARCH BAR IS Ask Google or Type a URL and Opera GX search bar is Enter search or web address. So use this when the user asks to click the search bar or something.
Return a valid JSON object only.
Return ONLY:
{{"found": true, "x": number, "y": number}}
Image size:
width={original_w}
height={original_h}
Rules:
- Must be exact center
- No estimating
- If unclear return found:false
- when the user says click sign in or something, make sure to click the actual button, not some random thing. 
- CLICK INSDE THE OBJECT BUTTON OR WHATEVER, MAKE SURE ITS THE CENTER, BECAUSE IF NOT, IT WON'T PROPERLY WORK. DONT CLICK THE EDGES, ONLY CENTER!!!
- the user may take shortcuts when saying stuff, so use the info the user gave to do corresponding things. Like if user says click the rsm button, but u can see RSM portal, use the info and click RSM portal. Follow this with other directions.
- DONT CLICK ON THE OUTLINES OF BUTTONS AND BOXES, ALWAYS INSIDE THEM.
- DONT CLICK RANDOM BUTTONS, MAKE SURE TO CLICK THE RIGHT ONE, AND DIRECTLY ON IT, NOT THE SIDE. MAKE SURE OF THIS. EXMPL: LIKE ON A TEXT INPUT BOX, CLICK IN THE MIDDLE, NOT ON THE SIDES BECAUSE IT MAY NOT WORK SOMETIMES.
MAKE SURE TO GO ALL THE WAY IN THE OBJECT, LIKE THE DEAD CENTER. Like if the user says, "Click on the Forza Horizon 6 video," you dont click on the text, but the actual video. Make sure to follow this rule with other things too.
"""
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},{"type": "image_url",   "image_url": {"url": f"data:image/png;base64,{base64_image}"   } } ]  }], response_format={"type": "json_object"},max_tokens=350)
    raw = response.choices[0].message.content.strip()
    data = json.loads(raw)
    print("AI RESULT:", data)
    if not data.get("found"):
        return None
    x = int(data["x"])
    y = int(data["y"])
    x, y = clamp_mouse_position(x, y)
    print(f"FINAL CLICK: {x}, {y}")
    return x, y
def exectuteactions(actions, update_ui=None, user_text=""):
    hasreadscreen = any(a.get("action") == "read_screen" for a in actions)
    pythoncom.CoInitialize()
    def clean_announce(text):
        blocked_phrases = ["click", "then", "next", "after that", "go to", "move your mouse","step", "open the", "now you should", "you can", "finally"]
        t = text.lower()
        if any(p in t for p in blocked_phrases):
            return None  
        return text
    def announce(text):
        text = clean_announce(text)
        if not text:
            return
        speak(text)
        if update_ui:
            try:
                app.after(0, lambda: update_ui(text))
            except:
                update_ui(text)
    for i, a in enumerate(actions):
        action = a.get("action")
        value = a.get("value")
        print(f"[STEP {i+1}/{len(actions)}] {action} -> {value}")
        try:
            if isinstance(value, str):
                value = value.strip()
            if action in ["open_app", "open_url", "screenshot"]:
                time.sleep(0.6)
            if action == "set_volume":
                vol = int(int(value) * 65535/100)
                subprocess.Popen([getpath("nir/nircmd.exe"), "setsysvolume", str(vol)])
            elif action == "mute_volume":
                subprocess.Popen([getpath("nir/nircmd.exe"), "mutesysvolume", "1"])
            elif action == "unmute_volume":
                subprocess.Popen([getpath("nir/nircmd.exe"), "mutesysvolume", "0"])
            elif action == "screenshot":
                picturefider = os.path.join(os.environ["USERPROFILE"], "Pictures")
                filename = f"screenshot_{int(time.time())}.png"
                fullpath = os.path.join(picturefider, filename)
                ss = pyautogui.screenshot()
                ss.save(fullpath)
                print(f"Ss here: {fullpath}")
                os.startfile(fullpath)
            elif action == "read_screen":
                import cv2
                import numpy as np
                requestid = time.time()
                ss= pyautogui.screenshot()
                img = cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                gray  = cv2.resize(gray, None, fx=2.5, fy=2.5, interpolation =cv2.INTER_CUBIC)
                gray = cv2.bilateralFilter(gray, 9, 75, 75)
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 7)
                kernel = np.ones((2, 2), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                config = r"--oem 3 --psm 6"
                text= pytesseract.image_to_string(thresh, config=config)
                text= text.strip()
                if not text:
                    text= "No readable text found on screen"
                def summarizescreen(reqid=requestid):
                    try:
                        response = client.chat.completions.create(model= COMMAND_MODEL, messages=[{"role": "system", "content": "You are given OCR text from a screen. Answer the user's question briefly, max 10 words unless solving a problem"
                        }, {"role": "user", "content": f"Screen text: \n{text[:2000]}\n\nUser question:\n{user_text}"}], max_tokens=350)
                        summary = response.choices[0].message.content.strip()
                        if reqid != requestid:
                            return
                        speak(summary)
                        try:
                            app.after(0, lambda: update_ui(summary) if update_ui else None)
                        except:
                            if update_ui:
                                update_ui(summary)
                    except Exception as e:
                        print(f"summarizescreen error: {e}")
                        announce(text[:80])
                threading.Thread(target=summarizescreen, daemon=True).start()
                # import re
                # requestid = time.time()
                # ss = pyautogui.screenshot()
                # ss = ss.convert("L")
                # ss = ss.point(lambda x: 0 if x < 180 else 255)
                # ss = ss.resize((ss.width * 2, ss.height * 2))
                # text = pytesseract.image_to_string(ss, config="--oem 3 --psm 6")
                # text= text.strip()
                # if not text.strip():
                #     text = "No readable text found on screen"
                # def summarizescreen(reqid =requestid):
                #     try:
                #         response = client.chat.completions.create(
                #             model="llama-3.3-70b-versatile",
                #             messages=[
                #                 {"role": "system", "content": "You are given OCR text from a screen and a user question. Answer the question based on the screen content. Max 10 words."},
                #                 {"role": "user", "content": f"Screen text:\n{text[:1000]}\n\nUser question:\n{user_text}"}
                #             ],
                #             max_tokens=50
                #         )
                #         summary = response.choices[0].message.content.strip()
                #         if reqid != requestid:
                #             return
                #         speak(summary)
                #         app.after(0, lambda: update_ui(summary) if update_ui else None)
                #     except Exception as e:
                #         announce(text[:60])
                # threading.Thread(target=summarizescreen, daemon=True).start()
            elif action == "speak_response":
                speak(value)
                if update_ui:
                    update_ui(value)
            elif action == "screen_move":
                coords = findtextscreen(value)
                if not coords:
                    coords = findscreentarget(value)
                if not coords:
                    announce("I cannot find it")
                    continue
                x, y = coords
                pyautogui.moveTo(x, y, duration=0.3)
            elif action == "screen_click":
                matches = find_all_text(value)
                if not matches:
                    coords = findscreentarget(value)
                    if not coords:
                        announce("I cannot find it")
                        continue
                    x, y = coords
                else:
                    if len(matches) > 1:
                        ss = pyautogui.screenshot()
                        filtered = filter_button_from_matches(matches, value, ss)
                        if filtered:
                            matches = filtered
                    
                    index = parse_index(value)
                    index = min(index, len(matches)-1)
                    _, x, y, text = matches[index]
                    print(f"Selected match #{index}: {text}")
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()
            elif action == "screen_double_click":
                coords = findtextscreen(value)
                if not coords:
                    coords = findtextscreen(value)
                if not coords:
                    coords = findscreentarget(value)
                if not coords:
                    announce("I cannot find it")
                    continue
                x, y = coords
                pyautogui.moveTo(x, y, duration=0.3)
                pyautogui.doubleClick()
            elif action == 'wait':
                time.sleep(float(value))
            elif action == "screen_right_click":
                coords = findtextscreen(value)
                if not coords:
                    coords = findscreentarget(value)
                if not coords:
                    announce("I cannot find it")
                    continue
                x, y = coords
                pyautogui.moveTo(x, y, duration=0.3)
                pyautogui.click(button='right')
            elif action == "move_mouse":
                if isinstance(value, dict):
                    x= value.get("x", 0)
                    y= value.get("y", 0)
                    duration = float(value.get('duration', 0.25))
                else:
                    parts = str(value).replace(",", "").split()
                    x = int(parts[0])
                    y =int(parts[1])
                    duration = 0.25
                x, y= clamp_mouse_position(x, y)
                pyautogui.moveTo(x, y, duration=duration)
            elif action =="move_mouse_relative":
                if isinstance(value, dict):
                    x= int(value.get("x", 0))
                    y = int(value.get("y", 0))
                    duration = float(value.get("duration", 0.25))
                else:
                    parts = str(value).replace(",", "").split()
                    x = int(parts[0])
                    y= int(parts[1])
                    duration = 0.25
                current_x, current_y = pyautogui.position()
                target_x, target_y = clamp_mouse_position(current_x + x, current_y + y)
                pyautogui.moveTo(target_x, target_y, duration=duration)
            elif action =="click_mouse":
                button = str(value or "left").lower()
                if button not in ["left", "right", "middle"]:
                    button = 'left'
                pyautogui.click(button=button)
            elif action == "double_click_mouse":
                pyautogui.doubleClick()
            elif action == 'scroll_mouse':
                pyautogui.scroll(int(value))
            elif action == "open_app":
                open_app(value, announce)
            elif action == "close_app":
                subprocess.Popen(["taskkill", "/f", "/im", f"{value}.exe"], shell=True)
                announce(f"Closing {value}")
            elif action == "open_url":
                os.startfile(value)
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
    items = []
    arc_kwargs = {"outline": color, "width": width}
    line_kwargs = {"fill": color, "width": width}

    items.append(canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style="arc", **arc_kwargs))
    items.append(canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style="arc", **arc_kwargs))
    items.append(canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style="arc", **arc_kwargs))
    items.append(canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style="arc", **arc_kwargs))
    items.append(canvas.create_line(x1+r, y1, x2-r, y1, **line_kwargs))
    items.append(canvas.create_line(x1+r, y2, x2-r, y2, **line_kwargs))           
    items.append(canvas.create_line(x1, y1+r, x1, y2-r, **line_kwargs))
    items.append(canvas.create_line(x2, y1+r, x2, y2-r, **line_kwargs))
    return items
voiceque = queue.Queue()
recordingactive  = [False]
def listenvoice(q):
    samplerate = 16000
    chunks = []
    def callback(indata, frames, timestamp, status):
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
        after_id = None
    for widget in app.winfo_children():
        widget.destroy()
    canvas = Canvas(app, width=700, height=500, highlightthickness=0, bd=0, bg="black")
    canvas.place(x=0, y=0)
    canvasbg = canvas.create_image(0, 0, anchor="nw")
    def animate(frame_index=0):
        global after_id
        if canvasbg is None:
            return
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
def showaigif(canvas, canvas_img, textinput_window):
    global after_id
    if after_id:
        app.after_cancel(after_id)
        after_id = None
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
    overlay1 = canvas.create_rectangle(0, 0, 700, 500, fill="black", stipple="gray50")
    overlay2 = canvas.create_rectangle(0, 0, 700, 500, fill="black", stipple="gray50")
    overlay3 = canvas.create_rectangle(0, 0, 700, 500, fill="black", stipple="gray50")
    procimg = canvas.create_image(350, 210, anchor="center")
    proctextshdw = canvas.create_text(353, 390, text="Processing...", font=("Necosmic Personal Use", 18), fill="#666666", anchor="center")
    proctext = canvas.create_text(350, 387, text="Processing...", font=("Necosmic Personal Use", 18), fill="#FFFFFF", anchor="center")
    canvas._proc_frames = proc_frames
    canvas._overlay_items = [overlay1, overlay2, overlay3, procimg, proctextshdw, proctext]
    for item in canvas._overlay_items:
        canvas.tag_raise(item)
    canvas.itemconfigure(textinput_window, state="hidden")
    procafter = [None]
    closed = [False]
    def animate_proc(frame_index=0):
        if closed[0]:
            return
        canvas.itemconfig(procimg, image=proc_frames[frame_index])
        procafter[0] = canvas.after(50, animate_proc, (frame_index + 1) % len(proc_frames))
    def close():
        global after_id
        if closed[0]:
            return
        closed[0] = True
        if procafter[0]:
            canvas.after_cancel(procafter[0])
        for item in canvas._overlay_items:
            try:
                canvas.delete(item)
            except:
                pass
        canvas._overlay_items = []
        canvas.itemconfigure(textinput_window, state="normal")
        def animate_bg(frame_index=0):
            global after_id
            canvas.itemconfig(canvas_img, image=frames[frame_index])
            after_id = app.after(20, animate_bg, (frame_index + 1) % len(frames))
        animate_bg()
    animate_proc()
    return close
def start_loading_from_thread():
    q = queue.Queue()
    def start():
        try:
            canvas = active_ui["canvas"]
            canvas_img = active_ui["canvas_img"]
            textinput_window = active_ui["textinput_window"]
            if not canvas or not canvas_img or not textinput_window:
                q.put(lambda: None)
                return
            close_loading = showaigif(canvas, canvas_img, textinput_window)
            q.put(close_loading)
        except Exception as e:
            print("loading start error:", e)
            q.put(lambda: None)
    app.after(0, start)
    try:
        return q.get(timeout=2)
    except queue.Empty:
        return lambda: None
def stop_loading_from_thread(close_loading):
    done = threading.Event()
    def stop():
        try:
            close_loading()
        except Exception as e:
            print("loading stop error:", e)
        finally:
            done.set()
    app.after(0, stop)
    done.wait(timeout=2)
def run_ai_command_with_gif(commandtext):
    close_loading = start_loading_from_thread()
    try:
        parsed = askgroq(commandtext)
        actions = parsed.get("actions", [])
        exectuteactions(actions, user_text=commandtext)
    finally:
        stop_loading_from_thread(close_loading)
def main(canvas, canvas_img):
    clear(canvas, canvas_img)
    lastfullresponse = [None]
    voiceresult = [None]
    textresult = [None]
    fullanswerready = [False]
    def getfullanswer(result):
        def run():
            response = client.chat.completions.create(model= COMMAND_MODEL, messages=[{"role": "system", "content": "Give me a full detailed answer to the user's question. Speak naturally, no lists or markdown"},
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
    active_ui["canvas"] = canvas
    active_ui["canvas_img"] = canvas_img
    active_ui["textinput_window"] = textinput_window
    responsetext_shdw = canvas.create_text(523, 175, text="", font=("Press Start 2P", 13), fill="#0a2e18", anchor="n", width=290)
    responsetext= canvas.create_text(520, 172, text="", font=("Press Start 2P", 13), fill="#319950", anchor="n", width=290)
    leftresponseshdw = canvas.create_text(237, 128, text="", font=('Press Start 2P', 13), fill="#0a2e18", anchor='n', width=220)
    lefresponse = canvas.create_text(234, 125, text="", font=("Press Start 2P", 13), fill="#319950", anchor='n', width=220)
    fullresbutton1shdw = canvas.create_text(244, 259, text="Full Answer", font=('Necosmic Personal use', 12), fill="#0a2e18")
    fullresbutton1 = canvas.create_text(241, 256, text="Full Answer", font=("Necosmic Personal use", 12), fill="#319950")
    fullresbutton2shdw = canvas.create_text(524, 273, text="Full Answer", font=("Necosmic Personal use", 12), fill="#0a2e18")
    fullresbutton2 = canvas.create_text(521, 270, text="Full Answer", font=("Necosmic Personal use", 12), fill="#319950")
    rounded_rect(canvas, 448, 259, 593, 284, r=9, color="#319950", width=3)
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
        close_loading = showaigif(canvas, canvas_img, textinput_window)
        def run():
            try:
                response = client.chat.completions.create(
                    model=COMMAND_MODEL,
                    messages=[
                        {"role": "system", "content": "Give me a full natural answer, no lists or markdown. Also, do NOT talk for too long, or get off track. Give a good answer, that's it."},{"role": "user", "content": result}],max_tokens=350)
                full = response.choices[0].message.content.strip()
                speak(full)
            finally:
                app.after(0, close_loading)
        threading.Thread(target=run, daemon=True).start()
    def fullanswerclicktext(e):
        if not textresult[0]:
            return
        result = textresult[0]
        close_loading = showaigif(canvas, canvas_img, textinput_window)
        def run():
            try:
                response = client.chat.completions.create(
                    model=COMMAND_MODEL,
                    messages=[
                        {"role": "system", "content": "Give me a full natural answer, no lists or markdown. Also, do NOT talk for too long, or get off track. Give a good answer, that's it."},  {"role": "user", "content": result}],max_tokens=350)
                full = response.choices[0].message.content.strip()
                speak(full)
            finally:
                app.after(0, close_loading)
        threading.Thread(target=run, daemon=True).start()
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
            canvas.itemconfig(rectext, text="Processed")
            canvas.itemconfig(rectextshdw, text="Processed")
            close_loading = showaigif(canvas, canvas_img, textinput_window)
            def run_groq():
                try:
                    parsed = askgroq(result)
                    actions = parsed.get("actions", [])
                    if actions and actions[0].get("action") == "unknown":
                        app.after(0, lambda: canvas.itemconfig(lefresponse, text="I don't understand"))
                        app.after(0, lambda: canvas.itemconfig(leftresponseshdw, text="I don't understand"))
                        return
                    def update_ui(text):
                        app.after(0, lambda: canvas.itemconfig(leftresponseshdw, text=text))
                        app.after(0, lambda: canvas.itemconfig(lefresponse, text=text))
                    exectuteactions(actions, update_ui, result)
                except Exception as e:
                    print("voice AI error:", e)
                finally:
                    app.after(0, close_loading)
            threading.Thread(target=run_groq, daemon=True).start()
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
        text = textinput.get().strip().lower()
        if text:
            textresult[0] = text
            textinput.delete(0, "end")
            close_loading = showaigif(canvas, canvas_img, textinput_window)
            def run_groq():
                try:
                    parsed = askgroq(text)
                    actions = parsed.get("actions", [])
                    def update_ui(t):
                        app.after(0, lambda: canvas.itemconfig(responsetext, text=t))
                        app.after(0, lambda: canvas.itemconfig(responsetext_shdw, text=t))
                    if actions and actions[0].get("action") == "unknown":
                        app.after(0, lambda: canvas.itemconfig(responsetext, text="I don't understand"))
                        app.after(0, lambda: canvas.itemconfig(responsetext_shdw, text="I don't understand"))
                    else:
                        exectuteactions(actions, update_ui, text)
                except Exception as e:
                    print("text AI error:", e)
                finally:
                    app.after(0, close_loading)
            threading.Thread(target=run_groq, daemon=True).start()
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
    settingsbtnshdw = canvas.create_text(473, 55, text="⚙", font=("Arial", 24), fill="#0a2e18")
    settingsbtn = canvas.create_text(470, 52, text="⚙", font=("Arial", 24), fill='#319950')
    def settingent(e):
        canvas.itemconfig(settingsbtn, fill="#0F4423")
        canvas.itemconfig(settingsbtnshdw, fill="#0E0D0D")
    def settinglev(e):
        canvas.itemconfig(settingsbtnshdw, fill="#0a2e18")
        canvas.itemconfig(settingsbtn, fill="#319950")
    canvas.tag_bind(settingsbtn, "<Enter>", settingent)
    canvas.tag_bind(settingsbtnshdw, "<Leave>", settinglev)
    canvas.tag_bind(settingsbtn, "<Leave>", settinglev)
    canvas.tag_bind(settingsbtnshdw, "<Enter>", settingent)
    canvas.tag_bind(settingsbtn, "<Button-1>", lambda e: settings(canvas, canvas_img))
    canvas.tag_bind(settingsbtnshdw, "<Button-1>", lambda e: settings(canvas, canvas_img))
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
def settings(canvas, canvas_img):
    clear(canvas, canvas_img)
    canvas.create_text(353, 63, text="Settings", font=("Necosmic Personal Use", 38), fill="#0a2e18")
    canvas.create_text(350, 60, text="Settings", font=('Necosmic Personal Use', 38), fill="#319950")
    voicecheckstate = voiceenabled
    voicecheck = canvas.create_rectangle(148, 122, 168, 142,outline='#319950',width=2,fill="black",stipple="gray12")
    voicebtnshdw = canvas.create_text(161, 135,text="✓",font=("Arial", 14),fill="#0a2e18")
    voicebtn = canvas.create_text(158, 132,text="✓",font=("Arial", 14),fill="#319950")
    state = "normal" if voiceenabled[0] else "hidden"
    canvas.itemconfig(voicebtn, state=state)
    canvas.itemconfig(voicebtnshdw, state=state)
    canvas.create_text(343, 133, text="Voice Responses", font=("Necosmic Personal Use", 20), fill="#0a2e18", anchor='center')
    canvas.create_text(340, 130, text="Voice Responses", font=('Necosmic Personal Use', 20), fill="#319950", anchor='center')
    wake_items = "Wake_toggle"
    wakecheck = canvas.create_rectangle(148, 172, 168, 192, outline="#319950", width=2, fill="black", stipple="gray12", tags=wake_items)
    wakebtnshdw = canvas.create_text(161, 185, text="✓", font=("Arial", 14), fill="#0a2e18", tags=wake_items)
    wakebtn = canvas.create_text(158, 182, text="✓", font=("Arial", 14), fill="#319950", tags=wake_items)
    wakelabelshdw = canvas.create_text(385, 183, text="Wake Word Detection", font=("Necosmic Personal Use", 20), fill="#0a2e18", anchor='center', tags=wake_items)
    wakelabel = canvas.create_text(382, 180, text="Wake Word Detection", font=("Necosmic Personal Use", 20), fill="#319950", anchor='center', tags=wake_items)
    def refreshwake():
        wakestate = "normal" if wakewordenabled[0] else "hidden"
        canvas.itemconfig(wakebtn, state=wakestate)
        canvas.itemconfig(wakebtnshdw, state=wakestate)
    def togglewake(e):
        wakewordenabled[0] = not wakewordenabled[0]
        savesettings()
        print("wakewordenabled:", wakewordenabled[0])
        refreshwake()
    refreshwake()
    canvas.tag_bind(wake_items, "<Button-1>", togglewake)
    canvas.create_text(353, 233, text="Voice Speed", font=("Necosmic Personal Use", 20), fill="#0a2e18", anchor='center')
    canvas.create_text(350, 230, text='Voice Speed', font=('Necosmic Personal Use', 20), fill="#319950", anchor='center')
    speedshdw = canvas.create_text(353, 298, text=str(tts_rate[0]), font=("Press Start 2P", 16), fill="#0a2e18", width = 90)
    speedtext = canvas.create_text(350, 295, text=str(tts_rate[0]), font=('Press Start 2P', 16), fill="#319950", width=90)
    minussshdw = canvas.create_text(263, 298, text="-", font=('Necosmic Personal Use', 24), fill="#0a2e18")
    minusbtn = canvas.create_text(260, 295, text="-", font=("Necosmic Personal Use", 24), fill="#319950")
    plusshdw = canvas.create_text(443, 298, text="+", font=("Necosmic Personal Use", 24),fill="#0a2e18" )
    plusbtn = canvas.create_text(440, 295, text="+", font=("Necosmic Personal Use", 24), fill="#319950")
    def updatespeedtext():
        canvas.itemconfig(speedtext, text=str(tts_rate[0]))
        canvas.itemconfig(speedshdw, text=str(tts_rate[0]))
    def slowspeech(e):
        tts_rate[0] = max(1, tts_rate[0] - 5)
        savesettings()
        updatespeedtext()
    def fastspeech(e):
        tts_rate[0] = min(100, tts_rate[0] + 5)
        savesettings()
        updatespeedtext()
    def minusenter(e):
        canvas.itemconfig(minusbtn, fill="#0F4423")
        canvas.itemconfig(minussshdw, fill="#0E0D0D")
    def minusleave(e):
        canvas.itemconfig(minussshdw, fill="#0a2e18")
        canvas.itemconfig(minusbtn, fill="#319950")
    def plusenter(e):
        canvas.itemconfig(plusbtn, fill="#0F4423")
        canvas.itemconfig(plusshdw, fill="#0E0D0D")
    def plusleave(e):
        canvas.itemconfig(plusbtn, fill="#319950")
        canvas.itemconfig(plusshdw, fill="#0E0D0D")
    canvas.tag_bind(minusbtn, "<Button-1>", slowspeech)
    canvas.tag_bind(minussshdw, "<Button-1>", slowspeech)
    canvas.tag_bind(plusbtn, "<Button-1>", fastspeech)
    canvas.tag_bind(plusshdw, "<Button-1>", fastspeech)
    canvas.tag_bind(minusbtn, "<Enter>", minusenter)
    canvas.tag_bind(minussshdw, "<Enter>", minusenter)
    canvas.tag_bind(minusbtn, "<Leave>", minusleave)
    canvas.tag_bind(minussshdw, "<Leave>", minusleave)
    canvas.tag_bind(plusbtn, "<Leave>", plusleave)
    canvas.tag_bind(plusshdw, "<Leave>", plusleave)
    canvas.tag_bind(plusbtn, "<Enter>", plusenter)
    canvas.tag_bind(plusshdw, "<Enter>", plusenter)
    def testvoice(e):
        speak("Say something")
        def run():
            time.sleep(2)
            samplerate = 16000
            chunks = []
            test_active = [True]
            def callback(indata, frames, timestamp, status):
                if test_active[0]:
                    chunks.append(indata.copy())
            try:
                with sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback):
                    time.sleep(4)
                test_active[0] = False
                if not chunks:
                    speak("I did not hear anything")
                    return
                audiodata = np.concatenate(chunks, axis=0)
                r = sr.Recognizer()
                audio = sr.AudioData(audiodata.tobytes(), samplerate, 2)
                text = r.recognize_google(audio)
                speak(f"You said {text}")
            except sr.UnknownValueError:
                speak("I did not hear anything")
            except Exception as e:
                print("test voice error:", e)
                speak("Voice test failed")
        threading.Thread(target=run, daemon=True).start()
    testrec = rounded_rect(canvas, 245, 350, 455, 390, r=9, color="#319950", width=3)
    testshdw = canvas.create_text(353, 375, text="Test Voice", font=("Necosmic Personal Use", 18), fill="#0a2e18")
    testbtn = canvas.create_text(350, 372, text="Test Voice", font=("Necosmic Personal Use", 18), fill="#319950")
    def recolortest(items, color):
        for item in items:
            kind = canvas.type(item)
            if kind == "arc":
                canvas.itemconfig(item, outline=color)
            elif kind == "line":
                canvas.itemconfig(item, fill=color)
    def entertest(e):
        canvas.itemconfig(testbtn, fill="#0F4423")
        canvas.itemconfig(testshdw, fill="#0E0D0D")
        recolortest(testrec, "#0a2e18")
    def leavetest(e):
        canvas.itemconfig(testbtn, fill="#319950")
        canvas.itemconfig(testshdw, fill="#0a2e18")
        recolortest(testrec, "#319950")
    canvas.tag_bind(testshdw, "<Button-1>",testvoice)
    canvas.tag_bind(testbtn, "<Button-1>",  testvoice)
    canvas.tag_bind(testbtn,"<Leave>", leavetest )
    canvas.tag_bind(testshdw, "<Leave>", leavetest)
    canvas.tag_bind(testbtn, "<Enter>", entertest)
    canvas.tag_bind(testshdw, "<Enter>", entertest)
    def togglebutton(e):
        voiceenabled[0] = not voiceenabled[0]
        savesettings()
        state = "normal" if voiceenabled[0] else "hidden"
        canvas.itemconfig(voicebtn, state=state)
        canvas.itemconfig(voicebtnshdw, state=state)
    canvas.tag_bind(voicecheck, "<Button-1>", togglebutton)
    canvas.tag_bind(voicebtn, "<Button-1>", togglebutton)
    canvas.tag_bind(voicebtnshdw, "<Button-1>", togglebutton)
    backbtnshdw = canvas.create_text(73, 55, text="Return", font=("Necosmic Personal Use", 18), fill="#0a2e18")
    backbtn = canvas.create_text(70, 52, text="Return", font=('Necosmic Personal Use', 18), fill="#319950")
    def backenter(e):
        canvas.itemconfig(backbtn, fill="#0F4423")
        canvas.itemconfig(backbtnshdw, fill="#0E0D0D")
    def backleave(e):
        canvas.itemconfig(backbtn, fill="#319950")
        canvas.itemconfig(backbtnshdw, fill="#0a2e18")
    def back(e):
        global after_id
        if after_id:
            app.after_cancel(after_id)
            after_id = None
        clear(canvas, canvas_img)
        main(canvas, canvas_img)
    canvas.tag_bind(backbtn, "<Button-1>", back)
    canvas.tag_bind(backbtnshdw, "<Button-1>", back)
    canvas.tag_bind(backbtn, "<Leave>", backleave)
    canvas.tag_bind(backbtnshdw, "<Leave>", backleave)
    canvas.tag_bind(backbtn, "<Enter>", backenter)
    canvas.tag_bind(backbtnshdw, "<Enter>", backenter)
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
def wakewordloop():
    recognizer = sr.Recognizer()
    samplerate = 16000
    duration = 2
    lastrigger = 0
    cooldown = 3
    while True:
        if not wakewordenabled[0]:
            time.sleep(0.2)
            continue
        try: 
            recording = sd.rec(int(duration*samplerate), samplerate=samplerate, channels=1, dtype="int16")
            sd.wait()
            audio = sr.AudioData(recording.tobytes(), samplerate, 2)
            text= recognizer.recognize_google(audio).lower()
            print("heard:", text)
            current = time.time()
            if "nova" in text and current - lastrigger >cooldown:
                lastrigger = current
                print("deteced word")
                speak("Yes?")
                commandrecording = sd.rec(int(5*samplerate), samplerate=samplerate, channels=1, dtype="int16")
                sd.wait()
                commandaudio = sr.AudioData(commandrecording.tobytes(), samplerate, 2)
                commandtext = recognizer.recognize_google(commandaudio).lower()
                print("command:", commandtext)
                run_ai_command_with_gif(commandtext)
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print("wakeword error:", e)
if __name__ == "__main__":
    threading.Thread(target=wakewordloop, daemon=True).start()
    welcome()
    app.mainloop()