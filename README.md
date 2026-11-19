<div align="center">

# Protocolo Helios: Defesa da Rede

**Jogo 2D de ação espacial, defesa tática e gerenciamento de energia desenvolvido em Python**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame-CE](https://img.shields.io/badge/Pygame--CE-2.5%2B-00E5FF?style=for-the-badge&logo=python&logoColor=black)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-00E676?style=for-the-badge)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-Acad%C3%AAmica%20%2F%20MIT-FFC400?style=for-the-badge)

[Identificação](#1-identificação) • [Descrição e História](#2-descrição-e-história) • [Como Rodar](#3-como-rodar) • [Como Jogar e Objetivos](#4-como-jogar-e-objetivos) • [Controles](#5-controles) • [Regras e Pontuação](#6-regras-e-pontuação) • [Equipe](#7-divisão-de-tarefas) • [Créditos](#8-créditos) • [Tecnologia](#9-tecnologia) • [Uso de IA](#10-uso-de-ia) • [Capturas de Tela](#11-capturas-de-tela)

</div>

---

## 1. Identificação

| Campo | Detalhe |
| :--- | :--- |
| **Nome do Jogo** | Protocolo Helios: Defesa da Rede |
| **Disciplina** | Usabilidade, desenvolvimento web, mobile e jogos |
| **Professora** | Patrícia Vitorino Gomes |

**Integrantes:**
* **Gabriel Pires Gomes Osório** — RA: `825117478`
* **André Luiz Lopes de Oliveira** — RA: `825129838`
* **Carlos Daniel da Silva Rodrigues** — RA: `82425705`

---

## 2. Descrição e História

**Protocolo Helios: Defesa da Rede** é um jogo digital original de ação espacial e defesa tática desenvolvido em Python com `pygame-ce`.

### A Premissa
No ano de **2142**, a estação orbital *Helios* abastece 80% da energia limpa da Terra por meio de **três Reatores Solares** sincronizados em órbita baixa. Uma frota autônoma corrompida — o **Enxame Entrópico** — inicia uma ofensiva coordenada para sobrecarregar os reatores e mergulhar o planeta em um apagão global.

### O Conflito e os Desfechos
No comando da nave interceptora **AEGIS-01**, o jogador precisa conter três ondas de invasão cada vez mais agressivas até enfrentar o núcleo de comando inimigo, o **Colosso Entrópico**:
* **Final de Vitória:** Ao destruir o *Colosso Entrópico* mantendo pelo menos um reator ativo, o sinal de corrupção é eliminado e o fornecimento energético da Terra é estabilizado.
* **Final de Derrota:** Se a nave perder todas as vidas ou todos os três reatores entrarem em colapso, a estação entra em falha crítica e o planeta sofre um apagão.

---

## 3. Como Rodar

### Pré-requisitos
* **Python 3.10** ou superior instalado no computador.

### Passo a passo para instalação e execução
1. Abra o terminal na pasta raiz do projeto (`A3_Modelagem_Protocolo_Helios_Defesa_da_Rede/`).
2. Crie e ative um ambiente virtual isolado:
   ```bash
   # Crie o ambiente virtual (no Windows, use 'py' caso 'python' não esteja no PATH):
   python -m venv .venv

   # Ative no Windows (PowerShell):
   .venv\Scripts\activate

   # Ative no Linux / macOS:
   source .venv/bin/activate