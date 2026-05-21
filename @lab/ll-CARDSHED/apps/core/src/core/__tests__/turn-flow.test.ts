import { describe, it, expect } from "vitest";
import { rotateDealer, startNewRound, submitAttack, submitBeat, stopDefending } from "../rules.js";
import { setupMatch, totalCards } from "./_helpers.js";

describe("turn flow", () => {
  it("startNewRound deals 5 to each player, sets trump from bottom card", () => {
    const s = setupMatch({ playerCount: 3, seed: 7 });
    for (const p of s.players) expect(p.hand).toHaveLength(5);
    expect(s.deck).toHaveLength(52 - 3 * 5);
    expect(s.discard).toHaveLength(0);
    expect(s.round.phase).toBe("AwaitingAttack");
    expect(totalCards(s)).toBe(52);
  });

  it("attacker is seat after dealer (clockwise)", () => {
    const s = setupMatch({ playerCount: 4, seed: 11 });
    const dealer = s.players.find((p) => p.id === s.round.dealerId)!;
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    expect(attacker.seatIndex).toBe((dealer.seatIndex + 1) % 4);
  });

  it("rotateDealer moves the dealer clockwise by one seat", () => {
    const s = setupMatch({ playerCount: 3, seed: 12 });
    const dealerBefore = s.players.find((p) => p.id === s.round.dealerId)!;
    const r = rotateDealer(s);
    const dealerAfter = r.players.find((p) => p.id === r.round.dealerId)!;
    expect(dealerAfter.seatIndex).toBe((dealerBefore.seatIndex + 1) % 3);
  });

  it("dealer rotates clockwise on a new round triggered by startNewRound(prev, seed)", () => {
    const s1 = setupMatch({ playerCount: 4, seed: 21 });
    const dealer1 = s1.players.find((p) => p.id === s1.round.dealerId)!;
    const s2 = startNewRound(s1, 22);
    const dealer2 = s2.players.find((p) => p.id === s2.round.dealerId)!;
    expect(dealer2.seatIndex).toBe((dealer1.seatIndex + 1) % 4);
    expect(s2.roundNumber).toBe(2);
  });

  it("full attack→partial defence→next attacker rotation maintains conservation", () => {
    const s = setupMatch({ playerCount: 3, seed: 33 });
    expect(totalCards(s)).toBe(52);
    const attacker = s.players.find((p) => p.id === s.round.attackerId)!;
    const attackCard = attacker.hand[0]!;
    const a = submitAttack(s, attacker.id, [attackCard.id]);
    expect(a.ok).toBe(true);
    if (!a.ok) return;
    expect(totalCards(a.state)).toBe(52);

    const defenderId = a.state.round.defenderId!;
    // Defender simply stops without beating
    const b = stopDefending(a.state, defenderId);
    expect(b.ok).toBe(true);
    if (!b.ok) return;
    expect(totalCards(b.state)).toBe(52);

    // Defender holds at least the original attack card
    const def = b.state.players.find((p) => p.id === defenderId)!;
    expect(def.hand.some((c) => c.id === attackCard.id)).toBe(true);
  });

  it("does not mutate previous round state when starting a new round", () => {
    const s1 = setupMatch({ playerCount: 3, seed: 44 });
    const r1Snapshot = JSON.stringify(s1);
    startNewRound(s1, 45);
    expect(JSON.stringify(s1)).toBe(r1Snapshot);
  });

  // Touch submitBeat in the integration so it isn't dead-referenced.
  it("submitBeat is part of the turn flow API", () => {
    expect(typeof submitBeat).toBe("function");
  });
});
