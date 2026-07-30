import React from "react";
import { AbsoluteFill } from "remotion";

type Segment = {
  text: string;
  accent?: boolean;
};

const palettes = {
  action_green: {
    backgroundColor: "#175941",
    primaryColor: "#FFFDF6",
    accentColor: "#F6D96B",
  },
  notice_blue: {
    backgroundColor: "#214E73",
    primaryColor: "#FFFDF6",
    accentColor: "#F6D96B",
  },
  risk_red: {
    backgroundColor: "#7A3732",
    primaryColor: "#FFFDF6",
    accentColor: "#F6D96B",
  },
} as const;

type PaletteId = keyof typeof palettes;

type PosterCoverProps = {
  eyebrow: string;
  headlineLines: Segment[][];
  format: "wide" | "square";
  paletteId?: PaletteId;
};

export const PosterCover: React.FC<PosterCoverProps> = ({
  eyebrow,
  headlineLines,
  format,
  paletteId = "action_green",
}) => {
  const square = format === "square";
  const { backgroundColor, primaryColor, accentColor } = palettes[paletteId];

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        color: primaryColor,
        fontFamily: '"PingFang SC", "Microsoft YaHei", sans-serif',
        padding: square ? "56px 48px 50px" : "52px 72px 46px",
        boxSizing: "border-box",
        justifyContent: "space-between",
      }}
    >
      <div
        style={{ fontSize: square ? 28 : 30, lineHeight: 1, fontWeight: 600 }}
      >
        {eyebrow}
      </div>

      <div
        style={{
          fontSize: square ? 82 : 86,
          lineHeight: square ? 1.12 : 1.08,
          fontWeight: 700,
          letterSpacing: 0,
        }}
      >
        {headlineLines.map((line, lineIndex) => (
          <div key={lineIndex}>
            {line.map((segment, segmentIndex) => (
              <span
                key={`${lineIndex}-${segmentIndex}`}
                style={{ color: segment.accent ? accentColor : primaryColor }}
              >
                {segment.text}
              </span>
            ))}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
