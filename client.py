import requests
from custom_types import *
from helpers import *
import json

AXIS_TILE_COUNT=29 #broj celija po x i y osi
TEST_MODE = False #tokom testiranja, staviti na True (kreira 4 igraca)

REQUEST_TIMEOUT = 180 #timeout za API request

class Client:
    __username = None
    __token = None
    __server_address = None
    __test_tokens = list[str]() #tokeni u slucaju testiranja
    map_name = None
    id = 0
    game_state = None

    state = None
    tiles = dict[str, Tile]()

    def __init__(self, server_address, creds: Cred):
        self.__server_address = server_address
        self.__username = creds.username
        self.game_state = None

        if not TEST_MODE: #autentifikuj sa username ako nije test mode
            self.__auth(creds)
        else: #ukoliko je test mod, uloguj svakog bota
            print("TEST MODE ACTIVE")
            
            for i in range(1, 5): #uzmi token za svakog usera i sacuvaj
                self.__auth(Cred(f"{self.__username}{i}", creds.password))

                if self.__token is not None:
                    self.__test_tokens.append(self.__token)
      
    def __auth(self, creds: Cred): #uzmi JWT token
        res = requests.post(url=f"http://{self.__server_address}/user/login", headers={ 
            "Content-Type": "application/json" 
        }, 
        json={
            "username": creds.username,
            "password": creds.password
        })

        if res.status_code not in (200, 202, 201):
            raise ConnectionRefusedError(f"Could not get auth token {res.status_code}, {res.text}")

        res_json = res.json()

        self.__token = res_json["token"]

    def __create_game(self): #kreiraj igricu sa test igracima, TEST ONLY
        res = requests.post(url=f"http://{self.__server_address}/game/createGame", timeout=REQUEST_TIMEOUT, json={
            "playerUsernames": [f"{self.__username}{i}" for i in range(1, 5)], #imeTima1, imeTima2, imeTima3, imeTima4
            "mapName": self.map_name
        }, headers={
            "Authorization": f"Bearer {self.__test_tokens[0] if TEST_MODE else self.__token}", #ako je test mod, koristi 1 test token
            "Content-Type": "application/json"
        })

        if res.status_code not in (200, 202, 201):
            if "je vec u igri sa ID:"  in res.text: #ako vec u igri
                self.id = int(res.json()["message"][-1]) #uzmi poslednji karakter iz poruke (id)
            else: #neka druga greska
                raise RuntimeError(f"Could not create game {res.status_code} {res.text}")

    def __parse_state_response(self, res_body: dict) -> GameState:
        res_body = json.loads(res_body["gameState"])
        
        is_over = res_body["skullWin"]
        alive_count = 0
        
        bots = []

        our_pos = GamePosition(0, 0)

        for p in res_body["scoreBoard"]["players"]:
            if p["playerIdx"] == self.id:
                our_pos = GamePosition(p["q"], p["r"])

            if p["health"] > 0: #ako su zivi
                alive_count += 1

                bots.append(Bot(
                    id=p["playerIdx"], 
                    is_enemy=p["playerIdx"] != self.id, #ako nismo mi, neprijatelj
                    position=GamePosition(p["q"], p["r"]), 
                    power=p["attackPower"],
                    health=p["health"],
                    level=p["scoreLevel"],
                    score=p["score"],
                    has_skull=p["skull"]
                ))
            
        if alive_count < 2:
            is_over = True

        tiles = dict[str, Tile]()

        for t in flatten_tiles(res_body["map"]["tiles"]):
            entity = None

            ent = t["entity"]

            if ent["type"] != "NONE":
                entity_type = get_entity_type(entity_type=ent["type"])

                match entity_type:
                    case EntityType.STONE:
                        entity = Entity(entity_type=entity_type, damage_to_player=50, score_to_player=50, attrs={"attackedTiles": ent["attackedTiles"]})
        
                    case EntityType.TREES:
                        entity = Entity(entity_type=entity_type, damage_to_player=0, score_to_player=100, attrs={"health": ent["health"]})

                    case EntityType.CLIFF:
                        entity = Entity(entity_type=entity_type, damage_to_player=0, score_to_player=0, attrs=None)
                
                    case EntityType.SKULL:
                        entity = Entity(entity_type=entity_type, damage_to_player=0, score_to_player=10000, attrs=None)
                
                    case EntityType.LEAVES:
                        entity = Entity(entity_type=entity_type, damage_to_player=10, score_to_player=20, attrs=None)
                
                    case EntityType.CHEST:
                        entity = Entity(entity_type=entity_type, damage_to_player=0, score_to_player=150, attrs={"used": ent["taken"], "idx": ent["idx"]})
                
                    case EntityType.PLAYER:
                        damage = ent["attackPower"] #+(if ent["sword"] 500 else 0)
                        entity = Entity(entity_type=entity_type, damage_to_player=damage, score_to_player=500, attrs={"score": ent["score"], "health": ent["health"]})
            
            tile_pos = GamePosition(t["q"], t["r"])

            tiles[tile_id(tile_pos)] = Tile(
                entity_on_tile=entity,
                position=tile_pos,
                can_iteract=entity_type in (EntityType.CHEST, EntityType.PLAYER)
            )

        return GameState(
            our_pos=our_pos,
            player_turn=res_body["turn"], 
            game_turn=res_body["gameTurn"], 
            is_over=is_over, 
            tiles=tiles, 
            bots=bots
        )

    def __join_game(self): #udji u igru
        res = requests.get(url=f"http://{self.__server_address}/game/joinGame", timeout=REQUEST_TIMEOUT, headers={
            "Authorization": f"Bearer {self.__token}"
        })

        if res.status_code not in (200, 202, 201):
            if res.status_code == 400 and "timeout-ovao" in res.json()["message"]: #ako timeout, probaj ponovo
                print(f"Request game join timeout after {REQUEST_TIMEOUT}s")
                self.__join_game()

            raise RuntimeError(f"Could not join game, {res.status_code}, {res.text}")

        res_json = res.json()

        self.id = res_json["playerIdx"]

        state = self.__parse_state_response(res_json)
        self.game_state = state
        self.tiles = self.game_state.tiles
    
    def game_join(self, map_name): #kreiraj igricu, udji
        self.map_name = map_name         

        if TEST_MODE: #ukoliko je test mod, kreiraj igricu (ovo je endpoint za admine))
            self.__create_game()

            for i in range(0, 4):
                self.__token = self.__test_tokens[i] #privremeno postavi token za bota sa id(x)
                self.__join_game() #udji u igru
            
        else: #join samo za sebe van test moda
            self.__join_game()

    def player_do_action(self, action: Action, position: GamePosition): #posalji zahtev da se uradi akcija
        res = requests.post(url=f"http://{self.__server_address}/game/doAction", json={
            "action": f"{action.value},{position.q},{position.r}"
        }, headers={
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json"
        })

        if res.status_code not in (200, 202, 201):
            raise RuntimeError(f"Could not do action {action.value} at {position},  {res.status_code} {res.text}")

        res_json = res.json()

        if "gameState" not in res_json:
            raise IllegalActionError(action.value, game_message=res_json["message"], postition=position)
        
        state = self.__parse_state_response(res_json)
        self.game_state = state
        self.tiles = self.game_state.tiles
    
    def get_tile(self, position: GamePosition) -> Tile: #uzmi polje po poziciji
        return self.tiles[tile_id(position)]
    
    def is_out_of_bounds(self, position: GamePosition) -> bool: #da li je van polja igre
        half_axis = AXIS_TILE_COUNT//2
        return not (abs(position.q) <= half_axis and abs(position.r) <= half_axis)

    def get_us(self) -> Bot: #vrati trenutnog bota kao objekat iz game state
        if self.game_state is None:
            raise ValueError("State is null")
        
        return next(filter(lambda b: b.id == self.id, self.game_state.bots))
        # our_tile_id = tile_id(self.game_state.our_pos)
        # return self.tiles[our_tile_id].entity_on_tile

    def get_neighbor_tiles(self, position: GamePosition) -> list[Tile]: #pronadji spojena polja
        neighbors = []

        for d in [Direction.BOTTOM_LEFT, Direction.BOTTOM_RIGHT, Direction.LEFT, Direction.RIGHT, Direction.TOP_RIGHT, Direction.TOP_LEFT]:
            pos = translate_pos(position, d)

            if not self.is_out_of_bounds(pos): #if not out of bounds
                neighbors.append(self.get_tile(pos))

        return neighbors
    
    def get_weakling(self) -> Bot: #uzmi najslabijeg protivnika
        if self.game_state is None:
            raise ValueError("State is null")

        us = self.get_us()
        other_bots = list(filter(lambda b: b.id is not self.id, self.game_state.bots)) #uzmi botove bez nas
        bots = sorted(other_bots, key=lambda b: get_strength_score(us, b), reverse=True) #sortiraj po najslabijima (gde je nas score veci)

        return bots[0] #vrati prvog bota (najslabijeg)