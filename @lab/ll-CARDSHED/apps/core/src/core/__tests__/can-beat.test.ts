import { describe, it, expect } from "vitest";
import { canBeat } from "../rules.js";
import type { Card, Rank, Suit } from "../types.js";

function c(suit: Suit, rank: Rank): Card {
  return { id: `${suit}-${rank}`, suit, rank };
}

const TRUMP: Suit = 3; // Spades

describe("canBeat", () => {
  it("same suit, higher rank, non-trump attack → true", () => {
    expect(canBeat(c(1, 7), c(1, 9), TRUMP)).toBe(true);
  });

  it("same suit, lower rank, non-trump attack → false", () => {
    expect(canBeat(c(1, 9), c(1, 7), TRUMP)).toBe(false);
  });

  it("same suit, equal rank → false", () => {
    expect(canBeat(c(1, 7), c(1, 7), TRUMP)).toBe(false);
  });

  it("different non-trump suits (counter non-trump) → false", () => {
    expect(canBeat(c(1, 9), c(2, 14), TRUMP)).toBe(false);
  });

  it("trump beats non-trump attack → true (any trump rank)", () => {
    expect(canBeat(c(1, 14), c(TRUMP, 2), TRUMP)).toBe(true);
  });

  it("higher trump beats trump attack → true", () => {
    expect(canBeat(c(TRUMP, 7), c(TRUMP, 9), TRUMP)).toBe(true);
  });

  it("lower trump cannot beat trump attack → false", () => {
    expect(canBeat(c(TRUMP, 9), c(TRUMP, 7), TRUMP)).toBe(false);
  });

  it("non-trump different suit vs trump attack → false", () => {
    expect(canBeat(c(TRUMP, 9), c(1, 14), TRUMP)).toBe(false);
  });
});
