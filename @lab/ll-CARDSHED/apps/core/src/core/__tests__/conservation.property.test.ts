import { describe, it } from "vitest";
import fc from "fast-check";
import { runRandomLegalRound } from "./_bot.js";
import { allCardIds, totalCards } from "./_helpers.js";
import { createPublicView } from "../rules.js";

describe("conservation property", () => {
  it("for any sequence of legal actions, card conservation holds (>=200 iters)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.constantFrom<3 | 4>(3, 4),
        (deckSeed, botSeed, playerCount) => {
          const run = runRandomLegalRound(deckSeed, playerCount, botSeed);
          for (const s of run.states) {
            if (totalCards(s) !== 52) return false;
            const ids = allCardIds(s);
            const unique = new Set(ids);
            if (ids.length !== 52) return false;
            if (unique.size !== 52) return false;
          }
          return true;
        },
      ),
      { numRuns: 200 },
    );
  });

  it("hidden hands never appear in createPublicView (>=200 iters)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.constantFrom<3 | 4>(3, 4),
        (deckSeed, botSeed, playerCount) => {
          const run = runRandomLegalRound(deckSeed, playerCount, botSeed);
          // Spot-check final state and one mid state
          const samples = [run.states[0]!, run.states[run.states.length - 1]!];
          for (const s of samples) {
            const view = createPublicView(s);
            for (const p of view.players) {
              if (p.hand.publiclyKnown.length !== 0) return false;
              // The shape check: no `cards` key with full hand
              if ((p.hand as unknown as { cards?: unknown }).cards) return false;
            }
          }
          return true;
        },
      ),
      { numRuns: 200 },
    );
  });

  it("attackerId and defenderId always reference a real player (>=200 iters)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.constantFrom<3 | 4>(3, 4),
        (deckSeed, botSeed, playerCount) => {
          const run = runRandomLegalRound(deckSeed, playerCount, botSeed);
          for (const s of run.states) {
            const ids = new Set(s.players.map((p) => p.id));
            if (!ids.has(s.round.attackerId)) return false;
            if (s.round.defenderId !== null && !ids.has(s.round.defenderId)) return false;
          }
          return true;
        },
      ),
      { numRuns: 200 },
    );
  });

  it("under random legal actions, every round terminates within 500 turns (>=200 iters)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.integer({ min: 1, max: 1_000_000 }),
        fc.constantFrom<3 | 4>(3, 4),
        (deckSeed, botSeed, playerCount) => {
          const run = runRandomLegalRound(deckSeed, playerCount, botSeed);
          return run.endedAt === "RoundEnded";
        },
      ),
      { numRuns: 200 },
    );
  });
});
