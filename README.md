# NOVA

### Nova is a Python based Windows app that interprets user requests using an AI model, which can then see what's on your screen, and perform actions autonomously. Using vision models, OCR,  and memory, Nova can open apps, interact with elements on your screen, and complete multi step tasks on your computer. Nova uses Claude Sonnet 4, an excellent AI desktop model, which perfectly matches the needs for this project. NOTE: Nova still currently is in BETA stage, and there may be many bugs I'm unaware of. 

## Key features:
- **Voice commands and wake word support.** To activate wake word, just say "Nova," or you could directly record your voice by clicking the mic on the left side of the UI.
- **Screen understanding with AI vision.** Give the command such as, "What's my screen about," to get a short sumamry of your screen. 
- **OCR based text detection and interaction.** Nova uses OCR text detection to pinpoint precise pixels on your screen, which it could then use for actions.
- **Desktop automation, like clicking, typing, and scrolling.** Ask Nova to do an action, such as, "Click the Youtube bookmark," and with OCR vision, it can precisely click on the requested item. 
-  **Memory and conversation history.** Nova is able to remember conversation history, allowing you to ask follow-up questions and such. You also have the ability to clear your history if you wish. Conversation history is showcased in the bottom left of the UI.
- **Text and voice responses.** When asking questions/doing actions, Nova will give both a voice response and a text response. You have the ability to change between two different voices. 
-  **Windows system controls.** You are able to ask NOVA to  take a screenshot, change the volume, open apps (this action may have bugs with some users), lock your computer, put your computer to sleep, etc...
- **Multi-step actions.** Nova can exectute multi-step actions, like solving a small six quetion quiz. This feature may have some problems, but for the most part, it works decently. NOTE: this feature may be a bit slow due to the AI model. 
- **Multi-monitor support.** Nova can view a total of two monitors, but features are very limited to this. For the most part, it can view/summarize screens, and click easy to read buttons, text, etc...
- **Context aware UI interaction.** During multi-step actions, Nova can correct iteself on the go, however, this feature is still being improved upon. 

## Example commands to try:
- "Open Discord."
- "Set my volume to 50%."
- "What's on my screen?"
- "What's on my other screen" or "What's my second screen about?" 
- "Open Youtube and play the third video."
- "Solve the first three problems on this worksheet by clicking the correct answer for each."
- "Click the login button."
- "Search for the latest news." 

## What Nova is built with:
- Python
- CustomTkinter
- EasyOCR
- Tesseract OCR
- PyAutoGUI
- OpenCV
- OpenAI (used for the previous model)
- PyTTSX3
- SpeechRecognition
- MSS
- PyCAW
- Pillow
- NirCMD

## Things to keep in mind
- Nova is in beta stages and may occasionally make mistakes
- Nova's context awareness and multi-step features best works on web browsers such as Chrome, Edge, or Opera GX
- OCR doesn't work on web pages that don't allow text to be extracted.
- Multi-step actions may take a bit of time to complete as each step requires AI reasoning and screen analysis
- Some desktop applications use custom UI frameworks that can make text detection more difficult
- Multi-monitor support is currently limited and may not work reliably in every situation.
- Nova performs best when UI elements are clearly visible and not obstructed
- Due to response limits, Nova may face some issues regarding AI status, which may randomly cut of actions.
- Nova may be slow due to Python, and your internet speed/system specs play a big factor in speeds. 

## Current limitations
- Vision models can sometimes misunderstand screen content.
- OCR doesn't work on web pages that don't allow text to be extracted. 
- Autonomous task completion is currently limited by model reasoning quality and API response speed.
- UI interactions are best reliable on browser based interfaces than customized desktop applications.
- Uses Python, which creates slow response times, unlike other languages such as Rust. Also, your internet speed and system specs play a big factor in speeds. 

## Current status of NOVA
### Nova is still currently in development. I plan to imrpove the vision, context awareness, and overall reliability in the future. 

## Why I built NOVA.
### Most desktops assistants can only answer questions or run simple commands, but I wanted to build something that can actually interact with a computer, understand context, and then carry out tasks. 

## Challenges I ran into
### I ran into a lot of challenges and problems when building this app. At first, I didn't think I could build this, but after hours of watching youtube tutorials, I managed to slowly build new features. I spent the majority of my time tuning the OCR feature, and it still isn't perfect. It got to a point where I had to compute the confidence of the AI, since it was always clicking the wrong buttons, and then filter out the best matches. In addition to that, I spent the rest of the time fixing random bugs that randomly pop up. This entire app has been a huge roller coaster, but in the end, I managed to pull through. 

## Disclaimer:
### Nova is an experimental AI desktop assistant, and because it directly interacts with your desktop, occasional mistakes may occur. From my experiences, Nova may occacsionally clicks random things on your screen, as this is an OCR bug I can't prevent. Please watch over your computer while Nova is running tasks. 

## Where AI assistance was used:
- AI assistance was used to help tune the OCR vision
- Small amounts of AI was used to help debug/fix parts of the code
- AI helped with the memory feature
- AI helped build some parts of the prompts
#### For the most part, the rest of the application logic, desktop automation, UI development, and system integration were implemented by me. 

## How to run
### To run Nova, download the latest EXE release, which can be found here:https://github.com/Beanzsigma/Nova/releases/tag/v1.0. Also, in that release, download the Tesseract OCR file, open it, and complete the installation steps. After you have downloaded the EXE file, open the app, and that's where it will then prompt you about some unknown publisher. To continue, click "More info," then "run anyway." After you get into the app, click the settings button at the top, and type you Hack Club AI API key in the designated area. After you've completed these steps, Nova should be ready to use. NOTE: Nova may take a bit of time to load for some users, and to operate it... be patient, Python is pretty slow! - This also depends on your PC specs/internet speed.

## Demo: 
### Here is a google drive link to a demo video. NOTE: this video is being played at two times speed, as it took around two minutes to complete the task: https://drive.google.com/file/d/10kO8fyIeC7EkRwF24mSDpGQW8ILIiUHG/view?usp=sharing
<img width="689" height="523" alt="Screenshot 2026-06-09 175623" src="https://github.com/user-attachments/assets/2ad913f3-5d8c-4e80-8e7e-bb5715a13ac5" />

