# Cluedo Game - Core Game Engine

import random
# Global stuff
players_list = []
current_turn = 0
answer = {}
weapon_places = {}
mansion_rooms = {}
secret_doors = {}
start_spots = {}
weapon_names = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]

def init_game():
    global mansion_rooms, secret_doors, start_spots, weapon_places

    # Set up the mansion
    mansion_rooms = {
        "Study": (0, 0),
        "Hall": (0, 1),
        "Lounge": (0, 2),
        "Library": (1, 0),
        "Billiard Room": (1, 1),
        "Dining Room": (1, 2),
        "Conservatory": (2, 0),
        "Ballroom": (2, 1),
        "Kitchen": (2, 2)
    }

    # Secret paths
    secret_doors = {
        "Study": "Kitchen",
        "Kitchen": "Study",
        "Conservatory": "Lounge",
        "Lounge": "Conservatory"
    }

    # Where players start
    start_spots = {
        "Miss Scarlett": (0, 0),
        "Colonel Mustard": (0, 2),
        "Mrs. White": (1, 0),
        "Reverend Green": (1, 2),
        "Mrs. Peacock": (2, 0),
        "Professor Plum": (2, 2)
    }

    # Put weapons in random rooms
    rooms = list(mansion_rooms.keys())
    random.shuffle(rooms)
    for i, w in enumerate(weapon_names):
        weapon_places[w] = rooms[i % len(rooms)]

def show_map():
    print("\n" + "="*50)
    print("MANSION MAP (3x3):")
    print("="*50)
    print("Study(0,0)   Hall(0,1)   Lounge(0,2)")
    print("Library(1,0) Billiard(1,1) Dining(1,2)")
    print("Conservatory(2,0) Ballroom(2,1) Kitchen(2,2)")
    print("\nSecret: Study<->Kitchen, Conservatory<->Lounge")
    print("Everyone starts in rooms!")
    print("="*50)

def start_game():
    global players_list, answer

    people = ["Miss Scarlett", "Colonel Mustard", "Mrs. White",
              "Reverend Green", "Mrs. Peacock", "Professor Plum"]

    # Pick who did it
    answer = {
        "character": random.choice(people),
        "weapon": random.choice(weapon_names),
        "room": random.choice(list(mansion_rooms.keys()))
    }

    print("Game solution picked (secret)")

    # Make cards
    all_cards = []
    for p in people:
        if p != answer["character"]:
            all_cards.append(("person", p))
    for w in weapon_names:
        if w != answer["weapon"]:
            all_cards.append(("weapon", w))
    for r in mansion_rooms:
        if r != answer["room"]:
            all_cards.append(("room", r))

    random.shuffle(all_cards)
    setup_players(all_cards)

def setup_players(cards):
    global players_list

    # How many players
    while True:
        try:
            num = int(input("Number of players (3-6): "))
            if 3 <= num <= 6:
                break
            print("Need 3 to 6 players")
        except:
            print("Give me a number")

    # Make players
    chars = ["Miss Scarlett", "Colonel Mustard", "Mrs. White",
             "Reverend Green", "Mrs. Peacock", "Professor Plum"][:num]

    for i in range(num):
        char_name = chars[i]
        spot = start_spots[char_name]
        room_name = get_room(spot)
        player = {
            "name": f"Player {i+1}",
            "character": char_name,
            "position": spot,
            "cards": [],
            "in_room": True,
            "current_room": room_name,
            "eliminated": False
        }
        players_list.append(player)

    # Deal cards
    cards_each = len(cards) // num
    for i, p in enumerate(players_list):
        start = i * cards_each
        end = start + cards_each
        if i == num - 1:
            end = len(cards)
        p["cards"] = [c[1] for c in cards[start:end]]

    print(f"Ready with {num} players")
    for p in players_list:
        print(f"{p['name']} ({p['character']}) in {p['current_room']}")

    print("\nWeapons start in:")
    for w, r in weapon_places.items():
        print(f"- {w} in {r}")

def get_room(pos):
    for room_name, room_pos in mansion_rooms.items():
        if pos == room_pos:
            return room_name
    return None

def can_move_to(pos):
    x, y = pos
    return 0 <= x <= 2 and 0 <= y <= 2

def get_directions(spot):
    x, y = spot
    dirs = []
    if x > 0: dirs.append("UP")
    if x < 2: dirs.append("DOWN")
    if y > 0: dirs.append("LEFT")
    if y < 2: dirs.append("RIGHT")
    return dirs

def move_player(player, dir, steps):
    x, y = player["position"]

    if dir == "UP":
        new_spot = (x - steps, y)
    elif dir == "DOWN":
        new_spot = (x + steps, y)
    elif dir == "LEFT":
        new_spot = (x, y - steps)
    elif dir == "RIGHT":
        new_spot = (x, y + steps)
    else:
        return False, "Bad direction"

    if not can_move_to(new_spot):
        return False, "Can't go there"

    player["position"] = new_spot

    # Check if in room now
    room_name = get_room(new_spot)
    if room_name:
        player["in_room"] = True
        player["current_room"] = room_name
        msg = f"Moved {dir} {steps} to {room_name}!"

        if room_name in secret_doors:
            msg += f" [Secret to {secret_doors[room_name]}]"

        return True, msg
    else:
        player["in_room"] = False
        player["current_room"] = None
        return True, f"Moved {dir} {steps} to {new_spot}"

def use_secret(player):
    room = player["current_room"]
    if room in secret_doors:
        to_room = secret_doors[room]
        to_spot = mansion_rooms[to_room]

        player["position"] = to_spot
        player["current_room"] = to_room

        return True, f"Secret passage to {to_room}!"
    return False, "No secret here"

def roll_dice():
    return random.randint(1, 6)

def next_turn():
    global current_turn
    current_turn = (current_turn + 1) % len(players_list)

def get_current_player():
    return players_list[current_turn]

def make_guess(player, room):
    print(f"\nYou're in {room}. Make a guess!")

    # Pick character
    print("\nCharacters:")
    chars = ["Miss Scarlett", "Colonel Mustard", "Mrs. White",
             "Reverend Green", "Mrs. Peacock", "Professor Plum"]
    for i, c in enumerate(chars, 1):
        print(f"{i}. {c}")

    guess_char = None
    while not guess_char:
        try:
            choice = input("Pick character (1-6): ").strip()
            num = int(choice) - 1
            if 0 <= num < len(chars):
                guess_char = chars[num]
            else:
                print("Pick 1-6")
        except:
            print("Need a number")

    # Pick weapon
    print("\nWeapons:")
    for i, w in enumerate(weapon_names, 1):
        print(f"{i}. {w}")

    guess_weapon = None
    while not guess_weapon:
        try:
            choice = input("Pick weapon (1-6): ").strip()
            num = int(choice) - 1
            if 0 <= num < len(weapon_names):
                guess_weapon = weapon_names[num]
            else:
                print("Pick 1-6")
        except:
            print("Need a number")

    print(f"\nGuess: {guess_char} with {guess_weapon} in {room}")

    # Move character if needed
    if guess_char != player["character"]:
        for p in players_list:
            if p["character"] == guess_char:
                old = p["current_room"] or f"spot {p['position']}"
                p["position"] = mansion_rooms[room]
                p["in_room"] = True
                p["current_room"] = room
                print(f"MOVED {guess_char} from {old} to {room}")
                break

    # Move weapon
    if guess_weapon in weapon_places:
        old_room = weapon_places[guess_weapon]
        weapon_places[guess_weapon] = room
        print(f"MOVED {guess_weapon} from {old_room} to {room}")

    # Check if anyone can disprove
    disprove = check_disprove(player, (guess_char, guess_weapon, room))
    if disprove:
        print(f"{disprove[0]} showed: {disprove[1]}")
    else:
        print("No one could disprove!")

    return (guess_char, guess_weapon, room)

def check_disprove(guesser, guess):
    guess_char, guess_weapon, guess_room = guess

    start_index = current_turn
    num_players = len(players_list)

    for i in range(1, num_players):
        check_index = (start_index + i) % num_players
        p = players_list[check_index]

        if p.get("eliminated", False):
            continue

        matching = []
        if guess_char in p["cards"]:
            matching.append(guess_char)
        if guess_weapon in p["cards"]:
            matching.append(guess_weapon)
        if guess_room in p["cards"]:
            matching.append(guess_room)

        if not matching:
            continue

        if len(matching) == 1:
            card_to_show = matching[0]
        else:
            print(f"\n{p['name']} can show one of: {', '.join(matching)}")
            while True:
                choice = input("Which card to show? ").strip()
                if choice in matching:
                    card_to_show = choice
                    break
                print("Invalid choice.")
        return (p["name"], card_to_show)

    return None

def do_turn():
    player = get_current_player()
    print(f"\n=== {player['name']}'s Turn ===")
    print(f"Playing as: {player['character']}")

    pos = player["position"]
    room = player["current_room"]

    # Room exit
    print(f"Current: {room} at {pos} [IN ROOM - need to exit]")

    # Secret passage check
    if room in secret_doors:
        secret_to = secret_doors[room]
        use_it = input(f"Use secret to {secret_to}? (y/n): ").lower().strip()
        if use_it == 'y':
            ok, msg = use_secret(player)
            print(msg)
            # Make guess in new room
            new_room = player["current_room"]
            make_guess(player, new_room)
            next_turn()
            return
    else:
        print("No secret here")

    print(f"Your cards: {', '.join(player['cards'])}")

    # Roll dice
    input("Press Enter to roll...")
    roll = roll_dice()
    print(f"Rolled: {roll}")

    # Exit room first
    moves_left = roll
    print("Must use 1 move to exit room.")

    # Simple exit logic
    x, y = player["position"]
    if x > 0: new_spot = (x-1, y)
    elif x < 2: new_spot = (x+1, y)
    elif y > 0: new_spot = (x, y-1)
    else: new_spot = (x, y+1)

    player["position"] = new_spot
    player["in_room"] = False
    player["current_room"] = None
    moves_left -= 1
    print(f"Exited room. Now at {new_spot}. Moves left: {moves_left}")

    # Movement
    while moves_left > 0:
        print(f"\nMoves left: {moves_left}")
        dirs = get_directions(player["position"])
        print(f"Can go: {', '.join(dirs)}")

        while True:
            try:
                move_cmd = input("Enter move like UP 1 or STOP: ").strip().upper()

                if move_cmd == "STOP":
                    print("Stopping movement.")
                    moves_left = 0
                    break

                parts = move_cmd.split()
                if len(parts) == 2 and parts[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
                    direction = parts[0]
                    steps = int(parts[1])

                    if steps <= 0:
                        print("Need positive steps")
                        continue

                    if steps > moves_left:
                        print(f"Only {moves_left} moves left")
                        continue

                    if direction not in dirs:
                        print(f"Can't go {direction} from here")
                        continue

                    # Try to move
                    ok, message = move_player(player, direction, steps)
                    if ok:
                        print(message)
                        moves_left -= steps

                        # Check if entered room
                        if player["in_room"]:
                            current_room = player["current_room"]
                            print(f"ENTERED {current_room}! Stop moving.")
                            make_guess(player, current_room)
                            moves_left = 0
                        break
                    else:
                        print(f"Move failed: {message}")
                else:
                    print('Use "DIRECTION STEPS" or STOP')
            except ValueError:
                print("Need a number for steps")

    next_turn()

def main():
    print("\n=== CLUEDO GAME ===")
    print("Project 2 Part 1")
    print("Starting...\n")

    init_game()
    start_game()
    show_map()

    turn_count = 0
    while True:
        do_turn()
        turn_count += 1

        if turn_count % len(players_list) == 0:
            print(f"\n=== Round {turn_count // len(players_list)} done ===")

        choice = input("\nPress Enter to keep going or 'q' to stop: ").lower()
        if choice == 'q':
            break

    print("\nGame ended. Thanks for playing!")

if __name__ == "__main__":
    main()