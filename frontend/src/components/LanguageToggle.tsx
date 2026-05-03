import type { Lang } from '../App'

interface Props { lang: Lang; setLang: (l: Lang) => void }

export default function LanguageToggle({ lang, setLang }: Props) {
  const next = lang === 'en' ? 'hi' : 'en'
  const label = lang === 'en' ? 'Switch to Hindi' : 'Switch to English'

  return (
    <button
      type="button"
      role="switch"
      aria-checked={lang === 'hi'}
      aria-label={label}
      onClick={() => setLang(next)}
      className="flex items-center gap-1 px-3 py-1.5 rounded-full border border-accent text-accent text-sm font-medium hover:bg-accent hover:text-white transition-colors focus-visible:outline-2 focus-visible:outline-accent"
    >
      <span className={lang === 'en' ? 'font-bold' : 'opacity-60'}>EN</span>
      <span className="opacity-40">|</span>
      <span className={lang === 'hi' ? 'font-bold' : 'opacity-60'}>हिं</span>
    </button>
  )
}
