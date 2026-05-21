import { describe, it, expect } from "vitest";
import {
  canBeat,
  getLegalActions,
  submitAttack,
  validateAttack,
} from "../rules.js";
import { buildState, c, setupMatch } from "./_helpers.js";

describe("getLegalActions", () => {
  it("returns Stop whenever defender is awaiting", () => {
    const s = setupMatch({ playerCount: 3, seed: 71 });
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const a = submitAttack(s, attacker.id, [attacker.hand[0]!.id]);
    if (!a.ok) throw new Error();
    const actions = getLegalActions(a.state, a.state.round.defenderId!);
    const stops = actions.filter((act) => act.kind === "Stop");
    expect(stops).toHaveLength(1);
  });

  it("every returned Attack passes validateAttack against the attacker's hand", () => {
    const s = setupMatch({ playerCount: 3, seed: 72 });
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const actions = getLegalActions(s, attacker.id);
    for (const action of actions) {
      if (action.kind !== "Attack") continue;
      const cards = action.cardIds.map((id) => attacker.hand.find((c) => c.id === id)!);
      const v = validateAttack(cards, attacker.hand);
      expect(v.ok).toBe(true);
    }
  });

  it("every returned Beat satisfies canBeat(attack, counter, trump)", () => {
    const s = setupMatch({ playerCount: 3, seed: 73 });
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const a = submitAttack(s, attacker.id, [attacker.hand[0]!.id]);
    if (!a.ok) throw new Error();
    const defenderId = a.state.round.defenderId!;
    const defender = a.state.players.find((p) => p.id === defenderId)!;
    const actions = getLegalActions(a.state, defenderId);
    const pa = a.state.round.pendingAttack!;
    const trump = a.state.round.trump;
    for (const action of actions) {
      if (action.kind !== "Beat") continue;
      const attack = pa.unbeatenCards.find((c) => c.id === action.attackCardId)!;
      const counter = defender.hand.find((c) => c.id === action.counterCardId)!;
      expect(canBeat(attack, counter, trump)).toBe(true);
    }
  });

  it("wrong-phase / wrong-player → empty list", () => {
    const s = buildState({ trump: 3, hands: [[c(0, 2, "x")], [c(0, 3, "y")]] });
    // It's p1's turn to attack; p2 asking for legal actions → empty
    expect(getLegalActions(s, "p2")).toEqual([]);
  });

  it("emits singleton + pair-based 3-card attacks where applicable", () => {
    const hand = [
      c(0, 7, "a"),
      c(1, 7, "b"),
      c(2, 10, "k"),
    ];
    const s = buildState({ trump: 3, hands: [hand, []] });
    const actions = getLegalActions(s, "p1");
    const attackActions = actions.filter((a) => a.kind === "Attack");
    expect(attackActions.length).toBeGreaterThan(0);
    // Includes the (7♣, 7♦, 10♥) pair+kicker
    const found = attackActions.find(
      (a) =>
        a.kind === "Attack" &&
        a.cardIds.length === 3 &&
        a.cardIds.includes(hand[0]!.id) &&
        a.cardIds.includes(hand[1]!.id) &&
        a.cardIds.includes(hand[2]!.id),
    );
    expect(found).toBeDefined();
  });
});
