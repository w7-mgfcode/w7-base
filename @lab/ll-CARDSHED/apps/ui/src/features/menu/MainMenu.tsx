/*
 * S01 MainMenu.
 * Stitch origin: docs/SCREENS/main-menu.md (DS-1, Stitch screen cb1645e2f8f84834914174930efbbfb6).
 * Tokens consumed verbatim from .stitch/DESIGN.md §9 — do not invent.
 */

import { cn } from "../../lib/cn";

export type MainMenuAction = "play" | "rules" | "settings";

interface MainMenuProps {
  onAction: (action: MainMenuAction) => void;
  version?: string;
}

export function MainMenu({ onAction, version = "v0.x" }: MainMenuProps) {
  return (
    <main
      role="main"
      className="relative min-h-screen flex flex-col items-center justify-center text-center overflow-hidden"
      style={{ color: "var(--color-ink)" }}
    >
      <FannedCardsMotif />

      <section className="relative z-10 flex flex-col items-center max-w-[600px] px-6">
        <header className="mb-12">
          <span
            className="block mb-3 uppercase"
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "12px",
              fontWeight: 600,
              letterSpacing: "0.05em",
              color: "var(--color-ink-muted)",
            }}
          >
            Welcome to
          </span>
          <h1
            className="uppercase mb-4"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "48px",
              lineHeight: 1.2,
              fontWeight: 700,
              letterSpacing: "0.15em",
              color: "var(--color-ink-strong)",
            }}
          >
            CARD SHED
          </h1>
          <p
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "18px",
              lineHeight: 1.6,
              color: "var(--color-ink-muted)",
            }}
          >
            A shifting-trump card game for three or four friends.
          </p>
        </header>

        <nav
          className="flex flex-col gap-4 items-center"
          aria-label="Main menu actions"
        >
          <PrimaryButton onClick={() => onAction("play")} label="Play" />
          <GhostButton onClick={() => onAction("rules")} label="Rules" />
          <GhostButton onClick={() => onAction("settings")} label="Settings" />
        </nav>
      </section>

      <footer
        className="fixed bottom-0 left-0 w-full flex flex-col items-center gap-2 pb-8 pointer-events-none"
        style={{ color: "var(--color-ink-muted)" }}
      >
        <div
          className="flex items-center gap-4"
          style={{
            fontFamily: "var(--font-body)",
            fontSize: "14px",
            opacity: 0.4,
          }}
        >
          <span>{version}</span>
          <span
            aria-hidden
            className="block w-px h-3"
            style={{ background: "var(--color-outline-variant)" }}
          />
          <span>MVP</span>
          <span
            aria-hidden
            className="block w-px h-3"
            style={{ background: "var(--color-outline-variant)" }}
          />
          <span>hot-seat browser</span>
        </div>
      </footer>
    </main>
  );
}

function PrimaryButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={cn(
        "w-[280px] h-[56px] uppercase",
        "transition-all duration-200 ease-out",
        "hover:scale-[1.02] hover:brightness-110 active:scale-95",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
      )}
      style={{
        borderRadius: "var(--radius-pill)",
        background: "var(--color-accent)",
        color: "var(--color-accent-ink)",
        fontFamily: "var(--font-body)",
        fontSize: "12px",
        fontWeight: 600,
        letterSpacing: "0.05em",
        boxShadow: "0 0 24px rgba(245, 158, 11, 0.25)",
      }}
    >
      {label}
    </button>
  );
}

function GhostButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={cn(
        "w-[280px] h-[56px] uppercase bg-transparent",
        "transition-all duration-200 ease-out",
        "hover:brightness-110 active:scale-95",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
      )}
      style={{
        borderRadius: "var(--radius-pill)",
        border: "1px solid var(--color-outline-variant)",
        color: "var(--color-ink)",
        fontFamily: "var(--font-body)",
        fontSize: "12px",
        fontWeight: 600,
        letterSpacing: "0.05em",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "var(--color-surface-high)";
        e.currentTarget.style.borderColor = "var(--color-outline)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "transparent";
        e.currentTarget.style.borderColor = "var(--color-outline-variant)";
      }}
    >
      {label}
    </button>
  );
}

function FannedCardsMotif() {
  const cardStyle = {
    width: 280,
    height: 400,
    background: "var(--color-ink-strong)",
    border: "3px solid var(--color-outline-variant)",
    borderRadius: "var(--radius-lg)",
    filter: "drop-shadow(0 10px 20px rgba(0, 0, 0, 0.5))",
    transformOrigin: "bottom center",
  } satisfies React.CSSProperties;

  return (
    <div
      aria-hidden
      className="fixed bottom-[-100px] left-[-80px] rotate-[25deg] pointer-events-none select-none"
      style={{ opacity: 0.07 }}
    >
      <div className="flex" style={{ gap: "-60px" }}>
        <div style={{ ...cardStyle, transform: "rotate(-15deg)" }} />
        <div style={{ ...cardStyle, marginTop: -20 }} />
        <div
          style={{
            ...cardStyle,
            transform: "rotate(15deg)",
            marginTop: -40,
          }}
        />
      </div>
    </div>
  );
}
