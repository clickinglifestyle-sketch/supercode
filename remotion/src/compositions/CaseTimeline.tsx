import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export interface TimelineEvent {
  date: string;
  title: string;
  description: string;
  type?: "discovery" | "arrest" | "trial" | "death" | "other";
}

export interface CaseTimelineProps {
  events: TimelineEvent[];
  caseName: string;
  channelName?: string;
  accentColor?: string;
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  discovery: "#2563eb",
  arrest: "#c41e3a",
  trial: "#d97706",
  death: "#6b7280",
  other: "#888899",
};

const FRAMES_PER_EVENT = 60;
const HEADER_FRAMES = 30;

export const CaseTimeline: React.FC<CaseTimelineProps> = ({
  events,
  caseName,
  channelName = "Finally Solved",
  accentColor = "#c41e3a",
}) => {
  const frame = useCurrentFrame();

  const headerOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  const visibleEvents = Math.floor(
    Math.max(0, frame - HEADER_FRAMES) / FRAMES_PER_EVENT
  ) + 1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#080810",
        fontFamily: "system-ui, sans-serif",
        padding: "60px 80px",
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

      {/* Header */}
      <div style={{ opacity: headerOpacity, marginBottom: 40 }}>
        <div
          style={{
            color: accentColor,
            fontSize: 16,
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            fontWeight: 700,
            marginBottom: 8,
          }}
        >
          {channelName}
        </div>
        <div style={{ color: "#f0f0f0", fontSize: 36, fontFamily: "Georgia, serif" }}>
          {caseName}
        </div>
        <div
          style={{
            marginTop: 12,
            height: 1,
            backgroundColor: "#333355",
            width: "100%",
          }}
        />
      </div>

      {/* Timeline */}
      <div style={{ position: "relative", paddingLeft: 40 }}>
        {/* Vertical line */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: 2,
            backgroundColor: "#1a1a2e",
          }}
        />

        {events.slice(0, Math.min(visibleEvents, events.length)).map((event, i) => {
          const eventStart = HEADER_FRAMES + i * FRAMES_PER_EVENT;
          const localFrame = Math.max(0, frame - eventStart);
          const opacity = interpolate(localFrame, [0, 20], [0, 1], {
            extrapolateRight: "clamp",
          });
          const translateX = interpolate(localFrame, [0, 20], [-20, 0], {
            extrapolateRight: "clamp",
          });

          const dotColor =
            EVENT_TYPE_COLORS[event.type ?? "other"] ?? "#888899";

          return (
            <div
              key={i}
              style={{
                opacity,
                transform: `translateX(${translateX}px)`,
                marginBottom: 36,
                position: "relative",
              }}
            >
              {/* Dot */}
              <div
                style={{
                  position: "absolute",
                  left: -46,
                  top: 4,
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  backgroundColor: dotColor,
                  border: "2px solid #080810",
                }}
              />

              {/* Date */}
              <div
                style={{
                  color: "#888899",
                  fontSize: 14,
                  letterSpacing: "0.1em",
                  marginBottom: 4,
                  textTransform: "uppercase",
                }}
              >
                {event.date}
              </div>

              {/* Title */}
              <div
                style={{
                  color: "#f0f0f0",
                  fontSize: 22,
                  fontWeight: 600,
                  marginBottom: 4,
                }}
              >
                {event.title}
              </div>

              {/* Description */}
              <div style={{ color: "#aaaacc", fontSize: 16, lineHeight: 1.5 }}>
                {event.description}
              </div>
            </div>
          );
        })}
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
