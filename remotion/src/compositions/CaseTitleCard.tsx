import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface CaseTitleCardProps {
  caseName: string;
  year?: number | null;
  channelName: string;
  microSeries: string;
  accentColor?: string;
}

export const CaseTitleCard: React.FC<CaseTitleCardProps> = ({
  caseName,
  year,
  channelName,
  microSeries,
  accentColor = "#c41e3a",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const channelOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const lineWidth = interpolate(frame, [15, 50], [0, 100], {
    extrapolateRight: "clamp",
  });

  const words = caseName.split(" ");

  const badgeOpacity = interpolate(frame, [80, 110], [0, 1], {
    extrapolateRight: "clamp",
  });

  const yearOpacity = interpolate(frame, [90, 120], [0, 1], {
    extrapolateRight: "clamp",
  });

  const fadeOut = interpolate(frame, [120, 150], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#080810", fontFamily: "Georgia, serif" }}>
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

      {/* Channel name */}
      <div
        style={{
          position: "absolute",
          top: 60,
          left: 80,
          opacity: channelOpacity * fadeOut,
          color: accentColor,
          fontSize: 22,
          fontFamily: "system-ui, sans-serif",
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          fontWeight: 700,
        }}
      >
        {channelName}
      </div>

      {/* Divider line */}
      <div
        style={{
          position: "absolute",
          top: 106,
          left: 80,
          height: 1,
          width: `${lineWidth}%`,
          backgroundColor: "#333355",
          opacity: fadeOut,
          maxWidth: "calc(100% - 160px)",
        }}
      />

      {/* Case name */}
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: "0 120px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ textAlign: "center", opacity: fadeOut }}>
          {words.map((word, i) => {
            const progress = spring({
              frame: frame - 30 - i * 8,
              fps,
              config: { damping: 12, stiffness: 100, mass: 0.8 },
            });
            return (
              <span
                key={i}
                style={{
                  display: "inline-block",
                  color: "#f0f0f0",
                  fontSize: 84,
                  lineHeight: 1.2,
                  marginRight: 18,
                  opacity: progress,
                  transform: `translateY(${interpolate(progress, [0, 1], [40, 0])}px)`,
                }}
              >
                {word}
              </span>
            );
          })}
        </div>
      </AbsoluteFill>

      {/* Year */}
      {year != null && (
        <div
          style={{
            position: "absolute",
            bottom: 140,
            left: 0,
            right: 0,
            textAlign: "center",
            color: "#888899",
            fontSize: 30,
            letterSpacing: "0.15em",
            opacity: yearOpacity * fadeOut,
            fontFamily: "system-ui, sans-serif",
          }}
        >
          {year}
        </div>
      )}

      {/* Micro-series badge */}
      <div
        style={{
          position: "absolute",
          bottom: 66,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          opacity: badgeOpacity * fadeOut,
        }}
      >
        <div
          style={{
            backgroundColor: accentColor + "22",
            border: `1px solid ${accentColor}55`,
            borderRadius: 4,
            padding: "8px 24px",
            color: accentColor,
            fontSize: 17,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            fontFamily: "system-ui, sans-serif",
            fontWeight: 600,
          }}
        >
          {microSeries}
        </div>
      </div>

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
