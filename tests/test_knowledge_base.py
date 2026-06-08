import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cluedo_game_part2 as game


def make_kb():
    # Access mansion_rooms via module attribute so we always get the
    # dict that initialize_mansion() just created (it rebinds the global).
    game.initialize_mansion()
    return game.KnowledgeBase("Miss Scarlett", game.mansion_rooms)


# --- own cards ---

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


# --- refutation recording ---

def test_refutation_removes_card_from_solution():
    kb = make_kb()
    kb.record_refutation("Player 2", ("Colonel Mustard", "Rope", "Kitchen"), "Rope")
    assert "Rope" not in kb.possible_solution["weapons"]
    assert "Rope" in kb.shown_cards


def test_refutation_records_player_has():
    kb = make_kb()
    kb.record_refutation("Player 2", ("Colonel Mustard", "Rope", "Kitchen"), "Kitchen")
    assert "Kitchen" in kb.player_has["Player 2"]


# --- no-refutation recording ---

def test_no_refutation_marks_all_three_cards():
    kb = make_kb()
    suggestion = ("Colonel Mustard", "Rope", "Kitchen")
    kb.record_no_refutation("Player 2", suggestion)
    not_has = kb.player_not_has["Player 2"]
    assert "Colonel Mustard" in not_has
    assert "Rope" in not_has
    assert "Kitchen" in not_has


# --- deduction by elimination ---

def test_infer_card_when_ai_owns_two_of_three():
    kb = make_kb()
    kb.mark_own_card("Colonel Mustard")
    kb.mark_own_card("Rope")
    # Player 2 refutes but AI doesn't see which card — must be Kitchen
    kb.record_someone_refuted("Player 2", ("Colonel Mustard", "Rope", "Kitchen"))
    assert "Kitchen" in kb.shown_cards
    assert "Kitchen" not in kb.possible_solution["rooms"]


def test_no_inference_when_multiple_possibilities():
    kb = make_kb()
    kb.record_someone_refuted("Player 2", ("Colonel Mustard", "Rope", "Kitchen"))
    # All three unknown — can't deduce anything
    assert len(kb.shown_cards) == 0


# --- accusation readiness ---

def test_get_solution_guess_requires_single_per_category():
    kb = make_kb()
    for char in game.character_names:
        if char != "Miss Scarlett":
            kb.eliminate_from_solution(char)
    for weapon in game.weapon_names:
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
    for char in game.character_names:
        if char != "Miss Scarlett":
            kb.eliminate_from_solution(char)
    for weapon in game.weapon_names[2:]:
        kb.eliminate_from_solution(weapon)
    for room in list(game.mansion_rooms.keys()):
        if room != "Kitchen":
            kb.eliminate_from_solution(room)
    assert kb.get_solution_guess() is None
