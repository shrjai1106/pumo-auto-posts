import { Composition } from "remotion";
import { PUMOVideo } from "./PUMOVideo";
import dataJson from "../public/data.json";

export const RemotionRoot: React.FC = () => {
  const fps              = 30;
  const durationInFrames = Math.ceil(dataJson.total_duration * fps);

  return (
    <Composition
      id="PUMOVideo"
      component={PUMOVideo}
      durationInFrames={durationInFrames}
      fps={fps}
      width={1080}
      height={1920}
      defaultProps={{ data: dataJson }}
    />
  );
};
