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
  headline: Segment[];
  format: "wide" | "square";
  paletteId?: PaletteId;
};

export const PosterCover: React.FC<PosterCoverProps> = ({
  eyebrow,
  headline,
  format,
  paletteId = "action_green",
}) => {
  const square = format === "square";
  const { backgroundColor, primaryColor, accentColor } = palettes[paletteId];
  const headlineLength = headline.reduce(
    (length, segment) => length + Array.from(segment.text).length,
    0,
  );
  const headlineFontSize = Math.min(
    square ? 82 : 86,
    Math.floor(((square ? 404 : 756) * 0.92) / Math.max(headlineLength, 1)),
  );

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
          fontSize: headlineFontSize,
          lineHeight: 1.08,
          fontWeight: 700,
          letterSpacing: 0,
          whiteSpace: "nowrap",
        }}
      >
        {headline.map((segment, segmentIndex) => (
          <span
            key={segmentIndex}
            style={{ color: segment.accent ? accentColor : primaryColor }}
          >
            {segment.text}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
