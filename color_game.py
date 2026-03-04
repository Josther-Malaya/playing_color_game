import tkinter as tk
from tkinter import messagebox
import random
import os
import pygame
from tkinter import simpledialog
class GameConfig:
    game_duration = 60
    colors = ['Red', 'Blue', 'Green', 'Pink', 'Yellow', 'Purple', 'Orange', 'Black']
    hex_codes = ['#FF0000', '#0000FF', '#008000', '#FF69B4', '#FFD700', '#8A2BE2', '#FF4500', '#000000']
    color_map = dict(zip(colors, hex_codes))
    high_score_file = 'highscore.txt'
class AudioManager:
    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init()
            pygame.mixer.music.load('01. Ground Theme.mp3')
            pygame.mixer.music.set_volume(0.3)
            self.correct_sound = pygame.mixer.Sound('mac-quack.mp3')
            self.wrong_sound = pygame.mixer.Sound('movie_1.mp3')
            self.enabled = True
        except Exception as e:
            print("Audio disabled:", e)

    def play_music(self):
        if self.enabled:
            pygame.mixer.music.play(-1)

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()

    def play_correct(self):
        if self.enabled:
            self.correct_sound.play()

    def play_wrong(self):
        if self.enabled:
            self.wrong_sound.play()

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

class LeaderboardManager:
    def __init__(self, filename="leaderboard.txt"):
        self.filename = filename
        self.max_entries = 10

    def load(self):
        if not os.path.exists(self.filename):
            return []
        leaderboard = []
        with open(self.filename, "r") as file:
            for line in file:
                name, score = line.strip().split(",")
                leaderboard.append((name, int(score)))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        return leaderboard

    def save(self, leaderboard):
        with open(self.filename, "w") as file:
            for name, score in leaderboard[:self.max_entries]:
                file.write(f"{name},{score}\n")

    def add_score(self, name, score):
        leaderboard = self.load()
        leaderboard.append((name, score))
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        leaderboard = leaderboard[:self.max_entries]
        self.save(leaderboard)
        return leaderboard

class GameEngine:
    def __init__(self, config):
        self.config = config
        self.reset()

    def reset(self):
        self.score = 0
        self.time_left = self.config.game_duration
        self.correct_color = None
        self.combo = 0

    def next_round(self):
        self.correct_color = random.choice(self.config.colors)
        display_word = random.choice(
            [c for c in self.config.colors if c != self.correct_color]
        )
        text_color = self.config.color_map[self.correct_color]
        return display_word, text_color

    def check_answer(self, choice):
        if choice == self.correct_color:
            self.combo += 1
            bonus = min(self.combo // 2, 5)
            self.score += 1 + bonus
            return True
        else:
            self.combo = 0
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
        self.high_score_label = tk.Label(
            self.info_frame,
            text=f"High Score: {self.controller.high_score}",
            font=('Arial', 14),
            bg='#3e4451',
            fg='white'
        )
        self.high_score_label.pack()
        self.main_frame = tk.Frame(self.root, bg='#282c34')
        self.main_frame.pack(expand=True, fill='both')
        self.game_frame = tk.Frame(self.main_frame, bg='#282c34')
        self.game_frame.pack(side=tk.LEFT, expand=True)
        self.leaderboard_frame = tk.Frame(self.main_frame, bg='#1f2228', width=300)
        self.leaderboard_frame.pack(side=tk.RIGHT, fill='y')
        self.lb_title = tk.Label(
            self.leaderboard_frame,
            text="🏆 Leaderboard",
            font=("Arial", 16, "bold"),
            bg="#1f2228",
            fg="gold"
        )
        self.lb_title.pack(pady=10)
        self.lb_entries = []
        for i in range(10):
            label = tk.Label(
                self.leaderboard_frame,
                text=f"{i + 1}. ---",
                font=("Arial", 12),
                bg="#1f2228",
                fg="white",
                anchor="w"
            )
            label.pack(fill="x", padx=10)
            self.lb_entries.append(label)
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
        self.combo_label = tk.Label(
            self.info_frame,
            text="Combo: 0",
            font=('Arial', 14, 'bold'),
            bg='#3e4451',
            fg='orange'
        )
        self.combo_label.pack()
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
                bg=self.config.color_map[color],
                fg='white',
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

    def show_leaderboard(self, leaderboard):
        top = tk.Toplevel(self.root)
        top.title("Leaderboard")
        top.geometry("400x400")
        top.config(bg="#282c34")
        title = tk.Label(
            top,
            text="🏆 Leaderboard 🏆",
            font=("Arial", 20, "bold"),
            bg="#282c34",
            fg="gold"
        )
        title.pack(pady=10)
        for i, (name, score) in enumerate(leaderboard, start=1):
            entry = tk.Label(
                top,
                text=f"{i}. {name} - {score}",
                font=("Arial", 16),
                bg="#282c34",
                fg="white"
            )
            entry.pack(anchor="w", padx=40)

    def update_leaderboard(self, leaderboard):
        for i in range(10):
            if i < len(leaderboard):
                name, score = leaderboard[i]
                self.lb_entries[i].config(text=f"{i + 1}. {name} - {score}")
            else:
                self.lb_entries[i].config(text=f"{i + 1}. ---")

    def update_combo(self, combo):
        if combo <= 1:
            self.combo_label.config(
                text="Combo: 0",
                fg="orange",
                font=('Arial', 14, 'bold')
            )
        elif combo < 5:
            self.combo_label.config(
                text=f"🔥 Combo: {combo}",
                fg="orange",
                font=('Arial', 16, 'bold')
            )
        elif combo < 10:
            self.combo_label.config(
                text=f"🔥🔥 COMBO x{combo}!",
                fg="red",
                font=('Arial', 18, 'bold')
            )
        else:
            self.combo_label.config(
                text=f"💥 ULTRA COMBO x{combo} 💥",
                fg="gold",
                font=('Arial', 20, 'bold')
            )
            
class ColorMatchGame:
    def __init__(self, root):
        self.config = GameConfig()
        self.engine = GameEngine(self.config)
        self.storage = HighScoreManager(self.config.high_score_file)
        self.high_score = self.storage.load()
        self.ui = GameUi(root, self, self.config)
        self.timer_id = None
        self.game_running = False
        self.audio = AudioManager()
        self.leaderboard = LeaderboardManager()
        self.ui.update_leaderboard(self.leaderboard.load())

    def start_game(self):
        self.engine.reset()
        self.game_running = True
        self.ui.toggle_buttons(tk.NORMAL)
        self.ui.update_score(0)
        self.ui.update_combo(0)
        self.audio.play_music()
        self.countdown()
        self.new_round()
        self.ui.start_button.config(state=tk.DISABLED)

    def new_round(self):
        word, color = self.engine.next_round()
        self.ui.update_word(word, color)
        self.ui.toggle_buttons(tk.NORMAL)

    def handle_guess(self, choice):
        if not self.game_running:
            return
        correct = self.engine.check_answer(choice)
        self.ui.update_score(self.engine.score)
        self.ui.update_combo(self.engine.combo)
        self.ui.show_feedback(correct)
        self.ui.toggle_buttons(tk.DISABLED)
        if correct:
            self.audio.play_correct()
        else:
            self.audio.play_wrong()
        self.ui.root.after(300, self.new_round)

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
        self.ui.start_button.config(text="Restart Game", state=tk.NORMAL)
        if self.timer_id:
            self.ui.root.after_cancel(self.timer_id)
        self.ui.toggle_buttons(tk.DISABLED)
        self.audio.stop_music()
        score = self.engine.score
        new_record = False
        if score > self.high_score:
            self.high_score = score
            self.storage.save(self.high_score)
            new_record = True
        self.ui.high_score_label.config(text=f"High Score: {self.high_score}")
        name = simpledialog.askstring("Game Over", "Enter your name:")
        if name:
            leaderboard = self.leaderboard.add_score(name, score)
            self.ui.update_leaderboard(leaderboard)
        self.ui.show_game_over(score, self.high_score, new_record)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorMatchGame(root)
    root.mainloop()