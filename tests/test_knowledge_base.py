import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cluedo_game as game


def make_kb(character="Miss Scarlett"):
    game.initialize_mansion()
    return game.KnowledgeBase(character, list(game.mansion_rooms.keys()))


# ---------------------------------------------------------------------------
# Own cards
# ---------------------------------------------------------------------------

def test_own_card_eliminates_character():
    kb = make_kb()
    kb.mark_own_card("Colonel Mustard")
    assert "Colonel Mustard" not in kb.possible_solution["characters"]
    assert "Colonel Mustard" in kb.own_cards


def test_own_card_eliminates_weapon():
    kb = make_kb()
    kb.mark_own_card("Rope")
    assert "Rope" not in kb.possible_solution["weapons"]


def test_own_card_eliminates_room():
    kb = make_kb()
    kb.mark_own_card("Kitchen")
    assert "Kitchen" not in kb.possible_solution["rooms"]


# ---------------------------------------------------------------------------
# Refutation recording
# ---------------------------------------------------------------------------

def test_refutation_removes_card_from_solution():
    kb = make_kb()
    kb.record_refutation("Player 2", "Rope")
    assert "Rope" not in kb.possible_solution["weapons"]
    assert "Rope" in kb.shown_cards


def test_refutation_records_player_has():
    kb = make_kb()
    kb.record_refutation("Player 2", "Kitchen")
    assert "Kitchen" in kb.player_has["Player 2"]


def test_refutation_with_no_card_shown_is_no_op():
    kb = make_kb()
    kb.record_refutation("Player 2")
    assert len(kb.shown_cards) == 0


# ---------------------------------------------------------------------------
# No-refutation recording
# ---------------------------------------------------------------------------

def test_no_refutation_marks_all_three_cards():
    kb = make_kb()
    suggestion = ("Colonel Mustard", "Rope", "Kitchen")
    kb.record_no_refutation("Player 2", suggestion)
    not_has = kb.player_not_has["Player 2"]
    assert "Colonel Mustard" in not_has
    assert "Rope" in not_has
    assert "Kitchen" in not_has


def test_no_refutation_does_not_eliminate_from_solution():
    """Cards that nobody refuted could still be the solution — must NOT be discarded."""
    kb = make_kb()
    suggestion = ("Colonel Mustard", "Rope", "Kitchen")
    kb.record_no_refutation("Player 2", suggestion)
    assert "Colonel Mustard" in kb.possible_solution["characters"]
    assert "Rope" in kb.possible_solution["weapons"]
    assert "Kitchen" in kb.possible_solution["rooms"]


# ---------------------------------------------------------------------------
# Deduction by elimination (record_someone_refuted)
# ---------------------------------------------------------------------------

def test_infer_card_when_ai_owns_two_of_three():
    kb = make_kb()
    kb.mark_own_card("Colonel Mustard")
    kb.mark_own_card("Rope")
    # AI doesn't see which card was shown — must be Kitchen
    kb.record_someone_refuted("Player 2", ("Colonel Mustard", "Rope", "Kitchen"))
    assert "Kitchen" in kb.shown_cards
    assert "Kitchen" not in kb.possible_solution["rooms"]


def test_infer_card_when_not_has_eliminates_two():
    kb = make_kb()
    kb.record_no_refutation("Player 2", ("Colonel Mustard", "Rope", "Study"))
    # Now Player 2 refutes (Colonel Mustard, Rope, Kitchen) — must be Kitchen
    kb.record_someone_refuted("Player 2", ("Colonel Mustard", "Rope", "Kitchen"))
    assert "Kitchen" in kb.shown_cards


def test_no_inference_when_multiple_possibilities():
    kb = make_kb()
    kb.record_someone_refuted("Player 2", ("Colonel Mustard", "Rope", "Kitchen"))
    assert len(kb.shown_cards) == 0


# ---------------------------------------------------------------------------
# Accusation readiness
# ---------------------------------------------------------------------------

def test_get_solution_guess_requires_single_per_category():
    kb = make_kb()
    for char in game.CHARACTER_NAMES:
        if char != "Miss Scarlett":
            kb.eliminate_from_solution(char)
    for weapon in game.WEAPON_NAMES:
        if weapon != "Candlestick":
            kb.eliminate_from_solution(weapon)
    for room in list(game.mansion_rooms.keys()):
        if room != "Kitchen":
            kb.eliminate_from_solution(room)
    assert kb.get_solution_guess() == ("Miss Scarlett", "Candlestick", "Kitchen")


def test_get_solution_guess_returns_none_when_uncertain():
    kb = make_kb()
    assert kb.get_solution_guess() is None


def test_get_solution_guess_returns_none_with_two_weapons_left():
    kb = make_kb()
    for char in game.CHARACTER_NAMES:
        if char != "Miss Scarlett":
            kb.eliminate_from_solution(char)
    for weapon in game.WEAPON_NAMES[2:]:
        kb.eliminate_from_solution(weapon)
    for room in list(game.mansion_rooms.keys()):
        if room != "Kitchen":
            kb.eliminate_from_solution(room)
    assert kb.get_solution_guess() is None


# ---------------------------------------------------------------------------
# Global independence — KnowledgeBase must not break if mansion_rooms changes
# ---------------------------------------------------------------------------

def test_eliminate_from_solution_uses_local_room_names():
    """eliminate_from_solution must work even if mansion_rooms global is cleared."""
    game.initialize_mansion()
    kb = game.KnowledgeBase("Miss Scarlett", list(game.mansion_rooms.keys()))
    game.mansion_rooms.clear()  # simulate the global being unavailable
    kb.eliminate_from_solution("Kitchen")  # must not raise and must eliminate correctly
    assert "Kitchen" not in kb.possible_solution["rooms"]
    game.initialize_mansion()  # restore for other tests
