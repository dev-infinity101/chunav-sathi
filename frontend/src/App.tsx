import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import EligibilityForm from './components/EligibilityForm'
import LanguageToggle from './components/LanguageToggle'
import LevelSelector from './components/LevelSelector'
import Timeline from './components/Timeline'

export type Lang = 'en' | 'hi'
export type Level = 'lok_sabha' | 'vidhan_sabha' | 'panchayat' | null
export type Tab = 'chat' | 'timeline' | 'eligibility'

const TAB_LABELS: Record<Tab, Record<Lang, string>> = {
  chat:        { en: 'Ask Anything',      hi: 'कुछ भी पूछें'   },
  timeline:    { en: 'Election Timeline', hi: 'चुनाव समयरेखा'  },
  eligibility: { en: 'Eligibility',       hi: 'पात्रता जांच'    },
}

export default function App() {
  const [lang, setLang] = useState<Lang>('en')
  const [level, setLevel] = useState<Level>(null)
  const [tab, setTab] = useState<Tab>('chat')

  return (
    <div className="min-h-screen bg-surface-secondary text-text-primary flex flex-col">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:bg-accent focus:text-white focus:px-4 focus:py-2 focus:rounded"
      >
        Skip to content
      </a>

      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div>
          <h1 className="text-xl font-bold text-accent">
            {lang === 'hi' ? 'चुनाव साथी' : 'Chunav Saathi'}
          </h1>
          <p className="text-xs text-text-muted hidden sm:block">
            {lang === 'hi'
              ? 'भारतीय चुनाव की द्विभाषी मार्गदर्शिका'
              : 'Your bilingual Indian election guide'}
          </p>
        </div>
        <LanguageToggle lang={lang} setLang={setLang} />
      </header>

      <nav className="bg-white border-b border-slate-200 px-4 flex" aria-label="Main navigation">
        {(Object.keys(TAB_LABELS) as Tab[]).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === t
                ? 'border-accent text-accent'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}
            aria-current={tab === t ? 'page' : undefined}
          >
            {TAB_LABELS[t][lang]}
          </button>
        ))}
      </nav>

      <div className="bg-white border-b border-slate-100 px-4 py-2">
        <LevelSelector lang={lang} level={level} setLevel={setLevel} />
      </div>

      <main id="main" className="flex-1 overflow-hidden flex flex-col">
        {tab === 'chat'        && <ChatPanel lang={lang} level={level} />}
        {tab === 'timeline'    && <Timeline lang={lang} level={level} />}
        {tab === 'eligibility' && <EligibilityForm lang={lang} />}
      </main>

      <footer className="text-center text-xs text-text-muted py-2 bg-white border-t border-slate-100">
        Chunav Saathi · Data source: Election Commission of India
      </footer>
    </div>
  )
}
