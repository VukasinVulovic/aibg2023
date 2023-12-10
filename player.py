from custom_types import *
from client import *
from helpers import *

INITIAL_HEALTH       = 1000
INITIAL_TURN         = 5000
INITIAL_ATTACK_POWER = 100

# START_POSITIONS = (
#     GamePosition(-7, -7),
#     GamePosition(14, -7),
#     GamePosition(-14, 7),
#     GamePosition(7, 7)
# )

#pocinjemo sa traženjem chest-a
class Player:
    __client = None
    position = GamePosition(0, 0) #nasa trenutna pozicija
    target_position = GamePosition(0, 0) #krajnji cilj gde hocemo da se pomerimo
    state = None #stanje u mome je bot 
    has_killed = False #da li je ubio igraca/ima lobanju igraca
    health = INITIAL_HEALTH
    attack_power = INITIAL_ATTACK_POWER
    turn = INITIAL_TURN
    chest_used = False #kovceg otvoren

    def __init__(self, client: Client):
        self.__client = client
        self.state = PlayerState.SEEK

        if client.game_state is None:
            raise RuntimeError("Game state is null")
        
        self.position = client.game_state.our_pos

        chest_pos = self.get_chest_position() #nadji poziciju svog chest-a i idi ka njemu
        self.seek_target(chest_pos)

    def seek_target(self, postition: GamePosition): #postavi cilj pomeranja
        self.target_position = GamePosition(min([postition.q, AXIS_TILE_COUNT]), min(postition.r, AXIS_TILE_COUNT)) #pozicija ili ivica mape
        self.state = PlayerState.SEEK

    # def seek_shelter(self): #bezi od neprijatelja

    def get_next_movable_tile(self, end_position: GamePosition): #sledece polje ka cilju koje smemo da zgazimo
        if self.__client is None:
            raise RuntimeError("Cient not initialized!")
        
        potential_neighbors = self.__client.get_neighbor_tiles(self.position)
        
        neighbors = []
        
        for n in potential_neighbors:
            if self.is_legal(Action.MOVE, n.position): #da li mogu da stanem na polje
                neighbors.append(n)
        
        #add leaves logic
        #add logic if enemy close and not attack, avoid

        return min(neighbors, key=lambda n: tile_dist(n.position, end_position)) #prvi komsija po najmanjoj distanci od cilja

    def get_closest_tile_with_entity(self, entity_type: EntityType): #najblize polje sa entitetom
        if self.__client is None:
            raise RuntimeError("Cient not initialized!")
        
        tiles = filter(lambda t: t.entity_on_tile is not None and t.entity_on_tile.entity_type is entity_type, self.__client.tiles.values()) #polja sa ovim vrstom entiteta

        return min(tiles, key=lambda t: tile_dist(t.position, self.position)) #prvi komsija po najmanjoj distanci od cilja

    def get_chest_position(self):
        if self.__client is None:
            raise RuntimeError("Cient not initialized!")
        
        tiles = filter(lambda t: t.entity_on_tile is not None and t.entity_on_tile.entity_type is EntityType.CHEST and t.entity_on_tile.attrs["idx"] is self.__client.id, self.__client.tiles.values()) #polja sa nasim chestom

        return tiles[0] #privo i jedino polje sa nsim chestom

    def is_legal(self, action: Action, position: GamePosition) -> bool:
        if self.__client is None:
            raise RuntimeError("Cient not initialized!")
        
        if action is None or position.q is None or position.r is None: #nema akcije ili nema pozicije
            return False
        
        if abs(position.q) > AXIS_TILE_COUNT//2 or abs(position.r) > AXIS_TILE_COUNT//2: #pozicija van mape
            return False
        
        if action not in (Action.ATTACK, Action.MOVE): #ako akcija nije definisana
            return False
        
        tile = self.__client.get_tile(position) #uzmi polje iz state

        if tile_dist(tile.position, position) > 1: #ako akcija nije za polje pored
            return False

        if action is Action.MOVE and ( #ukoliko hoce da se pomera na polje koje nije prazno polje sem lisca i kranje lobanje
            tile.entity_on_tile is not None and #puno polje
            tile.entity_on_tile.entity_type not in (EntityType.LEAVES, EntityType.SKULL, EntityType.CHEST)
        ):
            return False
        
        if action is Action.ATTACK and ( #ukoliko je napad u prazno ili ne sme da napadne entity, ili sebe
            tile.entity_on_tile is None or 
            tile.entity_on_tile in (EntityType.STONE, EntityType.LEAVES, EntityType.CHEST, EntityType.CLIFF, EntityType.SKULL) or
            pos_eq(self.position, position) #mi
        ): 
            return False
        
        if action is Action.MOVE and pos_eq(position, GamePosition(0, 0)) and not self.has_killed: #ukoliko hoce na kraj a nije zavrsio
            return False

        return True

    def run_to_finish(self): #juri na centar (pobedjujemo)
        self.seek_target(GamePosition(0, 0))

    def handle_state(self): #logika za trenutno stanje
        us = self.__client.get_us() #mi

        self.position = us.position #nasa pozicija
        self.attack_power = us.power #nasa snaga


        if us.has_skull: #da li imamo lobanju igraca
            self.run_to_finish()
            return #ne gledaj dalje

        neighbors = self.__client.get_neighbor_tiles(self.position) #uzmi komisje po nasoj poziciji

        for n in neighbors:
            ent = n.entity_on_tile

            if ent is None: #ako je celija prazna
                continue

            ##TODO: da li dodati da se juri igrac sa skullom? (rizik)

            if ent.entity_type is EntityType.PLAYER: #ako je entitet protivnik
                logic_score = (us.health-ent.attrs["attackPower"]) - (ent.attrs["health"]-us.power)

                if logic_score < 0: #ako smo mi jaci
                    self.state = PlayerState.ATTACK
                    self.target_position = n.position
                elif logic_score < self.health//2: #ako je score manji od polovine naseg healtha (duplo su jaci)
                    self.state = self.state = PlayerState.EVADE
                else: #nastavi dalje                    
                    if not self.chest_used: #ako kovceg nije otvoren
                        chest_pos = self.get_chest_position() #nadji kovceg

                        if not self.__client.get_tile(chest_pos).entity_on_tile.attrs["used"]: #prava provera
                            self.state = PlayerState.SEEK
                            self.target_position = chest_pos
                        else:
                            self.chest_used = True
                    else: #ako smo uzemi mac, ubi najslabijeg protivnika
                        weakling = self.__client.get_weakling() #najslabiji protivnik
                        self.target_position = weakling.position
                        self.state = PlayerState.ATTACK

        if not self.is_legal(self.state, self.target_position):
            raise IllegalActionError(self.state, "Internal legality check failed.", self.target_position)

        match self.state:
            case PlayerState.SEEK:
                next_tile = self.get_next_movable_tile(self.target_position) #sledece polje ka cilju na koje moze da se stane
                self.__client.player_do_action(Action.MOVE, next_tile) #idi na sledece polje

            case PlayerState.ATTACK:
                if tile_dist(self.position, self.target_position) == 1: #ako je blizu protivnika koga zeli da ubije
                    self.__client.player_do_action(Action.ATTACK, self.target_position)
                else: #ukoliko nije, dodji do njega
                    self.state = PlayerState.SEEK

            case PlayerState.EVADE:
                stone_pos = self.get_closest_tile_with_entity(EntityType.STONE)
                self.seek_target(stone_pos)

            case _:
                raise RuntimeError(f"Unknown player state {self.state}")

        
        