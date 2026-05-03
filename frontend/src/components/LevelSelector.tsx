import { Building2, Landmark, Users } from 'lucide-react'
import type { Lang, Level } from '../App'

interface Props { lang: Lang; level: Level; setLevel: (l: Level) => void }

const LEVELS: { id: NonNullable<Level>; icon: React.FC<{ className?: string }>; en: string; hi: string }[] = [
  { id: 'lok_sabha',    icon: Landmark,  en: 'Lok Sabha',    hi: 'लोक सभा'    },
  { id: 'vidhan_sabha', icon: Building2, en: 'Vidhan Sabha', hi: 'विधान सभा'  },
  { id: 'panchayat',   icon: Users,     en: 'Panchayat',    hi: 'पंचायत'      },
]

export default function LevelSelector({ lang, level, setLevel }: Props) {
  return (
    <div role="radiogroup" aria-label={lang === 'hi' ? 'चुनाव स्तर चुनें' : 'Select election level'} className="flex gap-2 flex-wrap">
      {LEVELS.map(({ id, icon: Icon, en, hi }) => {
        const selected = level === id
        return (
          <button
            key={id}
            role="radio"
            aria-checked={selected}
            onClick={() => setLevel(selected ? null : id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              selected
                ? 'bg-accent text-white border-accent'
                : 'border-slate-300 text-text-muted hover:border-accent hover:text-accent'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {lang === 'hi' ? hi : en}
          </button>
        )
      })}
    </div>
  )
}
