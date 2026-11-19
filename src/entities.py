"""Entidades jogáveis e inimigas: Jogador, Reatores, Inimigos, Chefe e Power-Ups."""

import math
import random
import pygame

from src.config import CRIMSON, CYAN_NEON, EMERALD, HEIGHT, SOLAR_GOLD, SOLAR_ORANGE, VIOLET, WIDTH


class Projectile:
    """Projétil disparado pelo jogador ou pelos inimigos."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        from_player: bool = True,
        damage: int = 1,
        radius: int = 5,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.from_player = from_player
        self.damage = damage
        self.radius = radius
        self.rect = pygame.Rect(int(x - radius), int(y - radius), radius * 2, radius * 2)
        self.alive = True

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        if self.y < -30 or self.y > HEIGHT + 30 or self.x < -30 or self.x > WIDTH + 30:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.from_player:
            pygame.draw.rect(surface, self.color, (self.rect.x + 1, self.rect.y - 4, 6, 14), border_radius=3)
        else:
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, max(2, self.radius // 2))


class Reactor:
    """Reator Solar orbital que o jogador deve proteger na base da tela."""

    def __init__(
        self,
        x: int,
        y: int,
        index: int,
        sprite_ok: pygame.Surface,
        sprite_dmg: pygame.Surface,
    ) -> None:
        self.index = index
        self.sprite_ok = sprite_ok
        self.sprite_dmg = sprite_dmg
        self.rect = self.sprite_ok.get_rect(center=(x, y))
        self.max_hp = 100
        self.hp = 100

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def repair(self, amount: int) -> None:
        if self.hp > 0:
            self.hp = min(self.max_hp, self.hp + amount)
        else:
            self.hp = min(self.max_hp, amount)

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self.sprite_ok if self.alive else self.sprite_dmg
        surface.blit(sprite, self.rect)
        # Barra de integridade do reator
        bar_w = self.rect.width
        bar_h = 5
        bar_x = self.rect.left
        bar_y = self.rect.bottom + 3
        pygame.draw.rect(surface, (30, 40, 60), (bar_x, bar_y, bar_w, bar_h))
        if self.hp > 0:
            fill_w = int(bar_w * (self.hp / self.max_hp))
            color = EMERALD if self.hp > 50 else SOLAR_GOLD
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h))


class Player:
    """Nave intercetora AEGIS-01 controlada pelo jogador."""

    def __init__(self, x: int, y: int, sprites: list[pygame.Surface]) -> None:
        self.sprites = sprites
        self.rect = self.sprites[0].get_rect(center=(x, y))
        self.speed = 360.0
        self.max_lives = 3
        self.lives = 3
        self.invuln_timer = 0.0
        self.shoot_timer = 0.0
        self.rapid_timer = 0.0
        self.triple_timer = 0.0
        self.pem_charge = 40.0  # 0 a 100%
        self.frame_index = 0
        self.anim_timer = 0.0

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0

        if dx != 0.0 and dy != 0.0:
            inv = 0.70710678
            dx *= inv
            dy *= inv

        self.rect.x += int(dx * self.speed * dt)
        self.rect.y += int(dy * self.speed * dt)

        # Limita à zona tática inferior/central
        self.rect.left = max(16, self.rect.left)
        self.rect.right = min(WIDTH - 16, self.rect.right)
        self.rect.top = max(int(HEIGHT * 0.36), self.rect.top)
        self.rect.bottom = min(HEIGHT - 78, self.rect.bottom)

        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)
        if self.shoot_timer > 0:
            self.shoot_timer = max(0.0, self.shoot_timer - dt)
        if self.rapid_timer > 0:
            self.rapid_timer = max(0.0, self.rapid_timer - dt)
        if self.triple_timer > 0:
            self.triple_timer = max(0.0, self.triple_timer - dt)

        self.anim_timer += dt
        if self.anim_timer >= 0.08:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.sprites)

    def shoot(self) -> list[Projectile]:
        cooldown = 0.13 if self.rapid_timer > 0 else 0.24
        if self.shoot_timer > 0:
            return []
        self.shoot_timer = cooldown
        cx, top = self.rect.centerx, self.rect.top
        if self.triple_timer > 0:
            return [
                Projectile(cx, top, 0, -560, CYAN_NEON, True, 1, 5),
                Projectile(cx - 10, top + 6, -115, -540, SOLAR_GOLD, True, 1, 4),
                Projectile(cx + 10, top + 6, 115, -540, SOLAR_GOLD, True, 1, 4),
            ]
        return [Projectile(cx, top, 0, -560, CYAN_NEON, True, 1, 5)]

    def take_damage(self) -> bool:
        """Retorna True se o dano foi aplicado (não estava invulnerável)."""
        if self.invuln_timer > 0:
            return False
        self.lives = max(0, self.lives - 1)
        self.invuln_timer = 1.6
        return True

    def draw(self, surface: pygame.Surface) -> None:
        # Pisca quando está em invulnerabilidade após dano
        if self.invuln_timer > 0 and int(self.invuln_timer * 14) % 2 == 0:
            return
        surface.blit(self.sprites[self.frame_index], self.rect)
        if self.triple_timer > 0 or self.rapid_timer > 0:
            pygame.draw.circle(surface, SOLAR_GOLD, self.rect.center, 29, 1)


class Enemy:
    """Drones inimigos do Enxame Entrópico com três comportamentos distintos."""

    def __init__(
        self,
        x: int,
        y: int,
        kind: str,
        sprites: list[pygame.Surface],
        stage: int,
    ) -> None:
        self.kind = kind
        self.sprites = sprites
        self.rect = self.sprites[0].get_rect(center=(x, y))
        self.base_x = float(x)
        self.y_pos = float(y)
        self.time_alive = random.uniform(0.0, 4.0)
        self.anim_timer = 0.0
        self.frame_index = 0
        self.alive = True
        self.target_reactor_idx = random.randint(0, 2)

        speed_bonus = (stage - 1) * 18
        if kind == "batedor":
            self.hp = 1
            self.speed = 115.0 + speed_bonus
            self.points = 100
            self.shoot_timer = random.uniform(1.1, 2.3)
        elif kind == "bombardeiro":
            self.hp = 2
            self.speed = 82.0 + speed_bonus * 0.8
            self.points = 180
            self.shoot_timer = random.uniform(1.8, 3.0)
        else:  # escudado
            self.hp = 3
            self.speed = 74.0 + speed_bonus * 0.7
            self.points = 260
            self.shoot_timer = random.uniform(1.3, 2.2)

    def update(self, dt: float, reactors: list[Reactor]) -> None:
        self.time_alive += dt
        self.anim_timer += dt
        if self.anim_timer >= 0.18:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.sprites)

        self.y_pos += self.speed * dt
        if self.kind == "batedor":
            x_pos = self.base_x + math.sin(self.time_alive * 3.2) * 58
        elif self.kind == "bombardeiro":
            # Move-se em direção ao reator alvo
            alive_reactors = [r for r in reactors if r.alive]
            if alive_reactors:
                target = alive_reactors[self.target_reactor_idx % len(alive_reactors)]
                diff = target.rect.centerx - self.rect.centerx
                self.base_x += max(-65 * dt, min(65 * dt, diff * 0.8 * dt))
            x_pos = self.base_x
        else:
            x_pos = self.base_x + math.cos(self.time_alive * 2.0) * 35

        self.rect.centerx = int(max(26, min(WIDTH - 26, x_pos)))
        self.rect.centery = int(self.y_pos)

    def try_shoot(self, dt: float, player_rect: pygame.Rect) -> list[Projectile]:
        self.shoot_timer -= dt
        if self.shoot_timer > 0 or self.rect.top < 40 or self.rect.bottom > HEIGHT - 150:
            return []

        if self.kind == "batedor":
            self.shoot_timer = random.uniform(1.6, 2.6)
            return [Projectile(self.rect.centerx, self.rect.bottom, 0, 290, CRIMSON, False, 1, 5)]
        if self.kind == "escudado":
            self.shoot_timer = random.uniform(1.9, 2.9)
            dx = player_rect.centerx - self.rect.centerx
            dy = max(80, player_rect.centery - self.rect.centery)
            dist = math.hypot(dx, dy)
            vx = (dx / dist) * 260
            vy = (dy / dist) * 260
            return [Projectile(self.rect.centerx, self.rect.bottom, vx, vy, VIOLET, False, 1, 5)]
        self.shoot_timer = 2.8
        return []

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprites[self.frame_index], self.rect)


class Boss:
    """Chefe Final (Colosso Entrópico) da Fase 3."""

    def __init__(self, sprites: list[pygame.Surface]) -> None:
        self.sprites = sprites
        self.rect = self.sprites[0].get_rect(center=(WIDTH // 2, 118))
        self.max_hp = 90
        self.hp = 90
        self.vx = 135.0
        self.attack_timer = 1.4
        self.pattern = 0
        self.anim_timer = 0.0
        self.frame_index = 0
        self.alive = True

    def update(self, dt: float) -> None:
        self.anim_timer += dt
        if self.anim_timer >= 0.22:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.sprites)

        self.rect.x += int(self.vx * dt)
        if self.rect.left <= 36:
            self.rect.left = 36
            self.vx = abs(self.vx)
        elif self.rect.right >= WIDTH - 36:
            self.rect.right = WIDTH - 36
            self.vx = -abs(self.vx)

    def try_attack(self, dt: float, player_rect: pygame.Rect) -> list[Projectile]:
        self.attack_timer -= dt
        if self.attack_timer > 0:
            return []

        self.pattern = (self.pattern + 1) % 2
        cx, bottom = self.rect.centerx, self.rect.bottom
        projectiles: list[Projectile] = []
        if self.pattern == 0:
            # Leque de 5 projéteis
            self.attack_timer = 1.5
            for angle_deg in (-36, -18, 0, 18, 36):
                rad = math.radians(angle_deg)
                vx = math.sin(rad) * 270
                vy = math.cos(rad) * 270
                projectiles.append(Projectile(cx, bottom - 8, vx, vy, SOLAR_ORANGE, False, 1, 6))
        else:
            # Rajada dupla direcionada ao jogador
            self.attack_timer = 1.25
            for offset in (-46, 46):
                dx = player_rect.centerx - (cx + offset)
                dy = max(100, player_rect.centery - bottom)
                dist = math.hypot(dx, dy)
                projectiles.append(
                    Projectile(
                        cx + offset,
                        bottom - 10,
                        (dx / dist) * 310,
                        (dy / dist) * 310,
                        CRIMSON,
                        False,
                        1,
                        6,
                    )
                )
        return projectiles

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprites[self.frame_index], self.rect)


class PowerUp:
    """Cápsula de melhoria deixada pelos inimigos."""

    def __init__(self, x: int, y: int, kind: str, sprite: pygame.Surface) -> None:
        self.kind = kind
        self.sprite = sprite
        self.rect = self.sprite.get_rect(center=(x, y))
        self.vy = 125.0
        self.alive = True

    def update(self, dt: float) -> None:
        self.rect.y += int(self.vy * dt)
        if self.rect.top > HEIGHT + 20:
            self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, self.rect)