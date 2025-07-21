from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional, Tuple
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
    office_exp: int = 0
    dealer_exp: int = 0
    clinic_exp: int = 0
    tokens: int = 0
    has_skateboard: bool = False
    facing_left: bool = False
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

    brawls_won: int = 0

    enemies_defeated: int = 0

    boss_defeated: bool = False

    companion: Optional[str] = None
    companion_level: int = 0

    home_upgrades: List[str] = field(default_factory=list)
    perk_points: int = 0
    perk_levels: Dict[str, int] = field(default_factory=dict)
    next_strength_perk: int = 5
    next_intelligence_perk: int = 5
    next_charisma_perk: int = 5

    current_quest: int = 0
    # Name of an optional side quest currently in progress
    side_quest: Optional[str] = None

    # Money stored in the bank
    bank_balance: float = 0.0

    # 1=apartment, 2=house, 3=mansion
    home_level: int = 1

    # Tracks per-NPC interaction states
    npc_progress: Dict[str, int] = field(default_factory=dict)

    # Story progression
    story_stage: int = 0
    story_branch: Optional[str] = None
    gang_package_done: bool = False

    # Crafting resources
    resources: Dict[str, int] = field(
        default_factory=lambda: {"metal": 0, "cloth": 0, "herbs": 0, "seeds": 0}
    )

    # Days when seeds were planted on the farm
    crops: List[int] = field(default_factory=list)

    # Seasonal state
    season: str = "Spring"
    weather: str = "Clear"

    # List of unlocked achievements
    achievements: List[str] = field(default_factory=list)

    # Collection of discovered trading cards
    cards: List[str] = field(default_factory=list)

    # Current honorific title earned through achievements
    epithet: str = ""

    # Active combat ability primed for next fight
    active_ability: Optional[str] = None
    # Cooldown timers for abilities (in frames)
    ability_cooldowns: Dict[str, int] = field(
        default_factory=lambda: {"heavy": 0, "guard": 0}
    )

    # Quick item hotkey slots
    hotkeys: List[Optional["InventoryItem"]] = field(
        default_factory=lambda: [None] * 5
    )

    # Furniture placed inside the home
    furniture: Dict[str, Optional["InventoryItem"]] = field(
        default_factory=lambda: {f"slot{i}": None for i in range(1, 7)}
    )

    # Saved positions for furniture pieces
    furniture_pos: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {f"slot{i}": (0, 0) for i in range(1, 7)}
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
class SideQuest:
    """Optional quests triggered by talking to NPCs"""
    name: str
    description: str
    target: str  # building type or NPC to complete
    reward: Callable[["Player"], None]


@dataclass
class NPC:
    """Simple moving NPC that can give side quests."""
    rect: pygame.Rect
    name: str
    quest: Optional[SideQuest] = None
    bubble_message: str = ""
    bubble_timer: int = 0


@dataclass
class InventoryItem:
    name: str
    slot: str
    attack: int = 0
    defense: int = 0
    speed: int = 0
    combo: int = 1
    level: int = 0

