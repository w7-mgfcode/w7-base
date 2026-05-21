import { shuffleInPlaceCopy } from "./prng.js";
import type {
  Action,
  ActionResult,
  BeatenPair,
  Card,
  GameEvent,
  MatchState,
  PendingAttack,
  Player,
  PlayerSetup,
  PrivatePlayerView,
  PublicGameView,
  Rank,
  RoundState,
  Suit,
  ValidationError,
} from "./types.js";

// ─── Helpers ─────────────────────────────────────────────────────────────
const SUIT_LETTERS: Record<Suit, string> = { 0: "C", 1: "D", 2: "H", 3: "S" };

function err(code: string, message: string): { ok: false; error: ValidationError } {
  return { ok: false, error: { code, message } };
}

function errResult(code: string, message: string): ActionResult {
  return { ok: false, error: { code, message } };
}

function clone<T>(x: T): T {
  return structuredClone(x);
}

function findPlayer(state: MatchState, id: string): Player {
  const p = state.players.find((pp) => pp.id === id);
  if (!p) throw new Error(`INVARIANT: player ${id} not found`);
  return p;
}

function leftOf(state: MatchState, id: string): string {
  const p = findPlayer(state, id);
  const next = (p.seatIndex + 1) % state.players.length;
  const np = state.players.find((pp) => pp.seatIndex === next);
  if (!np) throw new Error(`INVARIANT: seat ${next} not found`);
  return np.id;
}

export function pendingAttackCardCount(pa: PendingAttack | null): number {
  if (!pa) return 0;
  return pa.unbeatenCards.length + 2 * pa.beatenPairs.length;
}

// ─── Deck / setup ────────────────────────────────────────────────────────

// Canonical 52-card deck, suit-major, rank-ascending.
// id format:
//   - createDeck()      → "{suitLetter}-{rank}-{slotHex}"           e.g. "S-14-33"
//   - createDeck(salt)  → "{suitLetter}-{rank}-{slotHex}-{saltB36}" e.g. "S-14-33-1c"
// Salt is opaque (base36 of (salt >>> 0)). Use it to disambiguate cards across
// matches or rounds in long-running sessions. Card.id is OPAQUE — do NOT parse
// to extract suit/rank; always use card.suit / card.rank.
export function createDeck(salt?: number): Card[] {
  const out: Card[] = [];
  const suffix = salt === undefined ? "" : `-${(salt >>> 0).toString(36)}`;
  for (let s = 0 as Suit; s <= 3; s = ((s + 1) as Suit)) {
    for (let r = 2 as Rank; r <= 14; r = ((r + 1) as Rank)) {
      const idx = s * 13 + (r - 2);
      out.push({
        id: `${SUIT_LETTERS[s]}-${r}-${idx.toString(16).padStart(2, "0")}${suffix}`,
        suit: s,
        rank: r,
      });
    }
    if (s === 3) break; // guard the cast
  }
  return out;
}

export function shuffleDeck(deck: Card[], seed: number): Card[] {
  return shuffleInPlaceCopy(deck, seed);
}

export function determineTrumpFromBottomCard(deck: Card[]): Suit {
  const bottom = deck[0];
  if (!bottom) throw new Error("INVARIANT: deck is empty");
  return bottom.suit;
}

// Deals 5 cards to each player by popping from the TOP (deck.pop()).
// Bottom card (trump face) remains and will be drawn last.
export function dealInitialHands(
  deck: Card[],
  playerCount: 3 | 4,
): { hands: Card[][]; deck: Card[] } {
  const remaining = deck.slice();
  const hands: Card[][] = Array.from({ length: playerCount }, () => []);
  for (let round = 0; round < 5; round++) {
    for (let p = 0; p < playerCount; p++) {
      const c = remaining.pop();
      if (!c) throw new Error("INVARIANT: deck exhausted during initial deal");
      hands[p]!.push(c);
    }
  }
  return { hands, deck: remaining };
}

// startNewRound — initial setup OR rotate dealer + reshuffle + redeal.
export function startNewRound(
  prev: MatchState | null,
  seed: number,
  setup?: { matchId: string; players: PlayerSetup[] },
): MatchState {
  let players: Player[];
  let matchId: string;
  let roundNumber: number;
  let dealerSeat: number;

  if (prev === null) {
    if (!setup) {
      throw new Error("INVARIANT: startNewRound(null, ...) requires setup with players");
    }
    if (setup.players.length !== 3 && setup.players.length !== 4) {
      throw new Error("INVARIANT: playerCount must be 3 or 4");
    }
    players = setup.players.map((ps, idx) => ({
      id: ps.id,
      name: ps.name,
      hand: [],
      score: 0,
      isActive: true,
      seatIndex: idx,
    }));
    matchId = setup.matchId;
    roundNumber = 1;
    dealerSeat = 0;
  } else {
    matchId = prev.matchId;
    roundNumber = prev.roundNumber + 1;
    const prevDealer = prev.players.find((p) => p.id === prev.round.dealerId);
    if (!prevDealer) throw new Error("INVARIANT: previous dealer not found");
    dealerSeat = (prevDealer.seatIndex + 1) % prev.players.length;
    players = prev.players.map((p) => ({
      ...p,
      hand: [],
      isActive: true,
    }));
  }

  const playerCount = players.length as 3 | 4;
  // Salt card ids with the round seed so each round's cards are uniquely tagged.
  const shuffled = shuffleDeck(createDeck(seed), seed);
  const { hands, deck } = dealInitialHands(shuffled, playerCount);

  for (let i = 0; i < playerCount; i++) {
    players[i]!.hand = hands[i]!;
  }

  const trump = determineTrumpFromBottomCard(shuffled);
  const dealer = players.find((p) => p.seatIndex === dealerSeat)!;
  const attackerSeat = (dealerSeat + 1) % playerCount;
  const attacker = players.find((p) => p.seatIndex === attackerSeat)!;

  const round: RoundState = {
    trump,
    dealerId: dealer.id,
    attackerId: attacker.id,
    defenderId: null,
    phase: "AwaitingAttack",
    pendingAttack: null,
  };

  return {
    matchId,
    roundNumber,
    players,
    deck,
    discard: [],
    round,
    winner: null,
    rngSeed: seed,
  };
}

// ─── Attack validation ───────────────────────────────────────────────────

export function validateAttack(
  cards: Card[],
  hand: Card[],
): { ok: true } | { ok: false; error: ValidationError } {
  if (![1, 3, 5].includes(cards.length)) {
    return err(
      "ATTACK_INVALID_SIZE",
      `Attack must be 1/3/5 cards, got ${cards.length}`,
    );
  }
  const seenIds = new Set<string>();
  for (const c of cards) {
    if (seenIds.has(c.id)) {
      return err("ATTACK_DUPLICATE_CARD", `Duplicate card ${c.id}`);
    }
    seenIds.add(c.id);
    if (!hand.find((h) => h.id === c.id)) {
      return err("ATTACK_CARD_NOT_OWNED", `Card ${c.id} not in hand`);
    }
  }

  if (cards.length === 1) return { ok: true };

  const byRank = new Map<Rank, number>();
  for (const c of cards) byRank.set(c.rank, (byRank.get(c.rank) ?? 0) + 1);
  const distinctPairRanks = [...byRank.values()].filter((n) => n >= 2).length;

  if (cards.length === 3) {
    if (distinctPairRanks === 0) {
      return err("ATTACK_NO_PAIR", "3-card attack needs a pair");
    }
    return { ok: true };
  }

  // cards.length === 5
  if (distinctPairRanks < 2) {
    return err(
      "ATTACK_NO_TWO_PAIRS",
      "5-card attack needs two pairs of DISTINCT ranks",
    );
  }
  return { ok: true };
}

// ─── canBeat ─────────────────────────────────────────────────────────────

export function canBeat(attack: Card, counter: Card, trump: Suit): boolean {
  if (attack.suit === trump) {
    return counter.suit === trump && counter.rank > attack.rank;
  }
  if (counter.suit === trump) return true;
  return counter.suit === attack.suit && counter.rank > attack.rank;
}

// ─── drawToMinimum ───────────────────────────────────────────────────────

export function drawToMinimum(
  hand: Card[],
  deck: Card[],
  target: number,
): { hand: Card[]; deck: Card[] } {
  const h = hand.slice();
  const d = deck.slice();
  while (h.length < target && d.length > 0) {
    const c = d.pop()!;
    h.push(c);
  }
  return { hand: h, deck: d };
}

// ─── checkWin ────────────────────────────────────────────────────────────

export function checkWin(state: MatchState, playerId: string): boolean {
  const p = findPlayer(state, playerId);
  return state.deck.length === 0 && p.hand.length === 0;
}

// ─── submitAttack ────────────────────────────────────────────────────────

export function submitAttack(
  state: MatchState,
  playerId: string,
  cardIds: string[],
): ActionResult {
  if (state.round.phase !== "AwaitingAttack") {
    return errResult("PHASE_NOT_AWAITING_ATTACK", `Phase is ${state.round.phase}`);
  }
  if (state.round.attackerId !== playerId) {
    return errResult("NOT_YOUR_TURN", `${playerId} is not the attacker`);
  }
  const attacker = findPlayer(state, playerId);

  // Resolve cardIds against attacker's hand (preserving order from cardIds for stable replay).
  const cards: Card[] = [];
  for (const cid of cardIds) {
    const card = attacker.hand.find((c) => c.id === cid);
    if (!card) {
      return errResult("ATTACK_CARD_NOT_OWNED", `Card ${cid} not in hand`);
    }
    cards.push(card);
  }
  const v = validateAttack(cards, attacker.hand);
  if (!v.ok) return { ok: false, error: v.error };

  const next = clone(state);
  const nAttacker = findPlayer(next, playerId);
  const idSet = new Set(cardIds);
  nAttacker.hand = nAttacker.hand.filter((c) => !idSet.has(c.id));
  const defenderId = leftOf(next, playerId);
  next.round.pendingAttack = {
    attackerId: playerId,
    defenderId,
    unbeatenCards: cards.map((c) => ({ ...c })),
    beatenPairs: [],
  };

  // Refill attacker BEFORE win check.
  const before = nAttacker.hand.length;
  const refill = drawToMinimum(nAttacker.hand, next.deck, 5);
  const drawn = refill.hand.length - before;
  nAttacker.hand = refill.hand;
  next.deck = refill.deck;

  const events: GameEvent[] = [
    { type: "AttackSubmitted", attackerId: playerId, defenderId, cardIds },
  ];
  if (drawn > 0) events.push({ type: "CardsDrawn", playerId, count: drawn });

  if (checkWin(next, playerId)) {
    next.round.phase = "RoundEnded";
    next.winner = playerId;
    events.push({ type: "RoundWon", winnerId: playerId });
    return { ok: true, state: next, events };
  }

  next.round.phase = "AwaitingDefense";
  next.round.defenderId = defenderId;
  events.push({ type: "TurnChanged", nextAttackerId: playerId, phase: next.round.phase });
  return { ok: true, state: next, events };
}

// ─── submitBeat ──────────────────────────────────────────────────────────

export function submitBeat(
  state: MatchState,
  defenderId: string,
  attackCardId: string,
  counterCardId: string,
): ActionResult {
  if (
    state.round.phase !== "AwaitingDefense" &&
    state.round.phase !== "Resolving"
  ) {
    return errResult("PHASE_NOT_DEFENSE", `Phase is ${state.round.phase}`);
  }
  if (state.round.defenderId !== defenderId) {
    return errResult("NOT_YOUR_TURN", `${defenderId} is not the defender`);
  }
  const pa = state.round.pendingAttack;
  if (!pa) return errResult("NO_PENDING_ATTACK", "No pending attack to beat");

  const attack = pa.unbeatenCards.find((c) => c.id === attackCardId);
  if (!attack) {
    return errResult(
      "BEAT_TARGET_NOT_FOUND",
      `${attackCardId} is not an unbeaten attack card`,
    );
  }
  const defender = findPlayer(state, defenderId);
  const counter = defender.hand.find((c) => c.id === counterCardId);
  if (!counter) {
    return errResult(
      "BEAT_CARD_NOT_OWNED",
      `${counterCardId} not in defender's hand`,
    );
  }
  if (!canBeat(attack, counter, state.round.trump)) {
    return errResult("BEAT_ILLEGAL", `${counterCardId} cannot beat ${attackCardId}`);
  }

  const next = clone(state);
  const nDefender = findPlayer(next, defenderId);
  nDefender.hand = nDefender.hand.filter((c) => c.id !== counterCardId);
  const npa = next.round.pendingAttack!;
  npa.unbeatenCards = npa.unbeatenCards.filter((c) => c.id !== attackCardId);
  npa.beatenPairs.push({ attack: { ...attack }, counter: { ...counter } });
  next.round.phase =
    npa.unbeatenCards.length === 0 ? "Resolving" : "AwaitingDefense";

  return {
    ok: true,
    state: next,
    events: [{ type: "CardBeaten", defenderId, attackCardId, counterCardId }],
  };
}

// ─── stopDefending ───────────────────────────────────────────────────────

export function stopDefending(
  state: MatchState,
  defenderId: string,
): ActionResult {
  if (
    state.round.phase !== "AwaitingDefense" &&
    state.round.phase !== "Resolving"
  ) {
    return errResult("PHASE_NOT_DEFENSE", `Phase is ${state.round.phase}`);
  }
  if (state.round.defenderId !== defenderId) {
    return errResult("NOT_YOUR_TURN", `${defenderId} is not the defender`);
  }
  const pa = state.round.pendingAttack;
  if (!pa) return errResult("NO_PENDING_ATTACK", "No pending attack to stop");

  const next = clone(state);
  const nDefender = findPlayer(next, defenderId);
  const npa = next.round.pendingAttack!;
  const events: GameEvent[] = [];

  if (npa.unbeatenCards.length === 0) {
    // FULL DEFENCE: flush all beaten pairs to discard, defender becomes attacker.
    for (const { attack, counter } of npa.beatenPairs) {
      next.discard.push(attack, counter);
    }
    events.push({
      type: "FullDefense",
      defenderId,
      discardedPairs: npa.beatenPairs.length,
    });

    const before = nDefender.hand.length;
    const refill = drawToMinimum(nDefender.hand, next.deck, 5);
    const drawn = refill.hand.length - before;
    nDefender.hand = refill.hand;
    next.deck = refill.deck;
    if (drawn > 0)
      events.push({ type: "CardsDrawn", playerId: defenderId, count: drawn });

    if (checkWin(next, defenderId)) {
      next.round.phase = "RoundEnded";
      next.winner = defenderId;
      next.round.pendingAttack = null;
      events.push({ type: "RoundWon", winnerId: defenderId });
      return { ok: true, state: next, events };
    }

    next.round.attackerId = defenderId;
    next.round.defenderId = null;
    next.round.pendingAttack = null;
    next.round.phase = "AwaitingAttack";
    events.push({
      type: "TurnChanged",
      nextAttackerId: defenderId,
      phase: "AwaitingAttack",
    });
    return { ok: true, state: next, events };
  }

  // PARTIAL / NO DEFENCE: defender takes unbeaten cards into hand;
  // beaten pairs also go to discard (already-defeated cards leave play).
  const taken = npa.unbeatenCards.slice();
  for (const c of taken) nDefender.hand.push(c);
  for (const { attack, counter } of npa.beatenPairs) {
    next.discard.push(attack, counter);
  }
  events.push({
    type: "DefenseStopped",
    defenderId,
    takenCardIds: taken.map((c) => c.id),
  });

  const before = nDefender.hand.length;
  const refill = drawToMinimum(nDefender.hand, next.deck, 5);
  const drawn = refill.hand.length - before;
  nDefender.hand = refill.hand;
  next.deck = refill.deck;
  if (drawn > 0)
    events.push({ type: "CardsDrawn", playerId: defenderId, count: drawn });

  if (checkWin(next, defenderId)) {
    next.round.phase = "RoundEnded";
    next.winner = defenderId;
    next.round.pendingAttack = null;
    events.push({ type: "RoundWon", winnerId: defenderId });
    return { ok: true, state: next, events };
  }

  const nextAttacker = leftOf(next, defenderId);
  next.round.attackerId = nextAttacker;
  next.round.defenderId = null;
  next.round.pendingAttack = null;
  next.round.phase = "AwaitingAttack";
  events.push({
    type: "TurnChanged",
    nextAttackerId: nextAttacker,
    phase: "AwaitingAttack",
  });
  return { ok: true, state: next, events };
}

// ─── advanceTurn* (thin pure helpers around stopDefending semantics) ─────

export function advanceTurnAfterFullDefense(state: MatchState): MatchState {
  if (!state.round.defenderId) {
    throw new Error("INVARIANT: cannot advance after full defense with no defender");
  }
  const r = stopDefending(state, state.round.defenderId);
  if (!r.ok) throw new Error(`INVARIANT: advanceTurnAfterFullDefense failed: ${r.error.code}`);
  return r.state;
}

export function advanceTurnAfterPartialDefense(state: MatchState): MatchState {
  if (!state.round.defenderId) {
    throw new Error("INVARIANT: cannot advance after partial defense with no defender");
  }
  const r = stopDefending(state, state.round.defenderId);
  if (!r.ok) throw new Error(`INVARIANT: advanceTurnAfterPartialDefense failed: ${r.error.code}`);
  return r.state;
}

export function rotateDealer(state: MatchState): MatchState {
  const next = clone(state);
  const dealer = findPlayer(next, next.round.dealerId);
  const nextDealerSeat = (dealer.seatIndex + 1) % next.players.length;
  const newDealer = next.players.find((p) => p.seatIndex === nextDealerSeat);
  if (!newDealer) throw new Error("INVARIANT: next dealer seat not found");
  next.round.dealerId = newDealer.id;
  return next;
}

// ─── getLegalActions ─────────────────────────────────────────────────────

export function getLegalActions(state: MatchState, playerId: string): Action[] {
  const phase = state.round.phase;

  if (phase === "AwaitingAttack" && state.round.attackerId === playerId) {
    const attacker = state.players.find((p) => p.id === playerId);
    if (!attacker) return [];
    return enumerateAttacks(attacker.hand, playerId);
  }

  if (
    (phase === "AwaitingDefense" || phase === "Resolving") &&
    state.round.defenderId === playerId
  ) {
    const defender = state.players.find((p) => p.id === playerId);
    if (!defender || !state.round.pendingAttack) return [];
    const out: Action[] = [];
    for (const attack of state.round.pendingAttack.unbeatenCards) {
      for (const counter of defender.hand) {
        if (canBeat(attack, counter, state.round.trump)) {
          out.push({
            kind: "Beat",
            playerId,
            attackCardId: attack.id,
            counterCardId: counter.id,
          });
        }
      }
    }
    out.push({ kind: "Stop", playerId });
    return out;
  }

  return [];
}

function enumerateAttacks(hand: Card[], playerId: string): Action[] {
  const seen = new Set<string>();
  const out: Action[] = [];

  const push = (cardIds: string[]) => {
    const key = [...cardIds].sort().join(",");
    if (seen.has(key)) return;
    seen.add(key);
    out.push({ kind: "Attack", playerId, cardIds });
  };

  // 1-card attacks
  for (const c of hand) push([c.id]);

  // Group by rank for pair detection.
  const byRank = new Map<Rank, Card[]>();
  for (const c of hand) {
    const arr = byRank.get(c.rank) ?? [];
    arr.push(c);
    byRank.set(c.rank, arr);
  }
  const ranksWithPairs = [...byRank.entries()].filter(([, cs]) => cs.length >= 2);

  // 3-card attacks: pick two cards of one rank as the pair, then any third card as kicker.
  for (const [rank, cs] of ranksWithPairs) {
    for (let i = 0; i < cs.length; i++) {
      for (let j = i + 1; j < cs.length; j++) {
        for (const kicker of hand) {
          if (kicker.rank === rank) continue; // kicker must NOT be of pair rank (else it'd be a triple, still a "pair + kicker" — rules don't ban this, but we'll allow it)
          push([cs[i]!.id, cs[j]!.id, kicker.id]);
        }
        // Allow kicker of same rank too (still passes validateAttack — the pair exists).
        for (const kicker of cs) {
          if (kicker.id === cs[i]!.id || kicker.id === cs[j]!.id) continue;
          push([cs[i]!.id, cs[j]!.id, kicker.id]);
        }
      }
    }
  }

  // 5-card attacks: two pairs of DISTINCT ranks + a kicker.
  for (let a = 0; a < ranksWithPairs.length; a++) {
    for (let b = a + 1; b < ranksWithPairs.length; b++) {
      const [rA, csA] = ranksWithPairs[a]!;
      const [rB, csB] = ranksWithPairs[b]!;
      for (let i = 0; i < csA.length; i++) {
        for (let j = i + 1; j < csA.length; j++) {
          for (let k = 0; k < csB.length; k++) {
            for (let l = k + 1; l < csB.length; l++) {
              for (const kicker of hand) {
                if (kicker.rank === rA && (kicker.id === csA[i]!.id || kicker.id === csA[j]!.id))
                  continue;
                if (kicker.rank === rB && (kicker.id === csB[k]!.id || kicker.id === csB[l]!.id))
                  continue;
                push([csA[i]!.id, csA[j]!.id, csB[k]!.id, csB[l]!.id, kicker.id]);
              }
            }
          }
        }
      }
    }
  }

  return out;
}

// ─── Views ───────────────────────────────────────────────────────────────

export function createPublicView(
  state: MatchState,
  _viewerId?: string,
): PublicGameView {
  return {
    matchId: state.matchId,
    roundNumber: state.roundNumber,
    players: state.players.map((p) => ({
      id: p.id,
      name: p.name,
      seatIndex: p.seatIndex,
      score: p.score,
      isActive: p.isActive,
      hand: { ownerId: p.id, count: p.hand.length, publiclyKnown: [] },
    })),
    deckCount: state.deck.length,
    discardCount: state.discard.length,
    round: {
      trump: state.round.trump,
      dealerId: state.round.dealerId,
      attackerId: state.round.attackerId,
      defenderId: state.round.defenderId,
      phase: state.round.phase,
      pendingAttack: state.round.pendingAttack
        ? {
            attackerId: state.round.pendingAttack.attackerId,
            defenderId: state.round.pendingAttack.defenderId,
            unbeatenCards: state.round.pendingAttack.unbeatenCards.map((c) => ({
              ...c,
            })),
            beatenPairs: state.round.pendingAttack.beatenPairs.map(
              (bp): BeatenPair => ({
                attack: { ...bp.attack },
                counter: { ...bp.counter },
              }),
            ),
          }
        : null,
    },
    winner: state.winner,
  };
}

export function createPrivateView(
  state: MatchState,
  viewerId: string,
): PrivatePlayerView {
  const pub = createPublicView(state, viewerId);
  const viewer = findPlayer(state, viewerId);
  return { ...pub, viewerId, viewerHand: viewer.hand.map((c) => ({ ...c })) };
}
