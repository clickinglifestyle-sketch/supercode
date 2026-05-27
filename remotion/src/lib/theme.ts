export interface ChannelTheme {
  name: string;
  accentColor: string;
  backgroundColor: string;
  textColor: string;
  subtextColor: string;
}

export const CHANNEL_THEMES: Record<string, ChannelTheme> = {
  "finally-solved": {
    name: "Finally Solved",
    accentColor: "#c41e3a",
    backgroundColor: "#080810",
    textColor: "#f0f0f0",
    subtextColor: "#888899",
  },
  default: {
    name: "Channel",
    accentColor: "#2563eb",
    backgroundColor: "#080810",
    textColor: "#f0f0f0",
    subtextColor: "#888899",
  },
};

export function getTheme(channelId: string): ChannelTheme {
  return CHANNEL_THEMES[channelId] ?? CHANNEL_THEMES.default;
}
