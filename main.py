from client import *
from player import Player
import time

SERVER_ADDRESS  = "134.209.240.184:8081"
CREDS           = Cred("Innovex", "BSQYcUyd87")
MAP_NAME        = "test1.txt"
MOVE_TIMEOUT    = 2 #broj sekundi izmedju poteza

def main():    
    client = Client(SERVER_ADDRESS, creds=CREDS)

    print("Succesfully authentificated.")

    if input("Join game? ").lower() not in ("yes", "y"): #da li da bot udje u igru nakon auth
        exit(0)

    client.game_join(MAP_NAME)

    print(f"Successfully joined map {client.map_name} as player #{client.id}")

    player = Player(client)
    
    while not client.game_state.is_over: #sve do kraja
        player.handle_state() #pokreni logiku za trenutno stanje
        
        print(f"Player position: {player.position}, targeting: {player.target_position}, state: {player.state}, HP: {player.health}") #ispisi info

        if client.game_state.is_over:
            print(f"Game Over, DID WE WIN?")

        time.sleep(MOVE_TIMEOUT) #spavaj (x)sekundi
        print("STEP")

if __name__ == "__main__":
    print("""
 ______  __    __  __    __   ______   __     __  ________  __    __ 
/      |/  \  /  |/  \  /  | /      \ /  |   /  |/        |/  |  /  |
$$$$$$/ $$  \ $$ |$$  \ $$ |/$$$$$$  |$$ |   $$ |$$$$$$$$/ $$ |  $$ |
  $$ |  $$$  \$$ |$$$  \$$ |$$ |  $$ |$$ |   $$ |$$ |__    $$  \/$$/ 
  $$ |  $$$$  $$ |$$$$  $$ |$$ |  $$ |$$  \ /$$/ $$    |    $$  $$<  
  $$ |  $$ $$ $$ |$$ $$ $$ |$$ |  $$ | $$  /$$/  $$$$$/      $$$$  \ 
 _$$ |_ $$ |$$$$ |$$ |$$$$ |$$ \__$$ |  $$ $$/   $$ |_____  $$ /$$  |
/ $$   |$$ | $$$ |$$ | $$$ |$$    $$/    $$$/    $$       |$$ |  $$ |
$$$$$$/ $$/   $$/ $$/   $$/  $$$$$$/      $/     $$$$$$$$/ $$/   $$/ 
""")

    print("Authors: Vukašin, Filip, Stefan, Philippos")
    print("\n\nAIBG 2023")

    main()