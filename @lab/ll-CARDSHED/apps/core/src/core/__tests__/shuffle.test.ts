import { describe, it, expect } from "vitest";
import { createDeck, shuffleDeck, determineTrumpFromBottomCard } from "../rules.js";

describe("shuffleDeck", () => {
  it("is reproducible for the same seed", () => {
    const a = shuffleDeck(createDeck(), 42);
    const b = shuffleDeck(createDeck(), 42);
    expect(a.map((c) => c.id)).toEqual(b.map((c) => c.id));
  });

  it("differs across different seeds", () => {
    const a = shuffleDeck(createDeck(), 42);
    const b = shuffleDeck(createDeck(), 43);
    expect(a.map((c) => c.id)).not.toEqual(b.map((c) => c.id));
  });

  it("preserves the multiset of 52 cards", () => {
    const d = createDeck();
    const s = shuffleDeck(d, 42);
    expect(s).toHaveLength(52);
    const dIds = new Set(d.map((c) => c.id));
    const sIds = new Set(s.map((c) => c.id));
    expect(dIds).toEqual(sIds);
  });

  it("does not mutate input", () => {
    const d = createDeck();
    const before = d.map((c) => c.id).join(",");
    shuffleDeck(d, 42);
    const after = d.map((c) => c.id).join(",");
    expect(after).toBe(before);
  });

  it("freezes input safe — Object.freeze does not break shuffle", () => {
    const d = Object.freeze(createDeck().slice());
    const s = shuffleDeck(d as unknown as ReturnType<typeof createDeck>, 7);
    expect(s).toHaveLength(52);
  });

  it("bottom card determines trump", () => {
    const s = shuffleDeck(createDeck(), 99);
    const trump = determineTrumpFromBottomCard(s);
    expect(trump).toBe(s[0]!.suit);
  });

  it("bottom trump card stays in the deck (drawable)", () => {
    const s = shuffleDeck(createDeck(), 99);
    // bottom present at index 0
    expect(s).toHaveLength(52);
    expect(s[0]).toBeDefined();
  });

  it("byte-identical fixture for shuffleDeck(createDeck(), 42)", () => {
    const s = shuffleDeck(createDeck(), 42);
    // Cross-runtime determinism check: record once, then pin.
    const fingerprint = s.map((c) => c.id).join(",");
    expect(fingerprint).toMatchSnapshot();
  });
});
