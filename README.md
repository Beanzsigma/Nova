# NOVA
### Nova is a Python based Windows app that interprets user requests using an AI model, which can then see what's on your screen, and perform actions autonomously. Using vision models, OCR,  and memory, Nova can open apps, interact with elements on your screen, and complete multi step tasks on your computer. NOTE: Nova still currently is in BETA stage, and there may be many bugs I'm unaware of. 

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

## Why I built NOVA.
### Most desktops assistants can only answer questions or run simple commands, but I wanted to build something that can actually interact with a computer, understand context, and then carry out tasks. 

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

## Current status of NOVA
### Nova is still currently in development. I plan to imrpove the vision, context awareness, and overall reliability in the future. 