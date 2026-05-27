import React from "react";
import { Composition } from "remotion";
import { CaseTitleCard } from "./compositions/CaseTitleCard";
import { CaseTimeline } from "./compositions/CaseTimeline";
import { DataGraphic } from "./compositions/DataGraphic";
import { EpisodeIntro } from "./compositions/EpisodeIntro";
import { ShortHook } from "./compositions/ShortHook";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyComponent = React.ComponentType<any>;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 16:9 — 5 seconds */}
      <Composition
        id="CaseTitleCard"
        component={CaseTitleCard as AnyComponent}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          caseName: "The Disappearance of Jane Doe",
          year: 1987,
          channelName: "Finally Solved",
          microSeries: "The Evidence Was There",
          accentColor: "#c41e3a",
        }}
      />

      {/* 16:9 — duration scales with events (10 events = ~23 sec) */}
      <Composition
        id="CaseTimeline"
        component={CaseTimeline as AnyComponent}
        durationInFrames={390}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          caseName: "The Disappearance of Jane Doe",
          channelName: "Finally Solved",
          accentColor: "#c41e3a",
          events: [
            {
              date: "March 1987",
              title: "Victim last seen",
              description: "Last known contact with family members.",
              type: "other",
            },
            {
              date: "April 1987",
              title: "Body discovered",
              description: "Found by hikers in a remote area.",
              type: "discovery",
            },
            {
              date: "June 1989",
              title: "Primary suspect named",
              description: "Investigation stalls due to lack of evidence.",
              type: "other",
            },
            {
              date: "2018",
              title: "DNA match via genealogy",
              description: "Forensic genealogy identifies suspect's family line.",
              type: "discovery",
            },
            {
              date: "2019",
              title: "Arrest",
              description: "Suspect arrested and charged with first-degree murder.",
              type: "arrest",
            },
          ],
        }}
      />

      {/* 16:9 — 4 seconds */}
      <Composition
        id="DataGraphic"
        component={DataGraphic as AnyComponent}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          caseName: "The Disappearance of Jane Doe",
          failureType: "Institutional Failure",
          microSeries: "The Evidence Was There",
          complexity: "double",
          year: 1987,
          channelName: "Finally Solved",
          accentColor: "#c41e3a",
        }}
      />

      {/* 16:9 — 6 seconds */}
      <Composition
        id="EpisodeIntro"
        component={EpisodeIntro as AnyComponent}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={{
          channelName: "Finally Solved",
          episodeTitle: "The Disappearance of Jane Doe",
          subtitle: "A 30-year cold case finally cracked by forensic genealogy.",
          accentColor: "#c41e3a",
        }}
      />

      {/* 9:16 vertical Shorts — 3 seconds */}
      <Composition
        id="ShortHook"
        component={ShortHook as AnyComponent}
        durationInFrames={90}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          hookText: "They found the evidence. Then buried it.",
          caseName: "The Disappearance of Jane Doe",
          channelName: "Finally Solved",
          accentColor: "#c41e3a",
        }}
      />
    </>
  );
};
