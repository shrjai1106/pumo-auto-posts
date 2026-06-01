import React from "react";
import {
  AbsoluteFill, Audio, Video,
  useCurrentFrame, useVideoConfig,
  interpolate, spring, Sequence,
  staticFile, random,
} from "remotion";

// ============================================================
// TYPES
// ============================================================
interface WordTimestamp { word: string; start: number; end: number; }
interface Scene {
  scene_num: number; clip_path: string; script: string;
  start_time: number; duration: number; is_ai: boolean;
  transition_in: string; keyword_overlay: string;
  overlay_position: string; text_color: string;
}
interface VideoData {
  scenes: Scene[]; word_timestamps: WordTimestamp[];
  total_duration: number; course_name: string;
  hook: string; branding: string; has_music: boolean;
  video_format: string; format_label: string;
  keywords: string[]; stats: string[];
}

// ============================================================
// TRANSITION ENGINE
// Each scene has its own transition — directed by Claude
// ============================================================
const useTransition = (transition: string, fps: number) => {
  const frame = useCurrentFrame();

  const fast = spring({ fps, frame,
    config: { damping: 300, stiffness: 1000, mass: 0.3 },
    durationInFrames: 6,
  });
  const smooth = spring({ fps, frame,
    config: { damping: 18, stiffness: 280, mass: 0.8 },
    durationInFrames: 12,
  });
  const bounce = spring({ fps, frame,
    config: { damping: 10, stiffness: 350, mass: 0.6 },
    durationInFrames: 10,
  });

  const opacity = interpolate(frame, [0, 4], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  switch (transition) {
    case "slam": {
      const scale = interpolate(bounce, [0, 1], [1.25, 1]);
      return { transform: `scale(${scale})`, opacity };
    }
    case "slide_left": {
      const x = interpolate(fast, [0, 1], [120, 0]);
      return { transform: `translateX(${x}px)`, opacity };
    }
    case "slide_right": {
      const x = interpolate(fast, [0, 1], [-120, 0]);
      return { transform: `translateX(${x}px)`, opacity };
    }
    case "slide_up": {
      const y = interpolate(fast, [0, 1], [120, 0]);
      return { transform: `translateY(${y}px)`, opacity };
    }
    case "zoom_in": {
      const scale = interpolate(smooth, [0, 1], [0.7, 1]);
      return { transform: `scale(${scale})`, opacity };
    }
    case "zoom_out": {
      const scale = interpolate(smooth, [0, 1], [1.4, 1]);
      return { transform: `scale(${scale})`, opacity };
    }
    case "whip_pan": {
      const x     = interpolate(fast, [0, 1], [300, 0]);
      const blur  = interpolate(frame, [0, 5], [8, 0], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp",
      });
      return { transform: `translateX(${x}px)`, opacity, filter: `blur(${blur}px)` };
    }
    case "fade":
    default: {
      const op = interpolate(frame, [0, 8], [0, 1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp",
      });
      return { opacity: op };
    }
  }
};

// ============================================================
// SCENE CLIP — transition + Ken Burns + colour grade
// ============================================================
const SceneClip: React.FC<{
  clip_path: string; scene_num: number;
  duration_frames: number; is_ai: boolean; transition: string;
}> = ({ clip_path, scene_num, duration_frames, is_ai, transition }) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  const transStyle = useTransition(transition, fps);

  // Ken Burns — alternating direction per scene
  const zoomIn = scene_num % 2 === 1;
  const zoom   = interpolate(
    frame, [0, duration_frames],
    [zoomIn ? 1.0 : 1.14, zoomIn ? 1.14 : 1.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Camera shake — only first 4 frames
  const shakeDecay = Math.max(0, 1 - frame / 4);
  const sx = (random(frame + "sx") - 0.5) * 6 * shakeDecay;
  const sy = (random(frame + "sy") - 0.5) * 4 * shakeDecay;

  const shakeStyle = { transform: `translate(${sx}px, ${sy}px)` };

  if (!clip_path) {
    return (
      <AbsoluteFill style={{
        ...transStyle,
        background: `linear-gradient(135deg, #0a0a1a, #${is_ai ? "0d1527" : "1a1a2e"})`,
      }} />
    );
  }

  return (
    <AbsoluteFill style={transStyle}>
      <AbsoluteFill style={shakeStyle}>
        <Video
          src={staticFile(clip_path)}
          style={{
            width: "100%", height: "100%", objectFit: "cover",
            transform: `scale(${zoom})`,
            filter: is_ai
              ? "saturate(1.45) contrast(1.15) brightness(0.87)"
              : "saturate(1.12) contrast(1.05)",
          }}
          volume={0}
        />
      </AbsoluteFill>

      {/* Vignette */}
      <AbsoluteFill style={{
        background: "radial-gradient(ellipse at center, transparent 28%, rgba(0,0,0,0.58) 100%)",
        pointerEvents: "none",
      }} />

      {/* Glitch — AI scenes only */}
      {is_ai && <GlitchOverlay />}
    </AbsoluteFill>
  );
};

// ============================================================
// GLITCH OVERLAY
// ============================================================
const GlitchOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  if (frame % 23 >= 2 && frame % 37 >= 1) return null;
  const ox = (random(frame + "gx") - 0.5) * 20;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position:"absolute", inset:0, backgroundColor:"rgba(255,0,0,0.07)", transform:`translateX(${ox}px)`, mixBlendMode:"screen" as const }} />
      <div style={{ position:"absolute", inset:0, backgroundColor:"rgba(0,255,255,0.05)", transform:`translateX(${-ox*0.7}px)`, mixBlendMode:"screen" as const }} />
      <div style={{ position:"absolute", left:0, right:0, top:`${random(frame+"sl")*100}%`, height:"2px", backgroundColor:"rgba(255,255,255,0.3)" }} />
    </AbsoluteFill>
  );
};

// ============================================================
// CONFETTI PARTICLES
// ============================================================
const Particle: React.FC<{ seed: number }> = ({ seed }) => {
  const frame   = useCurrentFrame();
  const x       = random(seed + "x") * 100;
  const startY  = random(seed + "sy") * 120;
  const speed   = random(seed + "sp") * 0.7 + 0.2;
  const size    = random(seed + "sz") * 7 + 2;
  const isRect  = random(seed + "sh") > 0.6;
  const floatY  = (frame * speed) % 140;
  const opacity = interpolate(floatY, [0, 25, 110, 140], [0, 0.85, 0.75, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const rotate  = frame * (random(seed + "r") * 5 - 2.5);
  const color   = random(seed + "c") > 0.55 ? "#FFE500" : "#ffffff";

  return (
    <div style={{
      position: "absolute",
      left: `${x}%`,
      top: `calc(${startY}% - ${floatY}px)`,
      width: `${size}px`,
      height: isRect ? `${size * 0.4}px` : `${size}px`,
      borderRadius: isRect ? "1px" : "50%",
      backgroundColor: color,
      opacity,
      transform: `rotate(${rotate}deg)`,
      boxShadow: `0 0 ${size}px ${color}88`,
    }} />
  );
};

const ConfettiOverlay: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    {Array.from({ length: 28 }, (_, i) => <Particle key={i} seed={i} />)}
  </AbsoluteFill>
);

// ============================================================
// SCENE-DIRECTED KEYWORD OVERLAY
// Claude picks what word to show and where for each scene
// ============================================================
const SceneKeywordOverlay: React.FC<{
  keyword: string; position: string; textColor: string;
}> = ({ keyword, position, textColor }) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!keyword) return null;

  const pop = spring({ fps, frame,
    config: { damping: 10, stiffness: 380, mass: 0.5 }, durationInFrames: 8,
  });
  const opacity = interpolate(frame, [0, 4], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const scale = interpolate(pop, [0, 1], [0.6, 1]);

  const colorMap: Record<string, string> = {
    yellow: "#FFE500",
    white:  "#ffffff",
    red:    "#ff3b3b",
    green:  "#00ff88",
    blue:   "#3b8beb",
  };
  const color = colorMap[textColor] || "#FFE500";

  const positionStyle: React.CSSProperties = position === "center"
    ? { justifyContent: "center", alignItems: "center" }
    : position === "top"
    ? { justifyContent: "flex-start", alignItems: "center", paddingTop: "12%" }
    : { justifyContent: "flex-end", alignItems: "center", paddingBottom: "22%" };

  return (
    <AbsoluteFill style={{ ...positionStyle, pointerEvents: "none", opacity }}>
      <div style={{
        transform: `scale(${scale})`,
        backgroundColor: "rgba(0,0,0,0.45)",
        borderRadius: "14px",
        padding: "6px 22px",
      }}>
        <span style={{
          fontFamily:    "Arial Black, Impact, sans-serif",
          fontSize:      position === "center" ? "120px" : "80px",
          fontWeight:    900,
          color,
          textShadow:    `4px 4px 0px #000,-4px -4px 0px #000,4px -4px 0px #000,-4px 4px 0px #000, 0 0 30px ${color}88`,
          letterSpacing: "-3px",
          lineHeight:    0.95,
          display:       "block",
          textAlign:     "center",
          textTransform: "uppercase",
        }}>
          {keyword}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// WORD CAPTION — one word at a time, synced to ElevenLabs
// ============================================================
const Caption: React.FC<{
  word_timestamps: WordTimestamp[]; current_time: number;
}> = ({ word_timestamps, current_time }) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  const idx = word_timestamps.findIndex(
    w => current_time >= w.start && current_time <= w.end
  );
  if (idx === -1) return null;

  const w         = word_timestamps[idx];
  const wordFrame = Math.max(0, frame - Math.round(w.start * fps));

  const scale = spring({ fps, frame: wordFrame,
    config: { damping: 12, stiffness: 420, mass: 0.55 }, durationInFrames: 7,
  });
  const shakeX = wordFrame < 3 ? (random(frame + "cx") - 0.5) * 10 : 0;
  const glow   = interpolate(wordFrame, [0, 3, 8], [38, 20, 10], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      justifyContent: "flex-end",
      alignItems:     "center",
      paddingBottom:  "18%",
      pointerEvents:  "none",
    }}>
      <div style={{
        transform:       `scale(${scale}) translateX(${shakeX}px)`,
        backgroundColor: "rgba(0,0,0,0.48)",
        borderRadius:    "12px",
        padding:         "6px 22px",
      }}>
        <span style={{
          fontFamily:    "Arial Black, Impact, sans-serif",
          fontSize:      "84px",
          fontWeight:    900,
          color:         "#FFE500",
          textShadow:    `4px 4px 0px #000,-4px -4px 0px #000,4px -4px 0px #000,-4px 4px 0px #000,0 0 ${glow}px rgba(255,229,0,0.9)`,
          letterSpacing: "-2px",
          lineHeight:    1,
          display:       "block",
          textAlign:     "center",
          textTransform: "uppercase",
        }}>
          {w.word}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// HOOK BANNER
// ============================================================
const HookBanner: React.FC<{ hook: string; duration_frames: number }> = ({
  hook, duration_frames,
}) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  const arrive = spring({ fps, frame,
    config: { damping: 14, stiffness: 260, mass: 0.9 }, durationInFrames: 22,
  });
  const opacity = interpolate(
    frame, [0, 5, duration_frames - 10, duration_frames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const y    = interpolate(arrive, [0, 1], [80, 0]);
  const sc   = interpolate(arrive, [0, 1], [0.7, 1]);
  const glow = Math.sin(frame * 0.1) * 10 + 24;

  const words = hook.split(" ");
  const mid   = Math.ceil(words.length / 2);
  const line1 = words.slice(0, mid).join(" ");
  const line2 = words.slice(mid).join(" ");

  return (
    <AbsoluteFill style={{
      justifyContent: "center",
      alignItems:     "center",
      opacity,
      transform:      `translateY(${y}px) scale(${sc})`,
      pointerEvents:  "none",
    }}>
      <div style={{
        textAlign:       "center",
        padding:         "18px 32px",
        maxWidth:        "90%",
        backgroundColor: "rgba(0,0,0,0.58)",
        borderRadius:    "20px",
        border:          `3px solid rgba(255,229,0,0.85)`,
        boxShadow:       `0 0 ${glow}px rgba(255,229,0,0.55), inset 0 0 40px rgba(0,0,0,0.4)`,
      }}>
        {[line1, line2].filter(Boolean).map((line, i) => (
          <div key={i} style={{
            fontFamily:    "Arial Black, Impact, sans-serif",
            fontSize:      "70px",
            fontWeight:    900,
            color:         i === 0 ? "#ffffff" : "#FFE500",
            textShadow:    "4px 4px 0px #000,-4px -4px 0px #000",
            letterSpacing: "-2px",
            lineHeight:    1.05,
            textTransform: "uppercase",
          }}>
            {line}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// FORMAT LABEL
// ============================================================
const FormatLabel: React.FC<{ format_label: string }> = ({ format_label }) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  const arrive = spring({ fps, frame,
    config: { damping: 200, stiffness: 600 }, durationInFrames: 10,
  });
  const x = interpolate(arrive, [0, 1], [-260, 0]);

  const colors: Record<string,string> = {
    "Story-Driven":"#3b82f6","Myth vs Reality":"#ef4444",
    "Quick Tips":"#10b981","Day in the Life":"#f59e0b",
    "Before vs After":"#8b5cf6","Hot Take":"#f97316",
  };

  return (
    <AbsoluteFill style={{ justifyContent:"flex-start", alignItems:"flex-start", padding:"28px" }}>
      <div style={{
        transform:       `translateX(${x}px)`,
        backgroundColor: colors[format_label] || "#3b82f6",
        borderRadius:    "0 10px 10px 0",
        padding:         "5px 16px 5px 10px",
      }}>
        <span style={{
          fontFamily: "Arial Black, sans-serif", fontSize:"22px",
          fontWeight: 900, color: "#fff", textTransform:"uppercase", letterSpacing:"1px",
        }}>
          {format_label}
        </span>
      </div>
    </AbsoluteFill>
  );
};

// ============================================================
// BRANDING
// ============================================================
const BrandingOverlay: React.FC<{ course_name: string; branding: string }> = ({
  course_name, branding,
}) => {
  const frame   = useCurrentFrame();
  const { fps } = useVideoConfig();

  const top = spring({ fps, frame,
    config: { damping: 200, stiffness: 600 }, durationInFrames: 12,
  });
  const bot = spring({ fps, frame: Math.max(0, frame - 5),
    config: { damping: 200, stiffness: 600 }, durationInFrames: 12,
  });

  return (
    <>
      <AbsoluteFill style={{ justifyContent:"flex-start", alignItems:"flex-end", padding:"28px", flexDirection:"column" }}>
        <div style={{
          transform:       `translateY(${interpolate(top,[0,1],[-50,0])}px)`,
          backgroundColor: "rgba(0,0,0,0.78)",
          borderRadius:    "12px",
          padding:         "7px 16px",
          border:          "2px solid rgba(255,229,0,0.7)",
          boxShadow:       "0 0 18px rgba(255,229,0,0.28)",
        }}>
          <span style={{ fontFamily:"Arial Black,sans-serif", fontSize:"26px", fontWeight:900, color:"#FFE500" }}>
            {course_name}
          </span>
        </div>
      </AbsoluteFill>

      <AbsoluteFill style={{ justifyContent:"flex-end", alignItems:"center", paddingBottom:"2.5%" }}>
        <div style={{
          transform:       `translateY(${interpolate(bot,[0,1],[50,0])}px)`,
          backgroundColor: "rgba(0,0,0,0.78)",
          borderRadius:    "10px",
          padding:         "6px 22px",
          border:          "1px solid rgba(255,255,255,0.22)",
        }}>
          <span style={{ fontFamily:"Arial,sans-serif", fontSize:"24px", fontWeight:700, color:"#fff" }}>
            {branding}
          </span>
        </div>
      </AbsoluteFill>
    </>
  );
};

// ============================================================
// MAIN COMPOSITION
// ============================================================
export const PUMOVideo: React.FC<{ data: VideoData }> = ({ data }) => {
  const { fps }      = useVideoConfig();
  const frame        = useCurrentFrame();
  const current_time = frame / fps;

  // Build cumulative frame positions from Claude-directed durations
  let cursor = 0;
  const sceneFrames = data.scenes.map(scene => {
    const start = cursor;
    const dur   = Math.max(Math.round(scene.duration * fps), 1);
    cursor += dur;
    return { start, dur };
  });

  // Hook shows over first 2 scenes
  const hookDuration = (sceneFrames[0]?.dur ?? 0) + (sceneFrames[1]?.dur ?? 0);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000000" }}>

      {/* Audio — voiceover controls everything */}
      <Audio src={staticFile("voiceover.mp3")} volume={1} />
      {data.has_music && (
        <Audio src={staticFile("music.mp3")} volume={0.16} />
      )}

      {/* Confetti throughout */}
      <ConfettiOverlay />

      {/* Scenes — each follows Claude's direction */}
      {data.scenes.map((scene, i) => {
        const { start, dur } = sceneFrames[i];
        return (
          <Sequence key={scene.scene_num} from={start} durationInFrames={dur}>
            {/* Background clip */}
            <SceneClip
              clip_path={scene.clip_path || ""}
              scene_num={scene.scene_num}
              duration_frames={dur}
              is_ai={scene.is_ai}
              transition={scene.transition_in || "fade"}
            />
            {/* Scene-specific keyword overlay directed by Claude */}
            {scene.keyword_overlay && (
              <SceneKeywordOverlay
                keyword={scene.keyword_overlay}
                position={scene.overlay_position || "bottom"}
                textColor={scene.text_color || "yellow"}
              />
            )}
          </Sequence>
        );
      })}

      {/* Hook banner — first 2 scenes */}
      {hookDuration > 0 && (
        <Sequence from={0} durationInFrames={hookDuration}>
          <HookBanner hook={data.hook} duration_frames={hookDuration} />
        </Sequence>
      )}

      {/* Word-by-word caption — synced to ElevenLabs timestamps */}
      <Caption word_timestamps={data.word_timestamps} current_time={current_time} />

      {/* Format label — first 3 scenes */}
      {sceneFrames[2] && (
        <Sequence from={0} durationInFrames={sceneFrames[0].dur + sceneFrames[1].dur + sceneFrames[2].dur}>
          <FormatLabel format_label={data.format_label || ""} />
        </Sequence>
      )}

      {/* Branding — always visible */}
      <BrandingOverlay course_name={data.course_name} branding={data.branding} />

    </AbsoluteFill>
  );
};
