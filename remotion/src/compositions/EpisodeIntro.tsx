import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface EpisodeIntroProps {
  channelName: string;
  episodeTitle: string;
  subtitle?: string;
  accentColor?: string;
}

export const EpisodeIntro: React.FC<EpisodeIntroProps> = ({
  channelName,
  episodeTitle,
  subtitle,
  accentColor = "#c41e3a",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase 1: channel name reveal (0–60)
  const channelScale = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 80, mass: 1 },
    from: 0.85,
    to: 1,
  });
  const channelOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Phase 2: divider line grows (30–70)
  const lineWidth = interpolate(frame, [30, 70], [0, 100], {
    extrapolateRight: "clamp",
  });

  // Phase 3: episode title drops in (60–110)
  const titleProgress = spring({
    frame: frame - 60,
    fps,
    config: { damping: 14, stiffness: 100, mass: 0.9 },
  });
  const titleOpacity = interpolate(frame, [60, 85], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Phase 4: subtitle fades in (100–130)
  const subtitleOpacity = interpolate(frame, [100, 130], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out (160–180)
  const fadeOut = interpolate(frame, [160, 180], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#080810",
        fontFamily: "system-ui, sans-serif",
        opacity: fadeOut,
      }}
    >
      {/* Top accent bar */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 4,
          backgroundColor: accentColor,
        }}
      />

      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", padding: "0 140px" }}
      >
        <div style={{ width: "100%", textAlign: "center" }}>
          {/* Channel name */}
          <div
            style={{
              color: accentColor,
              fontSize: 20,
              letterSpacing: "0.4em",
              textTransform: "uppercase",
              fontWeight: 700,
              opacity: channelOpacity,
              transform: `scale(${channelScale})`,
              marginBottom: 20,
            }}
          >
            {channelName}
          </div>

          {/* Divider */}
          <div
            style={{
              height: 1,
              backgroundColor: "#333355",
              width: `${lineWidth}%`,
              margin: "0 auto 32px",
            }}
          />

          {/* Episode title */}
          <div
            style={{
              color: "#f0f0f0",
              fontSize: 72,
              fontFamily: "Georgia, serif",
              lineHeight: 1.2,
              opacity: titleOpacity,
              transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
            }}
          >
            {episodeTitle}
          </div>

          {/* Subtitle */}
          {subtitle && (
            <div
              style={{
                color: "#888899",
                fontSize: 22,
                marginTop: 24,
                opacity: subtitleOpacity,
                lineHeight: 1.5,
                maxWidth: 800,
                margin: "24px auto 0",
              }}
            >
              {subtitle}
            </div>
          )}
        </div>
      </AbsoluteFill>

      {/* Bottom accent bar */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 4,
          backgroundColor: accentColor,
        }}
      />
    </AbsoluteFill>
  );
};
