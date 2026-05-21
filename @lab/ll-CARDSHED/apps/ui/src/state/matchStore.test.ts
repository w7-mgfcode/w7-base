/*
 * matchStore — engine-integration tests.
 *
 * Asserts the PRP 3 M4 acceptance gates that agent-browser cannot directly
 * introspect (zustand state from outside React):
 *   - 3 names → MatchState has 3 players, 5 cards each, 37 in deck
 *   - 4 names → MatchState has 4 players, 5 cards each, 32 in deck
 *   - < 3 or > 4 → startMatch throws
 *   - Seed is exactly preserved on MatchState.rngSeed (replayability invariant)
 */
import { beforeEach, describe, expect, it } from "vitest";
import { useMatchStore, generateMatchSeed } from "./matchStore";

describe("matchStore.startMatch", () => {
  beforeEach(() => {
    useMatchStore.getState().reset();
  });

  it("produces a 3-player MatchState from 3 names", () => {
    useMatchStore.getState().startMatch({
      players: ["Ada", "Bo", "Cy"],
      seed: 0x1234,
    });
    const m = useMatchStore.getState().match!;
    expect(m).not.toBeNull();
    expect(m.players).toHaveLength(3);
    expect(m.players.map((p) => p.name)).toEqual(["Ada", "Bo", "Cy"]);
    // 3 × 5 + 37 = 52 — conservation invariant from core
    expect(m.deck.length).toBe(52 - 3 * 5);
    for (const p of m.players) expect(p.hand).toHaveLength(5);
    expect(m.rngSeed).toBe(0x1234);
    expect(m.round.phase).toBe("AwaitingAttack");
  });

  it("produces a 4-player MatchState from 4 names", () => {
    useMatchStore.getState().startMatch({
      players: ["Ada", "Bo", "Cy", "Di"],
      seed: 0xabcd,
    });
    const m = useMatchStore.getState().match!;
    expect(m.players).toHaveLength(4);
    expect(m.deck.length).toBe(52 - 4 * 5);
    expect(m.rngSeed).toBe(0xabcd);
  });

  it("rejects fewer than 3 names", () => {
    expect(() =>
      useMatchStore.getState().startMatch({ players: ["Solo"], seed: 1 }),
    ).toThrow();
    expect(() =>
      useMatchStore.getState().startMatch({ players: ["A", "B"], seed: 1 }),
    ).toThrow();
  });

  it("rejects more than 4 names", () => {
    expect(() =>
      useMatchStore.getState().startMatch({
        players: ["A", "B", "C", "D", "E"],
        seed: 1,
      }),
    ).toThrow();
  });

  it("the same seed produces an identical MatchState (replay invariant)", () => {
    useMatchStore.getState().startMatch({
      players: ["Ada", "Bo", "Cy"],
      seed: 0xdeadbeef,
    });
    const a = useMatchStore.getState().match!;
    useMatchStore.getState().reset();
    useMatchStore.getState().startMatch({
      players: ["Ada", "Bo", "Cy"],
      seed: 0xdeadbeef,
    });
    const b = useMatchStore.getState().match!;
    // Order-sensitive deep equality
    expect(JSON.stringify(a)).toBe(JSON.stringify(b));
  });
});

describe("generateMatchSeed", () => {
  it("returns a 32-bit unsigned integer", () => {
    const s = generateMatchSeed();
    expect(Number.isInteger(s)).toBe(true);
    expect(s).toBeGreaterThanOrEqual(0);
    expect(s).toBeLessThanOrEqual(0xffffffff);
  });

  it("returns distinct values across calls (probabilistic)", () => {
    const seen = new Set<number>();
    for (let i = 0; i < 16; i++) seen.add(generateMatchSeed());
    expect(seen.size).toBeGreaterThan(8); // overwhelmingly likely all 16 differ
  });
});
