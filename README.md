# Cluedo AI — Logical Deduction Agent

A Python implementation of the classic **Cluedo (Clue)** murder mystery board game, featuring an intelligent AI player that uses logical deduction and knowledge-based reasoning to solve the mystery.

## Project Structure

```
├── cluedo_game.py         # Core game engine (basic mechanics)
├── cluedo_game_part2.py   # Full game with AI logical deduction agent
├── requirements.txt
└── README.md
```

`cluedo_game.py` contains the foundational game engine — board setup, player movement, dice rolling, suggestions, refutations, and win conditions.

`cluedo_game_part2.py` is the complete game with the AI agent. It extends the engine with a `KnowledgeBase` and deduction logic, supporting a mix of human and AI players in the same session.

## Features

### Core Game Mechanics
- 3×3 mansion board with 9 rooms — Study, Hall, Lounge, Library, Billiard Room, Dining Room, Conservatory, Ballroom, Kitchen
- 6 characters: Miss Scarlett, Colonel Mustard, Mrs. White, Reverend Green, Mrs. Peacock, Professor Plum
- 6 weapons: Candlestick, Dagger, Lead Pipe, Revolver, Rope, Wrench
- Secret passages: Study ↔ Kitchen, Conservatory ↔ Lounge
- Dice-based movement, turn order, suggestion/refutation system, and accusation rules
- 3–6 players supported (any mix of human and AI)

### AI Logical Deduction Agent
The AI maintains a `KnowledgeBase` per player that:
- Tracks its own cards and immediately eliminates them from the solution space
- Records cards revealed during refutations
- Infers cards when only one candidate remains after a failed refutation
- Records which players cannot hold certain cards (no-refutation events)
- Makes an accusation only when all three solution components are pinned to a single possibility
- Chooses movement toward rooms still in the solution set

## Requirements

- Python 3.6+
- No external dependencies (standard library only)

## Installation

```bash
git clone https://github.com/prabhathv07/Cluedo-AI-Logical-Deduction-Agent.git
cd Cluedo-AI-Logical-Deduction-Agent
```

## How to Run

**Core engine only:**
```bash
python cluedo_game.py
```

**Full game with AI agent:**
```bash
python cluedo_game_part2.py
```

## Gameplay

1. Enter number of players (3–6)
2. Select how many should be AI players and which positions
3. Cards are distributed; the murder solution is sealed
4. Game begins with Player 1

**On your turn:**
- Optionally view the game log or make an accusation
- Use a secret passage if available
- Roll the die (Enter), then move with directional commands
- Entering a room triggers an automatic suggestion

**Movement commands:** `UP <n>`, `DOWN <n>`, `LEFT <n>`, `RIGHT <n>`, `STOP`

**Suggestions:** Choose a character + weapon. Other players refute clockwise by showing one matching card privately.

**Accusations:** Name character, weapon, and room. Correct = you win. Incorrect = eliminated from winning (but you can still refute others' suggestions).

## Board Layout

```
Study (0,0)          Hall (0,1)          Lounge (0,2)
Library (1,0)        Billiard Room (1,1) Dining Room (1,2)
Conservatory (2,0)   Ballroom (2,1)      Kitchen (2,2)

Secret passages:  Study <-> Kitchen  |  Conservatory <-> Lounge
```

## License

Educational project. Cluedo/Clue game concept by Hasbro.
