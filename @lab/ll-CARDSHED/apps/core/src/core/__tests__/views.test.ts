import { describe, it, expect } from "vitest";
import { createPrivateView, createPublicView } from "../rules.js";
import { setupMatch } from "./_helpers.js";

describe("views", () => {
  it("createPublicView strips opponent hand contents (only count)", () => {
    const s = setupMatch({ playerCount: 3, seed: 55 });
    const view = createPublicView(s);
    for (const p of view.players) {
      expect(p.hand.publiclyKnown).toHaveLength(0);
      expect(typeof p.hand.count).toBe("number");
      expect(p.hand.count).toBeGreaterThan(0);
    }
    // No Card[] on PublicPlayerInfo for opponents
    for (const p of view.players) {
      expect("count" in p.hand).toBe(true);
    }
  });

  it("createPublicView exposes deck and discard COUNT only", () => {
    const s = setupMatch({ playerCount: 3, seed: 56 });
    const view = createPublicView(s);
    expect(typeof view.deckCount).toBe("number");
    expect(typeof view.discardCount).toBe("number");
    // shape: no `deck` / `discard` keys with Card[] payload
    expect((view as unknown as { deck?: unknown }).deck).toBeUndefined();
    expect((view as unknown as { discard?: unknown }).discard).toBeUndefined();
  });

  it("createPrivateView reveals only the viewer's own hand", () => {
    const s = setupMatch({ playerCount: 3, seed: 57 });
    const view = createPrivateView(s, "p1");
    const viewer = s.players.find((p) => p.id === "p1")!;
    expect(view.viewerHand.map((c) => c.id).sort()).toEqual(
      viewer.hand.map((c) => c.id).sort(),
    );
    // Opponent hands still hidden in the public projection portion
    for (const p of view.players) {
      expect(p.hand.publiclyKnown).toHaveLength(0);
    }
  });

  it("mutating the returned view does NOT mutate state", () => {
    const s = setupMatch({ playerCount: 3, seed: 58 });
    const view = createPublicView(s);
    view.players[0]!.hand.publiclyKnown.push({ id: "ghost", suit: 0, rank: 2 });
    const fresh = createPublicView(s);
    expect(fresh.players[0]!.hand.publiclyKnown).toHaveLength(0);
  });
});
