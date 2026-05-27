import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface ShortHookProps {
  hookText: string;
  caseName: string;
  channelName?: string;
  accentColor?: string;
}

export const ShortHook: React.FC<ShortHookProps> = ({
  hookText,
  caseName,
  channelName = "Finally Solved",
  accentColor = "#c41e3a",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  const channelProgress = spring({
    frame: frame - 5,
    fps,
    config: { damping: 16, stiffness: 120 },
  });

  const hookWords = hookText.split(" ");

  const caseProgress = spring({
    frame: frame - 50,
    fps,
    config: { damping: 14, stiffness: 100 },
  });

  const fadeOut = interpolate(frame, [60, 90], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#080810",
        fontFamily: "system-ui, sans-serif",
        opacity: bgOpacity * fadeOut,
      }}
    >
      {/* Left accent bar (vertical short format) */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          left: 0,
          width: 6,
          backgroundColor: accentColor,
        }}
      />

      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "flex-start",
          padding: "0 70px 0 90px",
        }}
      >
        <div>
          {/* Channel name */}
          <div
            style={{
              color: accentColor,
              fontSize: 28,
              letterSpacing: "0.25em",
              textTransform: "uppercase",
              fontWeight: 700,
              opacity: channelProgress,
              transform: `translateX(${interpolate(channelProgress, [0, 1], [-20, 0])}px)`,
              marginBottom: 24,
            }}
          >
            {channelName}
          </div>

          {/* Hook text — big and punchy */}
          <div style={{ marginBottom: 40 }}>
            {hookWords.map((word, i) => {
              const wordProgress = spring({
                frame: frame - 15 - i * 5,
                fps,
                config: { damping: 12, stiffness: 110 },
              });
              return (
                <div
                  key={i}
                  style={{
                    display: "block",
                    color: "#f0f0f0",
                    fontSize: 76,
                    fontFamily: "Georgia, serif",
                    lineHeight: 1.1,
                    opacity: wordProgress,
                    transform: `translateX(${interpolate(wordProgress, [0, 1], [-30, 0])}px)`,
                  }}
                >
                  {word}
                </div>
              );
            })}
          </div>

          {/* Case name pill */}
          <div
            style={{
              opacity: caseProgress,
              transform: `translateY(${interpolate(caseProgress, [0, 1], [16, 0])}px)`,
              display: "inline-block",
              backgroundColor: accentColor + "22",
              border: `1px solid ${accentColor}55`,
              borderRadius: 6,
              padding: "10px 24px",
              color: accentColor,
              fontSize: 22,
              letterSpacing: "0.08em",
              fontWeight: 600,
            }}
          >
            {caseName}
          </div>
        </div>
      </AbsoluteFill>

      {/* Right accent bar */}
      <div
        style={{
          position: "absolute",
          top: 0,
          bottom: 0,
          right: 0,
          width: 6,
          backgroundColor: accentColor,
        }}
      />
    </AbsoluteFill>
  );
};
