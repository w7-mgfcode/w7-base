/*
 * matchStore — top-level match state for the hot-seat UI.
 *
 * The store wraps `@cardshed/core.startNewRound(null, seed, setup)` and stores
 * the returned `MatchState`. The seed is supplied by the caller; per PRP 3 M4
 * the caller — and not core — generates it with `crypto.getRandomValues` so the
 * core stays I/O-free.
 *
 * Persistence is intentionally NOT wired here. PRP 3 M4 warns that writing
 * MatchState to localStorage on every action risks the quota; the agreed
 * cadence is "throttle to round boundaries" and lands at M5+.
 */
import { create } from "zustand";
import { startNewRound, type MatchState, type PlayerSetup } from "@cardshed/core";

export interface StartMatchInput {
  /** Trimmed display names, in seat order. Must be length 3 or 4. */
  players: string[];
  /** 32-bit unsigned seed, supplied by the caller (e.g. crypto.getRandomValues). */
  seed: number;
}

interface MatchStoreState {
  match: MatchState | null;
  startMatch: (input: StartMatchInput) => void;
  reset: () => void;
}

export const useMatchStore = create<MatchStoreState>((set) => ({
  match: null,
  startMatch: ({ players, seed }) => {
    if (players.length !== 3 && players.length !== 4) {
      throw new Error(`matchStore: playerCount must be 3 or 4 (got ${players.length})`);
    }
    const setup: { matchId: string; players: PlayerSetup[] } = {
      matchId: `m-${seed.toString(16)}`,
      players: players.map((name, idx) => ({ id: `p${idx + 1}`, name })),
    };
    const match = startNewRound(null, seed, setup);
    set({ match });
  },
  reset: () => set({ match: null }),
}));

/**
 * Generates a 32-bit unsigned seed ONCE, outside `@cardshed/core`. The core
 * never touches `crypto`; the only seed source it accepts is a number caller-
 * supplied here. Per PRP 3 M4 "common bugs" — never use Math.random().
 */
export function generateMatchSeed(): number {
  const buf = new Uint32Array(1);
  crypto.getRandomValues(buf);
  return buf[0]!;
}
