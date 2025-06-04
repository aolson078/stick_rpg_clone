from dataclasses import dataclass
import pygame

@dataclass
class Building:
    rect: pygame.Rect
    name: str
    btype: str

@dataclass
class Player:
    rect: pygame.Rect
    money: float = 50
    energy: float = 100
    health: float = 100
    day: int = 1
