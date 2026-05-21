import { describe, it, expect } from "vitest";
import { submitAttack } from "../rules.js";
import { buildState, c, setupMatch, totalCards } from "./_helpers.js";

describe("submitAttack", () => {
  it("attacker sends 3-card pair+kicker, refills to 5, phase = AwaitingDefense", () => {
    const hand = [c(0, 7, "a"), c(1, 7, "b"), c(2, 10, "k"), c(0, 5, "x"), c(0, 6, "y")];
    const deck = [c(3, 2, "t1"), c(3, 3, "t2"), c(3, 4, "t3")];
    const s = buildState({ trump: 3, hands: [hand, [], []], deck });
    const r = submitAttack(s, "p1", [hand[0]!.id, hand[1]!.id, hand[2]!.id]);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.state.round.phase).toBe("AwaitingDefense");
    expect(r.state.round.defenderId).toBe("p2");
    expect(r.state.round.pendingAttack?.unbeatenCards).toHaveLength(3);
    const attacker = r.state.players.find((p) => p.id === "p1")!;
    expect(attacker.hand).toHaveLength(5);
  });

  it("rejects when phase is not AwaitingAttack", () => {
    const s = buildState({
      trump: 3,
      hands: [[c(0, 7, "a")], []],
      phase: "AwaitingDefense",
    });
    const r = submitAttack(s, "p1", [c(0, 7, "a").id]);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("PHASE_NOT_AWAITING_ATTACK");
  });

  it("rejects when caller is not the current attacker", () => {
    const s = buildState({
      trump: 3,
      hands: [[c(0, 7, "a")], [c(1, 7, "b")]],
    });
    const r = submitAttack(s, "p2", [c(1, 7, "b").id]);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("NOT_YOUR_TURN");
  });

  it("rejects illegal attack shape", () => {
    const hand = [c(0, 7, "a"), c(1, 7, "b"), c(2, 10, "k")];
    const s = buildState({ trump: 3, hands: [hand, []] });
    // 2-card attack — illegal size
    const r = submitAttack(s, "p1", [hand[0]!.id, hand[2]!.id]);
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.error.code).toBe("ATTACK_INVALID_SIZE");
  });

  it("preserves card conservation through the action", () => {
    const s = setupMatch({ playerCount: 3, seed: 100 });
    const totalBefore = totalCards(s);
    expect(totalBefore).toBe(52);
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const card = attacker.hand[0]!;
    const r = submitAttack(s, attacker.id, [card.id]);
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(totalCards(r.state)).toBe(52);
  });

  it("input state is not mutated", () => {
    const s = setupMatch({ playerCount: 3, seed: 101 });
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const beforeHandIds = attacker.hand.map((c) => c.id).join(",");
    submitAttack(s, attacker.id, [attacker.hand[0]!.id]);
    const after = s.players.find((p) => p.id === s.round.attackerId)!;
    expect(after.hand.map((c) => c.id).join(",")).toBe(beforeHandIds);
  });
});
