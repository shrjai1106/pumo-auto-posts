import React from "react";
import {
  AbsoluteFill,
  Audio,
  Video,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  staticFile,
} from "remotion";
import { useState, useEffect } from "react";

// ============================================================
// Types
// ============================================================
interface WordTimestamp {
  word: string;
  start: number;
  end: number;
}

interface Scene {
  scene_num: number;
  clip_path: string;
  script: string;
  start_time: number;
  duration: number;
  is_ai: boolean;
}

interface VideoData {
  scenes: Scene[];
  audio_path: string;
  word_timestamps: WordTimestamp[];
  total_duration: number;
  course_name: string;
  hook: string;
  branding: string;
}

// ============================================================
// Word-by-word Caption Component (TikTok style)
// ============================================================
const Caption: React.FC<{
  word_timestamps: WordTimestamp[];
  current_time: number;
}> = ({ word_timestamps, current_time }) => {
  const frame  = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Find current word
  const currentWordIdx = word_timestamps.findIndex(
    (w) => current_time >= w.start && current_time <= w.end
  );

  // Show 3 words at a time — current + context
  const startIdx  = Math.max(0, currentWordIdx - 1);
  const endIdx    = Math.min(word_timestamps.length, startIdx + 3);
  const visibleWords = word_timestamps.slice(startIdx, endIdx);

  if (currentWordIdx === -1 || visibleWords.length === 0) return null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems:     "center",
        paddingBottom:  "15%",
        paddingLeft:    "5%",
        paddingRight:   "5%",
      }}
    >
      <div
        style={{
          display:        "flex",
          flexWrap:       "wrap",
          justifyContent: "center",
          gap:            "8px",
          padding:        "16px 24px",
          borderRadius:   "16px",
          backgroundColor: "rgba(0,0,0,0.45)",
        }}
      >
        {visibleWords.map((w, i) => {
          const isActive    = current_time >= w.start && current_time <= w.end;
          const wordOpacity = interpolate(
            current_time,
            [w.start - 0.05, w.start],
            [0.4, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          );

          return (
            <span
              key={`${w.word}-${startIdx + i}`}
              style={{
                fontFamily:  "League Spartan, Arial Black, sans-serif",
                fontSize:    isActive ? "68px" : "56px",
                fontWeight:  900,
                color:       isActive ? "#FFE500" : "#ffffff",
                textShadow:  "3px 3px 0px #000, -3px -3px 0px #000, 3px -3px 0px #000, -3px 3px 0px #000",
                letterSpacing: "-1px",
                lineHeight:  1.1,
                opacity:     wordOpacity,
                transform:   isActive ? "scale(1.08)" : "scale(1)",
                transition:  "transform 0.1s ease",
              }}
            >
              {w.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// PUMO Branding Overlay
// ============================================================
const BrandingOverlay: React.FC<{
  course_name: string;
  branding: string;
}> = ({ course_name, branding }) => {
  return (
    <>
      {/* Course badge — top right */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-start",
          alignItems:     "flex-end",
          padding:        "24px",
          flexDirection:  "column",
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(0,0,0,0.65)",
            borderRadius:    "12px",
            padding:         "8px 16px",
            border:          "1px solid rgba(255,255,255,0.2)",
          }}
        >
          <span
            style={{
              fontFamily:  "League Spartan, Arial, sans-serif",
              fontSize:    "30px",
              fontWeight:  700,
              color:       "#ffffff",
              textShadow:  "1px 1px 3px rgba(0,0,0,0.8)",
            }}
          >
            {course_name}
          </span>
        </div>
      </AbsoluteFill>

      {/* PUMO branding — bottom */}
      <AbsoluteFill
        style={{
          justifyContent: "flex-end",
          alignItems:     "center",
          paddingBottom:  "3%",
        }}
      >
        <div
          style={{
            backgroundColor: "rgba(0,0,0,0.6)",
            borderRadius:    "10px",
            padding:         "6px 20px",
          }}
        >
          <span
            style={{
              fontFamily: "League Spartan, Arial, sans-serif",
              fontSize:   "26px",
              fontWeight: 600,
              color:      "#ffffff",
              opacity:    0.9,
            }}
          >
            {branding}
          </span>
        </div>
      </AbsoluteFill>
    </>
  );
};

// ============================================================
// Single Scene Component with zoom punch effect
// ============================================================
const SceneClip: React.FC<{
  clip_path: string;
  scene_num: number;
  is_ai: boolean;
  duration_frames: number;
}> = ({ clip_path, scene_num, is_ai, duration_frames }) => {
  const frame      = useCurrentFrame();
  const { fps }    = useVideoConfig();

  // Zoom effect: alternating zoom in / zoom out per scene
  const zoomIn   = scene_num % 2 === 1;
  const zoomStart = zoomIn ? 1.0 : 1.08;
  const zoomEnd   = zoomIn ? 1.08 : 1.0;

  const zoom = interpolate(frame, [0, duration_frames], [zoomStart, zoomEnd], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
  });

  // Fade in at start of each scene
  const opacity = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      <Video
        src={staticFile(clip_path)}
        style={{
          width:      "100%",
          height:     "100%",
          objectFit:  "cover",
          transform:  `scale(${zoom})`,
        }}
        volume={0} // Mute clip audio — using voiceover instead
      />
    </AbsoluteFill>
  );
};

// ============================================================
// Hook Banner — shows at start
// ============================================================
const HookBanner: React.FC<{ hook: string }> = ({ hook }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 5, 90, 100], [0, 1, 1, 0], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame, [0, 5], [30, 0], {
    extrapolateLeft:  "clamp",
    extrapolateRight: "clamp",
  });

  if (frame > 100) return null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-start",
        alignItems:     "center",
        paddingTop:     "12%",
        opacity,
        transform:      `translateY(${translateY}px)`,
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(0,0,0,0.5)",
          borderRadius:    "16px",
          padding:         "12px 28px",
          maxWidth:        "85%",
          textAlign:       "center",
        }}
      >
        <span
          style={{
            fontFamily:  "League Spartan, Arial Black, sans-serif",
            fontSize:    "64px",
            fontWeight:  900,
            color:       "#FFE500",
            textShadow:  "3px 3px 0px #000",
            letterSpacing: "-1px",
            lineHeight:  1.1,
          }}
        >
          {hook}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// MAIN VIDEO COMPOSITION
// ============================================================
export const PUMOVideo: React.FC<{ data: VideoData }> = ({ data }) => {
  const { fps }           = useVideoConfig();
  const frame             = useCurrentFrame();
  const current_time      = frame / fps;

  const scene_duration_frames = Math.floor((data.total_duration / 6) * fps);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>
      {/* Main voiceover audio */}
      <Audio src={staticFile("voiceover.mp3")} volume={1} />

      {/* 6 Scenes */}
      {data.scenes.map((scene, i) => {
        const start_frame = i * scene_duration_frames;
        const clip_file   = `scene_${scene.scene_num}.mp4`;

        return (
          <Sequence
            key={scene.scene_num}
            from={start_frame}
            durationInFrames={scene_duration_frames}
          >
            <SceneClip
              clip_path={clip_file}
              scene_num={scene.scene_num}
              is_ai={scene.is_ai}
              duration_frames={scene_duration_frames}
            />
          </Sequence>
        );
      })}

      {/* Hook banner — first 3 seconds */}
      <Sequence from={0} durationInFrames={100}>
        <HookBanner hook={data.hook} />
      </Sequence>

      {/* Word-by-word captions — throughout */}
      <Caption
        word_timestamps={data.word_timestamps}
        current_time={current_time}
      />

      {/* PUMO Branding — always visible */}
      <BrandingOverlay
        course_name={data.course_name}
        branding={data.branding}
      />
    </AbsoluteFill>
  );
};
