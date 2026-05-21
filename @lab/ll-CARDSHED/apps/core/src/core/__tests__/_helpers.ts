import type { Card, MatchState, PlayerSetup, Rank, Suit } from "../types.js";
import { startNewRound } from "../rules.js";

export function setupMatch(opts: {
  playerCount: 3 | 4;
  seed: number;
  matchId?: string;
}): MatchState {
  const players: PlayerSetup[] = Array.from(
    { length: opts.playerCount },
    (_, i) => ({ id: `p${i + 1}`, name: `Player ${i + 1}` }),
  );
  return startNewRound(null, opts.seed, {
    matchId: opts.matchId ?? "m1",
    players,
  });
}

export function c(suit: Suit, rank: Rank, tag = ""): Card {
  return { id: `${suit}-${rank}-${tag || "x"}`, suit, rank };
}

// Forge a tiny custom state for surgical tests. Caller is responsible for
// supplying a 52-card union when the conservation invariant matters.
export function buildState(opts: {
  trump: Suit;
  hands: Card[][];
  deck?: Card[];
  discard?: Card[];
  phase?: MatchState["round"]["phase"];
  attackerSeat?: number;
}): MatchState {
  const playerCount = opts.hands.length;
  const players = opts.hands.map((hand, idx) => ({
    id: `p${idx + 1}`,
    name: `Player ${idx + 1}`,
    hand: hand.slice(),
    score: 0,
    isActive: true,
    seatIndex: idx,
  }));
  const attackerSeat = opts.attackerSeat ?? 0;
  const attacker = players[attackerSeat]!;
  const dealerSeat = (attackerSeat - 1 + playerCount) % playerCount;
  return {
    matchId: "test",
    roundNumber: 1,
    players,
    deck: opts.deck ?? [],
    discard: opts.discard ?? [],
    round: {
      trump: opts.trump,
      dealerId: players[dealerSeat]!.id,
      attackerId: attacker.id,
      defenderId: null,
      phase: opts.phase ?? "AwaitingAttack",
      pendingAttack: null,
    },
    winner: null,
    rngSeed: 0,
  };
}

// Total cards everywhere — for conservation checks.
export function totalCards(state: MatchState): number {
  const inHands = state.players.reduce((n, p) => n + p.hand.length, 0);
  const inDeck = state.deck.length;
  const inDiscard = state.discard.length;
  const pa = state.round.pendingAttack;
  const inPending = pa
    ? pa.unbeatenCards.length + 2 * pa.beatenPairs.length
    : 0;
  return inHands + inDeck + inDiscard + inPending;
}

export function allCardIds(state: MatchState): string[] {
  const ids: string[] = [];
  for (const p of state.players) for (const c of p.hand) ids.push(c.id);
  for (const c of state.deck) ids.push(c.id);
  for (const c of state.discard) ids.push(c.id);
  const pa = state.round.pendingAttack;
  if (pa) {
    for (const c of pa.unbeatenCards) ids.push(c.id);
    for (const bp of pa.beatenPairs) {
      ids.push(bp.attack.id, bp.counter.id);
    }
  }
  return ids;
}
