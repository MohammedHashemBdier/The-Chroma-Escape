import pygame
import os

class SoundManager:
    def __init__(self):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Warning: Unable to initialize sound mixer. {e}")
            self.enabled = False
            return
            
        self.enabled = True
        self.sounds = {}
        self.sound_files = {
            'move': 'sounds/move.wav',
            'invalid': 'sounds/invalid.wav',
            'select': 'sounds/select.wav',
            'exit': 'sounds/exit.wav',
            'win': 'sounds/win.wav',
            'undo': 'sounds/undo.wav',
            'restart': 'sounds/restart.wav'
        }

    def load_sounds(self):
        if not self.enabled:
            return

        for name, path in self.sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"Loaded sound: {name}")
            except pygame.error as e:
                print(f"Warning: Could not load sound file {path}. {e}")
                self.sounds[name] = None

    def play(self, sound_name):
        if not self.enabled or sound_name not in self.sounds or self.sounds[sound_name] is None:
            return
        
        try:
            self.sounds[sound_name].play()
        except pygame.error as e:
            print(f"Warning: Could not play sound {sound_name}. {e}")

    def play_move(self):
        self.play('move')

    def play_invalid(self):
        self.play('invalid')

    def play_select(self):
        self.play('select')

    def play_exit(self):
        self.play('exit')

    def play_win(self):
        self.play('win')

    def play_undo(self):
        self.play('undo')

    def play_restart(self):
        self.play('restart')