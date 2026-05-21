// 1000 random-legal-bot games. Asserts 0 conservation violations and
// 100% reach RoundEnded. Exits non-zero on failure.
import { runRandomLegalRound } from "../src/core/__tests__/_bot.js";
import { allCardIds, totalCards } from "../src/core/__tests__/_helpers.js";

const N = 1000;
const startMs = Number(process.hrtime.bigint() / 1_000_000n);

let conservationViolations = 0;
let dupViolations = 0;
let nonTerminations = 0;
const turnsHistogram: number[] = [];

for (let i = 0; i < N; i++) {
  const playerCount: 3 | 4 = i % 2 === 0 ? 3 : 4;
  const run = runRandomLegalRound(i * 17 + 1, playerCount, i * 31 + 13);
  if (run.endedAt !== "RoundEnded") nonTerminations++;
  turnsHistogram.push(run.turnCount);
  for (const s of run.states) {
    if (totalCards(s) !== 52) conservationViolations++;
    const ids = allCardIds(s);
    if (new Set(ids).size !== 52 || ids.length !== 52) dupViolations++;
  }
}

const endMs = Number(process.hrtime.bigint() / 1_000_000n);
const elapsedMs = endMs - startMs;

turnsHistogram.sort((a, b) => a - b);
const mean = turnsHistogram.reduce((s, n) => s + n, 0) / turnsHistogram.length;
const p50 = turnsHistogram[Math.floor(turnsHistogram.length * 0.5)] ?? 0;
const p95 = turnsHistogram[Math.floor(turnsHistogram.length * 0.95)] ?? 0;

const reachedPct = ((N - nonTerminations) / N) * 100;
const ok = conservationViolations === 0 && dupViolations === 0 && nonTerminations === 0;

console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`  CARDSHED core — simulation smoke (${N} games)`);
console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
console.log(`📋 Results`);
console.log(`  ${conservationViolations === 0 ? "✅" : "❌"} Conservation violations: ${conservationViolations}`);
console.log(`  ${dupViolations === 0 ? "✅" : "❌"} Card-duplication violations: ${dupViolations}`);
console.log(`  ${nonTerminations === 0 ? "✅" : "❌"} Reached RoundEnded: ${reachedPct.toFixed(1)}% (${N - nonTerminations}/${N})`);
console.log(`📋 Performance`);
console.log(`  Elapsed: ${elapsedMs} ms`);
console.log(`  Turns per round — mean ${mean.toFixed(1)} · p50 ${p50} · p95 ${p95}`);
console.log(`────────────────────────────────────────────`);
if (ok) {
  console.log(`  ✅ Result: PASS`);
} else {
  console.log(`  ❌ Result: FAIL`);
}
console.log(`────────────────────────────────────────────`);

process.exit(ok ? 0 : 1);
