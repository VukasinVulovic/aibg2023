from dataclasses import dataclass
from enum import Enum

@dataclass
class Cred:
    username: str
    password: str

@dataclass
class GamePosition:
    q: int
    r: int

@dataclass
class Bot:
    id:         str
    is_enemy:   bool
    position:   GamePosition
    power:      int
    score:      int
    level:      int
    health:     int
    has_skull:  bool

class EntityType(Enum):
    STONE   = 1
    TREES   = 2
    CLIFF   = 3
    SKULL   = 4
    LEAVES  = 5
    CHEST   = 6
    PLAYER  = 7

@dataclass
class Entity:
    entity_type:        EntityType
    damage_to_player:   int
    score_to_player:    int
    attrs:              dict | None = None #atributi

class PlayerState(Enum):
    SEEK    = 1
    ATTACK  = 2
    EVADE   = 3

@dataclass
class Tile:
    entity_on_tile: Entity | None
    position:       GamePosition
    can_iteract:    bool #najbitnije za chest (da li je otvoren)

@dataclass
class GameState:
    player_turn:    int
    game_turn:      int
    is_over:        bool
    tiles:          dict[str, Tile]
    bots:           list[Bot]
    our_pos:        GamePosition

class Action(Enum):
    MOVE    = "move"
    ATTACK  = "attack"

class Direction(Enum):
    TOP_LEFT        = (0, -1)
    TOP_RIGHT       = (1, -1)
    RIGHT           = (1, 0)
    BOTTOM_RIGHT    = (0, 1)
    BOTTOM_LEFT     = (-1, 1)
    LEFT            = (-1, 0)

class IllegalActionError(Exception):
    def __init__(self, action_name: str, game_message: str, postition: GamePosition | None = None):
        if postition is None:
            super().__init__(f"Illegal action! Action {action_name} not allowed, {game_message}")
        else:
            super().__init__(f"Illegal action! Action {action_name} at {postition} not allowed, {game_message}")