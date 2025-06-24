from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional
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
    defense: int = 0
    speed: int = 1
    office_level: int = 1
    office_shifts: int = 0
    dealer_level: int = 1
    dealer_shifts: int = 0
    clinic_level: int = 1
    clinic_shifts: int = 0
    tokens: int = 0
    has_skateboard: bool = False
    inventory: List["InventoryItem"] = field(default_factory=list)
    equipment: Dict[str, Optional["InventoryItem"]] = field(
        default_factory=lambda: {
            "head": None,
            "chest": None,
            "arms": None,
            "legs": None,
            "weapon": None,
        }
    )

    defense: int = 0
    speed: int = 1

    office_level: int = 1
    office_shifts: int = 0
    dealer_level: int = 1
    dealer_shifts: int = 0
    clinic_level: int = 1
    clinic_shifts: int = 0
    tokens: int = 0

    brawls_won: int = 0

    enemies_defeated: int = 0

    has_skateboard: bool = False
    companion: Optional[str] = None

    home_upgrades: List[str] = field(default_factory=list)
    perk_points: int = 0
    perk_levels: Dict[str, int] = field(default_factory=dict)
    next_strength_perk: int = 5
    next_intelligence_perk: int = 5
    next_charisma_perk: int = 5

    current_quest: int = 0

    inventory: List["InventoryItem"] = field(default_factory=list)
    equipment: Dict[str, Optional["InventoryItem"]] = field(
        default_factory=lambda: {
            "head": None,
            "chest": None,
            "arms": None,
            "legs": None,
            "weapon": None,
        }
    )



@dataclass
class Quest:
    description: str
    check: Callable[["Player"], bool]
    completed: bool = False
    reward: Optional[Callable[["Player"], None]] = None
    next_index: Optional[int] = None


@dataclass
class Event:
    """Random world events with effects on the player"""
    description: str
    apply: Callable[["Player"], None]


@dataclass
class InventoryItem:
    name: str
    slot: str
    attack: int = 0
    defense: int = 0
    speed: int = 0

