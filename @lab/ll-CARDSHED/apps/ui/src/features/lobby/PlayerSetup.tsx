/*
 * S02 PlayerSetup.
 * Stitch origin: docs/SCREENS/player-setup.md
 *   (DS-1, Stitch screen 956dbc597742437da0c8c3309f3e0503).
 * Tokens consumed verbatim from .stitch/DESIGN.md §9 — do not invent.
 *
 * Engine coupling: the Start button calls back into the caller with
 * `(players, seed)`. The store + core call happens in App.tsx so the
 * presentational component stays testable in isolation.
 */
import { useId, useMemo, useState } from "react";
import { generateMatchSeed } from "../../state/matchStore";

interface PlayerSetupProps {
  /** Called once Start is clicked with ≥3 non-empty names. */
  onStart: (input: { players: string[]; seed: number }) => void;
  /** Caller-supplied seed generator (default uses crypto.getRandomValues). */
  generateSeed?: () => number;
  /** Back-to-menu callback. */
  onBack: () => void;
  /** Version chip in the footer. */
  version?: string;
}

const MIN_PLAYERS = 3;
const MAX_PLAYERS = 4;

export function PlayerSetup({
  onStart,
  generateSeed = generateMatchSeed,
  onBack,
  version = "v0.x",
}: PlayerSetupProps) {
  const [names, setNames] = useState<string[]>(["", "", "", ""]);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [seed, setSeed] = useState<number>(() => generateSeed());

  const filledNames = useMemo(
    () => names.map((n) => n.trim()).filter((n) => n.length > 0),
    [names],
  );
  const canStart = filledNames.length >= MIN_PLAYERS;

  const validationId = useId();

  const updateName = (index: number, value: string) => {
    setNames((prev) => {
      const next = prev.slice();
      next[index] = value;
      return next;
    });
  };

  const handleRemovePlayer4 = () => updateName(3, "");

  const handleRandomize = () => {
    setSeed(generateSeed());
  };

  const handleStart = () => {
    if (!canStart) return;
    onStart({ players: filledNames.slice(0, MAX_PLAYERS), seed });
  };

  return (
    <main
      role="main"
      className="relative min-h-screen flex flex-col overflow-hidden"
      style={{ color: "var(--color-ink)" }}
    >
      <FannedCardsMotif />

      <BackToMenuLink onBack={onBack} />

      <div className="flex-grow flex items-center justify-center relative z-10 px-6 py-24">
        <section className="w-full max-w-[640px] flex flex-col items-center">
          <h1
            className="text-center mb-12 uppercase"
            style={{
              fontFamily: "var(--font-display)",
              fontSize: "36px",
              lineHeight: 1.2,
              fontWeight: 700,
              letterSpacing: "0.05em",
              color: "var(--color-ink)",
            }}
          >
            Who's playing?
          </h1>

          <div className="w-full space-y-4 mb-8">
            {names.map((value, idx) => (
              <PlayerRow
                key={idx}
                index={idx}
                value={value}
                onChange={(v) => updateName(idx, v)}
                onRemove={idx === 3 ? handleRemovePlayer4 : undefined}
              />
            ))}
          </div>

          <AdvancedDisclosure
            open={advancedOpen}
            onToggle={() => setAdvancedOpen((s) => !s)}
            seed={seed}
            onRandomize={handleRandomize}
          />

          <div className="mt-12 flex flex-col items-center">
            <div
              id={validationId}
              role="status"
              aria-live="polite"
              className="h-5 mb-4 uppercase"
              style={{
                fontFamily: "var(--font-body)",
                fontSize: "12px",
                fontWeight: 600,
                letterSpacing: "0.05em",
                color: "var(--color-danger)",
                opacity: canStart ? 0 : 0.9,
                transition: "opacity 150ms ease-out",
              }}
            >
              Enter at least 3 names to start
            </div>

            <StartMatchButton
              disabled={!canStart}
              onClick={handleStart}
              aria-describedby={canStart ? undefined : validationId}
            />
          </div>
        </section>
      </div>

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

function BackToMenuLink({ onBack }: { onBack: () => void }) {
  return (
    <header className="fixed top-0 left-0 z-50 px-6 py-6">
      <button
        type="button"
        onClick={onBack}
        className="uppercase flex items-center gap-2 transition-opacity"
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.05em",
          color: "var(--color-ink-muted)",
          opacity: 0.7,
          background: "transparent",
          border: "none",
          padding: "8px 12px",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = "1")}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = "0.7")}
        aria-label="Back to main menu"
      >
        <span aria-hidden>◀</span>
        <span>Main menu</span>
      </button>
    </header>
  );
}

interface PlayerRowProps {
  index: number;
  value: string;
  onChange: (next: string) => void;
  onRemove?: () => void;
}

function PlayerRow({ index, value, onChange, onRemove }: PlayerRowProps) {
  const inputId = `player-name-${index + 1}`;
  return (
    <div
      className="grid items-center gap-4"
      style={{
        gridTemplateColumns: onRemove ? "100px 1fr auto" : "100px 1fr",
      }}
    >
      <label
        htmlFor={inputId}
        className="uppercase"
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.05em",
          color: "var(--color-ink-muted)",
        }}
      >
        Player {index + 1}
      </label>
      <input
        id={inputId}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Enter name"
        className="w-full max-w-[480px] h-14 px-4 outline-none"
        style={{
          background: "var(--color-surface-low)",
          border: "1px solid var(--color-outline-variant)",
          borderRadius: "var(--radius-md)",
          color: "var(--color-ink)",
          fontFamily: "var(--font-body)",
          fontSize: "16px",
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = "var(--color-legal)";
          e.currentTarget.style.boxShadow = "0 0 0 1px var(--color-legal)";
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = "var(--color-outline-variant)";
          e.currentTarget.style.boxShadow = "none";
        }}
      />
      {onRemove ? (
        <button
          type="button"
          onClick={onRemove}
          aria-label={`Remove player ${index + 1}`}
          className="uppercase transition-colors"
          style={{
            fontFamily: "var(--font-body)",
            fontSize: "12px",
            fontWeight: 600,
            letterSpacing: "0.05em",
            color: "var(--color-ink-muted)",
            background: "transparent",
            border: "none",
            cursor: "pointer",
            padding: "8px 12px",
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.color = "var(--color-danger)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.color = "var(--color-ink-muted)")
          }
        >
          Remove
        </button>
      ) : null}
    </div>
  );
}

interface AdvancedDisclosureProps {
  open: boolean;
  onToggle: () => void;
  seed: number;
  onRandomize: () => void;
}

function AdvancedDisclosure({
  open,
  onToggle,
  seed,
  onRandomize,
}: AdvancedDisclosureProps) {
  const seedHex = `0x${seed.toString(16).padStart(8, "0")}`;
  const panelId = useId();
  return (
    <div className="w-full flex flex-col items-center">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls={panelId}
        className="uppercase flex items-center gap-1 transition-colors"
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.05em",
          color: "var(--color-ink-muted)",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          padding: "8px 12px",
        }}
      >
        <span aria-hidden>{open ? "▲" : "▼"}</span>
        <span>Advanced</span>
      </button>
      {open ? (
        <div
          id={panelId}
          className="mt-6 flex items-center gap-4 p-4"
          style={{
            background: "var(--color-surface-highest)",
            opacity: 0.95,
            borderRadius: "var(--radius-md)",
          }}
        >
          <span
            className="uppercase"
            style={{
              fontFamily: "var(--font-body)",
              fontSize: "10px",
              fontWeight: 600,
              letterSpacing: "0.05em",
              color: "var(--color-outline)",
            }}
          >
            RNG Seed
          </span>
          <code
            className="px-3 py-1"
            style={{
              background: "var(--color-surface-low)",
              borderRadius: "var(--radius-sm)",
              fontFamily: "var(--font-card)",
              fontSize: "12px",
              color: "var(--color-legal)",
            }}
          >
            {seedHex}
          </code>
          <button
            type="button"
            onClick={onRandomize}
            className="uppercase px-3 py-1 transition-colors"
            style={{
              background: "var(--color-surface-highest)",
              border: "1px solid var(--color-outline-variant)",
              borderRadius: "var(--radius-sm)",
              fontFamily: "var(--font-body)",
              fontSize: "12px",
              fontWeight: 600,
              letterSpacing: "0.05em",
              color: "var(--color-ink-muted)",
              cursor: "pointer",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "var(--color-surface-high)";
              e.currentTarget.style.borderColor = "var(--color-outline)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "var(--color-surface-highest)";
              e.currentTarget.style.borderColor = "var(--color-outline-variant)";
            }}
          >
            Randomize
          </button>
        </div>
      ) : null}
    </div>
  );
}

interface StartMatchButtonProps {
  disabled: boolean;
  onClick: () => void;
  "aria-describedby"?: string;
}

function StartMatchButton({
  disabled,
  onClick,
  "aria-describedby": ariaDescribedBy,
}: StartMatchButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-disabled={disabled}
      aria-describedby={ariaDescribedBy}
      className="w-[280px] h-14 uppercase tracking-widest flex items-center justify-center transition-all"
      style={{
        borderRadius: "var(--radius-pill)",
        background: disabled
          ? "var(--color-surface-high)"
          : "var(--color-accent)",
        color: disabled
          ? "var(--color-outline-variant)"
          : "var(--color-accent-ink)",
        fontFamily: "var(--font-body)",
        fontSize: "12px",
        fontWeight: 600,
        letterSpacing: "0.1em",
        boxShadow: disabled ? "none" : "0 0 24px rgba(238, 152, 0, 0.3)",
        cursor: disabled ? "not-allowed" : "pointer",
        border: "none",
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.transform = "scale(1.02)";
          e.currentTarget.style.filter = "brightness(1.1)";
        }
      }}
      onMouseLeave={(e) => {
        if (!disabled) {
          e.currentTarget.style.transform = "scale(1)";
          e.currentTarget.style.filter = "brightness(1)";
        }
      }}
    >
      Start match
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
