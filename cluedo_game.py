"""
Cluedo — AI Logical Deduction Agent

Text-based Cluedo (Clue) with an intelligent AI player that uses
knowledge-based reasoning, logical inference, and strategic movement
to solve the murder mystery. Supports 3–6 players (any mix of human/AI).
"""
import random

WEAPON_NAMES = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
CHARACTER_NAMES = [
    "Miss Scarlett", "Colonel Mustard", "Mrs. White",
    "Reverend Green", "Mrs. Peacock", "Professor Plum",
]

# Module-level game state (reset via initialize_mansion / setup_game)
players_list = []
current_turn = 0
solution = {}
weapon_locations = {}
mansion_rooms = {}
secret_passages = {}
starting_positions = {}
game_log = []


def initialize_mansion():
    global mansion_rooms, secret_passages, starting_positions, weapon_locations

    mansion_rooms = {
        "Study": (0, 0), "Hall": (0, 1), "Lounge": (0, 2),
        "Library": (1, 0), "Billiard Room": (1, 1), "Dining Room": (1, 2),
        "Conservatory": (2, 0), "Ballroom": (2, 1), "Kitchen": (2, 2),
    }

    secret_passages = {
        "Study": "Kitchen", "Kitchen": "Study",
        "Conservatory": "Lounge", "Lounge": "Conservatory",
    }

    starting_positions = {
        "Miss Scarlett": (0, 0), "Colonel Mustard": (0, 2),
        "Mrs. White": (1, 0), "Reverend Green": (1, 2),
        "Mrs. Peacock": (2, 0), "Professor Plum": (2, 2),
    }

    rooms = list(mansion_rooms.keys())
    random.shuffle(rooms)
    for i, weapon in enumerate(WEAPON_NAMES):
        weapon_locations[weapon] = rooms[i % len(rooms)]


def display_mansion_layout():
    print("\n" + "=" * 60)
    print("CLUEDO MANSION LAYOUT")
    print("=" * 60)
    print("Study (0,0)          Hall (0,1)          Lounge (0,2)")
    print("Library (1,0)        Billiard Room (1,1) Dining Room (1,2)")
    print("Conservatory (2,0)   Ballroom (2,1)      Kitchen (2,2)")
    print("\nSecret Passages: Study <-> Kitchen  |  Conservatory <-> Lounge")
    print("=" * 60)


# ---------------------------------------------------------------------------
# KnowledgeBase — AI reasoning engine
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """
    Tracks what one AI player knows and can infer about the murder solution.

    Internally represents knowledge as sets of remaining possibilities per
    category. Elimination happens through three channels:
      1. Own cards dealt to the AI.
      2. Cards directly shown during refutations.
      3. Deduction: when a refuter's possible matching cards are narrowed to
         one (because the AI already ruled out the others), the remaining card
         is deduced without being shown.

    The AI only accuses when every category is pinned to exactly one candidate.
    """

    def __init__(self, character_name, room_names):
        self.character = character_name
        # Store locally so eliminate_from_solution never touches a global.
        self._room_names = set(room_names)
        self.own_cards = set()
        self.possible_solution = {
            "characters": set(CHARACTER_NAMES),
            "weapons": set(WEAPON_NAMES),
            "rooms": set(room_names),
        }
        self.player_has = {}      # player_name -> {cards confirmed held}
        self.player_not_has = {}  # player_name -> {cards confirmed NOT held}
        self.shown_cards = set()  # all cards revealed so far

    # --- internal helpers ---

    def _category(self, card):
        if card in CHARACTER_NAMES:
            return "characters"
        if card in WEAPON_NAMES:
            return "weapons"
        if card in self._room_names:
            return "rooms"
        return None

    # --- public interface ---

    def mark_own_card(self, card):
        self.own_cards.add(card)
        self.eliminate_from_solution(card)

    def eliminate_from_solution(self, card):
        cat = self._category(card)
        if cat:
            self.possible_solution[cat].discard(card)

    def record_refutation(self, player_name, card_shown=None):
        """Record that player_name showed card_shown (private to the AI suggester)."""
        if card_shown:
            self.shown_cards.add(card_shown)
            self.eliminate_from_solution(card_shown)
            self.player_has.setdefault(player_name, set()).add(card_shown)

    def record_no_refutation(self, player_name, suggestion):
        """Record that player_name holds none of the 3 suggested cards."""
        char, weapon, room = suggestion
        self.player_not_has.setdefault(player_name, set()).update([char, weapon, room])

    def record_someone_refuted(self, player_name, suggestion):
        """
        Called when player_name refuted suggestion but the shown card is private.
        Deduces which card was shown when only one candidate remains possible.
        """
        char, weapon, room = suggestion
        known_not_has = self.player_not_has.get(player_name, set())
        candidates = [
            c for c in (char, weapon, room)
            if c not in known_not_has and c not in self.own_cards
        ]
        if len(candidates) == 1:
            deduced = candidates[0]
            self.shown_cards.add(deduced)
            self.eliminate_from_solution(deduced)
            self.player_has.setdefault(player_name, set()).add(deduced)

    def get_solution_guess(self):
        """Returns (char, weapon, room) only when all 3 categories have exactly 1 candidate."""
        if all(len(v) == 1 for v in self.possible_solution.values()):
            return (
                next(iter(self.possible_solution["characters"])),
                next(iter(self.possible_solution["weapons"])),
                next(iter(self.possible_solution["rooms"])),
            )
        return None

    def make_suggestion(self, current_room):
        """Choose the most informative (char, weapon) from still-unknown candidates."""
        unknown_chars = [c for c in self.possible_solution["characters"] if c not in self.own_cards]
        unknown_weapons = [w for w in self.possible_solution["weapons"] if w not in self.own_cards]

        char = random.choice(unknown_chars) if unknown_chars else random.choice(CHARACTER_NAMES)
        weapon = random.choice(unknown_weapons) if unknown_weapons else random.choice(WEAPON_NAMES)
        return char, weapon, current_room

    def choose_room_to_visit(self):
        """Pick a room that is still a possible solution candidate."""
        unknown_rooms = [r for r in self.possible_solution["rooms"] if r not in self.own_cards]
        return random.choice(unknown_rooms) if unknown_rooms else random.choice(list(self._room_names))

    def show_status(self):
        """Print the current KB state so observers can follow AI reasoning."""
        print(f"\n[AI {self.character} — KB status]")
        for cat, candidates in self.possible_solution.items():
            print(f"  Possible {cat}: {', '.join(sorted(candidates))}")
        guess = self.get_solution_guess()
        if guess:
            print(f"  >> Ready to accuse: {guess[0]} with {guess[1]} in {guess[2]}")


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

class Player:
    def __init__(self, name, character, position, is_ai=False):
        self.name = name
        self.character = character
        self.position = position
        self.cards = []
        self.in_room = True
        self.current_room = self._room_at(position)
        self.is_ai = is_ai
        self.eliminated = False

        if is_ai:
            # Pass room names at construction time — no global dependency later.
            self.knowledge = KnowledgeBase(character, list(mansion_rooms.keys()))

    def _room_at(self, pos):
        for name, rpos in mansion_rooms.items():
            if pos == rpos:
                return name
        return None

    def add_card(self, card):
        self.cards.append(card)
        if self.is_ai:
            self.knowledge.mark_own_card(card)

    def can_refute(self, suggestion):
        char, weapon, room = suggestion
        return [c for c in (char, weapon, room) if c in self.cards]


# ---------------------------------------------------------------------------
# Game setup
# ---------------------------------------------------------------------------

def setup_game():
    global solution

    solution = {
        "character": random.choice(CHARACTER_NAMES),
        "weapon": random.choice(WEAPON_NAMES),
        "room": random.choice(list(mansion_rooms.keys())),
    }

    print("Murder solution has been sealed in the envelope.")

    all_cards = (
        [c for c in CHARACTER_NAMES if c != solution["character"]]
        + [w for w in WEAPON_NAMES if w != solution["weapon"]]
        + [r for r in mansion_rooms if r != solution["room"]]
    )
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

    characters = CHARACTER_NAMES[:num_players]
    ai_indices = []

    if num_ai > 0:
        print(f"\nSelect which player positions should be AI (1-{num_players}):")
        for i in range(num_ai):
            while True:
                try:
                    idx = int(input(f"  AI player {i + 1} position: ")) - 1
                    if 0 <= idx < num_players and idx not in ai_indices:
                        ai_indices.append(idx)
                        break
                    print("  Invalid or already selected. Try again.")
                except ValueError:
                    print("  Please enter a number.")

    for i in range(num_players):
        char = characters[i]
        pos = starting_positions[char]
        is_ai = i in ai_indices
        label = "AI" if is_ai else "Human"
        players_list.append(Player(f"Player {i + 1} ({label})", char, pos, is_ai))

    cards_per = len(cards) // num_players
    for i, player in enumerate(players_list):
        start = i * cards_per
        end = start + cards_per if i < num_players - 1 else len(cards)
        for card in cards[start:end]:
            player.add_card(card)

    print(f"\nGame setup complete with {num_players} players.")
    for player in players_list:
        print(f"  {player.name} as {player.character} starting in {player.current_room}")

    print("\nWeapon starting locations:")
    for weapon, room in weapon_locations.items():
        print(f"  {weapon} in {room}")


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------

def is_valid_position(pos):
    x, y = pos
    return 0 <= x <= 2 and 0 <= y <= 2


def get_available_directions(pos):
    x, y = pos
    dirs = []
    if x > 0: dirs.append("UP")
    if x < 2: dirs.append("DOWN")
    if y > 0: dirs.append("LEFT")
    if y < 2: dirs.append("RIGHT")
    return dirs


def move_in_direction(player, direction, steps):
    x, y = player.position
    deltas = {"UP": (-steps, 0), "DOWN": (steps, 0), "LEFT": (0, -steps), "RIGHT": (0, steps)}

    if direction not in deltas:
        return False, "Invalid direction"

    dx, dy = deltas[direction]
    new_pos = (x + dx, y + dy)

    if not is_valid_position(new_pos):
        return False, "Cannot move there — out of bounds"

    player.position = new_pos
    room = player._room_at(new_pos)
    if room:
        player.in_room = True
        player.current_room = room
        msg = f"Moved {direction} {steps} to {room}"
        if room in secret_passages:
            msg += f" (secret passage to {secret_passages[room]} available)"
        return True, msg

    player.in_room = False
    player.current_room = None
    return True, f"Moved {direction} {steps} to position {new_pos}"


def use_secret_passage(player):
    dest = secret_passages.get(player.current_room)
    if not dest:
        return False, "No secret passage in this room"
    player.position = mansion_rooms[dest]
    player.current_room = dest
    player.in_room = True
    return True, f"Used secret passage to {dest}"


def roll_die():
    return random.randint(1, 6)


# ---------------------------------------------------------------------------
# Suggestions and refutations
# ---------------------------------------------------------------------------

def _prompt_card_choice(player, matching):
    if len(matching) == 1:
        print(f"  You must show: {matching[0]}")
        return matching[0]
    print(f"  You can show: {', '.join(matching)}")
    while True:
        choice = input("  Which card to show? ").strip()
        if choice in matching:
            return choice
        print("  Invalid — choose from the list above.")


def check_refutation(suggester, suggestion):
    """
    Checks each non-suggesting, non-eliminated player (clockwise) for a match.

    Returns (refuter, card_shown, players_who_passed).
    players_who_passed contains every player asked before the refuter was found;
    they have been confirmed as not holding any of the 3 suggested cards.
    """
    start_idx = players_list.index(suggester)
    players_passed = []

    for i in range(1, len(players_list)):
        player = players_list[(start_idx + i) % len(players_list)]

        if player.eliminated:
            continue

        matching = player.can_refute(suggestion)
        if not matching:
            players_passed.append(player)
            continue

        if player.is_ai:
            card_to_show = random.choice(matching)
        else:
            card_to_show = _prompt_card_choice(player, matching)

        return player, card_to_show, players_passed

    return None, None, players_passed


def make_suggestion(suggesting_player, room):
    print(f"\n{suggesting_player.name} is making a suggestion in {room}")

    if suggesting_player.is_ai:
        char, weapon, suggested_room = suggesting_player.knowledge.make_suggestion(room)
        print(f"  AI suggests: {char} with {weapon} in {suggested_room}")
    else:
        print("\nSelect character:")
        for i, c in enumerate(CHARACTER_NAMES, 1):
            print(f"  {i}. {c}")
        while True:
            try:
                choice = int(input("  Choice (1-6): "))
                if 1 <= choice <= 6:
                    char = CHARACTER_NAMES[choice - 1]
                    break
                print("  Enter 1-6.")
            except ValueError:
                print("  Invalid input.")

        print("\nSelect weapon:")
        for i, w in enumerate(WEAPON_NAMES, 1):
            print(f"  {i}. {w}")
        while True:
            try:
                choice = int(input("  Choice (1-6): "))
                if 1 <= choice <= 6:
                    weapon = WEAPON_NAMES[choice - 1]
                    break
                print("  Enter 1-6.")
            except ValueError:
                print("  Invalid input.")

        suggested_room = room
        print(f"\n  Suggestion: {char} with {weapon} in {room}")

    suggestion = (char, weapon, suggested_room)

    # Move suggested character to the room
    for p in players_list:
        if p.character == char and p != suggesting_player:
            old = p.current_room or f"position {p.position}"
            p.position = mansion_rooms[suggested_room]
            p.in_room = True
            p.current_room = suggested_room
            print(f"  Moved {char} from {old} to {suggested_room}")
            break

    # Move suggested weapon to the room
    old_room = weapon_locations.get(weapon)
    weapon_locations[weapon] = suggested_room
    if old_room != suggested_room:
        print(f"  Moved {weapon} from {old_room} to {suggested_room}")

    refuter, card_shown, players_passed = check_refutation(suggesting_player, suggestion)

    # Update every AI's KB with what they can deduce from who passed.
    # A player who passed holds none of the 3 suggested cards — record this
    # for every AI (including the suggester, since it updates others' KBs too).
    for passed_player in players_passed:
        for p in players_list:
            if p.is_ai:
                p.knowledge.record_no_refutation(passed_player.name, suggestion)

    if refuter:
        print(f"\n  {refuter.name} refutes the suggestion.")

        if suggesting_player.is_ai:
            print(f"  Card shown privately to {suggesting_player.name}.")
            suggesting_player.knowledge.record_refutation(refuter.name, card_shown)
        else:
            print(f"  Card shown to you: {card_shown}")

        # AI observers who are neither the suggester nor the refuter note who refuted.
        # They don't see the card but can deduce it if only one candidate remains.
        for p in players_list:
            if p.is_ai and p != suggesting_player and p != refuter:
                p.knowledge.record_someone_refuted(refuter.name, suggestion)
    else:
        print("\n  No one could refute the suggestion!")

    game_log.append(
        f"{suggesting_player.name} suggested {char} with {weapon} in {suggested_room}"
        + (f" → refuted by {refuter.name}" if refuter else " → unrefuted")
    )
    return suggestion


def make_accusation(player):
    print(f"\n{player.name} is making an accusation!")

    if player.is_ai:
        guess = player.knowledge.get_solution_guess()
        if not guess:
            print("  AI is not confident enough to accuse yet.")
            return None
        char, weapon, room = guess
        print(f"  AI accuses: {char} with {weapon} in {room}")
    else:
        print("\nSelect character:")
        for i, c in enumerate(CHARACTER_NAMES, 1):
            print(f"  {i}. {c}")
        while True:
            try:
                choice = int(input("  Choice (1-6): "))
                if 1 <= choice <= 6:
                    char = CHARACTER_NAMES[choice - 1]
                    break
            except ValueError:
                print("  Invalid input.")

        print("\nSelect weapon:")
        for i, w in enumerate(WEAPON_NAMES, 1):
            print(f"  {i}. {w}")
        while True:
            try:
                choice = int(input("  Choice (1-6): "))
                if 1 <= choice <= 6:
                    weapon = WEAPON_NAMES[choice - 1]
                    break
            except ValueError:
                print("  Invalid input.")

        rooms = list(mansion_rooms.keys())
        print("\nSelect room:")
        for i, r in enumerate(rooms, 1):
            print(f"  {i}. {r}")
        while True:
            try:
                choice = int(input("  Choice (1-9): "))
                if 1 <= choice <= 9:
                    room = rooms[choice - 1]
                    break
            except ValueError:
                print("  Invalid input.")

        guess = (char, weapon, room)
        print(f"\n  Accusation: {char} with {weapon} in {room}")

    char, weapon, room = guess
    if (char == solution["character"]
            and weapon == solution["weapon"]
            and room == solution["room"]):
        print(f"\n{'*' * 60}")
        print(f"CORRECT! {player.name} wins!")
        print(f"The solution was: {char} with {weapon} in {room}")
        print("*" * 60)
        return True

    print(f"\n  WRONG! {player.name} is eliminated from making accusations.")
    print("  You may still refute suggestions from other players.")
    player.eliminated = True
    game_log.append(f"{player.name} made incorrect accusation and was eliminated")
    return False


# ---------------------------------------------------------------------------
# AI movement helpers
# ---------------------------------------------------------------------------

def _ai_should_use_passage(player):
    """Use the secret passage only when the destination is still an unknown room."""
    dest = secret_passages.get(player.current_room)
    return dest is not None and dest in player.knowledge.possible_solution["rooms"]


def ai_choose_move(player, moves_remaining):
    target_room = player.knowledge.choose_room_to_visit()
    target_pos = mansion_rooms[target_room]
    cx, cy = player.position
    tx, ty = target_pos

    if cx < tx: return "DOWN", min(moves_remaining, tx - cx)
    if cx > tx: return "UP",   min(moves_remaining, cx - tx)
    if cy < ty: return "RIGHT", min(moves_remaining, ty - cy)
    if cy > ty: return "LEFT",  min(moves_remaining, cy - ty)

    available = get_available_directions(player.position)
    if available:
        return random.choice(available), random.randint(1, min(moves_remaining, 2))
    return None, 0


# ---------------------------------------------------------------------------
# Turn management
# ---------------------------------------------------------------------------

def player_turn():
    global current_turn

    player = players_list[current_turn]

    if player.eliminated:
        print(f"\n{player.name} is eliminated — skipping turn.")
        current_turn = (current_turn + 1) % len(players_list)
        return False

    print(f"\n{'=' * 60}")
    print(f"{player.name}'s Turn  |  Character: {player.character}")
    print("=" * 60)
    print(f"Location: {player.current_room or f'position {player.position}'}")

    if not player.is_ai:
        print(f"Your cards: {', '.join(player.cards)}")
        if input("\nView game log? (y/n): ").lower().strip() == "y":
            _show_game_log()
        if input("Make an accusation? (y/n): ").lower().strip() == "y":
            result = make_accusation(player)
            if result is True:
                return True
            if result is False:
                current_turn = (current_turn + 1) % len(players_list)
                return False
    else:
        player.knowledge.show_status()
        if player.knowledge.get_solution_guess():
            result = make_accusation(player)
            if result is True:
                return True
            if result is False:
                current_turn = (current_turn + 1) % len(players_list)
                return False

    # Secret passage option
    if player.in_room and player.current_room in secret_passages:
        dest = secret_passages[player.current_room]
        use_passage = (
            _ai_should_use_passage(player)
            if player.is_ai
            else input(f"Use secret passage to {dest}? (y/n): ").lower().strip() == "y"
        )
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

    # Exit room (costs 1 move)
    if player.in_room:
        print("Exiting room (costs 1 move)")
        x, y = player.position
        # Pick the first valid adjacent corridor tile
        for exit_pos in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if is_valid_position(exit_pos) and player._room_at(exit_pos) is None:
                player.position = exit_pos
                break
        else:
            # All adjacent tiles are rooms — just step to the first valid one
            for exit_pos in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if is_valid_position(exit_pos):
                    player.position = exit_pos
                    break
        player.in_room = False
        player.current_room = None
        moves_remaining -= 1
        print(f"Exited to {player.position}. Moves left: {moves_remaining}")

    # Movement loop
    while moves_remaining > 0:
        available = get_available_directions(player.position)
        print(f"\nMoves remaining: {moves_remaining}  |  Available: {', '.join(available)}")

        if player.is_ai:
            direction, steps = ai_choose_move(player, moves_remaining)
            if direction is None:
                break
            print(f"  AI moves {direction} {steps}")
        else:
            move_input = input("Move (e.g. UP 2) or STOP: ").strip().upper()
            if move_input == "STOP":
                break
            try:
                parts = move_input.split()
                if len(parts) != 2:
                    print("  Format: DIRECTION STEPS")
                    continue
                direction, steps = parts[0], int(parts[1])
                if steps <= 0:
                    print("  Steps must be positive.")
                    continue
                if steps > moves_remaining:
                    print(f"  Only {moves_remaining} moves left.")
                    continue
                if direction not in available:
                    print(f"  Cannot go {direction} from here.")
                    continue
            except ValueError:
                print("  Invalid input.")
                continue

        success, message = move_in_direction(player, direction, steps)
        if success:
            print(f"  {message}")
            moves_remaining -= steps
            if player.in_room:
                print(f"  Entered {player.current_room}!")
                make_suggestion(player, player.current_room)
                break
        else:
            print(f"  Move failed: {message}")
            if player.is_ai:
                break

    current_turn = (current_turn + 1) % len(players_list)
    return False


def _show_game_log():
    print("\n" + "=" * 60)
    print("GAME LOG (last 10 entries)")
    print("=" * 60)
    for entry in game_log[-10:]:
        print(f"  {entry}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("       CLUEDO — AI LOGICAL DEDUCTION AGENT")
    print("=" * 60)

    initialize_mansion()
    cards = setup_game()
    create_players(cards)
    display_mansion_layout()

    print("\nGame starting!")
    print("Players may accuse at any time during their turn.")
    print("A wrong accusation eliminates you from winning — but you can still refute.\n")

    turn_number = 0
    game_won = False

    while not game_won:
        active = [p for p in players_list if not p.eliminated]
        if len(active) <= 1:
            print("\nGame over — not enough active players remain.")
            break

        game_won = player_turn()
        turn_number += 1

        if turn_number % len(players_list) == 0:
            round_num = turn_number // len(players_list)
            print(f"\n--- Round {round_num} complete ---")
            if not game_won:
                if input("Continue? (y/n): ").lower().strip() != "y":
                    break

    if not game_won:
        print("\nGame ended without a winner.")
        print(
            f"The solution was: {solution['character']} "
            f"with {solution['weapon']} in {solution['room']}"
        )

    print("\nThank you for playing Cluedo!")


if __name__ == "__main__":
    main()
