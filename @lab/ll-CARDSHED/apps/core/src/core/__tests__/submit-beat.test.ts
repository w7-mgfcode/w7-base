import { describe, it, expect } from "vitest";
import { submitAttack, submitBeat } from "../rules.js";
import { buildState, c } from "./_helpers.js";

describe("submitBeat", () => {
  function attackedState() {
    // Attacker hand minus the cards they used (single card 7♦)
    // After submitAttack, attacker refills to 5 from deck.
    const attackerHand = [c(1, 7, "atk")];
    const defenderHand = [c(1, 9, "d1"), c(0, 9, "d2"), c(3, 2, "trump-low")];
    const deck = [c(0, 2, "t1"), c(0, 3, "t2"), c(0, 4, "t3"), c(0, 5, "t4")];
    const s = buildState({
      trump: 3,
      hands: [attackerHand, defenderHand, []],
      deck,
    });
    const r = submitAttack(s, "p1", [attackerHand[0]!.id]);
    if (!r.ok) throw new Error("setup attack failed");
    return r.state;
  }

  it("moves the attack from unbeatenCards into beatenPairs", () => {
    const s = attackedState();
    const r = submitBeat(s, "p2", c(1, 7, "atk").id, c(1, 9, "d1").id);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.state.round.pendingAttack?.unbeatenCards).toHaveLength(0);
    expect(r.state.round.pendingAttack?.beatenPairs).toHaveLength(1);
  });

  it("transitions phase to Resolving when all attacks beaten", () => {
    const s = attackedState();
    const r = submitBeat(s, "p2", c(1, 7, "atk").id, c(1, 9, "d1").id);
    if (!r.ok) throw new Error();
    expect(r.state.round.phase).toBe("Resolving");
  });

  it("rejects when counter cannot beat attack", () => {
    // For BEAT_ILLEGAL we need a strictly losing combo: e.g. attacker has 7♦ in unbeatenCards;
    // counter 6♥ — different non-trump suit, not trump → illegal.
    const sBad = buildState({
      trump: 3,
      hands: [[c(1, 7, "atk")], [c(2, 6, "bad")], []],
      deck: [c(0, 2, "t1"), c(0, 3, "t2"), c(0, 4, "t3"), c(0, 5, "t4")],
    });
    const a = submitAttack(sBad, "p1", [c(1, 7, "atk").id]);
    if (!a.ok) throw new Error();
    const r = submitBeat(a.state, "p2", c(1, 7, "atk").id, c(2, 6, "bad").id);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("BEAT_ILLEGAL");
  });

  it("rejects when not in defense phase", () => {
    const s = buildState({ trump: 3, hands: [[], []], phase: "AwaitingAttack" });
    const r = submitBeat(s, "p2", "any", "any");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("PHASE_NOT_DEFENSE");
  });

  it("rejects when caller is not the defender", () => {
    const s = attackedState();
    const r = submitBeat(s, "p3", c(1, 7, "atk").id, "anything");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("NOT_YOUR_TURN");
  });

  it("rejects when counter card not in defender's hand", () => {
    const s = attackedState();
    const r = submitBeat(s, "p2", c(1, 7, "atk").id, "ghost-card-id");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("BEAT_CARD_NOT_OWNED");
  });

  it("rejects when attack card is not pending", () => {
    const s = attackedState();
    const r = submitBeat(s, "p2", "ghost-attack", c(1, 9, "d1").id);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("BEAT_TARGET_NOT_FOUND");
  });
});
