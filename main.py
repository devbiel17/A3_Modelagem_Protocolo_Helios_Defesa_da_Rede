"""Ponto de entrada do jogo Protocolo Helios: Defesa da Rede."""

import asyncio
from src.game import Game


async def main() -> None:
    jogo = Game()
    await jogo.run()


if __name__ == "__main__":
    asyncio.run(main())
