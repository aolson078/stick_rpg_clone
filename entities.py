from dataclasses import dataclass
from typing import Callable
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
    time: float = 8 * 60  # minutes in the day
    strength: int = 1
    intelligence: int = 1
    charisma: int = 1


@dataclass
class Quest:
    description: str
    check: Callable[["Player"], bool]
    completed: bool = False


@dataclass
class Event:
    """Random world events with effects on the player"""
    description: str
    apply: Callable[["Player"], None]
