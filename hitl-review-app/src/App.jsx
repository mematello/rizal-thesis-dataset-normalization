import { useState, useEffect, useCallback } from 'react'

function App() {
  const [queue, setQueue] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [diffMode, setDiffMode] = useState(false)
  const [stats, setStats] = useState({
    xp: 0,
    streak: 0,
    reviewed: 0,
    spanishProtected: 0
  })

  useEffect(() => {
    fetch('http://localhost:8000/queue')
      .then(res => res.json())
      .then(data => {
        setQueue(data)
        setLoading(false)
      })
      .catch(err => console.error("Failed to load queue:", err))
  }, [])

  const currentSentence = queue[currentIndex]

  const [focusedSegmentIndex, setFocusedSegmentIndex] = useState(-1)

  useEffect(() => {
    if (currentSentence) {
      const idx = currentSentence.segments.findIndex(s => s.type === 'token' && s.data.status === 'candidate')
      setFocusedSegmentIndex(idx)
    }
  }, [currentIndex, currentSentence])

  const handleAction = useCallback((actionType, manualValue = null) => {
    if (!currentSentence || focusedSegmentIndex === -1) return

    const segment = currentSentence.segments[focusedSegmentIndex]
    const tokenData = segment.data

    let finalWord = tokenData.proposed
    let logAction = actionType

    if (actionType === 'REJECT') {
      finalWord = tokenData.original
    } else if (actionType === 'EDIT') {
      finalWord = manualValue || prompt("Edit word:", tokenData.proposed)
      if (finalWord === null) return
      logAction = 'EDIT'
    } else if (actionType === 'SKIP') {
      finalWord = tokenData.original
    }

    fetch('http://localhost:8000/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sentence_id: currentSentence.id,
        original_word: tokenData.original,
        proposed_word: tokenData.proposed,
        final_word: finalWord,
        action: logAction,
        rule: tokenData.rule,
        timestamp: new Date().toISOString()
      })
    })

    const newQueue = [...queue]
    const newSentence = { ...currentSentence }
    const newSegments = [...newSentence.segments]

    newSegments[focusedSegmentIndex] = {
      ...segment,
      data: {
        ...tokenData,
        proposed: finalWord,
        status: 'reviewed'
      }
    }

    newSentence.segments = newSegments
    newQueue[currentIndex] = newSentence
    setQueue(newQueue)

    setStats(prev => ({
      ...prev,
      xp: prev.xp + (actionType === 'APPROVE' ? 10 : 5),
      streak: prev.streak + 1,
      reviewed: prev.reviewed + 1
    }))

    const nextCandidateIdx = newSegments.findIndex((s, i) => i > focusedSegmentIndex && s.type === 'token' && s.data.status === 'candidate')

    if (nextCandidateIdx !== -1) {
      setFocusedSegmentIndex(nextCandidateIdx)
    } else {
      if (currentIndex % 10 === 0) {
        fetch('http://localhost:8000/save_queue', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ queue: newQueue })
        })
      }

      if (currentIndex < queue.length - 1) {
        setCurrentIndex(prev => prev + 1)
      } else {
        alert("Review Complete!")
      }
    }

  }, [queue, currentIndex, focusedSegmentIndex, currentSentence])

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

      if (e.key.toLowerCase() === 'a') handleAction('APPROVE')
      if (e.key.toLowerCase() === 'r') handleAction('REJECT')
      if (e.key.toLowerCase() === 's') handleAction('SKIP')
      if (e.key.toLowerCase() === 'e') handleAction('EDIT')
      if (e.key.toLowerCase() === 'd') setDiffMode(prev => !prev)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleAction])

  if (loading) return <div className="flex h-screen items-center justify-center bg-zinc-950 text-white font-mono">Loading data...</div>
  if (!currentSentence) return <div className="flex h-screen items-center justify-center bg-zinc-950 text-white font-mono">No sentences loaded.</div>

  const currentToken = currentSentence.segments[focusedSegmentIndex]?.data

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-yellow-500/30">

      {/* Navbar */}
      <div className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-8 w-8 bg-gradient-to-br from-yellow-500 to-amber-600 rounded-lg flex items-center justify-center font-bold text-black font-serif">N</div>
            <div>
              <h1 className="text-sm font-semibold tracking-wide text-zinc-100">El Filibusterismo</h1>
              <p className="text-xs text-zinc-500 font-mono">Normalization Review</p>
            </div>
          </div>

          <div className="flex items-center gap-8">
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold font-mono tracking-tight">{stats.xp}</span>
              <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">XP</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold font-mono tracking-tight text-amber-500">{stats.streak}</span>
              <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Streak</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-xl font-bold font-mono tracking-tight text-blue-400">{currentIndex + 1}<span className="text-zinc-600 text-sm"> / {queue.length}</span></span>
              <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Progress</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-8 mt-4">

        {/* Main Text Area */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 min-h-[400px] shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-zinc-700 to-transparent opacity-20"></div>

            <h2 className="text-xs font-mono text-zinc-500 mb-6 flex justify-between">
              <span>SENTENCE ID: <span className="text-zinc-300">{currentSentence.id}</span></span>
              <span>CHAPTER: <span className="text-zinc-300">{currentSentence.chapter}</span></span>
            </h2>

            <div className="text-xl leading-9 font-serif text-zinc-300">
              {currentSentence.segments.map((seg, idx) => {
                const isToken = seg.type === 'token';
                if (!isToken) return <span key={idx}>{seg}</span>

                const { original, proposed, status } = seg.data
                const isFocused = idx === focusedSegmentIndex

                let displayText = diffMode ? original : proposed

                // Styles
                let baseStyle = "px-1 rounded mx-0.5 transition-all duration-200 cursor-default inline-block"

                if (status === 'candidate') {
                  if (isFocused) {
                    return (
                      <span key={idx} className={`${baseStyle} bg-amber-500/20 text-amber-200 border-b-2 border-amber-500 font-medium transform scale-105 shadow-[0_0_15px_-3px_rgba(245,158,11,0.3)]`}>
                        {displayText}
                      </span>
                    )
                  }
                  return (
                    <span key={idx} className={`${baseStyle} bg-amber-900/10 text-amber-100/60 border-b border-amber-900/30 hover:bg-amber-900/20`}>
                      {displayText}
                    </span>
                  )
                }

                if (status === 'protected_quote') {
                  return <span key={idx} className={`${baseStyle} text-sky-300/80 bg-sky-900/10`}>{original}</span>
                }

                if (status === 'protected_lexicon') {
                  return <span key={idx} className={`${baseStyle} text-purple-300/80 bg-purple-900/10 border-b border-purple-900/20`}>{original}</span>
                }

                if (status === 'reviewed') {
                  return <span key={idx} className={`${baseStyle} text-emerald-300/80 bg-emerald-900/10`}>{displayText}</span>
                }

                return <span key={idx} className="text-zinc-300">{displayText}</span>
              })}
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setDiffMode(!diffMode)}
              className="text-xs font-mono text-zinc-500 hover:text-zinc-300 transition-colors flex items-center gap-2"
            >
              <span className={`w-2 h-2 rounded-full ${diffMode ? 'bg-amber-500' : 'bg-zinc-700'}`}></span>
              {diffMode ? "VIEWING ORIGINAL (Press D to toggle)" : "VIEWING PROPOSED (Press D to toggle)"}
            </button>
          </div>
        </div>

        {/* Sidebar / Controls */}
        <div className="lg:col-span-4 space-y-6">

          {currentToken ? (
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl sticky top-24">
              <div className="flex items-center gap-2 mb-6 text-amber-500">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                <h3 className="text-xs font-bold uppercase tracking-widest">Active Candidate</h3>
              </div>

              <div className="bg-zinc-950 rounded-xl p-6 border border-zinc-800/50 mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-8 h-8 rounded-full bg-red-900/20 text-red-500 flex items-center justify-center font-bold text-xs">OLD</div>
                  <div className="text-lg font-serif text-zinc-400 line-through decoration-red-500/30 decoration-2">{currentToken.original}</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-emerald-900/20 text-emerald-500 flex items-center justify-center font-bold text-xs">NEW</div>
                  <div className="text-2xl font-serif text-emerald-400 font-medium">{currentToken.proposed}</div>
                </div>
              </div>

              <div className="mb-8">
                <div className="text-[10px] uppercase text-zinc-500 font-bold tracking-wider mb-2">Applied Rule</div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-zinc-800 border border-zinc-700 text-xs font-mono text-zinc-300">
                  {currentToken.rule}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <ControlBtn label="Accept" sub="A" color="emerald" onClick={() => handleAction('APPROVE')} />
                <ControlBtn label="Reject" sub="R" color="red" onClick={() => handleAction('REJECT')} />
                <ControlBtn label="Edit" sub="E" color="blue" onClick={() => handleAction('EDIT')} />
                <ControlBtn label="Skip" sub="S" color="zinc" onClick={() => handleAction('SKIP')} />
              </div>
            </div>
          ) : (
            <div className="bg-zinc-900 border border-zinc-800 border-dashed rounded-2xl p-6 h-64 flex flex-col items-center justify-center text-zinc-600">
              <svg className="w-8 h-8 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
              <span className="text-sm font-medium">No active candidate</span>
            </div>
          )}

        </div>

      </div>
    </div>
  )
}

function ControlBtn({ label, sub, color, onClick }) {
  const colorClasses = {
    emerald: "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-900/20",
    red: "bg-red-600 hover:bg-red-500 shadow-red-900/20",
    blue: "bg-blue-600 hover:bg-blue-500 shadow-blue-900/20",
    zinc: "bg-zinc-700 hover:bg-zinc-600 shadow-zinc-900/20"
  }

  return (
    <button
      onClick={onClick}
      className={`${colorClasses[color]} text-white h-14 rounded-xl font-bold shadow-lg transition-all hover:-translate-y-0.5 active:translate-y-0 relative overflow-hidden group`}
    >
      <span className="relative z-10 flex flex-col items-center leading-none">
        <span className="text-sm">{label}</span>
        <span className="text-[10px] opacity-60 font-mono mt-1 font-medium bg-black/20 px-1.5 rounded-sm">({sub})</span>
      </span>
    </button>
  )
}

export default App
