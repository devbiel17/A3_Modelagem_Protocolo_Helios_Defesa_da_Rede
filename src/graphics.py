"""Gerador de sprites originais, fundo espacial parallax e sistema de partículas."""

import math
import os
import random
import pygame

from src.config import (
    ASSETS_IMG_DIR,
    BG_DEEP,
    CRIMSON,
    CYAN_NEON,
    EMERALD,
    GRID_LINE,
    HEIGHT,
    SOLAR_GOLD,
    SOLAR_ORANGE,
    VIOLET,
    WHITE,
    WIDTH,
)


def _save_and_return(surface: pygame.Surface, filename: str) -> pygame.Surface:
    os.makedirs(ASSETS_IMG_DIR, exist_ok=True)
    pygame.image.save(surface, os.path.join(ASSETS_IMG_DIR, filename))
    return surface


def build_sprites() -> dict[str, list[pygame.Surface] | pygame.Surface]:
    """Cria e guarda os sprites originais do jogo em assets/img/."""
    sprites: dict[str, list[pygame.Surface] | pygame.Surface] = {}

    # 1. Nave do Jogador (4 quadros de animação do propulsor)
    nave_frames = []
    for frame in range(4):
        surf = pygame.Surface((48, 52), pygame.SRCALPHA)
        flame_len = 8 + (frame % 3) * 4
        # Propulsores duplos
        pygame.draw.polygon(surf, SOLAR_ORANGE, [(15, 40), (19, 40 + flame_len), (23, 40)])
        pygame.draw.polygon(surf, SOLAR_ORANGE, [(25, 40), (29, 40 + flame_len), (33, 40)])
        pygame.draw.polygon(surf, SOLAR_GOLD, [(17, 40), (19, 37 + flame_len), (21, 40)])
        pygame.draw.polygon(surf, SOLAR_GOLD, [(27, 40), (29, 37 + flame_len), (31, 40)])
        # Asas e fuselagem
        pygame.draw.polygon(surf, (32, 92, 148), [(24, 4), (4, 38), (16, 40), (24, 32), (32, 40), (44, 38)])
        pygame.draw.polygon(surf, CYAN_NEON, [(24, 2), (14, 34), (24, 28), (34, 34)])
        # Cabine
        pygame.draw.ellipse(surf, WHITE, (20, 14, 8, 12))
        pygame.draw.ellipse(surf, (15, 40, 80), (21, 16, 6, 8))
        nave_frames.append(_save_and_return(surf, f"nave_{frame}.png"))
    sprites["player"] = nave_frames

    # 2. Inimigo Batedor (2 quadros)
    batedor_frames = []
    for frame in range(2):
        surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        wing_offset = 2 if frame == 0 else -2
        pygame.draw.polygon(
            surf,
            CRIMSON,
            [(18, 34), (2, 10 + wing_offset), (12, 14), (18, 4), (24, 14), (34, 10 + wing_offset)],
        )
        pygame.draw.circle(surf, SOLAR_GOLD, (18, 18), 5)
        batedor_frames.append(_save_and_return(surf, f"inimigo_batedor_{frame}.png"))
    sprites["batedor"] = batedor_frames

    # 3. Inimigo Bombardeiro (2 quadros)
    bomb_frames = []
    for frame in range(2):
        surf = pygame.Surface((44, 42), pygame.SRCALPHA)
        pygame.draw.rect(surf, SOLAR_ORANGE, (6, 8, 32, 26), border_radius=8)
        pygame.draw.rect(surf, (85, 30, 18), (10, 12, 24, 18), border_radius=5)
        core_r = 6 if frame == 0 else 8
        pygame.draw.circle(surf, SOLAR_GOLD, (22, 21), core_r)
        pygame.draw.rect(surf, CRIMSON, (12, 34, 6, 6))
        pygame.draw.rect(surf, CRIMSON, (26, 34, 6, 6))
        bomb_frames.append(_save_and_return(surf, f"inimigo_bombardeiro_{frame}.png"))
    sprites["bombardeiro"] = bomb_frames

    # 4. Inimigo Escudado (2 quadros)
    esc_frames = []
    for frame in range(2):
        surf = pygame.Surface((46, 44), pygame.SRCALPHA)
        pygame.draw.polygon(surf, VIOLET, [(23, 40), (4, 18), (12, 6), (34, 6), (42, 18)])
        pygame.draw.circle(surf, WHITE, (23, 20), 6)
        alpha = 150 if frame == 0 else 90
        shield_surf = pygame.Surface((46, 44), pygame.SRCALPHA)
        pygame.draw.arc(shield_surf, (0, 229, 255, alpha), (2, 4, 42, 38), 3.14, 6.28, 3)
        surf.blit(shield_surf, (0, 0))
        esc_frames.append(_save_and_return(surf, f"inimigo_escudado_{frame}.png"))
    sprites["escudado"] = esc_frames

    # 5. Chefe Final: Colosso Entrópico (2 quadros)
    boss_frames = []
    for frame in range(2):
        surf = pygame.Surface((164, 96), pygame.SRCALPHA)
        pygame.draw.polygon(
            surf,
            (95, 22, 48),
            [(82, 92), (10, 56), (4, 24), (36, 6), (128, 6), (160, 24), (154, 56)],
        )
        pygame.draw.polygon(
            surf,
            CRIMSON,
            [(82, 82), (24, 50), (22, 24), (48, 12), (116, 12), (142, 24), (140, 50)],
        )
        # Canhões laterais
        pygame.draw.rect(surf, SOLAR_ORANGE, (26, 56, 14, 22), border_radius=3)
        pygame.draw.rect(surf, SOLAR_ORANGE, (124, 56, 14, 22), border_radius=3)
        # Núcleo central pulsante
        core_radius = 16 if frame == 0 else 20
        pygame.draw.circle(surf, SOLAR_GOLD, (82, 44), core_radius)
        pygame.draw.circle(surf, WHITE, (82, 44), 8)
        boss_frames.append(_save_and_return(surf, f"chefe_{frame}.png"))
    sprites["boss"] = boss_frames

    # 6. Reatores Solares (Ativo e Danificado)
    r_ok = pygame.Surface((74, 34), pygame.SRCALPHA)
    pygame.draw.rect(r_ok, (24, 58, 92), (2, 6, 70, 24), border_radius=6)
    pygame.draw.rect(r_ok, CYAN_NEON, (2, 6, 70, 24), 2, border_radius=6)
    pygame.draw.circle(r_ok, SOLAR_GOLD, (37, 18), 8)
    sprites["reactor_ok"] = _save_and_return(r_ok, "reator_ativo.png")

    r_dmg = pygame.Surface((74, 34), pygame.SRCALPHA)
    pygame.draw.rect(r_dmg, (55, 24, 32), (2, 6, 70, 24), border_radius=6)
    pygame.draw.rect(r_dmg, CRIMSON, (2, 6, 70, 24), 2, border_radius=6)
    pygame.draw.line(r_dmg, SOLAR_ORANGE, (20, 10), (54, 26), 2)
    pygame.draw.line(r_dmg, SOLAR_ORANGE, (54, 10), (20, 26), 2)
    sprites["reactor_dmg"] = _save_and_return(r_dmg, "reator_danificado.png")

    # 7. Power-Ups
    pw_configs = {
        "triplo": (CYAN_NEON, "T"),
        "rapido": (SOLAR_GOLD, "R"),
        "reparo": (EMERALD, "+"),
    }
    font = pygame.font.SysFont("arial", 15, bold=True)
    for kind, (color, label) in pw_configs.items():
        surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(surf, (15, 25, 45), (14, 14), 13)
        pygame.draw.circle(surf, color, (14, 14), 13, 2)
        txt = font.render(label, True, WHITE)
        surf.blit(txt, (14 - txt.get_width() // 2, 14 - txt.get_height() // 2))
        sprites[f"pw_{kind}"] = _save_and_return(surf, f"powerup_{kind}.png")

    return sprites


class Starfield:
    """Campo estelar animado com efeito parallax em 3 camadas."""

    def __init__(self) -> None:
        self.stars: list[list[float]] = []
        rng = random.Random(101)
        for _ in range(75):
            layer = rng.choice([1, 2, 3])
            self.stars.append(
                [
                    rng.uniform(0, WIDTH),
                    rng.uniform(0, HEIGHT),
                    float(layer * 24),
                    float(layer),
                ]
            )
        self.grid_offset = 0.0

    def update(self, dt: float) -> None:
        self.grid_offset = (self.grid_offset + 28 * dt) % 48
        for s in self.stars:
            s[1] += s[2] * dt
            if s[1] > HEIGHT:
                s[1] = 0.0
                s[0] = random.uniform(0, WIDTH)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DEEP)
        # Grade energética sutil de fundo
        for x in range(0, WIDTH, 48):
            pygame.draw.line(surface, GRID_LINE, (x, 0), (x, HEIGHT), 1)
        y = int(self.grid_offset)
        while y < HEIGHT:
            pygame.draw.line(surface, GRID_LINE, (0, y), (WIDTH, y), 1)
            y += 48

        for x, y_pos, _, size in self.stars:
            brightness = 110 + int(size * 45)
            color = (brightness, brightness, min(255, brightness + 25))
            pygame.draw.circle(surface, color, (int(x), int(y_pos)), int(size))


class ParticleSystem:
    """Sistema de partículas para explosões, impactos e feedback visual."""

    def __init__(self) -> None:
        self.particles: list[dict] = []
        self.floating_texts: list[dict] = []

    def emit_explosion(self, x: float, y: float, color: tuple[int, int, int], count: int = 16) -> None:
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(55, 230)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(0.25, 0.55),
                    "max_life": 0.55,
                    "color": color,
                    "size": random.randint(2, 5),
                }
            )

    def emit_text(self, x: float, y: float, text: str, color: tuple[int, int, int]) -> None:
        self.floating_texts.append(
            {"x": x, "y": y, "text": text, "color": color, "life": 0.85}
        )

    def update(self, dt: float) -> None:
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

        for ft in self.floating_texts:
            ft["y"] -= 34 * dt
            ft["life"] -= dt
        self.floating_texts = [ft for ft in self.floating_texts if ft["life"] > 0]

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for p in self.particles:
            ratio = max(0.0, p["life"] / p["max_life"])
            radius = max(1, int(p["size"] * ratio))
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), radius)

        for ft in self.floating_texts:
            img = font.render(ft["text"], True, ft["color"])
            surface.blit(img, (int(ft["x"] - img.get_width() // 2), int(ft["y"])))
            