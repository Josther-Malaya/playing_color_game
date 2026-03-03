import tkinter as tk
import os
import random
from tkinter import messagebox

GAME_DURATION_SECONDS = 60
COLOR_NAMES = ['Red', 'Blue', 'Green', 'Pink', 'Yellow', 'Purple', 'Orange', 'Black']
HEX_CODES = ['#FF0000', '#0000FF', '#008000', '#FF69B4', '#FFD700', '#8A2BE2', '#FF4500', '#000000']
COLOR_MAP = dict(zip(COLOR_NAMES, HEX_CODES))


class ColorMatchGame:
    def __init__(self, master):
        self.master = master
        master.title("Chroma Challenge: The Color Game")
        master.geometry("600x600")
        master.config(bg='#282c34')
        self.score = 0
        self.time_left = GAME_DURATION_SECONDS
        self.game_running = False
        self.correct_color_name = ""
        self.font_title = ('Arial', 24, 'bold')
        self.font_score = ('Arial', 18, 'bold')
        self.font_word = ('Arial', 72, 'bold')
        self.font_button = ('Arial', 26, 'bold')
        self.info_frame = tk.Frame(master, bg='#3e4451', pady=10)
        self.info_frame.pack(fill='x')
        self.game_frame = tk.Frame(master, bg='#282c34', pady=30)
        self.game_frame.pack(expand=True, fill='both')
        self.button_frame = tk.Frame(master, bg='#282c34', pady=10)
        self.button_frame.pack(fill='x')
        self.score_label = tk.Label(self.info_frame, text="Score: 0", font=self.font_score, bg='#3e4451', fg='#61dafb')
        self.score_label.pack(side=tk.LEFT, padx=20)
        self.time_label = tk.Label(self.info_frame, text=f"Time: {self.time_left}s", font=self.font_score, bg='#3e4451', fg='#61dafb')
        self.time_label.pack(side=tk.RIGHT, padx=20)
        self.word_label = tk.Label(self.game_frame, text="Click Start", font=self.font_word, bg='#282c34', fg='white')
        self.word_label.pack(expand=True)
        self.start_button = tk.Button(self.button_frame, text=f"Start Game ({GAME_DURATION_SECONDS}s)", font=self.font_button,
                                      command=self.start_game, bg='#4CAF50', fg='white',
                                      padx=15, pady=8, relief=tk.RAISED)
        self.start_button.pack(pady=10)
        self.buttons = []
        self.create_color_buttons()
        self.high_score = self.load_high_score()
        self.high_score_label = tk.Label(
            self.info_frame,
            text=f"High Score: {self.high_score}",
            font=self.font_score,
            bg='#3e4451',
            fg='#FFD700'
        )
        self.high_score_label.pack()
        self.instructions = tk.Label(
            self.game_frame,
            text="Click the button matching the TEXT COLOR (not the word!)",
            font=('Arial', 14),
            bg='#282c34',
            fg='white'
        )
        self.instructions.pack()
    def create_color_buttons(self):
        button_row = tk.Frame(self.button_frame, bg='#282c34')
        button_row.pack(expand=True, fill='x', padx=10)
        for i, color_name in enumerate(COLOR_NAMES):
            button = tk.Button(button_row, text=color_name, font=self.font_button, width=10,
                               command=lambda c=color_name: self.check_answer(c),
                               bg='#606060', fg='white', activebackground='#808080',
                               padx=5, pady=5)

            button.grid(row=0, column=i, padx=5, pady=10)
            button.config(state=tk.DISABLED)
            self.buttons.append(button)
    def start_game(self):
        if not self.game_running:
            self.score = 0
            self.time_left = GAME_DURATION_SECONDS
            self.game_running = True
            self.score_label.config(text="Score: 0")
            self.start_button.config(text="Game In Progress...", state=tk.DISABLED, bg='#e53935')
            for button in self.buttons:
                button.config(state=tk.NORMAL)
            self.next_round()
            self.countdown()
    def countdown(self):
        if self.game_running:
            self.time_label.config(text=f"Time: {self.time_left}s")
            if self.time_left <= 5:
                 self.time_label.config(fg='#FF4500')
            else:
                 self.time_label.config(fg='#61dafb')
            if self.time_left > 0:
                self.time_left -= 1
                self.master.after(1000, self.countdown)
            else:
                self.end_game()
    def end_game(self):
        self.game_running = False
        self.word_label.config(text="FINISH", fg='white')
        self.start_button.config(text="Restart Game", state=tk.NORMAL, bg='#4CAF50')
        for button in self.buttons:
            button.config(state=tk.DISABLED)
        # Update high score if beaten
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.high_score_label.config(text=f"High Score: {self.high_score}")
            messagebox.showinfo("New High Score! 🎉", f"Congratulations! New High Score: {self.high_score}")
        else:
            messagebox.showinfo("Game Over!", f"Your final score is: {self.score} points.")
    def next_round(self, correct_guess=None):
        if not self.game_running:
            return
        self.correct_color_name = random.choice(COLOR_NAMES)
        display_word = random.choice(COLOR_NAMES)
        text_color_hex = COLOR_MAP[self.correct_color_name]
        if correct_guess is True:
            self.word_label.config(text="✔", fg='green')
            self.master.after(100, lambda: self.set_word(display_word, text_color_hex))
        elif correct_guess is False:
            self.word_label.config(text="❌", fg='red')
            self.master.after(100, lambda: self.set_word(display_word, text_color_hex))
        else:
            self.set_word(display_word, text_color_hex)
    def set_word(self, display_word, text_color_hex):
        self.word_label.config(text=display_word, fg=text_color_hex)
    def check_answer(self, chosen_color):
        if not self.game_running:
            return
        if chosen_color == self.correct_color_name:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.next_round(correct_guess=True)
        else:
            self.next_round(correct_guess=False)
    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                try:
                    return int(file.read())
                except:
                    return 0
        return 0
    def save_high_score(self):
        with open("highscore.txt", "w") as file:
            file.write(str(self.high_score))
if __name__ == "__main__":
    root = tk.Tk()
    game = ColorMatchGame(root)
    root.mainloop()
