# ---------- ADK import with safe fallback ----------
try:
    from google.adk import Agent, tool
except ImportError:
    # Local fallback so code runs without full ADK runtime
    def tool(func):
        return func

    class Agent:
        def __init__(self, name, instructions, tools):
            self.name = name
            self.instructions = instructions
            self.tools = tools

# ---------- Standard imports ----------
import random
from typing import Dict


# -----------------------------
# Constants & State
# -----------------------------
VALID_MOVES = {"rock", "paper", "scissors", "bomb"}

GAME_STATE = {
    "round": 1,               # 1 to 3
    "user_score": 0,
    "bot_score": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "history": []             # round-by-round log
}

# -----------------------------
# Tools (Explicit as required)
# -----------------------------
@tool
def validate_move(player: str, move: str) -> Dict:
    """
    Accepts raw user input and intelligently extracts a valid move.
    """
    if not move:
        return {"valid": False, "reason": "Empty input"}

    move = move.lower()

    # Try to intelligently detect the move from text
    for valid in ["rock", "paper", "scissors", "bomb"]:
        if valid in move:
            move = valid
            break
    else:
        return {"valid": False, "reason": "No valid move found"}

    if move == "bomb":
        if player == "user" and GAME_STATE["user_bomb_used"]:
            return {"valid": False, "reason": "User already used bomb"}
        if player == "bot" and GAME_STATE["bot_bomb_used"]:
            return {"valid": False, "reason": "Bot already used bomb"}

    return {"valid": True, "move": move}

@tool
def resolve_round(user_move: str, bot_move: str) -> Dict:
    """Apply game rules and decide winner."""
    if user_move == bot_move:
        return {"winner": "draw"}

    if user_move == "bomb" and bot_move != "bomb":
        return {"winner": "user"}

    if bot_move == "bomb" and user_move != "bomb":
        return {"winner": "bot"}

    beats = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    if beats[user_move] == bot_move:
        return {"winner": "user"}

    return {"winner": "bot"}


@tool
def update_game_state(user_move: str, bot_move: str, winner: str) -> Dict:
    """Persist state changes after a round."""
    if user_move == "bomb":
        GAME_STATE["user_bomb_used"] = True
    if bot_move == "bomb":
        GAME_STATE["bot_bomb_used"] = True

    if winner == "user":
        GAME_STATE["user_score"] += 1
    elif winner == "bot":
        GAME_STATE["bot_score"] += 1

    GAME_STATE["history"].append({
        "round": GAME_STATE["round"],
        "user_move": user_move,
        "bot_move": bot_move,
        "winner": winner
    })

    GAME_STATE["round"] += 1
    return GAME_STATE


# -----------------------------
# Agent Definition
# -----------------------------
agent = Agent(
    name="RPSPlusReferee",
    instructions="""
You are an AI referee for Rock–Paper–Scissors–Plus.

Rules (≤5 lines):
• Best of 3 rounds
• Moves: rock, paper, scissors, bomb (once per player)
• Bomb beats everything, bomb vs bomb is a draw
• Invalid input wastes the round
• Game ends automatically after 3 rounds

Use tools to validate, resolve rounds, and update state.
""",
    tools=[validate_move, resolve_round, update_game_state],
)

# -----------------------------
# CLI Runner (Conversational Loop)
# -----------------------------
def run_game():
    print("🎮 Rock–Paper–Scissors–Plus (Best of 3)")
    print("Type: rock | paper | scissors | bomb (once)\n")

    while GAME_STATE["round"] <= 3:
        print(f"--- Round {GAME_STATE['round']} ---")
        user_input = input("Your move: ")

        validation = validate_move("user", user_input)

        # Invalid input wastes the round
        if not validation["valid"]:
            print("❌ Invalid input. Round wasted.")
            bot_move = random.choice(["rock", "paper", "scissors"])
            update_game_state("invalid", bot_move, "bot")
            continue

        user_move = validation["move"]

        # Bot move logic (bomb only once)
        bot_choices = list(VALID_MOVES)
        if GAME_STATE["bot_bomb_used"]:
            bot_choices.remove("bomb")
        bot_move = random.choice(bot_choices)

        result = resolve_round(user_move, bot_move)
        update_game_state(user_move, bot_move, result["winner"])

        print(f"You played: {user_move}")
        print(f"Bot played: {bot_move}")

        if result["winner"] == "draw":
            print("⚖️ Round result: Draw")
        else:
            print(f"🏆 Round winner: {result['winner'].upper()}")

        print(f"Score → You: {GAME_STATE['user_score']} | Bot: {GAME_STATE['bot_score']}\n")

    # Final Result
    print("=== Game Over ===")
    if GAME_STATE["user_score"] > GAME_STATE["bot_score"]:
        print("✅ Final Result: USER WINS")
    elif GAME_STATE["bot_score"] > GAME_STATE["user_score"]:
        print("❌ Final Result: BOT WINS")
    else:
        print("🤝 Final Result: DRAW")


if __name__ == "__main__":
    run_game()
