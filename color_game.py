import tkinter as tk
from tkinter import messagebox
import random
import os
import pyttsx3
import threading
class GameConfig:
    game_duration = 60
    colors = ['Red', 'Blue', 'Green', 'Pink', 'Yellow', 'Purple', 'Orange', 'Black']
    hex_codes = ['#FF0000', '#0000FF', '#008000', '#FF69B4', '#FFD700', '#8A2BE2', '#FF4500', '#000000']
    color_map = dict(zip(colors, hex_codes))
    high_score_file = 'highscore.txt'
class HighScoreManager:
    def __init__(self, filename):
        self.filename = filename
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as file:
                    return int(file.read())
            except:
                return 0
        return 0
    def save(self, score):
        with open(self.filename, 'w') as file:
            file.write(str(score))
class GameEngine:
    def __init__(self, config):
        self.config = config
        self.reset()
    def reset(self):
        self.score = 0
        self.time_left = self.config.game_duration
        self.correct_color = None
    def next_round(self):
        self.correct_color = random.choice(self.config.colors)
        display_word = random.choice(
            [c for c in self.config.colors if c != self.correct_color]
        )
        text_color = self.config.color_map[self.correct_color]
        return display_word, text_color
    def check_answer(self, choice):
        if choice == self.correct_color:
            self.score += 1
            return True
        return False
class GameUi:
    def __init__(self, root, controller, config):
        self.root = root
        self.controller = controller
        self.config = config
        self.setup_window()
        self.create_widgets()
    def setup_window(self):
        self.root.title("Chroma Challenge")
        self.root.geometry("600x600")
        self.root.config(bg='#282c34')
    def create_widgets(self):
        self.info_frame = tk.Frame(self.root, bg='#3e4451', pady=10)
        self.info_frame.pack(fill='x')
        self.game_frame = tk.Frame(self.root, bg='#282c34')
        self.game_frame.pack(expand=True)
        self.button_frame = tk.Frame(self.root, bg='#282c34')
        self.button_frame.pack()
        self.score_label = tk.Label(
            self.info_frame,
            text="Score: 0",
            font=('Arial', 18, 'bold'),
            bg='#3e4451',
            fg='#61dafb'
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        self.time_label = tk.Label(
            self.info_frame,
            text="Time: 60",
            font=('Arial', 18, 'bold'),
            bg='#3e4451',
            fg='#61dafb'
        )
        self.time_label.pack(side=tk.RIGHT, padx=20)
        self.word_label = tk.Label(
            self.game_frame,
            text="Click Start",
            font=('Arial', 72, 'bold'),
            bg='#282c34',
            fg='white'
        )
        self.word_label.pack(expand=True)
        self.start_button = tk.Button(
            self.button_frame,
            text="Start Game",
            font=('Arial', 24, 'bold'),
            bg='#4CAF50',
            fg='white',
            command=self.controller.start_game
        )
        self.start_button.pack(pady=10)
        self.buttons = []
        self.create_color_button()
    def create_color_button(self):
        row = tk.Frame(self.button_frame, bg='#282c34')
        row.pack()
        for i, color in enumerate(self.config.colors):
            button = tk.Button(
                row,
                text=color,
                font=('Arial', 27, 'bold'),
                width=10,
                state=tk.DISABLED,
                command=lambda c=color: self.controller.handle_guess(c)
            )
            button.grid(row=0, column=i, padx=5, pady=10)
            self.buttons.append(button)
    def update_score(self, score):
        self.score_label.config(text=f"Score: {score}")
    def update_time(self, time_left):
        self.time_label.config(text=f"Time: {time_left}")
    def update_word(self, word, color):
        self.word_label.config(text=word, fg=color)
    def show_feedback(self, correct):
        symbol = "✔" if correct else "❌"
        color = "green" if correct else "red"
        self.word_label.config(text=symbol, fg=color)
    def toggle_buttons(self, state):
        for button in self.buttons:
            button.config(state=state)
    def show_game_over(self, score, high_score, new_record):
        if new_record:
            messagebox.showinfo("New HighScore!", f"New High Score: {high_score}")
        else:
            messagebox.showinfo("Game Over!", f"Final Score: {score}")
class ColorMatchGame:
    def __init__(self, root):
        self.config = GameConfig()
        self.engine = GameEngine(self.config)
        self.storage = HighScoreManager(self.config.high_score_file)
        self.ui = GameUi(root, self, self.config)
        self.voice = pyttsx3.init()
        self.voice.setProperty('rate', 180)
        self.high_score = self.storage.load()
        self.timer_id = None
        self.game_running = False
    def speak_word(self, word):
        threading.Thread(target=self._speak, args=(word,), daemon=True).start()
    def _speak(self, word):
        self.voice.stop()
        self.voice.say(word)
        self.voice.runAndWait()
    def start_game(self):
        self.engine.reset()
        self.game_running = True
        self.ui.toggle_buttons(tk.NORMAL)
        self.ui.update_score(0)
        self.countdown()
        self.new_round()
    def new_round(self):
        word, color = self.engine.next_round()
        self.ui.update_word(word, color)
        self.speak_word(word)
    def handle_guess(self, choice):
        if not self.game_running:
            return
        correct = self.engine.check_answer(choice)
        self.ui.update_score(self.engine.score)
        self.ui.show_feedback(correct)
        self.ui.root.after(200, self.new_round)
    def countdown(self):
        if not self.game_running:
            return
        self.ui.update_time(self.engine.time_left)
        if self.engine.time_left > 0:
            self.engine.time_left -= 1
            self.timer_id = self.ui.root.after(1000, self.countdown)
        else:
            self.end_game()
    def end_game(self):
        self.game_running = False
        self.ui.toggle_buttons(tk.DISABLED)
        new_record = False
        if self.engine.score > self.high_score:
            self.high_score = self.engine.score
            self.storage.save(self.high_score)
            new_record = True
        self.ui.show_game_over(self.engine.score, self.high_score, new_record)
if __name__ == "__main__":
    root = tk.Tk()
    app = ColorMatchGame(root)
    root.mainloop()