# AI Agent Service
# LLM-powered agents with memory and learning

import os
import json
import requests
from typing import Optional

class LLMProvider:
    """OpenRouter LLM Integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY', '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')  # 'free' for free tier
        self.base_url = "https://openrouter.ai/api/v1"
    
    def chat(self, prompt: str, model: str = "openrouter/free") -> str:
        """Send prompt to LLM and get response"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agent-games-arena.dev",
            "X-Title": "Agent Games Arena"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"


# Game-specific prompts
GAME_PROMPTS = {
    "rps": """You are playing Rock Paper Scissors.
Current game state: {state}

Your options: rock, paper, scissors

Reply with exactly ONE word: rock, paper, or scissors""",
    
    "tictactoe": """You are playing Tic-Tac-Toe.
You are {player} (symbol: {symbol})

Current board:
{board}

Your move position (0-8, top-left is 0, top-middle is 1, etc.):
0 | 1 | 2
--+---+--
3 | 4 | 5
--+---+--
6 | 7 | 8

Reply with just the number (0-8) of your move.""",
    
    "connect4": """You are playing Connect Four.
You are {player} (symbol: {symbol})

Current board (0 is empty, X is player 1, O is player 2):
{board}

Columns are 0-6 (left to right).

Reply with just the column number (0-6) of your move.""",
    
    "numberguess": """You are playing Number Guessing.
The secret number is between 1-100.

Previous guesses: {guesses}
Your goal is to guess closest to the secret number.

Reply with a single number between 1-100.""",
    
    "mastermind": """You are playing Mastermind (code breaking).
You need to guess a 4-color code.

Available colors: 🔴 🟡 🟢 🔵 🟣 🟤

Previous guesses and feedback:
{history}

Feedback: exact = correct color & position, color = correct color wrong position

Reply with 4 colors separated by spaces (e.g., 🔴 🟡 🟢 🔵)""",
    
    "default": """You are playing a game.
Game type: {game_type}
Current state: {state}

What is your best move? Reply with your move."""
}


class AIAgent:
    """AI Agent that uses LLM to play games"""
    
    def __init__(self, name: str, api_key: str = None):
        self.name = name
        self.llm = LLMProvider(api_key)
        self.memory = []  # Store game experiences
    
    def get_prompt(self, game_type: str, state: dict) -> str:
        """Build game-specific prompt"""
        
        prompt_template = GAME_PROMPTS.get(game_type, GAME_PROMPTS["default"])
        
        # Format state for each game
        if game_type == "tictactoe":
            board = state.get("board", [None] * 9)
            board_display = ""
            for i in range(3):
                row = []
                for j in range(3):
                    cell = board[i * 3 + j]
                    row.append(cell or ".")
                board_display += " | ".join(row) + "\n"
            
            player = state.get("current_player", "X")
            symbol = "X" if player == 1 else "O"
            
            return prompt_template.format(
                player=player,
                symbol=symbol,
                board=board_display
            )
        
        elif game_type == "rps":
            return prompt_template.format(state=json.dumps(state))
        
        elif game_type == "connect4":
            board = state.get("board", [])
            board_str = "\n".join([" ".join(row) for row in board])
            
            player = state.get("current_player", 1)
            symbol = "X" if player == 1 else "O"
            
            return prompt_template.format(
                player=player,
                symbol=symbol,
                board=board_str
            )
        
        else:
            return prompt_template.format(
                game_type=game_type,
                state=json.dumps(state)
            )
    
    def decide_move(self, game_type: str, state: dict) -> str:
        """Get LLM to decide move"""
        
        prompt = self.get_prompt(game_type, state)
        
        response = self.llm.chat(prompt)
        
        # Store in memory
        self.memory.append({
            "game_type": game_type,
            "state": state,
            "llm_response": response
        })
        
        return response.strip()
    
    def learn_from_result(self, result: str):
        """Update memory with game result"""
        if self.memory:
            self.memory[-1]["result"] = result
    
    def get_best_strategies(self) -> list:
        """Get strategies that led to wins"""
        return [m for m in self.memory if m.get("result") == "win"]


# Default agent (uses free OpenRouter)
default_agent = AIAgent("AI Agent")
