"""Máquina de estados principal, HUD, regras de progressão e telas do jogo."""

import asyncio
import json
import os
import random
import pygame

from src.audio_synth import AudioManager
from src.config import (
    CRIMSON,
    CYAN_NEON,
    DEFEAT_TEXT,
    EMERALD,
    FPS,
    HEIGHT,
    HIGHSCORE_FILE,
    INTRO_TEXT,
    MUTED_TEXT,
    PANEL_BG,
    PANEL_BORDER,
    SOLAR_GOLD,
    SOLAR_ORANGE,
    STAGE_TRANSITIONS,
    TITLE,
    VICTORY_TEXT,
    VIOLET,
    WHITE,
    WIDTH,
)
from src.entities import Boss, Enemy, Player, PowerUp, Projectile, Reactor
from src.graphics import ParticleSystem, Starfield, build_sprites


class Game:
    """Controla o ciclo principal (entrada, atualização, desenho) e todos os estados."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Fontes legíveis e proporcionais
        self.font_title = pygame.font.SysFont("arial", 40, bold=True)
        self.font_sub = pygame.font.SysFont("arial", 22, bold=True)
        self.font_body = pygame.font.SysFont("arial", 18)
        self.font_hud = pygame.font.SysFont("arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("arial", 14)

        self.audio = AudioManager()
        self.sprites = build_sprites()
        self.starfield = Starfield()
        self.particles = ParticleSystem()

        self.highscore = self._load_highscore()
        self.state = "MENU"
        self.running = True

        # Variáveis de partida
        self.score = 0
        self.new_record = False
        self.stage = 1
        self.stage_kills = 0
        self.stage_target = 10
        self.spawn_timer = 1.0
        self.shake_timer = 0.0
        self.shake_intensity = 0
        self.intro_chars = 0.0

        self.player: Player | None = None
        self.reactors: list[Reactor] = []
        self.enemies: list[Enemy] = []
        self.projectiles: list[Projectile] = []
        self.powerups: list[PowerUp] = []
        self.boss: Boss | None = None

        self.audio.play_music("musica_menu")

    def _load_highscore(self) -> int:
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return int(data.get("highscore", 0))
            except (OSError, ValueError, json.JSONDecodeError):
                return 0
        return 0

    def _save_highscore(self) -> None:
        if self.score > self.highscore:
            self.highscore = self.score
            self.new_record = True
            try:
                with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                    json.dump({"highscore": self.highscore}, f, indent=2)
            except OSError:
                pass

    def start_new_game(self, skip_intro: bool = False) -> None:
        self.score = 0
        self.new_record = False
        self.stage = 1
        self.particles = ParticleSystem()
        self.player = Player(WIDTH // 2, HEIGHT - 115, self.sprites["player"])
        reactor_positions = [WIDTH // 4, WIDTH // 2, (WIDTH * 3) // 4]
        self.reactors = [
            Reactor(x, HEIGHT - 42, idx, self.sprites["reactor_ok"], self.sprites["reactor_dmg"])
            for idx, x in enumerate(reactor_positions)
        ]
        self._setup_stage(1)
        if skip_intro:
            self.state = "PLAYING"
            self.audio.play_music("musica_partida")
        else:
            self.intro_chars = 0.0
            self.state = "INTRO"

    def _setup_stage(self, stage: int) -> None:
        self.stage = stage
        self.stage_kills = 0
        self.enemies.clear()
        self.projectiles.clear()
        self.powerups.clear()
        self.boss = None
        self.spawn_timer = 0.8

        if stage == 1:
            self.stage_target = 10
        elif stage == 2:
            self.stage_target = 15
        else:
            self.stage_target = 12  # Após 12 inimigos surge o Chefe Final

    def trigger_shake(self, duration: float = 0.18, intensity: int = 6) -> None:
        self.shake_timer = duration
        self.shake_intensity = intensity

    async def run(self) -> None:
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            self._handle_events()
            self._update(dt)
            self._draw()
            await asyncio.sleep(0)
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type != pygame.KEYDOWN:
                continue

            # Controles globais de áudio
            if event.key == pygame.K_m:
                self.audio.toggle_mute()
            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                self.audio.change_volume(0.1)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.audio.change_volume(-0.1)

            if self.state == "MENU":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.start_new_game(skip_intro=False)
                elif event.key == pygame.K_F1:
                    self.start_new_game(skip_intro=True)

            elif self.state == "INTRO":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    total_chars = sum(len(line) for line in INTRO_TEXT)
                    if self.intro_chars < total_chars:
                        self.intro_chars = float(total_chars)
                    else:
                        self.state = "PLAYING"
                        self.audio.play_music("musica_partida")

            elif self.state == "PLAYING":
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = "PAUSED"
                elif event.key == pygame.K_r:
                    self.start_new_game(skip_intro=True)
                elif event.key in (pygame.K_e, pygame.K_x):
                    self._activate_pem()

            elif self.state == "PAUSED":
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = "PLAYING"
                elif event.key == pygame.K_r:
                    self.start_new_game(skip_intro=True)
                elif event.key == pygame.K_q:
                    self.state = "MENU"
                    self.audio.play_music("musica_menu")

            elif self.state == "STAGE_CLEAR":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._setup_stage(self.stage + 1)
                    self.state = "PLAYING"

            elif self.state in ("VICTORY", "GAME_OVER"):
                if event.key in (pygame.K_RETURN, pygame.K_r):
                    self.start_new_game(skip_intro=True)
                elif event.key == pygame.K_ESCAPE:
                    self.state = "MENU"
                    self.audio.play_music("musica_menu")

    def _activate_pem(self) -> None:
        if not self.player or self.player.pem_charge < 100.0:
            return
        self.player.pem_charge = 0.0
        self.audio.play_sfx("pem")
        self.trigger_shake(0.32, 10)
        self.particles.emit_explosion(self.player.rect.centerx, self.player.rect.centery, CYAN_NEON, 40)
        self.particles.emit_text(self.player.rect.centerx, self.player.rect.top - 20, "PULSO PEM ATIVADO!", CYAN_NEON)

        # Limpa projéteis inimigos e causa dano em área
        self.projectiles = [p for p in self.projectiles if p.from_player]
        for enemy in self.enemies:
            enemy.hp -= 3
            if enemy.hp <= 0:
                enemy.alive = False
                self._on_enemy_destroyed(enemy)
        if self.boss and self.boss.alive:
            self.boss.hp -= 16
            self.particles.emit_explosion(self.boss.rect.centerx, self.boss.rect.centery, SOLAR_GOLD, 24)
            if self.boss.hp <= 0:
                self._on_boss_defeated()

    def _update(self, dt: float) -> None:
        self.starfield.update(dt)
        self.particles.update(dt)

        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)

        if self.state == "INTRO":
            self.intro_chars += 55.0 * dt
            return

        if self.state != "PLAYING" or not self.player:
            return

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        if keys[pygame.K_SPACE] or keys[pygame.K_z]:
            new_shots = self.player.shoot()
            if new_shots:
                self.projectiles.extend(new_shots)
                self.audio.play_sfx("tiro")

        # Geração de ondas de inimigos
        self._update_spawner(dt)

        # Atualização de projéteis
        for proj in self.projectiles:
            proj.update(dt)

        # Atualização de inimigos
        for enemy in self.enemies:
            enemy.update(dt, self.reactors)
            self.projectiles.extend(enemy.try_shoot(dt, self.player.rect))

            # Colisão inimigo com reatores na base
            for reactor in self.reactors:
                if reactor.alive and enemy.rect.colliderect(reactor.rect):
                    enemy.alive = False
                    reactor.take_damage(35)
                    self.audio.play_sfx("dano")
                    self.trigger_shake(0.22, 8)
                    self.particles.emit_explosion(reactor.rect.centerx, reactor.rect.top, SOLAR_ORANGE, 20)
                    self.particles.emit_text(reactor.rect.centerx, reactor.rect.top - 12, "-35 REATOR!", CRIMSON)
                    break

            if enemy.alive and enemy.rect.top > HEIGHT:
                enemy.alive = False
                alive_r = [r for r in self.reactors if r.alive]
                if alive_r:
                    target_r = random.choice(alive_r)
                    target_r.take_damage(20)
                    self.audio.play_sfx("dano")

            # Colisão inimigo com jogador
            if enemy.alive and enemy.rect.colliderect(self.player.rect.inflate(-10, -10)):
                enemy.alive = False
                self.particles.emit_explosion(enemy.rect.centerx, enemy.rect.centery, CRIMSON, 16)
                if self.player.take_damage():
                    self.audio.play_sfx("dano")
                    self.trigger_shake(0.25, 9)

        # Atualização do Chefe Final
        if self.boss and self.boss.alive:
            self.boss.update(dt)
            self.projectiles.extend(self.boss.try_attack(dt, self.player.rect))
            if self.boss.rect.colliderect(self.player.rect.inflate(-12, -12)):
                if self.player.take_damage():
                    self.audio.play_sfx("dano")
                    self.trigger_shake(0.25, 9)

        # Atualização de Power-Ups
        for pw in self.powerups:
            pw.update(dt)
            if pw.alive and pw.rect.colliderect(self.player.rect):
                pw.alive = False
                self.audio.play_sfx("powerup")
                self.score += 75
                if pw.kind == "triplo":
                    self.player.triple_timer = 8.0
                    self.particles.emit_text(self.player.rect.centerx, self.player.rect.top, "TIRO TRIPLO!", CYAN_NEON)
                elif pw.kind == "rapido":
                    self.player.rapid_timer = 8.0
                    self.particles.emit_text(self.player.rect.centerx, self.player.rect.top, "CADÊNCIA RÁPIDA!", SOLAR_GOLD)
                elif pw.kind == "reparo":
                    damaged = sorted(self.reactors, key=lambda r: r.hp)
                    damaged[0].repair(40)
                    self.particles.emit_text(self.player.rect.centerx, self.player.rect.top, "REATOR REPARADO!", EMERALD)

        self._resolve_projectile_collisions()

        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.powerups = [pw for pw in self.powerups if pw.alive]

        self._check_stage_and_end_conditions()

    def _update_spawner(self, dt: float) -> None:
        if self.stage == 3 and self.stage_kills >= self.stage_target:
            if self.boss is None and not self.enemies:
                self.boss = Boss(self.sprites["boss"])
                self.particles.emit_text(WIDTH // 2, 180, "ALERTA: COLOSSO ENTRÓPICO!", CRIMSON)
            return

        if self.stage_kills + len(self.enemies) >= self.stage_target:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = max(0.65, 1.45 - self.stage * 0.22)
            x = random.randint(55, WIDTH - 55)
            if self.stage == 1:
                kind = random.choices(["batedor", "bombardeiro"], weights=[70, 30])[0]
            elif self.stage == 2:
                kind = random.choices(["batedor", "bombardeiro", "escudado"], weights=[45, 30, 25])[0]
            else:
                kind = random.choices(["batedor", "bombardeiro", "escudado"], weights=[35, 30, 35])[0]
            self.enemies.append(Enemy(x, -28, kind, self.sprites[kind], self.stage))

    def _resolve_projectile_collisions(self) -> None:
        if not self.player:
            return
        for proj in self.projectiles:
            if not proj.alive:
                continue
            if proj.from_player:
                for enemy in self.enemies:
                    if enemy.alive and proj.rect.colliderect(enemy.rect):
                        proj.alive = False
                        enemy.hp -= proj.damage
                        self.particles.emit_explosion(proj.x, proj.y, CYAN_NEON, 6)
                        if enemy.hp <= 0:
                            enemy.alive = False
                            self._on_enemy_destroyed(enemy)
                        break

                if proj.alive and self.boss and self.boss.alive and proj.rect.colliderect(self.boss.rect.inflate(-16, -12)):
                    proj.alive = False
                    self.boss.hp -= proj.damage
                    self.particles.emit_explosion(proj.x, proj.y, SOLAR_GOLD, 8)
                    if self.boss.hp <= 0:
                        self._on_boss_defeated()
            else:
                if proj.rect.colliderect(self.player.rect.inflate(-12, -12)):
                    proj.alive = False
                    if self.player.take_damage():
                        self.audio.play_sfx("dano")
                        self.trigger_shake(0.22, 8)
                        self.particles.emit_explosion(self.player.rect.centerx, self.player.rect.centery, CRIMSON, 18)

    def _on_enemy_destroyed(self, enemy: Enemy) -> None:
        self.score += enemy.points
        self.stage_kills += 1
        self.audio.play_sfx("explosao")
        self.trigger_shake(0.10, 4)
        self.particles.emit_explosion(enemy.rect.centerx, enemy.rect.centery, SOLAR_ORANGE, 18)
        self.particles.emit_text(enemy.rect.centerx, enemy.rect.centery, f"+{enemy.points}", WHITE)

        if self.player:
            self.player.pem_charge = min(100.0, self.player.pem_charge + 14.0)

        # Probabilidade de soltar Power-Up
        drop_chance = 0.35 if enemy.kind == "escudado" else 0.20
        if random.random() < drop_chance:
            kind = random.choice(["triplo", "rapido", "reparo"])
            self.powerups.append(PowerUp(enemy.rect.centerx, enemy.rect.centery, kind, self.sprites[f"pw_{kind}"]))

    def _on_boss_defeated(self) -> None:
        if not self.boss:
            return
        self.boss.alive = False
        self.score += 1500
        self.audio.play_sfx("explosao")
        self.trigger_shake(0.45, 12)
        self.particles.emit_explosion(self.boss.rect.centerx, self.boss.rect.centery, SOLAR_GOLD, 55)
        self._save_highscore()
        self.audio.play_sfx("vitoria")
        self.state = "VICTORY"

    def _check_stage_and_end_conditions(self) -> None:
        if not self.player:
            return
        # Derrota: perdeu todas as vidas ou todos os 3 reatores foram destruídos
        if self.player.lives <= 0 or not any(r.alive for r in self.reactors):
            self._save_highscore()
            self.audio.play_sfx("derrota")
            self.state = "GAME_OVER"
            return

        # Avanço de fase
        if self.stage in (1, 2) and self.stage_kills >= self.stage_target and not self.enemies:
            self.score += 300 * self.stage
            self.audio.play_sfx("powerup")
            self.state = "STAGE_CLEAR"

    def _draw(self) -> None:
        canvas = pygame.Surface((WIDTH, HEIGHT))
        self.starfield.draw(canvas)

        if self.state == "MENU":
            self._draw_menu(canvas)
        elif self.state == "INTRO":
            self._draw_narrative_screen(canvas, INTRO_TEXT, "Pressione ENTER para avançar / iniciar missão", typewriter=True)
        elif self.state in ("PLAYING", "PAUSED"):
            self._draw_gameplay(canvas)
            if self.state == "PAUSED":
                self._draw_pause_overlay(canvas)
        elif self.state == "STAGE_CLEAR":
            lines = STAGE_TRANSITIONS.get(self.stage + 1, [])
            self._draw_narrative_screen(canvas, lines, "Pressione ENTER para iniciar a próxima fase")
        elif self.state == "VICTORY":
            self._draw_end_screen(canvas, VICTORY_TEXT, EMERALD)
        elif self.state == "GAME_OVER":
            self._draw_end_screen(canvas, DEFEAT_TEXT, CRIMSON)

        # Aplica tremor de câmera (screen shake) no impacto
        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        self.screen.fill((0, 0, 0))
        self.screen.blit(canvas, (offset_x, offset_y))
        pygame.display.flip()

    def _draw_menu(self, surf: pygame.Surface) -> None:
        title_img = self.font_title.render("PROTOCOLO HELIOS", True, CYAN_NEON)
        sub_img = self.font_sub.render("DEFESA DA REDE ORBITAL", True, SOLAR_GOLD)
        surf.blit(title_img, (WIDTH // 2 - title_img.get_width() // 2, 68))
        surf.blit(sub_img, (WIDTH // 2 - sub_img.get_width() // 2, 118))

        # Pré-visualização animada da nave
        frame = (pygame.time.get_ticks() // 90) % 4
        ship = pygame.transform.scale2x(self.sprites["player"][frame])
        surf.blit(ship, (WIDTH // 2 - ship.get_width() // 2, 165))

        # Painel de controles e objetivos
        panel = pygame.Rect(WIDTH // 2 - 330, 280, 660, 225)
        pygame.draw.rect(surf, PANEL_BG, panel, border_radius=12)
        pygame.draw.rect(surf, PANEL_BORDER, panel, 2, border_radius=12)

        instructions = [
            "OBJETIVO: Proteja os 3 Reatores Solares e derrote o Colosso Entrópico (3 Fases).",
            "",
            "CONTROLES:",
            "  • Mover Nave: Setas Direcionais ou W / A / S / D",
            "  • Disparar Laser: ESPAÇO ou Z   |   Pulso PEM (100%): E ou X",
            "  • Pausa: P ou ESC   |   Reiniciar: R   |   Silenciar: M   |   Volume: + / -",
        ]
        for idx, line in enumerate(instructions):
            color = SOLAR_GOLD if line.startswith("CONTROLES") or line.startswith("OBJETIVO") else WHITE
            txt = self.font_small.render(line, True, color)
            surf.blit(txt, (panel.x + 24, panel.y + 20 + idx * 28))

        hs_txt = self.font_hud.render(f"RECORDE ATUAL: {self.highscore} PTS", True, EMERALD)
        surf.blit(hs_txt, (WIDTH // 2 - hs_txt.get_width() // 2, 522))

        start_txt = self.font_sub.render("Pressione ENTER para Iniciar (F1 pula a introdução)", True, CYAN_NEON)
        surf.blit(start_txt, (WIDTH // 2 - start_txt.get_width() // 2, 562))

    def _draw_narrative_screen(
        self,
        surf: pygame.Surface,
        lines: list[str],
        footer: str,
        typewriter: bool = False,
    ) -> None:
        panel = pygame.Rect(90, 85, WIDTH - 180, HEIGHT - 170)
        pygame.draw.rect(surf, PANEL_BG, panel, border_radius=14)
        pygame.draw.rect(surf, CYAN_NEON, panel, 2, border_radius=14)

        remaining = int(self.intro_chars) if typewriter else 99999
        y = panel.y + 34
        for idx, line in enumerate(lines):
            if remaining <= 0:
                break
            visible = line[:remaining]
            remaining -= len(line)
            color = SOLAR_GOLD if idx == 0 else WHITE
            font = self.font_sub if idx == 0 else self.font_body
            txt = font.render(visible, True, color)
            surf.blit(txt, (panel.x + 36, y))
            y += 34 if idx == 0 else 28

        foot_img = self.font_hud.render(footer, True, CYAN_NEON)
        surf.blit(foot_img, (WIDTH // 2 - foot_img.get_width() // 2, panel.bottom - 42))

    def _draw_gameplay(self, surf: pygame.Surface) -> None:
        for r in self.reactors:
            r.draw(surf)
        for pw in self.powerups:
            pw.draw(surf)
        for proj in self.projectiles:
            proj.draw(surf)
        for enemy in self.enemies:
            enemy.draw(surf)
        if self.boss and self.boss.alive:
            self.boss.draw(surf)
        if self.player:
            self.player.draw(surf)

        self.particles.draw(surf, self.font_small)
        self._draw_hud(surf)

    def _draw_hud(self, surf: pygame.Surface) -> None:
        # Barra superior limpa que não cobre a área de combate
        pygame.draw.rect(surf, PANEL_BG, (0, 0, WIDTH, 44))
        pygame.draw.line(surf, PANEL_BORDER, (0, 44), (WIDTH, 44), 2)

        score_txt = self.font_hud.render(f"PONTOS: {self.score}   RECORDE: {self.highscore}", True, WHITE)
        surf.blit(score_txt, (16, 13))

        stage_label = f"FASE {self.stage}/3"
        if self.boss and self.boss.alive:
            stage_label += " - CHEFE FINAL"
        else:
            stage_label += f" ({min(self.stage_kills, self.stage_target)}/{self.stage_target})"
        stage_txt = self.font_hud.render(stage_label, True, SOLAR_GOLD)
        surf.blit(stage_txt, (WIDTH // 2 - stage_txt.get_width() // 2, 13))

        if self.player:
            lives_txt = self.font_hud.render(f"VIDAS: {self.player.lives}", True, EMERALD if self.player.lives > 1 else CRIMSON)
            surf.blit(lives_txt, (WIDTH - 275, 13))

            # Barra de carga do Pulso PEM
            pem_ready = self.player.pem_charge >= 100.0
            pem_label = "PEM [E] PRONTO!" if pem_ready else f"PEM: {int(self.player.pem_charge)}%"
            pem_txt = self.font_small.render(pem_label, True, CYAN_NEON if pem_ready else MUTED_TEXT)
            surf.blit(pem_txt, (WIDTH - 170, 5))
            pygame.draw.rect(surf, (30, 42, 68), (WIDTH - 170, 24, 150, 10), border_radius=4)
            fill = int(150 * (self.player.pem_charge / 100.0))
            pygame.draw.rect(surf, CYAN_NEON if pem_ready else VIOLET, (WIDTH - 170, 24, fill, 10), border_radius=4)

        # Barra de vida do Chefe Final
        if self.boss and self.boss.alive:
            bw = 360
            bx = WIDTH // 2 - bw // 2
            pygame.draw.rect(surf, (45, 18, 28), (bx, 52, bw, 12), border_radius=4)
            fill_b = int(bw * max(0.0, self.boss.hp / self.boss.max_hp))
            pygame.draw.rect(surf, CRIMSON, (bx, 52, fill_b, 12), border_radius=4)
            pygame.draw.rect(surf, WHITE, (bx, 52, bw, 12), 1, border_radius=4)

        # Rodapé discreto com status de áudio e atalhos
        vol_status = "MUDO" if self.audio.muted or not self.audio.enabled else f"{int(self.audio.volume * 100)}%"
        hint = f"[WASD/Setas] Mover  [Espaço] Atirar  [E] PEM  [P] Pausa  [R] Reiniciar  [M] Áudio ({vol_status})"
        hint_img = self.font_small.render(hint, True, MUTED_TEXT)
        surf.blit(hint_img, (WIDTH // 2 - hint_img.get_width() // 2, HEIGHT - 20))

    def _draw_pause_overlay(self, surf: pygame.Surface) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 10, 20, 185))
        surf.blit(overlay, (0, 0))

        box = pygame.Rect(WIDTH // 2 - 210, HEIGHT // 2 - 110, 420, 220)
        pygame.draw.rect(surf, PANEL_BG, box, border_radius=12)
        pygame.draw.rect(surf, CYAN_NEON, box, 2, border_radius=12)

        t1 = self.font_title.render("JOGO PAUSADO", True, CYAN_NEON)
        t2 = self.font_body.render("P ou ESC — Continuar partida", True, WHITE)
        t3 = self.font_body.render("R — Reiniciar missão", True, WHITE)
        t4 = self.font_body.render("Q — Voltar ao menu principal", True, MUTED_TEXT)

        surf.blit(t1, (WIDTH // 2 - t1.get_width() // 2, box.y + 24))
        surf.blit(t2, (WIDTH // 2 - t2.get_width() // 2, box.y + 88))
        surf.blit(t3, (WIDTH // 2 - t3.get_width() // 2, box.y + 124))
        surf.blit(t4, (WIDTH // 2 - t4.get_width() // 2, box.y + 160))

    def _draw_end_screen(
        self,
        surf: pygame.Surface,
        lines: list[str],
        accent: tuple[int, int, int],
    ) -> None:
        panel = pygame.Rect(90, 75, WIDTH - 180, HEIGHT - 150)
        pygame.draw.rect(surf, PANEL_BG, panel, border_radius=14)
        pygame.draw.rect(surf, accent, panel, 2, border_radius=14)

        y = panel.y + 32
        for idx, line in enumerate(lines):
            font = self.font_sub if idx == 0 else self.font_body
            color = accent if idx == 0 else WHITE
            img = font.render(line, True, color)
            surf.blit(img, (WIDTH // 2 - img.get_width() // 2, y))
            y += 38 if idx == 0 else 28

        score_line = f"PONTUAÇÃO FINAL: {self.score} PTS   |   RECORDE: {self.highscore} PTS"
        sc_img = self.font_sub.render(score_line, True, SOLAR_GOLD)
        surf.blit(sc_img, (WIDTH // 2 - sc_img.get_width() // 2, y + 26))

        if self.new_record:
            rec_img = self.font_hud.render("NOVO RECORDE REGISTADO!", True, EMERALD)
            surf.blit(rec_img, (WIDTH // 2 - rec_img.get_width() // 2, y + 62))

        opt = self.font_hud.render("ENTER ou R — Jogar Novamente   |   ESC — Menu Principal", True, CYAN_NEON)
        surf.blit(opt, (WIDTH // 2 - opt.get_width() // 2, panel.bottom - 44))