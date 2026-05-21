import { describe, it, expect } from "vitest";
import { drawToMinimum } from "../rules.js";
import { c } from "./_helpers.js";

describe("drawToMinimum", () => {
  it("draws from top (end) of deck until hand reaches target", () => {
    const hand = [c(0, 5, "a"), c(0, 6, "b")];
    const deck = [c(1, 2, "t1"), c(1, 3, "t2"), c(1, 4, "t3"), c(1, 5, "t4"), c(1, 6, "t5")];
    const r = drawToMinimum(hand, deck, 5);
    expect(r.hand).toHaveLength(5);
    // Drawn from top — last 3 of deck consumed.
    expect(r.deck).toHaveLength(2);
  });

  it("stops when deck empty even if hand below target", () => {
    const hand = [c(0, 5, "a")];
    const deck = [c(1, 2, "t1"), c(1, 3, "t2")];
    const r = drawToMinimum(hand, deck, 5);
    expect(r.hand).toHaveLength(3);
    expect(r.deck).toHaveLength(0);
  });

  it("does not draw if hand already at target", () => {
    const hand = [c(0, 5, "a"), c(0, 6, "b"), c(0, 7, "c"), c(0, 8, "d"), c(0, 9, "e")];
    const deck = [c(1, 2, "t")];
    const r = drawToMinimum(hand, deck, 5);
    expect(r.hand).toHaveLength(5);
    expect(r.deck).toHaveLength(1);
  });

  it("does not mutate input arrays", () => {
    const hand = [c(0, 5, "a")];
    const deck = [c(1, 2, "t1"), c(1, 3, "t2")];
    const handBefore = hand.length;
    const deckBefore = deck.length;
    drawToMinimum(hand, deck, 5);
    expect(hand).toHaveLength(handBefore);
    expect(deck).toHaveLength(deckBefore);
  });
});
