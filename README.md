# AI-Music-Composer
A Pygame‑based Piano‑Roll editor that leverages AI (Transformer &amp; LSTM) to compose and continue multi‑track music seamlessly.

---

## ✨ Features

- 🎼 Multi-track composition editor
- 🤖 Transformer model for music continuation
- 🧬 LSTM model support for musical sequence prediction
- ⌨️ Keyboard-controlled interaction

---

![image](https://github.com/user-attachments/assets/cc8b6210-2db4-4ce1-9eb2-08ff0376db63)


## 🎮 Controls

| Key       | Action                            |
|-----------|-----------------------------------|
| `G`       | Generate continuation of current music |
| `C`       | Clear the track                   |
| `Space`   | Play / Pause                      |
| `1–6`     | Select note duration              |

---

## 📁 How to Use

1. **Place MIDI files**  
   Drop your `.midi` files into the `Documents/` directory.

2. **Save generated music**  
   After saving, rename the file in the directory manually to avoid overwriting.

3. **Run the application**  
   Launch the app using:

   ```bash
   python Display.py
