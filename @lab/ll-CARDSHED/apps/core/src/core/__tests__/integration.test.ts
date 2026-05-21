import { describe, it, expect } from "vitest";
import { runRandomLegalRound } from "./_bot.js";
import { createPrivateView } from "../rules.js";
import { setupMatch, totalCards } from "./_helpers.js";

describe("integration", () => {
  it("a scripted 3-player round runs to RoundEnded", () => {
    const run = runRandomLegalRound(1234, 3, 5678);
    expect(run.endedAt).toBe("RoundEnded");
    const final = run.states[run.states.length - 1]!;
    expect(final.winner).not.toBeNull();
    expect(totalCards(final)).toBe(52);
  });

  it("a scripted 4-player round runs to RoundEnded", () => {
    const run = runRandomLegalRound(4321, 4, 9999);
    expect(run.endedAt).toBe("RoundEnded");
    const final = run.states[run.states.length - 1]!;
    expect(final.winner).not.toBeNull();
    expect(totalCards(final)).toBe(52);
  });

  it("createPrivateView has enough info to resume — viewerHand + public state", () => {
    const s = setupMatch({ playerCount: 3, seed: 1001 });
    const viewer = s.players[0]!;
    const view = createPrivateView(s, viewer.id);
    expect(view.viewerId).toBe(viewer.id);
    expect(view.viewerHand.length).toBe(viewer.hand.length);
    expect(view.deckCount).toBe(s.deck.length);
    expect(view.round.attackerId).toBe(s.round.attackerId);
    expect(view.round.trump).toBe(s.round.trump);
  });

  it("conservation holds across every state in a full 3-player run", () => {
    const run = runRandomLegalRound(7777, 3, 8888);
    for (const s of run.states) {
      expect(totalCards(s)).toBe(52);
    }
  });

  it("conservation holds across every state in a full 4-player run", () => {
    const run = runRandomLegalRound(2222, 4, 3333);
    for (const s of run.states) {
      expect(totalCards(s)).toBe(52);
    }
  });
});
