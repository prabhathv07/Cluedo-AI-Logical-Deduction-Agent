import random

# Game state variables
players_list = []
current_turn = 0
solution = {}
weapon_locations = {}
mansion_rooms = {}
secret_passages = {}
starting_positions = {}
weapon_names = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
character_names = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", 
                   "Reverend Green", "Mrs. Peacock", "Professor Plum"]
game_log = []

def initialize_mansion():
    global mansion_rooms, secret_passages, starting_positions, weapon_locations
    
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
    
    secret_passages = {
        "Study": "Kitchen",
        "Kitchen": "Study",
        "Conservatory": "Lounge",
        "Lounge": "Conservatory"
    }
    
    starting_positions = {
        "Miss Scarlett": (0, 0),
        "Colonel Mustard": (0, 2),
        "Mrs. White": (1, 0),
        "Reverend Green": (1, 2),
        "Mrs. Peacock": (2, 0),
        "Professor Plum": (2, 2)
    }
    
    rooms_list = list(mansion_rooms.keys())
    random.shuffle(rooms_list)
    for i, weapon in enumerate(weapon_names):
        weapon_locations[weapon] = rooms_list[i % len(rooms_list)]

def display_mansion_layout():
    print("\n" + "=" * 60)
    print("CLUEDO MANSION LAYOUT")
    print("=" * 60)
    print("Study (0,0)          Hall (0,1)          Lounge (0,2)")
    print("Library (1,0)        Billiard Room (1,1) Dining Room (1,2)")
    print("Conservatory (2,0)   Ballroom (2,1)      Kitchen (2,2)")
    print("\nSecret Passages:")
    print("  Study <-> Kitchen")
    print("  Conservatory <-> Lounge")
    print("=" * 60)

class Player:
    def __init__(self, name, character, position, is_ai=False):
        self.name = name
        self.character = character
        self.position = position
        self.cards = []
        self.in_room = True
        self.current_room = self.get_room_at_position(position)
        self.is_ai = is_ai
        self.eliminated = False
        
        if is_ai:
            self.knowledge = KnowledgeBase(character, mansion_rooms)
    
    def get_room_at_position(self, pos):
        for room_name, room_pos in mansion_rooms.items():
            if pos == room_pos:
                return room_name
        return None
    
    def add_card(self, card):
        self.cards.append(card)
        if self.is_ai:
            self.knowledge.mark_own_card(card)
    
    def has_card(self, card):
        return card in self.cards
    
    def can_refute(self, suggestion):
        char, weapon, room = suggestion
        matching_cards = []
        if char in self.cards:
            matching_cards.append(char)
        if weapon in self.cards:
            matching_cards.append(weapon)
        if room in self.cards:
            matching_cards.append(room)
        return matching_cards

class KnowledgeBase:
    def __init__(self, character_name, rooms):
        self.character = character_name
        self.own_cards = set()
        self.possible_solution = {
            'characters': set(character_names),
            'weapons': set(weapon_names),
            'rooms': set(rooms.keys())
        }
        self.player_has = {}
        self.player_not_has = {}
        self.shown_cards = set()
    
    def mark_own_card(self, card):
        self.own_cards.add(card)
        self.eliminate_from_solution(card)
    
    def eliminate_from_solution(self, card):
        if card in character_names:
            self.possible_solution['characters'].discard(card)
        elif card in weapon_names:
            self.possible_solution['weapons'].discard(card)
        elif card in mansion_rooms.keys():
            self.possible_solution['rooms'].discard(card)
    
    def record_refutation(self, player_name, suggestion, card_shown=None):
        if card_shown:
            self.shown_cards.add(card_shown)
            self.eliminate_from_solution(card_shown)
            
            if player_name not in self.player_has:
                self.player_has[player_name] = set()
            self.player_has[player_name].add(card_shown)
    
    def record_no_refutation(self, player_name, suggestion):
        char, weapon, room = suggestion
        
        if player_name not in self.player_not_has:
            self.player_not_has[player_name] = set()
        
        self.player_not_has[player_name].add(char)
        self.player_not_has[player_name].add(weapon)
        self.player_not_has[player_name].add(room)
    
    def record_someone_refuted(self, player_name, suggestion):
        if player_name not in self.player_has:
            self.player_has[player_name] = set()
        
        char, weapon, room = suggestion
        possible_cards = [char, weapon, room]
        
        known_not_has = self.player_not_has.get(player_name, set())
        possible_has = [c for c in possible_cards if c not in known_not_has and c not in self.own_cards]
        
        if len(possible_has) == 1:
            self.shown_cards.add(possible_has[0])
            self.eliminate_from_solution(possible_has[0])
            self.player_has[player_name].add(possible_has[0])
    
    def get_solution_guess(self):
        if (len(self.possible_solution['characters']) == 1 and 
            len(self.possible_solution['weapons']) == 1 and 
            len(self.possible_solution['rooms']) == 1):
            return (
                list(self.possible_solution['characters'])[0],
                list(self.possible_solution['weapons'])[0],
                list(self.possible_solution['rooms'])[0]
            )
        return None
    
    def make_suggestion(self, current_room):
        unknown_chars = [c for c in self.possible_solution['characters'] 
                        if c not in self.own_cards]
        unknown_weapons = [w for w in self.possible_solution['weapons'] 
                          if w not in self.own_cards]
        
        if not unknown_chars:
            unknown_chars = [c for c in character_names if c not in self.own_cards]
        if not unknown_weapons:
            unknown_weapons = [w for w in weapon_names if w not in self.own_cards]
        
        char = random.choice(unknown_chars) if unknown_chars else random.choice(character_names)
        weapon = random.choice(unknown_weapons) if unknown_weapons else random.choice(weapon_names)
        
        return (char, weapon, current_room)
    
    def choose_room_to_visit(self):
        unknown_rooms = [r for r in self.possible_solution['rooms'] 
                        if r not in self.own_cards]
        if unknown_rooms:
            return random.choice(unknown_rooms)
        return random.choice(list(mansion_rooms.keys()))

def setup_game():
    global solution
    
    solution = {
        "character": random.choice(character_names),
        "weapon": random.choice(weapon_names),
        "room": random.choice(list(mansion_rooms.keys()))
    }
    
    print("Murder solution has been sealed in the envelope.")
    
    all_cards = []
    for char in character_names:
        if char != solution["character"]:
            all_cards.append(char)
    for weapon in weapon_names:
        if weapon != solution["weapon"]:
            all_cards.append(weapon)
    for room in mansion_rooms.keys():
        if room != solution["room"]:
            all_cards.append(room)
    
    random.shuffle(all_cards)
    return all_cards

def create_players(cards):
    global players_list
    
    while True:
        try:
            num_players = int(input("Enter number of players (3-6): "))
            if 3 <= num_players <= 6:
                break
            print("Please enter a number between 3 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    while True:
        try:
            num_ai = int(input(f"How many AI players (0-{num_players}): "))
            if 0 <= num_ai <= num_players:
                break
            print(f"Please enter a number between 0 and {num_players}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    characters = character_names[:num_players]
    
    ai_indices = []
    if num_ai > 0:
        print(f"\nSelect which players should be AI (1-{num_players}):")
        for i in range(num_ai):
            while True:
                try:
                    idx = int(input(f"AI player {i+1} position: ")) - 1
                    if 0 <= idx < num_players and idx not in ai_indices:
                        ai_indices.append(idx)
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
    
    for i in range(num_players):
        char = characters[i]
        pos = starting_positions[char]
        is_ai = i in ai_indices
        player_type = "AI" if is_ai else "Human"
        player = Player(f"Player {i+1} ({player_type})", char, pos, is_ai)
        players_list.append(player)
    
    cards_per_player = len(cards) // num_players
    for i, player in enumerate(players_list):
        start_idx = i * cards_per_player
        end_idx = start_idx + cards_per_player
        if i == num_players - 1:
            end_idx = len(cards)
        
        for card in cards[start_idx:end_idx]:
            player.add_card(card)
    
    print(f"\nGame setup complete with {num_players} players.")
    for player in players_list:
        print(f"{player.name} as {player.character} in {player.current_room}")
    
    print("\nWeapon locations:")
    for weapon, room in weapon_locations.items():
        print(f"  {weapon} in {room}")

def is_valid_position(pos):
    x, y = pos
    return 0 <= x <= 2 and 0 <= y <= 2

def get_available_directions(pos):
    x, y = pos
    directions = []
    if x > 0:
        directions.append("UP")
    if x < 2:
        directions.append("DOWN")
    if y > 0:
        directions.append("LEFT")
    if y < 2:
        directions.append("RIGHT")
    return directions

def move_in_direction(player, direction, steps):
    x, y = player.position
    
    if direction == "UP":
        new_pos = (x - steps, y)
    elif direction == "DOWN":
        new_pos = (x + steps, y)
    elif direction == "LEFT":
        new_pos = (x, y - steps)
    elif direction == "RIGHT":
        new_pos = (x, y + steps)
    else:
        return False, "Invalid direction"
    
    if not is_valid_position(new_pos):
        return False, "Cannot move there - out of bounds"
    
    player.position = new_pos
    room = player.get_room_at_position(new_pos)
    
    if room:
        player.in_room = True
        player.current_room = room
        message = f"Moved {direction} {steps} spaces to {room}"
        
        if room in secret_passages:
            message += f" (Secret passage to {secret_passages[room]} available)"
        
        return True, message
    else:
        player.in_room = False
        player.current_room = None
        return True, f"Moved {direction} {steps} spaces to position {new_pos}"

def use_secret_passage(player):
    current = player.current_room
    if current in secret_passages:
        destination = secret_passages[current]
        dest_pos = mansion_rooms[destination]
        
        player.position = dest_pos
        player.current_room = destination
        player.in_room = True
        
        return True, f"Used secret passage to {destination}"
    return False, "No secret passage in this room"

def roll_die():
    return random.randint(1, 6)

def make_suggestion(player, room):
    print(f"\n{player.name} is making a suggestion in {room}")
    
    if player.is_ai:
        suggestion = player.knowledge.make_suggestion(room)
        char, weapon, suggested_room = suggestion
        print(f"AI suggests: {char} with {weapon} in {suggested_room}")
    else:
        print("\nSelect character:")
        for i, char in enumerate(character_names, 1):
            print(f"{i}. {char}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-6): "))
                if 1 <= choice <= 6:
                    char = character_names[choice - 1]
                    break
                print("Please enter 1-6")
            except ValueError:
                print("Invalid input")
        
        print("\nSelect weapon:")
        for i, weapon in enumerate(weapon_names, 1):
            print(f"{i}. {weapon}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-6): "))
                if 1 <= choice <= 6:
                    weapon = weapon_names[choice - 1]
                    break
                print("Please enter 1-6")
            except ValueError:
                print("Invalid input")
        
        suggestion = (char, weapon, room)
        print(f"\nSuggestion: {char} with {weapon} in {room}")
    
    char, weapon, room = suggestion
    
    for p in players_list:
        if p.character == char and p != player:
            old_location = p.current_room or f"position {p.position}"
            p.position = mansion_rooms[room]
            p.in_room = True
            p.current_room = room
            print(f"Moved {char} from {old_location} to {room}")
            break
    
    if weapon in weapon_locations:
        old_room = weapon_locations[weapon]
        weapon_locations[weapon] = room
        print(f"Moved {weapon} from {old_room} to {room}")
    
    refutation = check_refutation(player, suggestion)
    
    if refutation:
        refuter, card = refutation
        print(f"\n{refuter.name} refutes the suggestion")
        
        if not player.is_ai:
            print(f"Card shown privately to {player.name}: {card}")
        else:
            print(f"Card shown privately to {player.name}")
        
        if player.is_ai:
            player.knowledge.record_refutation(refuter.name, suggestion, card)
        
        for p in players_list:
            if p.is_ai and p != player and p != refuter:
                p.knowledge.record_someone_refuted(refuter.name, suggestion)
            elif p.is_ai and p == refuter:
                p.knowledge.record_refutation(player.name, suggestion)
    else:
        print("\nNo one could refute the suggestion!")
        
        for p in players_list:
            if p.is_ai and p != player:
                p.knowledge.record_no_refutation(player.name, suggestion)
                for card in suggestion:
                    p.knowledge.eliminate_from_solution(card)
    
    game_log.append(f"{player.name} suggested {char} with {weapon} in {room}")
    return suggestion

def check_refutation(suggester, suggestion):
    char, weapon, room = suggestion
    
    start_idx = players_list.index(suggester)
    num_players = len(players_list)
    
    for i in range(1, num_players):
        check_idx = (start_idx + i) % num_players
        player = players_list[check_idx]
        
        if player.eliminated:
            continue
        
        matching = player.can_refute(suggestion)
        
        if matching:
            if player.is_ai:
                card_to_show = random.choice(matching)
            else:
                if len(matching) == 1:
                    card_to_show = matching[0]
                    print(f"\nYou have {card_to_show} to show")
                else:
                    print(f"\nYou can show: {', '.join(matching)}")
                    while True:
                        choice = input("Which card to show? ").strip()
                        if choice in matching:
                            card_to_show = choice
                            break
                        print("Invalid choice")
            
            return (player, card_to_show)
    
    return None

def make_accusation(player):
    print(f"\n{player.name} is making an accusation!")
    
    if player.is_ai:
        guess = player.knowledge.get_solution_guess()
        if guess:
            char, weapon, room = guess
            print(f"AI accuses: {char} with {weapon} in {room}")
        else:
            print("AI is not ready to accuse yet")
            return None
    else:
        print("\nSelect character:")
        for i, char in enumerate(character_names, 1):
            print(f"{i}. {char}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-6): "))
                if 1 <= choice <= 6:
                    char = character_names[choice - 1]
                    break
            except ValueError:
                print("Invalid input")
        
        print("\nSelect weapon:")
        for i, weapon in enumerate(weapon_names, 1):
            print(f"{i}. {weapon}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-6): "))
                if 1 <= choice <= 6:
                    weapon = weapon_names[choice - 1]
                    break
            except ValueError:
                print("Invalid input")
        
        print("\nSelect room:")
        rooms = list(mansion_rooms.keys())
        for i, room in enumerate(rooms, 1):
            print(f"{i}. {room}")
        
        while True:
            try:
                choice = int(input("Enter choice (1-9): "))
                if 1 <= choice <= 9:
                    room = rooms[choice - 1]
                    break
            except ValueError:
                print("Invalid input")
        
        guess = (char, weapon, room)
        print(f"\nAccusation: {char} with {weapon} in {room}")
    
    if guess:
        char, weapon, room = guess
        if (char == solution["character"] and 
            weapon == solution["weapon"] and 
            room == solution["room"]):
            print(f"\n{'*' * 60}")
            print(f"CORRECT! {player.name} wins!")
            print(f"The solution was: {char} with {weapon} in {room}")
            print(f"{'*' * 60}")
            return True
        else:
            print(f"\nWRONG! {player.name} is eliminated from making accusations")
            print("You can still refute suggestions from other players")
            player.eliminated = True
            game_log.append(f"{player.name} made incorrect accusation and was eliminated")
            return False
    
    return None

def ai_choose_move(player, moves):
    target_room = player.knowledge.choose_room_to_visit()
    
    if target_room in mansion_rooms:
        target_pos = mansion_rooms[target_room]
        current_x, current_y = player.position
        target_x, target_y = target_pos
        
        if current_x < target_x and moves > 0:
            return "DOWN", min(moves, target_x - current_x)
        elif current_x > target_x and moves > 0:
            return "UP", min(moves, current_x - target_x)
        elif current_y < target_y and moves > 0:
            return "RIGHT", min(moves, target_y - current_y)
        elif current_y > target_y and moves > 0:
            return "LEFT", min(moves, current_y - target_y)
    
    available = get_available_directions(player.position)
    if available:
        direction = random.choice(available)
        steps = random.randint(1, min(moves, 2))
        return direction, steps
    
    return None, 0

def player_turn():
    global current_turn
    
    player = players_list[current_turn]
    
    if player.eliminated:
        print(f"\n{player.name} is eliminated from active play")
        current_turn = (current_turn + 1) % len(players_list)
        return False
    
    print(f"\n{'=' * 60}")
    print(f"{player.name}'s Turn")
    print(f"Character: {player.character}")
    print(f"{'=' * 60}")
    
    if player.current_room:
        print(f"Current location: {player.current_room} at {player.position}")
    else:
        print(f"Current position: {player.position}")
    
    if not player.is_ai:
        print(f"Your cards: {', '.join(player.cards)}")
        
        view_log = input("\nView game log? (y/n): ").lower().strip()
        if view_log == 'y':
            show_game_log()
        
        accuse = input("\nMake an accusation? (y/n): ").lower().strip()
        if accuse == 'y':
            result = make_accusation(player)
            if result == True:
                return True
            elif result == False:
                current_turn = (current_turn + 1) % len(players_list)
                return False
    else:
        if player.knowledge.get_solution_guess():
            print("AI is confident about the solution")
            result = make_accusation(player)
            if result == True:
                return True
            elif result == False:
                current_turn = (current_turn + 1) % len(players_list)
                return False
    
    if player.in_room and player.current_room in secret_passages:
        dest = secret_passages[player.current_room]
        
        if player.is_ai:
            use_passage = random.choice([True, False])
        else:
            choice = input(f"Use secret passage to {dest}? (y/n): ").lower().strip()
            use_passage = choice == 'y'
        
        if use_passage:
            success, message = use_secret_passage(player)
            print(message)
            if success:
                make_suggestion(player, player.current_room)
                current_turn = (current_turn + 1) % len(players_list)
                return False
    
    if not player.is_ai:
        input("Press Enter to roll the die...")
    
    roll = roll_die()
    print(f"Rolled: {roll}")
    
    moves_remaining = roll
    
    if player.in_room:
        print("Exiting room (uses 1 move)")
        x, y = player.position
        
        if x > 0:
            exit_pos = (x - 1, y)
        elif x < 2:
            exit_pos = (x + 1, y)
        elif y > 0:
            exit_pos = (x, y - 1)
        else:
            exit_pos = (x, y + 1)
        
        player.position = exit_pos
        player.in_room = False
        player.current_room = None
        moves_remaining -= 1
        print(f"Exited to position {exit_pos}. Moves left: {moves_remaining}")
    
    while moves_remaining > 0:
        print(f"\nMoves remaining: {moves_remaining}")
        available = get_available_directions(player.position)
        print(f"Available directions: {', '.join(available)}")
        
        if player.is_ai:
            direction, steps = ai_choose_move(player, moves_remaining)
            if direction:
                print(f"AI moves {direction} {steps}")
            else:
                print("AI stops moving")
                break
        else:
            move_input = input("Enter move (e.g., UP 2) or STOP: ").strip().upper()
            
            if move_input == "STOP":
                print("Stopping movement")
                break
            
            try:
                parts = move_input.split()
                if len(parts) != 2:
                    print("Format: DIRECTION STEPS")
                    continue
                
                direction = parts[0]
                steps = int(parts[1])
                
                if steps <= 0:
                    print("Steps must be positive")
                    continue
                
                if steps > moves_remaining:
                    print(f"Only {moves_remaining} moves left")
                    continue
                
                if direction not in available:
                    print(f"Cannot go {direction} from here")
                    continue
            except ValueError:
                print("Invalid input format")
                continue
        
        success, message = move_in_direction(player, direction, steps)
        
        if success:
            print(message)
            moves_remaining -= steps
            
            if player.in_room:
                print(f"Entered {player.current_room}!")
                make_suggestion(player, player.current_room)
                moves_remaining = 0
        else:
            print(f"Move failed: {message}")
            if player.is_ai:
                break
    
    current_turn = (current_turn + 1) % len(players_list)
    return False

def show_game_log():
    print("\n" + "=" * 60)
    print("GAME LOG")
    print("=" * 60)
    for entry in game_log[-10:]:
        print(entry)
    print("=" * 60)

def main():
    print("\n" + "=" * 60)
    print("CLUEDO - MURDER MYSTERY GAME")
    print("Project 2 Part 2")
    print("=" * 60)
    
    initialize_mansion()
    cards = setup_game()
    create_players(cards)
    display_mansion_layout()
    
    print("\nGame starting...")
    print("Players can make accusations at any time during their turn")
    print("Incorrect accusations eliminate you from winning but you can still refute")
    
    turn_number = 0
    game_won = False
    
    while not game_won:
        active_players = [p for p in players_list if not p.eliminated]
        if len(active_players) <= 1:
            print("\nGame over - not enough active players")
            break
        
        game_won = player_turn()
        turn_number += 1
        
        if turn_number % len(players_list) == 0:
            print(f"\n--- Round {turn_number // len(players_list)} complete ---")
            
            if not game_won:
                continue_game = input("Continue? (y/n): ").lower().strip()
                if continue_game != 'y':
                    break
    
    if not game_won:
        print("\nGame ended without a winner")
        print(f"The solution was: {solution['character']} with {solution['weapon']} in {solution['room']}")
    
    print("\nThank you for playing Cluedo!")

if __name__ == "__main__":
    main()
