
# Rock–Paper–Scissors–Plus AI Referee (Google ADK)

## Overview
This project implements a minimal AI referee chatbot for Rock–Paper–Scissors–Plus,
built strictly according to the upliance.ai assignment requirements.

## State Model
Game state is stored in-memory and mutated only via ADK tools.
It includes:
- Current round (1–3)
- User score and bot score
- Bomb usage flags (user & bot)
- Round history (moves and winner)

## Agent & Tool Design
The solution uses a single ADK Agent with explicit tools:
- validate_move: intent understanding and rule validation
- resolve_round: pure game logic
- update_game_state: persistent state mutation

State does not live in the prompt and persists across turns.

## Game Flow
- Rules explained in ≤5 lines
- User prompted each round
- Invalid input wastes the round
- Bomb usable once per player
- Game ends automatically after 3 rounds
- Clear round-by-round feedback and final result

## Tradeoffs
- Simple random bot strategy
- CLI-based conversational loop instead of UI

## Improvements With More Time
- Smarter bot strategy
- Structured JSON-only responses
- Separate player and referee agents
- Automated unit tests

## How to Run
```bash
python rps_plus_agent.py
```
