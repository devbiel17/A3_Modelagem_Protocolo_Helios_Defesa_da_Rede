"""Configurações globais, paleta de cores e textos narrativos do jogo."""

import os

# Dimensões e desempenho
WIDTH = 960
HEIGHT = 640
FPS = 60
TITLE = "Protocolo Helios: Defesa da Rede"

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_IMG_DIR = os.path.join(BASE_DIR, "assets", "img")
ASSETS_SONS_DIR = os.path.join(BASE_DIR, "assets", "sons")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

# Paleta de cores (tema orbital / rede solar de alto contraste)
BG_DEEP = (10, 14, 26)
GRID_LINE = (20, 32, 56)
PANEL_BG = (15, 22, 40)
PANEL_BORDER = (46, 74, 118)

CYAN_NEON = (0, 229, 255)
SOLAR_GOLD = (255, 196, 0)
SOLAR_ORANGE = (255, 109, 0)
EMERALD = (0, 230, 118)
CRIMSON = (255, 61, 87)
VIOLET = (179, 136, 255)
WHITE = (242, 246, 255)
MUTED_TEXT = (160, 176, 204)

# Textos da história integrada no jogo
INTRO_TEXT = [
    "ANO 2142 — ESTAÇÃO ORBITAL HELIOS",
    "",
    "A rede orbital Helios abastece 80% da energia limpa da Terra",
    "através de três Reatores Solares sincronizados em órbita baixa.",
    "",
    "Uma frota autónoma corrompida — o Enxame Entrópico — iniciou",
    "um ataque coordenado para sobrecarregar os reatores e mergulhar",
    "o planeta num apagão global.",
    "",
    "Como piloto da nave intercetora AEGIS-01, a sua missão é",
    "defender os reatores, neutralizar as ondas inimigas e destruir",
    "o núcleo de comando inimigo antes que a rede entre em colapso.",
]

STAGE_TRANSITIONS = {
    2: [
        "FASE 1 CONCLUÍDA — ÓRBITA BAIXA ESTABILIZADA",
        "",
        "Os primeiros batedores foram repelidos, mas os sensores",
        "detetam drones blindados com escudos de fase a aproximarem-se.",
        "Recolha cápsulas de melhoria para aumentar o poder de fogo!",
    ],
    3: [
        "FASE 2 CONCLUÍDA — ALERTA CRÍTICO DE COMANDO",
        "",
        "O núcleo central do enxame entrou no perímetro da estação:",
        "o COLOSSO ENTRÓPICO está a carregar o feixe principal.",
        "Use o Pulso PEM (tecla E) quando a barra atingir 100%!",
    ],
}

VICTORY_TEXT = [
    "MISSÃO CUMPRIDA — REDE HELIOS PROTEGIDA",
    "",
    "Com a destruição do Colosso Entrópico, o sinal de corrupção",
    "foi eliminado da órbita terrestre. Os Reatores Solares voltaram",
    "à capacidade nominal e o fornecimento global foi salvo.",
]

DEFEAT_TEXT = [
    "FALHA CRÍTICA — COLAPSO DA REDE HELIOS",
    "",
    "Sem defesas ativas em órbita, a sobrecarga atingiu os",
    "reatores principais. A estação entrou em modo de emergência",
    "e a Terra enfrenta um apagão energético sem precedentes.",
]