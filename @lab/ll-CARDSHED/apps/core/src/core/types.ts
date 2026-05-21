// Shared Contract — frozen, byte-identical to PRP 3.
export type Suit = 0 | 1 | 2 | 3; // Clubs, Diamonds, Hearts, Spades
export type Rank = 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14;

export interface Card {
  id: string;
  suit: Suit;
  rank: Rank;
}

export type TurnState =
  | "Dealing"
  | "AwaitingAttack"
  | "AwaitingDefense"
  | "Resolving"
  | "RoundEnded"
  | "MatchEnded";

export interface ValidationError {
  code: string;
  message: string;
  details?: unknown;
}

export type ActionResult<T = unknown> =
  | { ok: true; state: MatchState; events: GameEvent[]; value?: T }
  | { ok: false; error: ValidationError };

// Domain entities

export interface Player {
  id: string;
  name: string;
  hand: Card[];
  score: number;
  isActive: boolean;
  seatIndex: number;
}

export interface BeatenPair {
  attack: Card;
  counter: Card;
}

export interface PendingAttack {
  attackerId: string;
  defenderId: string;
  unbeatenCards: Card[];
  beatenPairs: BeatenPair[];
}

export interface RoundState {
  trump: Suit;
  dealerId: string;
  attackerId: string;
  defenderId: string | null;
  phase: TurnState;
  pendingAttack: PendingAttack | null;
}

export interface MatchState {
  matchId: string;
  roundNumber: number;
  players: Player[]; // ordered by seatIndex
  deck: Card[]; // deck[0] = bottom (trump face); deck[length-1] = top (drawn next)
  discard: Card[];
  round: RoundState;
  winner: string | null;
  rngSeed: number;
}

// Action union — discriminated on `kind`
export type Action =
  | { kind: "Attack"; playerId: string; cardIds: string[] }
  | { kind: "Beat"; playerId: string; attackCardId: string; counterCardId: string }
  | { kind: "Stop"; playerId: string };

// GameEvent union — append-only audit / animation trail
export type GameEvent =
  | { type: "RoundStarted"; roundNumber: number; dealerId: string; trump: Suit }
  | { type: "TrumpSelected"; trump: Suit; bottomCardId: string }
  | { type: "CardsDealt"; perPlayer: { playerId: string; count: number }[] }
  | {
      type: "AttackSubmitted";
      attackerId: string;
      defenderId: string;
      cardIds: string[];
    }
  | {
      type: "CardBeaten";
      defenderId: string;
      attackCardId: string;
      counterCardId: string;
    }
  | { type: "DefenseStopped"; defenderId: string; takenCardIds: string[] }
  | { type: "FullDefense"; defenderId: string; discardedPairs: number }
  | { type: "CardsDrawn"; playerId: string; count: number }
  | { type: "TurnChanged"; nextAttackerId: string; phase: TurnState }
  | { type: "RoundWon"; winnerId: string }
  | { type: "MatchEnded"; winnerId: string };

// View projections — used by PRP 3 for UI + network

export interface HandSummary {
  ownerId: string;
  count: number;
  publiclyKnown: Card[];
}

export interface PublicPlayerInfo {
  id: string;
  name: string;
  seatIndex: number;
  score: number;
  isActive: boolean;
  hand: HandSummary;
}

export interface PublicGameView {
  matchId: string;
  roundNumber: number;
  players: PublicPlayerInfo[];
  deckCount: number;
  discardCount: number;
  round: {
    trump: Suit;
    dealerId: string;
    attackerId: string;
    defenderId: string | null;
    phase: TurnState;
    pendingAttack: {
      attackerId: string;
      defenderId: string;
      unbeatenCards: Card[];
      beatenPairs: BeatenPair[];
    } | null;
  };
  winner: string | null;
}

export interface PrivatePlayerView extends PublicGameView {
  viewerId: string;
  viewerHand: Card[];
}

// Setup input — the engine is pure; the caller supplies the player roster.
export interface PlayerSetup {
  id: string;
  name: string;
}
