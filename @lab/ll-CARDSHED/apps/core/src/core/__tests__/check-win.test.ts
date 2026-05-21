import { describe, it, expect } from "vitest";
import { checkWin } from "../rules.js";
import { buildState, c } from "./_helpers.js";

describe("checkWin", () => {
  it("returns true only when deck is empty AND hand is empty", () => {
    const s = buildState({ trump: 3, hands: [[], [c(0, 2, "a")], [c(0, 3, "b")]], deck: [] });
    expect(checkWin(s, "p1")).toBe(true);
    expect(checkWin(s, "p2")).toBe(false);
  });

  it("returns false when deck non-empty even if hand empty", () => {
    const s = buildState({ trump: 3, hands: [[], [c(0, 3, "b")]], deck: [c(0, 2, "t")] });
    expect(checkWin(s, "p1")).toBe(false);
  });

  it("returns false when hand non-empty even if deck empty", () => {
    const s = buildState({ trump: 3, hands: [[c(0, 3, "h")], []], deck: [] });
    expect(checkWin(s, "p1")).toBe(false);
  });
});
