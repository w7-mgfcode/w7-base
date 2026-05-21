/*
 * Boilerplate boot screen — placeholder ONLY.
 *
 * Per @lab/ll-CARDSHED/.claude/rules/ui-design-pipeline.md, no hand-rolled
 * UI past this stub. M3 onward replaces every screen via Skill: stitch-design.
 *
 * The smoke-import from @cardshed/core proves the workspace file: link works.
 */

import { createDeck } from "@cardshed/core";

const DECK_SIZE = createDeck().length;

export default function App() {
  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <section className="max-w-xl text-center space-y-6">
        <h1 className="text-5xl font-semibold tracking-tight">
          CARD SHED — MVP M1
        </h1>
        <p className="opacity-70">
          Scaffold boots. The table is empty.
          <br />
          Stitch-driven screens land at M2 → M11.
        </p>

        <div className="mt-10 text-sm font-mono opacity-80 space-y-1">
          <div>core: @cardshed/core linked</div>
          <div>deck: {DECK_SIZE} cards</div>
        </div>

        <footer className="text-xs opacity-50 mt-12">
          Next: <code>docs/STORYBOARD.md</code> §5 wireframes, then{" "}
          <code>Skill: stitch-design</code>.
        </footer>
      </section>
    </main>
  );
}
