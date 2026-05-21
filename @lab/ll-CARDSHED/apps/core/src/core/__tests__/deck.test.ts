import { describe, it, expect } from "vitest";
import { createDeck, startNewRound } from "../rules.js";

describe("createDeck", () => {
  it("returns 52 unique cards", () => {
    const deck = createDeck();
    expect(deck).toHaveLength(52);
    const ids = new Set(deck.map((c) => c.id));
    expect(ids.size).toBe(52);
  });

  it("has 4 suits × 13 ranks", () => {
    const deck = createDeck();
    const bySuit = new Map<number, number>();
    for (const c of deck) bySuit.set(c.suit, (bySuit.get(c.suit) ?? 0) + 1);
    expect(bySuit.get(0)).toBe(13);
    expect(bySuit.get(1)).toBe(13);
    expect(bySuit.get(2)).toBe(13);
    expect(bySuit.get(3)).toBe(13);
  });

  it("contains every rank 2..14 in each suit", () => {
    const deck = createDeck();
    for (let s = 0; s < 4; s++) {
      for (let r = 2; r <= 14; r++) {
        const has = deck.find((c) => c.suit === s && c.rank === r);
        expect(has).toBeDefined();
      }
    }
  });

  it("ids are unsalted by default — stable format {letter}-{rank}-{slotHex}", () => {
    const ids = createDeck().map((c) => c.id);
    expect(ids[0]).toBe("C-2-00");
    expect(ids[51]).toBe("S-14-33");
    // No suffix beyond the slot hex
    for (const id of ids) expect(id.split("-")).toHaveLength(3);
  });

  it("createDeck(salt) appends a base36 salt suffix", () => {
    const salt = 42;
    const ids = createDeck(salt).map((c) => c.id);
    const expectedSuffix = salt.toString(36); // "1c"
    expect(ids[0]).toBe(`C-2-00-${expectedSuffix}`);
    expect(ids[51]).toBe(`S-14-33-${expectedSuffix}`);
    for (const id of ids) expect(id.split("-")).toHaveLength(4);
  });

  it("different salts produce disjoint id sets", () => {
    const a = new Set(createDeck(42).map((c) => c.id));
    const b = new Set(createDeck(43).map((c) => c.id));
    let overlap = 0;
    for (const id of a) if (b.has(id)) overlap++;
    expect(overlap).toBe(0);
  });

  it("startNewRound produces salted ids that uniquely tag the round", () => {
    // Verified by reading any card from the produced deck/hand state.
    // Round 1 seed 100, round 2 seed 200 → distinct salts → no id overlap.
    const r1 = startNewRound(null, 100, {
      matchId: "m1",
      players: [
        { id: "p1", name: "A" },
        { id: "p2", name: "B" },
        { id: "p3", name: "C" },
      ],
    });
    const r2 = startNewRound(r1, 200);
    const r1Ids = new Set([
      ...r1.players.flatMap((p) => p.hand.map((c) => c.id)),
      ...r1.deck.map((c) => c.id),
    ]);
    const r2Ids = new Set([
      ...r2.players.flatMap((p) => p.hand.map((c) => c.id)),
      ...r2.deck.map((c) => c.id),
    ]);
    expect(r1Ids.size).toBe(52);
    expect(r2Ids.size).toBe(52);
    let overlap = 0;
    for (const id of r1Ids) if (r2Ids.has(id)) overlap++;
    expect(overlap).toBe(0);
  });
});
