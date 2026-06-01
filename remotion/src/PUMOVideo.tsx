import React from "react";
import {
  AbsoluteFill,
  Audio,
  Video,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
  staticFile,
} from "remotion";

interface WordTimestamp { word: string; start: number; end: number; }
interface Scene { scene_num: number; clip_path: string; script: string; start_time: number; duration: number; is_ai: boolean; }
interface VideoData { scenes: Scene[]; audio_path: string; word_timestamps: WordTimestamp[]; total_duration: number; course_name: string; hook: string; branding: string; }

const Caption: React.FC<{word_timestamps: WordTimestamp[]; current_time: number}> = ({word_timestamps, current_time}) => {
  const currentWordIdx = word_timestamps.findIndex(w => current_time >= w.start && current_time <= w.end);
  if (currentWordIdx === -1) return null;
  const startIdx = Math.max(0, currentWordIdx - 1);
  const visibleWords = word_timestamps.slice(startIdx, startIdx + 3);
  return (
    <AbsoluteFill style={{justifyContent:"flex-end",alignItems:"center",paddingBottom:"15%",paddingLeft:"5%",paddingRight:"5%"}}>
      <div style={{display:"flex",flexWrap:"wrap",justifyContent:"center",gap:"8px",padding:"16px 24px",borderRadius:"16px",backgroundColor:"rgba(0,0,0,0.45)"}}>
        {visibleWords.map((w, i) => {
          const isActive = current_time >= w.start && current_time <= w.end;
          return (
            <span key={`${w.word}-${startIdx+i}`} style={{fontFamily:"Arial Black,sans-serif",fontSize:isActive?"68px":"56px",fontWeight:900,color:isActive?"#FFE500":"#ffffff",textShadow:"3px 3px 0px #000,-3px -3px 0px #000",letterSpacing:"-1px",lineHeight:1.1}}>
              {w.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const BrandingOverlay: React.FC<{course_name: string; branding: string}> = ({course_name, branding}) => (
  <>
    <AbsoluteFill style={{justifyContent:"flex-start",alignItems:"flex-end",padding:"24px",flexDirection:"column"}}>
      <div style={{backgroundColor:"rgba(0,0,0,0.65)",borderRadius:"12px",padding:"8px 16px"}}>
        <span style={{fontFamily:"Arial Black,sans-serif",fontSize:"30px",fontWeight:700,color:"#ffffff"}}>{course_name}</span>
      </div>
    </AbsoluteFill>
    <AbsoluteFill style={{justifyContent:"flex-end",alignItems:"center",paddingBottom:"3%"}}>
      <div style={{backgroundColor:"rgba(0,0,0,0.6)",borderRadius:"10px",padding:"6px 20px"}}>
        <span style={{fontFamily:"Arial,sans-serif",fontSize:"26px",fontWeight:600,color:"#ffffff",opacity:0.9}}>{branding}</span>
      </div>
    </AbsoluteFill>
  </>
);

const SceneClip: React.FC<{clip_path: string; scene_num: number; duration_frames: number}> = ({clip_path, scene_num, duration_frames}) => {
  const frame = useCurrentFrame();
  const zoomIn = scene_num % 2 === 1;
  const zoom = interpolate(frame,[0,duration_frames],[zoomIn?1.0:1.08,zoomIn?1.08:1.0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
  const opacity = interpolate(frame,[0,8],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
  if (!clip_path) {
    return <AbsoluteFill style={{backgroundColor:"#1a1a2e",opacity}} />;
  }
  return (
    <AbsoluteFill style={{opacity}}>
      <Video src={staticFile(clip_path)} style={{width:"100%",height:"100%",objectFit:"cover",transform:`scale(${zoom})`}} volume={0} />
    </AbsoluteFill>
  );
};

export const PUMOVideo: React.FC<{data: VideoData}> = ({data}) => {
  const {fps} = useVideoConfig();
  const frame = useCurrentFrame();
  const current_time = frame / fps;
  const scene_duration_frames = Math.floor((data.total_duration / Math.max(data.scenes.length, 1)) * fps);
  return (
    <AbsoluteFill style={{backgroundColor:"#000000"}}>
      {data.audio_path && <Audio src={staticFile("voiceover.mp3")} volume={1} />}
      {data.scenes.map((scene, i) => (
        <Sequence key={scene.scene_num} from={i * scene_duration_frames} durationInFrames={scene_duration_frames}>
          <SceneClip clip_path={scene.clip_path ? `scene_${scene.scene_num}.mp4` : ""} scene_num={scene.scene_num} duration_frames={scene_duration_frames} />
        </Sequence>
      ))}
      <Caption word_timestamps={data.word_timestamps} current_time={current_time} />
      <BrandingOverlay course_name={data.course_name} branding={data.branding} />
    </AbsoluteFill>
  );
};
