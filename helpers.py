from custom_types import *

def translate_pos(curr_pos: GamePosition, to_direction: Direction) -> GamePosition:
    return GamePosition(curr_pos.q+to_direction.value[0], curr_pos.r+to_direction.value[1])

def tile_dist(pos1: GamePosition, pos2: GamePosition) -> int:
    return (abs(pos1.q - pos2.q) + abs(pos1.q + pos1.r - pos2.q - pos2.r) + abs(pos1.q - pos2.r)) // 2

def tile_id(position: GamePosition) -> str:
    return f"{position.q}_{position.r}" 

def pos_eq(pos1: GamePosition, pos2: GamePosition):
    return pos1.q == pos2.q and pos1.r == pos2.r

def flatten_tiles(tiles_arr: list[list[Tile]]):
    tiles:list[Tile] = list()
    
    for ta in tiles_arr:
        for t in ta: 
            tiles.append(t)
        
    return tiles

def get_entity_type(entity_type: str):
    match entity_type:
        case "STONE":
            return EntityType.STONE
        
        case "TREES":
            return EntityType.TREES
        
        case "CLIFF":
            return EntityType.CLIFF
        
        case "SKULL":
            return EntityType.SKULL
        
        case "LEAVES":
            return EntityType.LEAVES
        
        case "CHEST":
            return EntityType.CHEST
        
        case "PLAYER":
            return EntityType.PLAYER
        
        case _:
            raise ValueError(f"No entity type {entity_type}")

def get_strength_score(bot1: Bot, bot2: Bot) -> int: #neki score koji govori koliko je protivnik 1 od 2
    return (bot1.health - bot2.power) - (bot2.health - bot1.power)
