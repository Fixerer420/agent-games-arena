// Game Components
// RockPaperScissors, TicTacToe, ConnectFour, NumberGuessing, Memory

import { useState, useEffect } from 'react'

// ============ ROCK PAPER SCISSORS ============

export function RockPaperScissorsGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (move: string) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  
  const moves = ['rock', 'paper', 'scissors']
  
  return (
    <div className="text-center">
      <div className="text-2xl mb-4">
        Round: {state.round} | Current Turn: Player {currentPlayer}
      </div>
      
      {/* Show last round results */}
      {state.round > 1 && (
        <div className="mb-4 p-4 bg-gray-800 rounded">
          <p>Last Round:</p>
          <p>Player 1: {state.player1_move} | Player 2: {state.player2_move}</p>
          {state.round_winner && (
            <p className="text-yellow-400">
              Winner: Player {state.round_winner} {state.is_draw && '(Draw)'}
            </p>
          )}
        </div>
      )}
      
      {/* Move buttons */}
      <div className="flex justify-center gap-4">
        {moves.map(move => (
          <button
            key={move}
            onClick={() => onMove(move)}
            disabled={state.game_over}
            className="px-6 py-3 bg-blue-600 rounded-lg text-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {move === 'rock' ? '🪨' : move === 'paper' ? '📄' : '✂️'} {move}
          </button>
        ))}
      </div>
    </div>
  )
}

// ============ TIC TAC TOE ============

export function TicTacToeGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (pos: number) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const board = state.board || []
  const currentSymbol = state.current_player || 'X'
  
  const getSymbol = (cell: string | null) => {
    if (cell === 'X') return '❌'
    if (cell === 'O') return '⭕'
    return ''
  }
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Current Player: {currentSymbol === 'X' ? '❌' : '⭕'} ({currentSymbol})
      </div>
      
      {/* Board */}
      <div className="grid grid-cols-3 gap-2 max-w-xs mx-auto mb-4">
        {board.map((cell: string | null, i: number) => (
          <button
            key={i}
            onClick={() => onMove(i)}
            disabled={cell !== null || state.game_over}
            className="w-20 h-20 bg-gray-700 rounded text-4xl flex items-center justify-center hover:bg-gray-600 disabled:cursor-not-allowed"
          >
            {getSymbol(cell)}
          </button>
        ))}
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400">
          {state.winner === 'draw' ? "It's a Draw!" : `${state.winner === 'X' ? '❌' : '⭕'} Wins!`}
        </div>
      )}
    </div>
  )
}

// ============ CONNECT FOUR ============

export function ConnectFourGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (col: number) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const board = state.board || []
  const currentSymbol = state.current_player || 'X'
  
  const getSymbol = (cell: string | null) => {
    if (cell === 'X') return '🔴'
    if (cell === 'O') return '🟡'
    return ''
  }
  
  // Rotate for display (show row 0 at top)
  const displayBoard = [...board].reverse()
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Current Player: {currentSymbol === 'X' ? '🔴' : '🟡'} ({currentSymbol})
      </div>
      
      {/* Column buttons */}
      <div className="flex justify-center gap-1 mb-2">
        {Array(7).fill(0).map((_, col) => (
          <button
            key={col}
            onClick={() => onMove(col)}
            disabled={state.game_over || board[0][col] !== null}
            className="w-12 h-8 bg-gray-600 rounded hover:bg-gray-500 disabled:opacity-50"
          >
            ⬇️
          </button>
        ))}
      </div>
      
      {/* Board */}
      <div className="inline-grid grid-cols-7 gap-1 p-2 bg-blue-800 rounded">
        {displayBoard.map((row: string[], rowIdx: number) => 
          row.map((cell: string | null, colIdx: number) => (
            <div
              key={`${rowIdx}-${colIdx}`}
              className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-2xl"
            >
              {getSymbol(cell)}
            </div>
          ))
        )}
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400 mt-4">
          {state.winner === 'draw' ? "It's a Draw!" : `${state.winner === 'X' ? '🔴' : '🟡'} Wins!`}
        </div>
      )}
    </div>
  )
}

// ============ NUMBER GUESSING ============

export function NumberGuessingGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (guess: number) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const [guess, setGuess] = useState(50)
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Round: {state.round}/5 | Current Turn: Player {currentPlayer}
      </div>
      
      {/* Score */}
      <div className="flex justify-center gap-8 mb-4">
        <div className="text-2xl">Player 1: {state.score_p1}</div>
        <div className="text-2xl">Player 2: {state.score_p2}</div>
      </div>
      
      {/* Guess input */}
      {!state.game_over && (
        <div className="mb-4">
          <input
            type="range"
            min="1"
            max="100"
            value={guess}
            onChange={(e) => setGuess(parseInt(e.target.value))}
            className="w-64"
          />
          <p className="text-3xl font-bold">{guess}</p>
          <button
            onClick={() => onMove(guess)}
            className="mt-2 px-6 py-2 bg-green-600 rounded hover:bg-green-700"
          >
            Guess!
          </button>
        </div>
      )}
      
      {/* Guesses history */}
      <div className="grid grid-cols-2 gap-4 max-w-md mx-auto text-left">
        <div className="bg-gray-800 p-2 rounded">
          <h4 className="font-bold mb-1">Player 1 Guesses:</h4>
          {state.guesses_p1?.map((g: number, i: number) => (
            <span key={i} className="mr-2">{g}({state.results_p1?.[i]?.[0]})</span>
          ))}
        </div>
        <div className="bg-gray-800 p-2 rounded">
          <h4 className="font-bold mb-1">Player 2 Guesses:</h4>
          {state.guesses_p2?.map((g: number, i: number) => (
            <span key={i} className="mr-2">{g}({state.results_p2?.[i]?.[0]})</span>
          ))}
        </div>
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400 mt-4">
          {state.is_draw ? "It's a Draw!" : `Player ${state.winner} Wins!`}
        </div>
      )}
    </div>
  )
}

// ============ MEMORY GAME ============

export function MemoryGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (index: number) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const cards = state.cards || []
  const flipped = state.flipped || []
  const matched = state.matched || []
  
  // Determine which cards to show
  const getCardContent = (index: number) => {
    if (matched.includes(index)) return cards[index]
    if (flipped.includes(index)) return cards[index]
    return '❓'
  }
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Score - P1: {state.score_p1} | P2: {state.score_p2} | Turn: Player {currentPlayer}
      </div>
      
      {/* Cards grid */}
      <div className="grid grid-cols-4 gap-2 max-w-sm mx-auto mb-4">
        {cards.map((_: string, i: number) => (
          <button
            key={i}
            onClick={() => onMove(i)}
            disabled={flipped.includes(i) || matched.includes(i) || state.game_over}
            className="w-16 h-16 bg-gray-700 rounded text-2xl hover:bg-gray-600 disabled:opacity-50"
          >
            {getCardContent(i)}
          </button>
        ))}
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400">
          {state.is_draw ? "It's a Draw!" : `Player ${state.winner} Wins!`}
        </div>
      )}
    </div>
  )
}

// ============ GAME COMPONENT SELECTOR ============

// Add before the GameComponent selector:

// ============ BATTLESHIP ============

export function BattleshipGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (move: {row: number, col: number}) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const [targetRow, setTargetRow] = useState(0)
  const [targetCol, setTargetCol] = useState(0)
  
  // Get opponent's board for viewing
  const myBoard = currentPlayer === 1 ? state.p1_board : state.p2_board
  const myHits = currentPlayer === 1 ? state.p1_hits : state.p2_hits
  const enemyBoard = currentPlayer === 1 ? state.p2_board : state.p1_board
  const enemyHits = currentPlayer === 1 ? state.p2_hits : state.p1_hits
  
  const getCellContent = (isMyBoard: boolean, row: number, col: number) => {
    const board = isMyBoard ? myBoard : enemyBoard
    const hits = isMyBoard ? myHits : enemyHits
    
    if (hits[row][col]) {
      return board[row][col] === 'ship' ? '💥' : '💦'
    }
    if (isMyBoard && board[row][col] === 'ship') {
      return '🚢'
    }
    return ''
  }
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Current Turn: Player {currentPlayer}
      </div>
      
      <div className="flex justify-center gap-8">
        {/* My Board */}
        <div>
          <h4 className="mb-2">Your Fleet</h4>
          <div className="inline-grid grid-cols-10 gap-0.5 bg-gray-700 p-1 rounded">
            {myBoard.map((row: string[], r: number) => 
              row.map((cell: string, c: number) => (
                <div
                  key={`my-${r}-${c}`}
                  className="w-6 h-6 bg-blue-800 rounded flex items-center justify-center text-sm"
                >
                  {getCellContent(true, r, c)}
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Enemy Board */}
        <div>
          <h4 className="mb-2">Enemy Waters</h4>
          <div className="inline-grid grid-cols-10 gap-0.5 bg-gray-700 p-1 rounded">
            {enemyBoard.map((row: string[], r: number) => 
              row.map((cell: string, c: number) => (
                <button
                  key={`enemy-${r}-${c}`}
                  onClick={() => onMove({row: r, col: c})}
                  disabled={state.game_over || enemyHits[r][c]}
                  className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-sm hover:bg-blue-500 disabled:opacity-50"
                >
                  {getCellContent(false, r, c)}
                </button>
              ))
            )}
          </div>
        </div>
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400 mt-4">
          Player {state.winner} Wins!
        </div>
      )}
    </div>
  )
}

// ============ MASTERMIND ============

const COLORS = ['🔴', '🟡', '🟢', '🔵', '🟣', '🟤']

export function MastermindGame({ gameState, onMove, currentPlayer }: { 
  gameState: any, 
  onMove: (guess: string[]) => void,
  currentPlayer: number 
}) {
  const state = typeof gameState === 'string' ? JSON.parse(gameState) : gameState
  const [guess, setGuess] = useState<string[]>([COLORS[0], COLORS[0], COLORS[0], COLORS[0]])
  
  const guesses = currentPlayer === 1 ? state.guesses_p1 : state.guesses_p2
  const results = currentPlayer === 1 ? state.results_p1 : state.results_p2
  
  const toggleColor = (idx: number) => {
    const newGuess = [...guess]
    const currentIdx = COLORS.indexOf(newGuess[idx])
    newGuess[idx] = COLORS[(currentIdx + 1) % COLORS.length]
    setGuess(newGuess)
  }
  
  return (
    <div className="text-center">
      <div className="text-xl mb-4">
        Round: {state.round}/10 | Current Turn: Player {currentPlayer}
      </div>
      
      {/* Color picker */}
      <div className="mb-6">
        <p className="mb-2">Select your code:</p>
        <div className="flex justify-center gap-2 mb-4">
          {guess.map((color, idx) => (
            <button
              key={idx}
              onClick={() => toggleColor(idx)}
              className="w-12 h-12 text-2xl bg-gray-700 rounded hover:bg-gray-600"
            >
              {color}
            </button>
          ))}
        </div>
        <button
          onClick={() => onMove(guess)}
          disabled={state.game_over}
          className="px-6 py-2 bg-green-600 rounded hover:bg-green-700"
        >
          Submit Guess
        </button>
      </div>
      
      {/* Guess history */}
      <div className="max-w-md mx-auto">
        <h4 className="mb-2">Guess History:</h4>
        {guesses?.map((g: string[], i: number) => (
          <div key={i} className="flex justify-center gap-2 mb-2">
            <span className="text-xl">{g.join(' ')}</span>
            <span className="text-sm">
              🎯 {results[i]?.exact || 0} exact | 🎨 {results[i]?.color || 0} color
            </span>
          </div>
        ))}
      </div>
      
      {state.game_over && (
        <div className="text-xl text-yellow-400 mt-4">
          {state.winner ? `Player ${state.winner} Wins!` : 'Game Over - No Winner!'}
          <p className="text-sm">Secret code was: {state.secret_code?.join(' ')}</p>
        </div>
      )}
    </div>
  )
}

// ============ GAME COMPONENT SELECTOR ============

export function GameComponent({ gameType, gameState, onMove, currentPlayer }: {
  gameType: string
  gameState: any
  onMove: (move: any) => void
  currentPlayer: number
}) {
  switch (gameType) {
    case 'rps':
      return <RockPaperScissorsGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'tictactoe':
      return <TicTacToeGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'connect4':
      return <ConnectFourGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'numberguess':
      return <NumberGuessingGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'memory':
      return <MemoryGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'battleship':
      return <BattleshipGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    case 'mastermind':
      return <MastermindGame gameState={gameState} onMove={onMove} currentPlayer={currentPlayer} />
    default:
      return <div>Unknown game: {gameType}</div>
  }
}
