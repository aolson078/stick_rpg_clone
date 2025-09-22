"""Data classes for players, items, and NPC entities."""
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Optional, Tuple, Any
import pygame
import settings


@dataclass
class Building:
    rect: pygame.Rect
    name: str
    btype: str
    image: Optional[pygame.Surface] = None
    window_layers: List[pygame.Surface] = field(default_factory=list)


@dataclass
class Player:
    rect: pygame.Rect
    name: str = "Player"
    color: Tuple[int, int, int] = settings.PLAYER_COLOR
    head_color: Tuple[int, int, int] = settings.PLAYER_HEAD_COLOR
    pants_color: Tuple[int, int, int] = (50, 50, 150)
    hat_color: Tuple[int, int, int] = (200, 200, 0)
    has_hat: bool = False
    money: float = 50
    energy: float = 100
    health: float = 100
    day: int = 1
    weekday: int = 0  # 0=Monday

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
    # Currency found within lucid dreams
    dream_shards: int = 0
    # Pending dream shop offers available after waking
    pending_dream_shop: List[Dict[str, Any]] = field(default_factory=list)
    # Crafting skills and experience per skill
    crafting_skills: Dict[str, int] = field(default_factory=dict)
    crafting_exp: Dict[str, int] = field(default_factory=dict)
    # Names of crafting recipes the player has discovered
    known_recipes: List[str] = field(default_factory=list)
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

    # Wins in the trading card duel mini-game
    card_duels_won: int = 0

    enemies_defeated: int = 0

    boss_defeated: bool = False

    companion: Optional[str] = None
    companion_level: int = 0
    companion_morale: int = 100
    # Ability levels for each companion ability
    companion_abilities: Dict[str, Dict[str, int]] = field(default_factory=dict)

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

    # Player owned businesses with base profits
    businesses: Dict[str, int] = field(default_factory=dict)
    # Temporary profit bonuses earned from management
    business_bonus: Dict[str, int] = field(default_factory=dict)
    # Number of staff hired for each business
    business_staff: Dict[str, int] = field(default_factory=dict)
    # Temporary reputation boosts from marketing
    business_reputation: Dict[str, int] = field(default_factory=dict)
    # Temporary staff skill training to reduce robberies
    business_skill: Dict[str, int] = field(default_factory=dict)
    # Speculative futures contracts keyed by business name
    business_futures: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Narrative log of resolved futures deals
    business_future_log: List[str] = field(default_factory=list)

    # Tracks per-NPC interaction states
    npc_progress: Dict[str, int] = field(default_factory=dict)

    # Story progression
    story_stage: int = 0
    story_branch: Optional[str] = None
    gang_package_done: bool = False

    # Crafting resources
    resources: Dict[str, int] = field(
        default_factory=lambda: {
            "ore": 0,
            "metal": 0,
            "stone": 0,
            "gems": 0,
            "cloth": 0,
            "herbs": 0,
            "eggs": 0,
            "milk": 0,
        }
    )

    # Farm animals owned by the player
    animals: Dict[str, int] = field(
        default_factory=lambda: {"chicken": 0, "cow": 0}
    )

    # Planted crops with type and day planted
    crops: List[Dict[str, Any]] = field(default_factory=list)

    # Seasonal state
    season: str = "Spring"
    weather: str = "Clear"

    # List of unlocked achievements
    achievements: List[str] = field(default_factory=list)

    # Collection of discovered trading cards
    cards: List[str] = field(default_factory=list)
    # Active deck used for card duels (up to 30 card names)
    deck: List[str] = field(default_factory=list)

    # Current honorific title earned through achievements
    epithet: str = ""

    # Active combat ability primed for next fight
    active_ability: Optional[str] = None
    # Cooldown timers for abilities (in frames)
    ability_cooldowns: Dict[str, int] = field(
        default_factory=lambda: {"heavy": 0, "guard": 0, "special": 0}
    )

    # Quick item hotkey slots
    hotkeys: List[Optional["InventoryItem"]] = field(default_factory=lambda: [None] * 5)

    # Temporary bonuses gained from events keyed by bonus name
    temporary_bonuses: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # Short notes about dream events experienced by the player
    dream_journal: List[str] = field(default_factory=list)

    # Reference to the active game instance (not persisted to save files)
    game: Any = field(default=None, repr=False, compare=False)

    # Furniture placed inside the home
    furniture: Dict[str, Optional["InventoryItem"]] = field(
        default_factory=lambda: {f"slot{i}": None for i in range(1, 10)}
    )

    # Saved positions for furniture pieces
    furniture_pos: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {f"slot{i}": (0, 0) for i in range(1, 10)}
    )

    # Rotation angles for furniture pieces
    furniture_rot: Dict[str, int] = field(
        default_factory=lambda: {f"slot{i}": 0 for i in range(1, 10)}
    )

    # Relationship data with NPCs
    relationships: Dict[str, int] = field(default_factory=dict)
    last_talk: Dict[str, int] = field(default_factory=dict)
    romanced: List[str] = field(default_factory=list)
    # Additional relationship milestones and marriage state
    relationship_stage: Dict[str, int] = field(default_factory=dict)
    married_to: Optional[str] = None

    # Reputation with various city factions
    reputation: Dict[str, int] = field(
        default_factory=lambda: {"mayor": 0, "business": 0, "gang": 0}
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
    dialogue: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)


@dataclass
class NPC:
    """Simple moving NPC that can give side quests."""

    rect: pygame.Rect
    name: str
    quest: Optional[SideQuest] = None
    romanceable: bool = False
    gender: str = ""
    bubble_message: str = ""
    bubble_timer: int = 0
    # daily schedule details
    home: str = "suburbs"
    work: Optional[str] = None
    work_start: int = 9
    work_end: int = 17
    # movement state
    destination: Optional[Tuple[int, int]] = None
    path: List[Tuple[int, int]] = field(default_factory=list)
    speed: int = 4

    def move(self) -> None:
        """Advance the NPC along its path one step."""
        if not self.path:
            return
        target_x, target_y = self.path[0]
        if self.rect.x < target_x:
            self.rect.x += min(self.speed, target_x - self.rect.x)
        elif self.rect.x > target_x:
            self.rect.x -= min(self.speed, self.rect.x - target_x)
        if self.rect.y < target_y:
            self.rect.y += min(self.speed, target_y - self.rect.y)
        elif self.rect.y > target_y:
            self.rect.y -= min(self.speed, self.rect.y - target_y)
        if self.rect.x == target_x and self.rect.y == target_y:
            self.path.pop(0)


@dataclass
class InventoryItem:
    name: str
    slot: str
    attack: int = 0
    defense: int = 0
    speed: int = 0
    combo: int = 1
    level: int = 0
    # melee, ranged or magic for weapons
    weapon_type: str = "melee"
    max_durability: int = 100
    durability: int = 100
    # rotation angle for furniture pieces
    rotation: int = 0
