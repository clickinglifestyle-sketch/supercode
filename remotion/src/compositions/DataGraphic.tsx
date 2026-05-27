import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface DataGraphicProps {
  caseName: string;
  failureType: string;
  microSeries: string;
  complexity: "single" | "double" | "triple";
  year?: number | null;
  channelName?: string;
  accentColor?: string;
}

const COMPLEXITY_DOTS: Record<string, number> = {
  single: 1,
  double: 2,
  triple: 3,
};

const StatRow: React.FC<{
  label: string;
  value: string;
  frame: number;
  startFrame: number;
  fps: number;
  accentColor: string;
}> = ({ label, value, frame, startFrame, fps, accentColor }) => {
  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 14, stiffness: 120, mass: 0.7 },
  });
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateX(${interpolate(progress, [0, 1], [-24, 0])}px)`,
        marginBottom: 28,
      }}
    >
      <div
        style={{
          color: "#888899",
          fontSize: 13,
          letterSpacing: "0.25em",
          textTransform: "uppercase",
          marginBottom: 6,
          fontFamily: "system-ui, sans-serif",
        }}
      >
        {label}
      </div>
      <div
        style={{
          color: "#f0f0f0",
          fontSize: 26,
          fontWeight: 600,
          fontFamily: "system-ui, sans-serif",
          borderLeft: `3px solid ${accentColor}`,
          paddingLeft: 14,
        }}
      >
        {value}
      </div>
    </div>
  );
};

export const DataGraphic: React.FC<DataGraphicProps> = ({
  caseName,
  failureType,
  microSeries,
  complexity,
  year,
  channelName = "Finally Solved",
  accentColor = "#c41e3a",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const dots = COMPLEXITY_DOTS[complexity] ?? 1;

  const headerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const fadeOut = interpolate(frame, [100, 120], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#080810",
        fontFamily: "system-ui, sans-serif",
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
        style={{
          padding: "80px 120px",
          justifyContent: "center",
          opacity: fadeOut,
        }}
      >
        {/* Channel name */}
        <div
          style={{
            color: accentColor,
            fontSize: 16,
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            fontWeight: 700,
            marginBottom: 10,
            opacity: headerOpacity,
          }}
        >
          {channelName}
        </div>

        {/* Case name */}
        <div
          style={{
            color: "#f0f0f0",
            fontSize: 44,
            fontFamily: "Georgia, serif",
            marginBottom: 8,
            lineHeight: 1.2,
            opacity: headerOpacity,
          }}
        >
          {caseName}
          {year != null && (
            <span style={{ color: "#888899", fontSize: 28, marginLeft: 16 }}>
              ({year})
            </span>
          )}
        </div>

        <div
          style={{
            height: 1,
            backgroundColor: "#1a1a2e",
            marginBottom: 40,
            opacity: headerOpacity,
          }}
        />

        {/* Stats */}
        <StatRow
          label="Micro-Series"
          value={microSeries}
          frame={frame}
          startFrame={30}
          fps={fps}
          accentColor={accentColor}
        />
        <StatRow
          label="Failure Type"
          value={failureType}
          frame={frame}
          startFrame={45}
          fps={fps}
          accentColor={accentColor}
        />

        {/* Complexity dots */}
        <div
          style={{
            opacity: spring({ frame: frame - 60, fps, config: { damping: 14 } }),
            marginBottom: 0,
          }}
        >
          <div
            style={{
              color: "#888899",
              fontSize: 13,
              letterSpacing: "0.25em",
              textTransform: "uppercase",
              marginBottom: 10,
            }}
          >
            Complexity Tier
          </div>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 18,
                  height: 18,
                  borderRadius: "50%",
                  backgroundColor: i < dots ? accentColor : "#1a1a2e",
                  border: `2px solid ${i < dots ? accentColor : "#333355"}`,
                }}
              />
            ))}
            <span
              style={{
                color: "#888899",
                fontSize: 16,
                marginLeft: 8,
                textTransform: "capitalize",
              }}
            >
              {complexity}
            </span>
          </div>
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
