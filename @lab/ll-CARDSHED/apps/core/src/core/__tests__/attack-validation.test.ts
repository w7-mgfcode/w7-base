import { describe, it, expect } from "vitest";
import { validateAttack } from "../rules.js";
import type { Card, Rank, Suit } from "../types.js";

function c(suit: Suit, rank: Rank, tag = "x"): Card {
  return { id: `${suit}-${rank}-${tag}`, suit, rank };
}

describe("validateAttack", () => {
  const hand: Card[] = [
    c(0, 7, "a"),
    c(1, 7, "b"),
    c(2, 7, "c"),
    c(3, 7, "d"),
    c(0, 9, "e"),
    c(1, 9, "f"),
    c(2, 10, "g"),
    c(0, 5, "h"),
  ];

  it("1-card attack is valid", () => {
    expect(validateAttack([hand[0]!], hand).ok).toBe(true);
  });

  it("3-card pair + kicker is valid", () => {
    expect(validateAttack([hand[0]!, hand[1]!, hand[6]!], hand).ok).toBe(true);
  });

  it("5-card two pairs of distinct ranks + kicker is valid", () => {
    // 7♣ 7♦ + 9♣ 9♦ + 10♥
    expect(
      validateAttack([hand[0]!, hand[1]!, hand[4]!, hand[5]!, hand[6]!], hand).ok,
    ).toBe(true);
  });

  it("rejects 0/2/4/6 cards", () => {
    for (const size of [0, 2, 4, 6]) {
      const subset = hand.slice(0, size);
      const r = validateAttack(subset, hand);
      expect(r.ok).toBe(false);
      if (!r.ok) expect(r.error.code).toBe("ATTACK_INVALID_SIZE");
    }
  });

  it("3-card with no pair", () => {
    const r = validateAttack([hand[0]!, hand[6]!, hand[7]!], hand);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_NO_PAIR");
  });

  it("5-card with only one pair (trips + 2 unrelated)", () => {
    // three 7s (one pair-rank) + 10 + 5 — only one distinct pair-rank
    const r = validateAttack(
      [hand[0]!, hand[1]!, hand[2]!, hand[6]!, hand[7]!],
      hand,
    );
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_NO_TWO_PAIRS");
  });

  it("5-card with quad (4 same rank) + kicker — only ONE distinct pair-rank", () => {
    const r = validateAttack(
      [hand[0]!, hand[1]!, hand[2]!, hand[3]!, hand[6]!],
      hand,
    );
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_NO_TWO_PAIRS");
  });

  it("cards not in hand → ATTACK_CARD_NOT_OWNED", () => {
    const r = validateAttack([c(0, 2, "ghost")], hand);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_CARD_NOT_OWNED");
  });

  it("duplicate card ids → ATTACK_DUPLICATE_CARD", () => {
    const r = validateAttack([hand[0]!, hand[0]!, hand[1]!], hand);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_DUPLICATE_CARD");
  });
});
