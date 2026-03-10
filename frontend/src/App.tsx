import { useState, useEffect } from 'react'
import { GameComponent } from './components/GameComponents'

interface Agent {
  id: string
  name: string
  description: string
  stats: {
    games_played: number
    games_won: number
    games_drawn: number
    elo: number
    win_rate: number
  }
}

interface GameType {
  type: string
  name: string
  players: number
}

interface Game {
  id: number
  game_type: string
  player1: Agent
  player2: Agent | null
  state: string
  status: string
  current_turn: number
}

const API = window.location.hostname === 'localhost' 
  ? '/api' 
  : 'http://5.61.91.8:5000/api'

function App() {
  const [view, setView] = useState<'agents' | 'games' | 'leaderboard'>('agents')
  const [agents, setAgents] = useState<Agent[]>([])
  const [gameTypes, setGameTypes] = useState<GameType[]>([])
  const [leaderboard, setLeaderboard] = useState<any[]>([])
  const [newAgentName, setNewAgentName] = useState('')
  const [selectedGame, setSelectedGame] = useState<string>('rps')
  const [activeGame, setActiveGame] = useState<Game | null>(null)

  useEffect(() => {
    fetchAgents()
    fetchGameTypes()
  }, [])

  const fetchAgents = async () => {
    const res = await fetch(`${API}/agents`)
    const data = await res.json()
    setAgents(data)
  }

  const fetchGameTypes = async () => {
    const res = await fetch(`${API}/games`)
    const data = await res.json()
    setGameTypes(data)
  }

  const fetchLeaderboard = async () => {
    const res = await fetch(`${API}/leaderboard`)
    const data = await res.json()
    setLeaderboard(data)
  }

  useEffect(() => {
    if (view === 'leaderboard') {
      fetchLeaderboard()
    }
  }, [view])

  // Poll for active game updates
  useEffect(() => {
    if (!activeGame) return
    
    const interval = setInterval(async () => {
      const res = await fetch(`${API}/games/${activeGame.id}`)
      if (res.ok) {
        const game = await res.json()
        setActiveGame(game)
      }
    }, 2000)
    
    return () => clearInterval(interval)
  }, [activeGame?.id])

  const createAgent = async () => {
    if (!newAgentName.trim()) return
    await fetch(`${API}/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newAgentName })
    })
    setNewAgentName('')
    fetchAgents()
  }

  const deleteAgent = async (id: string) => {
    await fetch(`${API}/agents/${id}`, { method: 'DELETE' })
    fetchAgents()
  }

  const startMatch = async () => {
    const p1 = (document.getElementById('p1') as HTMLSelectElement).value
    const p2 = (document.getElementById('p2') as HTMLSelectElement).value
    
    const res = await fetch(`${API}/games/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player1_id: p1, player2_id: p2, game_type: selectedGame })
    })
    
    if (res.ok) {
      const game = await res.json()
      setActiveGame(game)
      setView('games')
    }
  }

  const makeMove = async (move: any) => {
    if (!activeGame) return
    
    const currentAgentId = activeGame.current_turn === 1 ? activeGame.player1?.id : activeGame.player2?.id
    if (!currentAgentId) return
    
    const res = await fetch(`${API}/games/${activeGame.id}/play`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: currentAgentId, move })
    })
    
    if (res.ok) {
      const game = await res.json()
      setActiveGame(game)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">🎮 Agent Games Arena</h1>
        
        {/* Navigation */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => { setView('agents'); setActiveGame(null); }}
            className={`px-4 py-2 rounded ${view === 'agents' ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Agents
          </button>
          <button
            onClick={() => setView('games')}
            className={`px-4 py-2 rounded ${view === 'games' ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Games
          </button>
          <button
            onClick={() => setView('leaderboard')}
            className={`px-4 py-2 rounded ${view === 'leaderboard' ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Leaderboard
          </button>
        </div>

        {/* Active Game View */}
        {activeGame && activeGame.status === 'playing' && (
          <div className="bg-gray-800 p-6 rounded-lg mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">
                {gameTypes.find(g => g.type === activeGame.game_type)?.name}
              </h2>
              <button
                onClick={() => setActiveGame(null)}
                className="px-4 py-2 bg-red-600 rounded"
              >
                Exit Game
              </button>
            </div>
            
            {/* Players */}
            <div className="flex justify-around mb-6">
              <div className={`text-center p-4 rounded ${activeGame.current_turn === 1 ? 'bg-blue-900' : 'bg-gray-700'}`}>
                <p className="text-sm text-gray-400">Player 1</p>
                <p className="text-xl font-bold">{activeGame.player1?.name}</p>
              </div>
              <div className="text-center">
                <p className="text-2xl">VS</p>
              </div>
              <div className={`text-center p-4 rounded ${activeGame.current_turn === 2 ? 'bg-blue-900' : 'bg-gray-700'}`}>
                <p className="text-sm text-gray-400">Player 2</p>
                <p className="text-xl font-bold">{activeGame.player2?.name}</p>
              </div>
            </div>
            
            {/* Game Board */}
            <GameComponent 
              gameType={activeGame.game_type}
              gameState={activeGame.state}
              onMove={makeMove}
              currentPlayer={activeGame.current_turn}
            />
            
            {/* Game Over */}
            {activeGame.status === 'finished' && (
              <div className="text-center mt-6 p-4 bg-yellow-900 rounded">
                <p className="text-2xl font-bold">
                  {activeGame.is_draw ? "It's a Draw!" : 
                    `Winner: ${activeGame.winner?.name || (activeGame.winner_id === activeGame.player1?.id ? activeGame.player1?.name : activeGame.player2?.name)}`}
                </p>
                <button
                  onClick={() => setActiveGame(null)}
                  className="mt-4 px-6 py-2 bg-green-600 rounded"
                >
                  Back to Menu
                </button>
              </div>
            )}
          </div>
        )}

        {/* Agents View */}
        {view === 'agents' && !activeGame && (
          <div>
            <div className="flex gap-2 mb-6">
              <input
                type="text"
                value={newAgentName}
                onChange={(e) => setNewAgentName(e.target.value)}
                placeholder="Agent name..."
                className="flex-1 px-4 py-2 rounded bg-gray-800 border border-gray-700"
              />
              <button
                onClick={createAgent}
                className="px-6 py-2 bg-green-600 rounded hover:bg-green-700"
              >
                Add Agent
              </button>
            </div>

            <div className="grid gap-4">
              {agents.map((agent) => (
                <div key={agent.id} className="bg-gray-800 p-4 rounded-lg flex justify-between items-center">
                  <div>
                    <h3 className="text-xl font-bold">{agent.name}</h3>
                    <p className="text-gray-400 text-sm">{agent.description || 'No description'}</p>
                    <div className="flex gap-4 mt-2 text-sm">
                      <span>🎮 {agent.stats.games_played} games</span>
                      <span>🏆 {agent.stats.games_won} wins</span>
                      <span>📊 ELO: {agent.stats.elo}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteAgent(agent.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    Delete
                  </button>
                </div>
              ))}
              {agents.length === 0 && (
                <p className="text-center text-gray-500">No agents yet. Add one to get started!</p>
              )}
            </div>
          </div>
        )}

        {/* Games View */}
        {view === 'games' && !activeGame && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Available Games</h2>
            <div className="grid gap-4 mb-8">
              {gameTypes.map((game) => (
                <div 
                  key={game.type} 
                  className={`bg-gray-800 p-4 rounded-lg cursor-pointer ${selectedGame === game.type ? 'ring-2 ring-blue-500' : ''}`}
                  onClick={() => setSelectedGame(game.type)}
                >
                  <h3 className="text-xl font-bold">{game.name}</h3>
                  <p className="text-gray-400">{game.players} players</p>
                </div>
              ))}
            </div>

            <h2 className="text-2xl font-bold mb-4">Start Match</h2>
            <div className="flex gap-4 items-center flex-wrap">
              <select
                value={selectedGame}
                onChange={(e) => setSelectedGame(e.target.value)}
                className="px-4 py-2 rounded bg-gray-800 border border-gray-700"
              >
                {gameTypes.map((g) => (
                  <option key={g.type} value={g.type}>{g.name}</option>
                ))}
              </select>
              <span className="text-gray-400">VS</span>
              <select id="p1" className="px-4 py-2 rounded bg-gray-800 border border-gray-700">
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
              <span className="text-gray-400">VS</span>
              <select id="p2" className="px-4 py-2 rounded bg-gray-800 border border-gray-700">
                {agents.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
              <button
                onClick={startMatch}
                disabled={agents.length < 2}
                className="px-6 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Start Match
              </button>
            </div>
          </div>
        )}

        {/* Leaderboard View */}
        {view === 'leaderboard' && !activeGame && (
          <div>
            <h2 className="text-2xl font-bold mb-4">🏆 Leaderboard</h2>
            <div className="space-y-2">
              {leaderboard.map((entry) => (
                <div key={entry.agent.id} className="bg-gray-800 p-4 rounded-lg flex items-center gap-4">
                  <span className="text-2xl font-bold w-12">
                    {entry.rank <= 3 ? ['🥇', '🥈', '🥉'][entry.rank - 1] : `#${entry.rank}`}
                  </span>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold">{entry.agent.name}</h3>
                    <p className="text-gray-400 text-sm">
                      {entry.agent.stats.games_won}W / {entry.agent.stats.games_drawn}D / 
                      {entry.agent.stats.games_played - entry.agent.stats.games_won - entry.agent.stats.games_drawn}L
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-yellow-400">{entry.agent.stats.elo}</p>
                    <p className="text-gray-400 text-sm">ELO</p>
                  </div>
                </div>
              ))}
              {leaderboard.length === 0 && (
                <p className="text-center text-gray-500">No games played yet!</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
