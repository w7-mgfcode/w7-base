import {
  getLegalActions,
  startNewRound,
  submitAttack,
  submitBeat,
  stopDefending,
} from "../rules.js";
import { mulberry32 } from "../prng.js";
import type { Action, MatchState } from "../types.js";

export interface BotRunResult {
  states: MatchState[];
  endedAt: "RoundEnded" | "MatchEnded" | "TurnCap";
  turnCount: number;
}

// Drive a single round to completion using a seeded random-legal bot.
// Caps turns at `maxTurns` to detect infinite loops.
export function runRandomLegalRound(
  initialSeed: number,
  playerCount: 3 | 4,
  rngSeed: number,
  maxTurns = 500,
): BotRunResult {
  let state = startNewRound(null, initialSeed, {
    matchId: `bot-${initialSeed}-${rngSeed}`,
    players: Array.from({ length: playerCount }, (_, i) => ({
      id: `p${i + 1}`,
      name: `P${i + 1}`,
    })),
  });
  const states: MatchState[] = [state];
  const rng = mulberry32(rngSeed);

  for (let turn = 0; turn < maxTurns; turn++) {
    if (state.round.phase === "RoundEnded" || state.round.phase === "MatchEnded") {
      return { states, endedAt: state.round.phase, turnCount: turn };
    }

    // Determine whose turn it is.
    const actorId =
      state.round.phase === "AwaitingAttack"
        ? state.round.attackerId
        : state.round.defenderId!;
    const actions = getLegalActions(state, actorId);
    if (actions.length === 0) {
      throw new Error(
        `INVARIANT: no legal actions for ${actorId} in phase ${state.round.phase}`,
      );
    }
    const pick = actions[Math.floor(rng() * actions.length)]!;
    state = apply(state, pick);
    states.push(state);
  }

  return { states, endedAt: "TurnCap", turnCount: maxTurns };
}

function apply(state: MatchState, a: Action): MatchState {
  let r;
  switch (a.kind) {
    case "Attack":
      r = submitAttack(state, a.playerId, a.cardIds);
      break;
    case "Beat":
      r = submitBeat(state, a.playerId, a.attackCardId, a.counterCardId);
      break;
    case "Stop":
      r = stopDefending(state, a.playerId);
      break;
  }
  if (!r.ok) {
    throw new Error(
      `INVARIANT: bot picked an illegal action: ${a.kind} → ${r.error.code} (${r.error.message})`,
    );
  }
  return r.state;
}
