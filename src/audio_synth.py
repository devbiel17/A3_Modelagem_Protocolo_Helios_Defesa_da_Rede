"""Gerador procedural de efeitos sonoros/músicas WAV e gestor de áudio."""

import math
import os
import random
import struct
import wave
import pygame

from src.config import ASSETS_SONS_DIR


def _write_wav(filepath: str, samples: list[float], sample_rate: int = 22050) -> None:
    """Guarda uma lista de amostras normalizadas [-1.0, 1.0] num ficheiro WAV 16-bit."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            frames.extend(struct.pack("<h", int(clamped * 32767)))
        wf.writeframes(bytes(frames))


def ensure_audio_assets() -> None:
    """Gera os ficheiros WAV originais em assets/sons/ caso ainda não existam."""
    os.makedirs(ASSETS_SONS_DIR, exist_ok=True)
    sr = 22050

    # 1. Tiro laser
    tiro_path = os.path.join(ASSETS_SONS_DIR, "tiro.wav")
    if not os.path.exists(tiro_path):
        dur = 0.11
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            freq = 920 - 620 * (t / dur)
            env = (1.0 - t / dur) ** 1.5
            samples.append(0.35 * env * math.sin(2 * math.pi * freq * t))
        _write_wav(tiro_path, samples, sr)

    # 2. Explosão
    exp_path = os.path.join(ASSETS_SONS_DIR, "explosao.wav")
    if not os.path.exists(exp_path):
        dur = 0.28
        n = int(sr * dur)
        rng = random.Random(42)
        samples = []
        low_pass = 0.0
        for i in range(n):
            t = i / sr
            env = (1.0 - t / dur) ** 2.0
            noise = rng.uniform(-1.0, 1.0)
            low_pass = 0.82 * low_pass + 0.18 * noise
            boom = math.sin(2 * math.pi * (95 - 55 * (t / dur)) * t)
            samples.append(0.55 * env * (0.65 * low_pass + 0.35 * boom))
        _write_wav(exp_path, samples, sr)

    # 3. Power-up (arpejo ascendente)
    pw_path = os.path.join(ASSETS_SONS_DIR, "powerup.wav")
    if not os.path.exists(pw_path):
        notes = [523.25, 659.25, 783.99, 1046.50]
        note_dur = 0.065
        samples = []
        for freq in notes:
            n = int(sr * note_dur)
            for i in range(n):
                t = i / sr
                env = math.sin(math.pi * (t / note_dur))
                samples.append(0.35 * env * math.sin(2 * math.pi * freq * t))
        _write_wav(pw_path, samples, sr)

    # 4. Dano sofrido
    dano_path = os.path.join(ASSETS_SONS_DIR, "dano.wav")
    if not os.path.exists(dano_path):
        dur = 0.22
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            freq = 160 - 70 * (t / dur)
            env = 1.0 - (t / dur)
            sq = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            samples.append(0.35 * env * sq)
        _write_wav(dano_path, samples, sr)

    # 5. Pulso PEM
    pem_path = os.path.join(ASSETS_SONS_DIR, "pem.wav")
    if not os.path.exists(pem_path):
        dur = 0.50
        n = int(sr * dur)
        samples = []
        for i in range(n):
            t = i / sr
            freq = 480 * ((0.18) ** (t / dur)) + 55
            env = math.sin(math.pi * min(1.0, t / 0.05)) * (1.0 - t / dur)
            samples.append(0.5 * env * math.sin(2 * math.pi * freq * t))
        _write_wav(pem_path, samples, sr)

    # 6. Vitória
    vit_path = os.path.join(ASSETS_SONS_DIR, "vitoria.wav")
    if not os.path.exists(vit_path):
        melody = [(523.25, 0.14), (659.25, 0.14), (783.99, 0.14), (1046.50, 0.45)]
        samples = []
        for freq, d in melody:
            n = int(sr * d)
            for i in range(n):
                t = i / sr
                env = min(1.0, t / 0.02) * (1.0 - 0.6 * (t / d))
                samples.append(0.35 * env * math.sin(2 * math.pi * freq * t))
        _write_wav(vit_path, samples, sr)

    # 7. Derrota
    der_path = os.path.join(ASSETS_SONS_DIR, "derrota.wav")
    if not os.path.exists(der_path):
        melody = [(392.00, 0.18), (349.23, 0.18), (311.13, 0.18), (261.63, 0.50)]
        samples = []
        for freq, d in melody:
            n = int(sr * d)
            for i in range(n):
                t = i / sr
                env = min(1.0, t / 0.02) * (1.0 - 0.5 * (t / d))
                samples.append(0.35 * env * math.sin(2 * math.pi * freq * t))
        _write_wav(der_path, samples, sr)

    # 8. Música do Menu (loop ambiente em Ré menor)
    menu_music = os.path.join(ASSETS_SONS_DIR, "musica_menu.wav")
    if not os.path.exists(menu_music):
        arp = [293.66, 349.23, 440.00, 523.25, 440.00, 349.23, 329.63, 440.00] * 4
        step_dur = 0.20
        samples = []
        for idx, freq in enumerate(arp):
            n = int(sr * step_dur)
            bass = 146.83 if idx < 16 else 110.00
            for i in range(n):
                t = i / sr
                env = math.sin(math.pi * (t / step_dur))
                lead = 0.14 * env * math.sin(2 * math.pi * freq * t)
                pad = 0.10 * math.sin(2 * math.pi * bass * t)
                samples.append(lead + pad)
        _write_wav(menu_music, samples, sr)

    # 9. Música da Partida (loop rítmico em Lá menor)
    game_music = os.path.join(ASSETS_SONS_DIR, "musica_partida.wav")
    if not os.path.exists(game_music):
        bass_seq = [110.0, 110.0, 130.81, 146.83, 164.81, 164.81, 146.83, 130.81] * 4
        lead_seq = [440.0, 0.0, 523.25, 659.25, 587.33, 523.25, 493.88, 392.0] * 4
        step_dur = 0.16
        samples = []
        for b_freq, l_freq in zip(bass_seq, lead_seq):
            n = int(sr * step_dur)
            for i in range(n):
                t = i / sr
                env = 1.0 - 0.65 * (t /step_dur)
                b_wave = 0.16 * env * (1.0 if math.sin(2 * math.pi * b_freq * t) >= 0 else -1.0)
                l_wave = 0.12 * env * math.sin(2 * math.pi * l_freq * t) if l_freq > 0 else 0.0
                samples.append(b_wave + l_wave)
        _write_wav(game_music, samples, sr)


class AudioManager:
    """Controla efeitos sonoros (Sound) e trilhas em loop (music) com mute e volume."""

    def __init__(self) -> None:
        self.enabled = False
        self.muted = False
        self.volume = 0.65
        self.current_track = ""
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        ensure_audio_assets()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            sfx_names = ["tiro", "explosao", "powerup", "dano", "pem", "vitoria", "derrota"]
            for name in sfx_names:
                path = os.path.join(ASSETS_SONS_DIR, f"{name}.wav")
                snd = pygame.mixer.Sound(path)
                snd.set_volume(self.volume)
                self.sounds[name] = snd
        except pygame.error:
            # Permite jogar mesmo em computadores sem placa de som ativa
            self.enabled = False

    def play_sfx(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.set_volume(self.volume)
            snd.play()

    def play_music(self, track_name: str) -> None:
        if not self.enabled or self.current_track == track_name:
            return
        path = os.path.join(ASSETS_SONS_DIR, f"{track_name}.wav")
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.0 if self.muted else self.volume * 0.6)
                pygame.mixer.music.play(-1)
                self.current_track = track_name
            except pygame.error:
                pass

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.music.set_volume(0.0 if self.muted else self.volume * 0.6)

    def change_volume(self, delta: float) -> None:
        self.volume = max(0.1, min(1.0, round(self.volume + delta, 2)))
        if self.muted:
            self.muted = False
        if self.enabled:
            pygame.mixer.music.set_volume(self.volume * 0.6)