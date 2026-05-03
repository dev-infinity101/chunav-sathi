// Full implementation: Prompt 7

export function useChat() {
  return {
    messages: [] as const,
    isStreaming: false,
    error: null as string | null,
    send: async (_message: string, _lang: string, _level: string | null) => {},
    clear: () => {},
  }
}
