import { describe, it, expect } from "vitest";
import { submitAttack, submitBeat, stopDefending } from "../rules.js";
import { buildState, c, totalCards } from "./_helpers.js";

describe("stopDefending", () => {
  it("FULL DEFENCE: defender becomes attacker, pairs go to discard", () => {
    // Deck large enough for both attacker refill AND defender refill so neither
    // triggers a deck-empty win condition.
    const s = buildState({
      trump: 3,
      hands: [[c(1, 7, "atk")], [c(1, 9, "d1")], []],
      deck: [
        c(0, 2, "t1"),
        c(0, 3, "t2"),
        c(0, 4, "t3"),
        c(0, 5, "t4"),
        c(0, 6, "t5"),
        c(0, 7, "t6"),
        c(0, 8, "t7"),
        c(0, 10, "t8"),
        c(0, 11, "t9"),
        c(0, 12, "t10"),
      ],
    });
    const a = submitAttack(s, "p1", [c(1, 7, "atk").id]);
    if (!a.ok) throw new Error();
    const b = submitBeat(a.state, "p2", c(1, 7, "atk").id, c(1, 9, "d1").id);
    if (!b.ok) throw new Error();
    const r = stopDefending(b.state, "p2");
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.state.round.attackerId).toBe("p2");
    expect(r.state.round.defenderId).toBeNull();
    expect(r.state.round.phase).toBe("AwaitingAttack");
    expect(r.state.round.pendingAttack).toBeNull();
    // Beaten pair flushed to discard
    expect(r.state.discard).toHaveLength(2);
    expect(totalCards(r.state)).toBe(
      totalCards(s) /* same set, no draws beyond setup */,
    );
  });

  it("PARTIAL DEFENCE: defender takes unbeaten cards, next attacker is leftOf(defender)", () => {
    const s = buildState({
      trump: 3,
      hands: [
        [c(1, 7, "atk"), c(2, 7, "atk2"), c(0, 5, "kick")],
        [c(0, 14, "useless")],
        [],
      ],
      // Deck big enough for both attacker refill (to 5 = 5 draws) and defender refill.
      deck: [
        c(3, 2, "t1"),
        c(3, 3, "t2"),
        c(3, 4, "t3"),
        c(3, 5, "t4"),
        c(3, 6, "t5"),
        c(3, 7, "t6"),
        c(3, 8, "t7"),
      ],
    });
    const a = submitAttack(s, "p1", [
      c(1, 7, "atk").id,
      c(2, 7, "atk2").id,
      c(0, 5, "kick").id,
    ]);
    if (!a.ok) throw new Error();
    // Defender beats none, just stops
    const r = stopDefending(a.state, "p2");
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.state.round.attackerId).toBe("p3"); // leftOf(defender p2) = p3
    expect(r.state.round.phase).toBe("AwaitingAttack");
    // Defender took 3 cards and refilled to at least 5
    const def = r.state.players.find((p) => p.id === "p2")!;
    expect(def.hand.length).toBeGreaterThanOrEqual(5);
  });

  it("PARTIAL DEFENCE then empty deck → no refill, hand may end below 5", () => {
    // Attacker must keep ≥1 card after attacking so they don't win immediately
    // when the deck is empty (checkWin = deck===0 && hand===0).
    const s = buildState({
      trump: 3,
      hands: [
        [c(1, 7, "atk"), c(2, 7, "atk2"), c(0, 5, "kick"), c(3, 9, "atk-keep")],
        [c(0, 14, "huge")],
        [],
      ],
      deck: [], // empty
    });
    const a = submitAttack(s, "p1", [
      c(1, 7, "atk").id,
      c(2, 7, "atk2").id,
      c(0, 5, "kick").id,
    ]);
    if (!a.ok) throw new Error();
    const r = stopDefending(a.state, "p2");
    if (!r.ok) throw new Error();
    const def = r.state.players.find((p) => p.id === "p2")!;
    // Took 3, started with 1 → 4 cards, deck empty so no refill.
    expect(def.hand).toHaveLength(4);
  });

  it("win triggers on full defence with deck empty + defender ends at 0 hand", () => {
    // Defender has exactly one card to beat exactly one attack, deck empty.
    // Attacker keeps a spare card so submitAttack does NOT trigger an attacker win
    // (checkWin would otherwise fire as deck===0 && hand===0 for the attacker).
    const s = buildState({
      trump: 3,
      hands: [[c(1, 7, "atk"), c(3, 5, "spare")], [c(1, 9, "d1")], []],
      deck: [],
    });
    const a = submitAttack(s, "p1", [c(1, 7, "atk").id]);
    if (!a.ok) throw new Error();
    const b = submitBeat(a.state, "p2", c(1, 7, "atk").id, c(1, 9, "d1").id);
    if (!b.ok) throw new Error();
    const r = stopDefending(b.state, "p2");
    if (!r.ok) throw new Error();
    expect(r.state.winner).toBe("p2");
    expect(r.state.round.phase).toBe("RoundEnded");
  });

  it("rejects when no pending attack", () => {
    const s = buildState({ trump: 3, hands: [[], []], phase: "AwaitingDefense" });
    s.round.defenderId = "p2";
    const r = stopDefending(s, "p2");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("NO_PENDING_ATTACK");
  });
});
