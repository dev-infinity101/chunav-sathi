// Full implementation: Prompt 6

export function useI18n() {
  return {
    t: (key: string) => key,
    lang: 'en' as 'en' | 'hi',
    setLang: (_lang: 'en' | 'hi') => {},
  }
}
