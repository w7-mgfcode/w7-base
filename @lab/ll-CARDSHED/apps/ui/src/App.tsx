/*
 * App shell — routes between the MVP screens.
 *
 * M3 wires MainMenu (S01). M4 replaces the "player-setup" placeholder with the
 * real PlayerSetup screen + matchStore. Per .claude/rules/ui-design-pipeline.md,
 * every screen past MainMenu has a Stitch origin in docs/SCREENS/.
 */

import { useState } from "react";
import { MainMenu, type MainMenuAction } from "./features/menu/MainMenu";

type Screen =
  | "mainmenu"
  | "player-setup-placeholder"
  | "rules-placeholder"
  | "settings-placeholder";

export default function App() {
  const [screen, setScreen] = useState<Screen>("mainmenu");

  const onMenuAction = (action: MainMenuAction) => {
    if (action === "play") setScreen("player-setup-placeholder");
    else if (action === "rules") setScreen("rules-placeholder");
    else if (action === "settings") setScreen("settings-placeholder");
  };

  if (screen === "mainmenu") {
    return <MainMenu onAction={onMenuAction} />;
  }
  return <Placeholder screen={screen} onBack={() => setScreen("mainmenu")} />;
}

function Placeholder({
  screen,
  onBack,
}: {
  screen: Exclude<Screen, "mainmenu">;
  onBack: () => void;
}) {
  const labels: Record<
    Exclude<Screen, "mainmenu">,
    { title: string; milestone: string }
  > = {
    "player-setup-placeholder": { title: "Player Setup", milestone: "M4 (S02)" },
    "rules-placeholder": { title: "Rules Help", milestone: "M11 (S09)" },
    "settings-placeholder": { title: "Settings", milestone: "M11 (S10)" },
  };
  const { title, milestone } = labels[screen];

  return (
    <main
      role="main"
      className="min-h-screen flex flex-col items-center justify-center text-center px-6"
      style={{ color: "var(--color-ink)" }}
    >
      <h2
        className="uppercase mb-4"
        style={{
          fontFamily: "var(--font-display)",
          fontSize: "48px",
          fontWeight: 700,
          letterSpacing: "0.15em",
          color: "var(--color-ink-strong)",
        }}
      >
        {title}
      </h2>
      <p
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "18px",
          color: "var(--color-ink-muted)",
        }}
      >
        Coming at {milestone}.
      </p>
      <button
        type="button"
        onClick={onBack}
        className="mt-10 w-[280px] h-[56px] uppercase"
        style={{
          borderRadius: "var(--radius-pill)",
          border: "1px solid var(--color-outline-variant)",
          color: "var(--color-ink)",
          fontFamily: "var(--font-body)",
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.05em",
        }}
      >
        Back to menu
      </button>
    </main>
  );
}
