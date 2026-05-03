import * as Accordion from '@radix-ui/react-accordion'
import { ChevronDown } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { Lang, Level } from '../App'

interface Phase { id: string; order: number; name: string; duration_days_typical?: number; description: string; key_facts: string[] }
interface TimelineData { level: string; name: string; phases: Phase[] }

interface Props { lang: Lang; level: Level }

export default function Timeline({ lang, level }: Props) {
  const [data, setData] = useState<TimelineData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!level) { setData(null); return }
    setLoading(true); setError('')
    fetch(`/api/timeline/${level}?lang=${lang}`)
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then(setData)
      .catch(() => setError(lang === 'hi' ? 'डेटा लोड नहीं हो सका।' : 'Failed to load timeline.'))
      .finally(() => setLoading(false))
  }, [level, lang])

  if (!level) {
    return (
      <div className="flex-1 flex items-center justify-center text-text-muted p-8 text-center">
        <div>
          <p className="text-4xl mb-3">🗳️</p>
          <p>{lang === 'hi' ? 'ऊपर चुनाव स्तर चुनें' : 'Select an election level above to view the timeline'}</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex-1 p-6 space-y-3" aria-busy="true" aria-label={lang === 'hi' ? 'लोड हो रहा है' : 'Loading'}>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-14 bg-slate-200 rounded-xl animate-pulse" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div role="alert" className="m-6 p-4 bg-error-light text-error rounded-xl">
        {error}
        <button onClick={() => setLoading(true)} className="ml-3 underline">
          {lang === 'hi' ? 'पुनः प्रयास' : 'Retry'}
        </button>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <h2 className="text-lg font-bold text-text-primary mb-4">{data.name}</h2>
      <Accordion.Root type="multiple" className="space-y-2">
        {data.phases.map((phase, idx) => (
          <Accordion.Item key={phase.id} value={phase.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <Accordion.Header>
              <Accordion.Trigger className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-50 transition-colors group">
                <span className="flex-shrink-0 w-7 h-7 rounded-full bg-accent-light text-accent text-xs font-bold flex items-center justify-center group-data-[state=open]:bg-accent group-data-[state=open]:text-white transition-colors">
                  {idx + 1}
                </span>
                <span className="flex-1 font-medium text-sm">{phase.name}</span>
                {phase.duration_days_typical && (
                  <span className="text-xs text-text-muted mr-2">~{phase.duration_days_typical}d</span>
                )}
                <ChevronDown className="w-4 h-4 text-text-muted transition-transform group-data-[state=open]:rotate-180 flex-shrink-0" />
              </Accordion.Trigger>
            </Accordion.Header>
            <Accordion.Content className="px-4 pb-4 data-[state=open]:animate-none">
              <p className="text-sm text-text-muted mb-3 leading-relaxed">{phase.description}</p>
              {phase.key_facts.length > 0 && (
                <ul className="space-y-1.5">
                  {phase.key_facts.map((fact, fi) => (
                    <li key={fi} className="flex gap-2 text-sm">
                      <span className="text-accent flex-shrink-0 mt-0.5">•</span>
                      <span className="text-text-primary">{fact}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Accordion.Content>
          </Accordion.Item>
        ))}
      </Accordion.Root>
    </div>
  )
}
