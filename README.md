# Cluedo AI — Logical Deduction Agent

A Python implementation of the classic **Cluedo (Clue)** murder mystery board game with an AI player that uses **knowledge representation**, **logical inference**, and **strategic decision-making** to solve the mystery.

---

## One-liner

> Developed a complete text-based Cluedo board game with an intelligent AI player that uses a knowledge base, logical inference, and strategic movement to solve the murder mystery — supporting any combination of 3–6 human and AI players.

---

## Project Structure

```
├── cluedo_game.py              # Core game engine (basic mechanics)
├── cluedo_game_part2.py        # Full game with AI logical deduction agent
├── tests/
│   └── test_knowledge_base.py  # pytest suite for KnowledgeBase AI logic
├── requirements.txt
└── README.md
```

`cluedo_game.py` contains the foundational game engine — board setup, player movement, dice rolling, suggestions, refutations, and turn management.

`cluedo_game_part2.py` is the complete game with the AI agent. It introduces an OOP design (`Player`, `KnowledgeBase`) and supports a mix of human and AI players in the same session.

---

## Architecture

```
Game Initialization
        │
        ▼
┌──────────────────────────────────────────────────────┐
│                  Mansion (3×3 Grid)                   │
│  Study(0,0)    Hall(0,1)    Lounge(0,2)              │
│  Library(1,0)  Billiard(1,1)  Dining(1,2)            │
│  Conservatory(2,0)  Ballroom(2,1)  Kitchen(2,2)      │
│                                                      │
│  Secret passages: Study ↔ Kitchen, Cons ↔ Lounge     │
└──────────────────────────────────────────────────────┘
        │
        ▼
Solution sealed (1 character + 1 weapon + 1 room)
        │
        ▼
Card distribution (remaining 18 cards to 3–6 players)
        │
        ▼
┌──────────────────────────────────────────────────────┐
│                Turn loop (3–6 players)                │
│                                                      │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐       │
│  │  Human    │   │  AI Agent │   │  AI Agent │       │
│  └───────────┘   └───────────┘   └───────────┘       │
│                        │                             │
│               ┌────────▼────────┐                    │
│               │  KnowledgeBase  │                    │
│               │  own_cards      │                    │
│               │  possible_soln  │                    │
│               │  player_has     │                    │
│               │  player_not_has │                    │
│               └─────────────────┘                    │
└──────────────────────────────────────────────────────┘
        │
        ▼
Game end (correct accusation wins; incorrect eliminates)
```

---

## Features

### Core Game Mechanics

| Component | Details |
|-----------|---------|
| Rooms | 9 rooms on a 3×3 grid |
| Characters | Miss Scarlett, Colonel Mustard, Mrs. White, Reverend Green, Mrs. Peacock, Professor Plum |
| Weapons | Candlestick, Dagger, Lead Pipe, Revolver, Rope, Wrench |
| Secret passages | Study ↔ Kitchen, Conservatory ↔ Lounge |
| Players | 3–6 (any mix of human and AI) |
| Solution | 1 character + 1 weapon + 1 room, sealed at game start |
| Cards | 18 remaining cards distributed to players |

### AI `KnowledgeBase` Class

```python
class KnowledgeBase:
    own_cards: set          # Cards the AI holds
    possible_solution: dict # Remaining candidates per category
    player_has: dict        # Cards confirmed held by specific players
    player_not_has: dict    # Cards confirmed NOT held by specific players
    shown_cards: set        # All cards revealed so far
```

### AI Inference Methods

| Method | Purpose |
|--------|---------|
| `mark_own_card(card)` | Adds to `own_cards`; eliminates from `possible_solution` |
| `eliminate_from_solution(card)` | Removes card from the correct category set |
| `record_refutation(player, suggestion, card)` | Records a specific shown card |
| `record_no_refutation(player, suggestion)` | Marks all 3 suggested cards as not held by that player |
| `record_someone_refuted(player, suggestion)` | Deduces the shown card when only one candidate remains |
| `get_solution_guess()` | Returns solution only when exactly 1 possibility per category |

---

## Key Challenge — Deduction Under Uncertainty

The hard part of the AI is not tracking known cards, but **inferring unknown ones**.

When Player 2 refutes a suggestion but the AI can't see which card was shown, `record_someone_refuted` checks whether two of the three suggested cards are already ruled out (either in the AI's own hand or in `player_not_has`). If only one remains possible, that must be what was shown — and it's eliminated from the solution.

**Example:**
- AI owns: `Colonel Mustard`, `Rope`
- Player 2 refutes: `(Colonel Mustard, Rope, Kitchen)`
- Since the AI holds two of the three, Player 2 **must** have `Kitchen`
- `Kitchen` is deduced and removed from `possible_solution['rooms']`

---

## AI Decision Flow

```
Start of AI turn
        │
        ▼
   Can accuse with 100% certainty?
   (1 possibility in each category)
        │
   Yes ─┤─ No
        │         │
   Accuse     Move toward unknown room
        │         │
   Win / elim     Enter room → make suggestion
                  using unknown chars/weapons
```

---

## Requirements

- Python 3.6+
- No external dependencies for gameplay (standard library only)
- `pytest>=7.0` for running tests

## Installation

```bash
git clone https://github.com/prabhathv07/Cluedo-AI-Logical-Deduction-Agent.git
cd Cluedo-AI-Logical-Deduction-Agent
```

## How to Run

```bash
# Core engine:
python cluedo_game.py

# Full game with AI agent:
python cluedo_game_part2.py

# Tests:
pytest tests/ -v
```

## Game Setup

1. Enter number of players (3–6)
2. Select how many should be AI and which positions
3. Cards are distributed; the murder solution is sealed
4. Game begins with Player 1

## Movement Commands

| Command | Action |
|---------|--------|
| `UP <n>` | Move up n spaces |
| `DOWN <n>` | Move down n spaces |
| `LEFT <n>` | Move left n spaces |
| `RIGHT <n>` | Move right n spaces |
| `STOP` | End movement early |

Entering a room triggers an automatic suggestion. Other players refute clockwise by showing one matching card privately.

---

## Board Layout

```
Study (0,0)          Hall (0,1)          Lounge (0,2)
Library (1,0)        Billiard Room (1,1) Dining Room (1,2)
Conservatory (2,0)   Ballroom (2,1)      Kitchen (2,2)

Secret passages:  Study ↔ Kitchen  |  Conservatory ↔ Lounge
```

---

## Description

Cluedo AI is a fully playable, text-based implementation of the classic Cluedo (Clue) board game built in Python. The project has two layers:

The **core engine** (`cluedo_game.py`) handles all fundamental game mechanics — a 3×3 mansion grid, six characters, six weapons, nine rooms, secret passages, dice-based movement, suggestion/refutation rounds, and win/elimination conditions.

The **AI agent layer** (`cluedo_game_part2.py`) introduces a `KnowledgeBase` class that each AI player uses to reason about the hidden murder solution. The agent tracks every card it holds, every card shown during refutations, and every player who failed to refute a suggestion. It applies process-of-elimination inference: when all but one candidate for a card are ruled out, the AI deduces the remaining card without being told. The agent only makes an accusation when it has narrowed every category (character, weapon, room) to exactly one possibility — mimicking how a human detective reasons under uncertainty.

The project demonstrates knowledge-based AI, OOP design, and logical inference implemented entirely without external libraries.

---

## Tools & Technologies

| Category | Tool / Technology |
|----------|-------------------|
| **Language** | Python 3.6+ |
| **Paradigm** | Object-Oriented Programming (OOP) |
| **AI technique** | Knowledge-Based Reasoning, Logical Inference, Process of Elimination |
| **Standard library** | `random` — dice rolls, card shuffling, weapon placement |
| **Testing** | `pytest` — 11 unit tests for `KnowledgeBase` logic |
| **Version control** | Git, GitHub |
| **Development environment** | CLI / Terminal |
| **No external dependencies** | Runs on any Python 3.6+ installation out of the box |

---

## What I'd Do Next

- **GUI** — Visual board using Pygame or Tkinter with clickable rooms and card display
- **Stronger AI** — Bayesian inference or MCTS to handle deeper uncertainty
- **Difficulty levels** — Easy (random), Medium (own cards only), Hard (full KB)
- **Network multiplayer** — Socket support for online play
- **Save / load** — Serialize game state to JSON
- **CI pipeline** — GitHub Actions to run pytest on every push

---

## License

[MIT License](LICENSE) — Cluedo/Clue game concept by Hasbro.
