import * as RadioGroup from '@radix-ui/react-radio-group'
import { useState } from 'react'
import type { Lang } from '../App'

const STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat',
  'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
  'Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan',
  'Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
  'Andaman & Nicobar Islands','Chandigarh','Dadra & Nagar Haveli and Daman & Diu',
  'Delhi','Jammu & Kashmir','Ladakh','Lakshadweep','Puducherry',
]

interface NextStep { label: string; url: string }
interface Result { eligible: boolean; reasons: string[]; next_steps: NextStep[] }
interface Props { lang: Lang }

export default function EligibilityForm({ lang: l }: Props) {
  const [age, setAge] = useState('')
  const [citizenship, setCitizenship] = useState<'indian' | 'other'>('indian')
  const [state, setState] = useState('')
  const [registered, setRegistered] = useState<'true' | 'false'>('false')
  const [result, setResult] = useState<Result | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const valid = age !== '' && Number(age) >= 0 && Number(age) <= 120 && state !== ''

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!valid) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await fetch(`/api/eligibility?lang=${l}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: Number(age), citizenship, state, already_registered: registered === 'true' }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      setResult(await res.json())
    } catch {
      setError(l === 'hi' ? 'कुछ गलत हुआ। पुनः प्रयास करें।' : 'Something went wrong. Try again.')
    } finally {
      setLoading(false)
    }
  }

  const L = (en: string, hi: string) => l === 'hi' ? hi : en

  return (
    <div className="flex-1 overflow-y-auto p-4 max-w-lg mx-auto w-full">
      <h2 className="text-lg font-bold mb-4">{L('Voter Eligibility Check', 'मतदाता पात्रता जांच')}</h2>

      <form onSubmit={submit} className="space-y-4 bg-white p-4 rounded-xl border border-slate-200">
        {/* Age */}
        <div>
          <label htmlFor="age" className="block text-sm font-medium mb-1">{L('Your age', 'आपकी आयु')}</label>
          <input
            id="age" type="number" min={0} max={120} value={age}
            onChange={e => setAge(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            aria-required="true"
          />
        </div>

        {/* Citizenship */}
        <fieldset>
          <legend className="text-sm font-medium mb-2">{L('Citizenship', 'नागरिकता')}</legend>
          <RadioGroup.Root value={citizenship} onValueChange={v => setCitizenship(v as 'indian' | 'other')} className="flex gap-4">
            {([['indian', L('Indian', 'भारतीय')], ['other', L('Other', 'अन्य')]] as const).map(([val, label]) => (
              <div key={val} className="flex items-center gap-2">
                <RadioGroup.Item value={val} id={`cit-${val}`} className="w-4 h-4 rounded-full border border-slate-400 data-[state=checked]:border-accent data-[state=checked]:bg-accent focus:outline-none focus:ring-2 focus:ring-accent">
                  <RadioGroup.Indicator className="flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  </RadioGroup.Indicator>
                </RadioGroup.Item>
                <label htmlFor={`cit-${val}`} className="text-sm">{label}</label>
              </div>
            ))}
          </RadioGroup.Root>
        </fieldset>

        {/* State */}
        <div>
          <label htmlFor="state" className="block text-sm font-medium mb-1">{L('State / UT', 'राज्य / UT')}</label>
          <select
            id="state" value={state} onChange={e => setState(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            aria-required="true"
          >
            <option value="">{L('Select state…', 'राज्य चुनें…')}</option>
            {STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {/* Already registered */}
        <fieldset>
          <legend className="text-sm font-medium mb-2">{L('Already registered as voter?', 'पहले से मतदाता पंजीकृत हैं?')}</legend>
          <RadioGroup.Root value={registered} onValueChange={v => setRegistered(v as 'true' | 'false')} className="flex gap-4">
            {([['true', L('Yes', 'हां')], ['false', L('No', 'नहीं')]] as const).map(([val, label]) => (
              <div key={val} className="flex items-center gap-2">
                <RadioGroup.Item value={val} id={`reg-${val}`} className="w-4 h-4 rounded-full border border-slate-400 data-[state=checked]:border-accent data-[state=checked]:bg-accent focus:outline-none focus:ring-2 focus:ring-accent">
                  <RadioGroup.Indicator className="flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  </RadioGroup.Indicator>
                </RadioGroup.Item>
                <label htmlFor={`reg-${val}`} className="text-sm">{label}</label>
              </div>
            ))}
          </RadioGroup.Root>
        </fieldset>

        <button
          type="submit" disabled={!valid || loading}
          className="w-full bg-accent text-white py-2.5 rounded-xl font-medium text-sm disabled:opacity-40 hover:bg-accent-hover transition-colors"
          aria-busy={loading}
        >
          {loading ? L('Checking…', 'जांच हो रही है…') : L('Check Eligibility', 'पात्रता जांचें')}
        </button>
      </form>

      {error && <div role="alert" className="mt-4 p-3 bg-error-light text-error rounded-xl text-sm">{error}</div>}

      {result && (
        <div className={`mt-4 p-4 rounded-xl border ${result.eligible ? 'bg-success-light border-success' : 'bg-error-light border-error'}`}>
          <p className={`text-lg font-bold mb-3 ${result.eligible ? 'text-success' : 'text-error'}`}>
            {result.eligible ? L('Eligible to Vote ✓', 'मतदान के लिए पात्र ✓') : L('Not Yet Eligible', 'अभी पात्र नहीं')}
          </p>
          <ul className="space-y-1.5 mb-4">
            {result.reasons.map((r, i) => (
              <li key={i} className="text-sm text-text-primary flex gap-2">
                <span className="flex-shrink-0">•</span>{r}
              </li>
            ))}
          </ul>
          {result.next_steps.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-text-muted mb-2">{L('Next Steps', 'अगले कदम')}</p>
              <div className="space-y-2">
                {result.next_steps.map((s, i) => (
                  <a key={i} href={s.url} target="_blank" rel="noopener noreferrer"
                    className="block text-sm text-accent underline hover:text-accent-hover">
                    {s.label} ↗
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
