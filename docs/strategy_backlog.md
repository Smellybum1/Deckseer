# Strategy Knowledge Backlog

Deckseer can learn from high-level Slay the Spire 2 creators, but creator knowledge should enter the project as reviewed strategy claims before it becomes scoring logic.

This backlog is for compact research notes, not full transcripts. The current implementation remains the manual JSON card reward advisor.

## Research Workflow

1. Start from specific trusted videos, not whole-channel scraping.
2. Attempt transcript fetching when practical.
3. If transcript fetching fails, keep the source entry ready for manual notes.
4. Extract compact strategy claims in our own words.
5. Review whether each claim is durable, repeatable, and testable.
6. Convert reviewed claims into one of:
   - scoring rule
   - regression test
   - card role or tag update
   - docs-only note

## Research Boundaries

- Do not store full copied transcripts in this repository.
- Keep creator-derived knowledge as attributed notes until reviewed.
- Avoid long direct quotations; summarize strategy claims in our own words.
- Do not update scoring from a single claim unless it is durable, repeatable, and testable.
- Keep Deckseer deterministic and transparent.
- Preserve the project boundary: decision assistance only, no gameplay automation.

## Seed Sources

### Video Sources

| ID | URL | Creator | Title | Date | Topic Focus | Transcript Status | Extraction Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YT-001 | <https://www.youtube.com/watch?v=lmSRnG4eaKs> | TBD | Why you lose in Slay the Spire 2 | TBD | `card_rewards`, `pathing`, `run_diagnosis` | Provided as local text; not copied into repo | Initial claims extracted |
| YT-002 | <https://www.youtube.com/watch?v=NzAoe1P7ayw> | TBD | Why you're taking too much damage | TBD | `combat_planning`, `damage_prevention` | Provided as local text; not copied into repo | Initial claims extracted |
| YT-003 | <https://www.youtube.com/watch?v=zCh7P7O6NqM> | TBD | You should be destroying act 1 elites | TBD | `card_rewards`, `elite_prep`, `act_1_pathing` | Provided as local text; not copied into repo | Initial claims extracted |

Provided transcript files:

- `D:\Codex\Why you lose in Slay the Spire 2.txt`
- `D:\Codex\Why you're taking too much damage.txt`
- `D:\Codex\You should be destroying act 1 elites.txt`

### Local Tier List Sources

These tier lists are useful as card-quality priors and review prompts. They should not override run context, deck needs, or current patch changes. Do not copy the full tier lists into the repository unless the format is intentionally converted into reviewed, hand-curated Deckseer data.

Current card metadata is intentionally simplified. Imported class data should be treated as heuristic roles, weak quality priors, and rough effects for recommendation scoring, not as complete card rules text or exact combat simulation data.

| ID | Local File | Class | Patch / Version | Source Type | Extraction Status |
| --- | --- | --- | --- | --- | --- |
| TL-DEFECT-001 | `D:\Slay the Spire\Defect1.txt` | Defect | TBD | tier list | Imported as initial curated seed data |
| TL-IRONCLAD-001 | `D:\Slay the Spire\Ironclad v0.102.0.txt` | Ironclad | `v0.102.0` | tier list | Imported as broader curated seed data |
| TL-NECROBINDER-001 | `D:\Slay the Spire\Necrobinder1.txt` | Necrobinder | TBD | tier list | Imported as initial curated seed data |
| TL-REGENT-001 | `D:\Slay the Spire\Regent World's best v0.103.0.txt` | Regent | `v0.103.0` | categorized tier list | Imported as initial curated seed data |
| TL-SILENT-001 | `D:\Slay the Spire\Silent v0.102.0.txt` | Silent | `v0.102.0` | tier list | Imported as initial curated seed data |

### Empirical Community Data Sources

Empirical stats are higher-signal than isolated tier lists, but they still need context. Use them to generate hypotheses, priors, and review targets rather than automatic recommendations.

| ID | URL | Source Type | Useful Signals | Known Caveats | Extraction Status |
| --- | --- | --- | --- | --- | --- |
| STS2FUN-001 | <https://sts2.fun/> | community run database | patch-filtered run stats, leaderboard, player run histories, card/relic/potion/event pages | uploaded-run bias, possible cherry-picked submissions, patch drift, correlation is not causation | Manual reviewed card rows imported for all classes; live scraping not implemented |

Useful STS2.fun areas to investigate later:

- Cards page: pick rate, offer counts, win rate, win-rate impact, by-act views, ascension views, and pairings.
- Leaderboard/player pages: high-performing player histories, card picks, route choices, potion use, relics, and run outcomes.
- Patch filter: compare current main patch against beta, older patches, and All Patches before trusting a stat.
- FAQ caveats: solo-run inclusion rules, modded-run rejection, leaderboard filtering, and the stated inability to detect cherry-picked uploads.

## Claim Template

Use this template for each extracted strategy claim.

```markdown
### Claim: Short descriptive title

- Claim:
- Context:
- Confidence: low | medium | high
- Source video:
- Timestamp:
- Creator:
- Deckseer impact:
- Candidate implementation target: scoring rule | regression test | card role | docs-only note
- Review status: proposed | accepted | rejected | implemented
- Notes:
```

## Candidate Claims

These claims are summarized in our own words from the provided transcripts. They are not scoring rules yet.

### Claim: Treat bad outcomes as accumulated decision debt

- Claim: A run-ending draw or fight usually reflects earlier choices in deck building, pathing, potion use, shops, and combat sequencing rather than pure RNG.
- Context: General run diagnosis and post-loss review.
- Confidence: high
- Source video: YT-001
- Timestamp: broad theme around `1:32` to `8:21`
- Creator: TBD
- Deckseer impact: Recommendation caveats should mention unresolved run problems and not frame close choices as certainty.
- Candidate implementation target: docs-only note | scoring rule
- Review status: proposed
- Notes: Useful later for a "run autopsy" feature.

### Claim: Act 1 deaths usually come from poor pathing or too little damage

- Claim: If a player dies in Act 1, the likely causes are pathing into danger without enough setup or failing to add enough damage before elites.
- Context: Act 1 card rewards and pathing.
- Confidence: high
- Source video: YT-001
- Timestamp: around `8:21`
- Creator: TBD
- Deckseer impact: Early Act 1 card reward scoring should keep frontload highly valued when damage density is low.
- Candidate implementation target: scoring rule | regression test
- Review status: proposed
- Notes: This aligns with Deckseer's current `frontload` need.

### Claim: Act 1 planning should include elites, fires, shops, and fail-safes

- Claim: Good Act 1 paths build toward elite fights with enough card rewards, upgrades, shops, and fallback routes if the run is too weak.
- Context: Map reading and future pathing advice.
- Confidence: medium
- Source video: YT-001
- Timestamp: around `9:00` to `17:01`
- Creator: TBD
- Deckseer impact: Future pathing advice should evaluate late elites, fire-before-elite opportunities, shop timing, and bailout options.
- Candidate implementation target: docs-only note | future pathing module
- Review status: proposed
- Notes: Not directly actionable for current manual card reward scoring unless path context is added.

### Claim: Early card rewards should improve damage output before elites

- Claim: Cards that deal meaningfully more damage than starter attacks are important before early elites; a rough target is enough damage to handle elite HP before their scaling overwhelms you.
- Context: Act 1 card rewards.
- Confidence: high
- Source video: YT-001
- Timestamp: around `17:06`
- Creator: TBD
- Deckseer impact: Add tests where low-damage early decks prefer efficient damage over speculative scaling.
- Candidate implementation target: scoring rule | regression test | card role
- Review status: proposed
- Notes: Avoid turning this into "always take attacks"; defensive elite regions can change the need.

### Claim: Potions should be spent aggressively when they save meaningful HP

- Claim: A potion that prevents a large elite hit is often worth using; preserving 10-20 HP can matter more than saving the potion indefinitely.
- Context: Elite preparation and combat.
- Confidence: medium
- Source video: YT-001, YT-003
- Timestamp: YT-001 around `23:07`; YT-003 around `25:12`
- Creator: TBD
- Deckseer impact: Future potion advice should compare expected HP saved against upcoming fight risk.
- Candidate implementation target: future potion module | docs-only note
- Review status: proposed
- Notes: Current run-state input has potion IDs but no combat forecast.

### Claim: Act 2 requires a scaling plan and a more focused deck

- Claim: Act 2 punishes decks that only contain random good cards; the run needs a way to scale and a focused plan that makes key cards show up and work together.
- Context: Act 2 card rewards and deck direction.
- Confidence: high
- Source video: YT-001
- Timestamp: around `23:33` to `32:23`
- Creator: TBD
- Deckseer impact: Act 2+ scoring should raise scaling, synergy, and Skip pressure while reducing generic frontload picks.
- Candidate implementation target: scoring rule | regression test
- Review status: proposed
- Notes: This aligns with current `scaling`, `consistency`, and `deck_quality` needs.

### Claim: Start skipping more often once the deck has a direction

- Claim: In Act 2 and later, cards that do not support the deck's plan can make the deck less reliable even if they are individually fine.
- Context: Card reward choices after fundamentals are established.
- Confidence: high
- Source video: YT-001
- Timestamp: around `30:50`
- Creator: TBD
- Deckseer impact: Skip should become more competitive when a deck has enough fundamentals and an offered card misses the active theme.
- Candidate implementation target: scoring rule | regression test
- Review status: proposed
- Notes: Good candidate for a "focused_plan" or "theme_fit" need.

### Claim: Act 3 is about making bad draws impossible

- Claim: By Act 3, the deck should identify worst-case hands and reduce their chance or impact through removes, draw, retain, relics, and potions.
- Context: Late-run deck quality and boss preparation.
- Confidence: high
- Source video: YT-001
- Timestamp: around `33:39`
- Creator: TBD
- Deckseer impact: Later scoring should value consistency, draw manipulation, retain, removes, and potion planning more than raw card quality.
- Candidate implementation target: future scoring rule | future run diagnosis
- Review status: proposed
- Notes: Requires richer card roles such as `retain`, `deck_control`, and `bad_draw_mitigation`.

### Claim: Full blocking every hit can increase total damage taken

- Claim: Playing too passively can extend fights long enough for scaling enemies to deal more total damage than a more efficient damage/block balance would allow.
- Context: Combat planning and damage prevention.
- Confidence: high
- Source video: YT-002
- Timestamp: around `0:44` to `1:08`
- Creator: TBD
- Deckseer impact: Combat advice should not optimize only current-turn HP loss; it should consider fight length and enemy scaling.
- Candidate implementation target: future combat module | docs-only note
- Review status: proposed
- Notes: Not directly part of card reward scoring, but it informs frontload value.

### Claim: Look ahead one or two turns, not just at the current hand

- Claim: Strong combat play evaluates likely future draws and enemy actions, asking whether current plays enable kills or safer turns later.
- Context: Combat planning and elite fights.
- Confidence: high
- Source video: YT-002
- Timestamp: around `1:39` to `3:13`; conclusion around `13:27`
- Creator: TBD
- Deckseer impact: Future combat advice should use simple lookahead heuristics before any complex simulation.
- Candidate implementation target: future combat module | docs-only note
- Review status: proposed
- Notes: This could eventually inspire deterministic combat simulations, but not for current v0.

### Claim: Act 1 elites are high expected value and should usually be planned for

- Claim: Act 1 elites provide rare-card odds, relics, and gold; avoiding them can leave the run underpowered later.
- Context: Act 1 pathing and card reward pressure.
- Confidence: high
- Source video: YT-003
- Timestamp: around `0:36` to `6:04`
- Creator: TBD
- Deckseer impact: Card reward scoring should assume early picks are preparing for elites unless run context says otherwise.
- Candidate implementation target: scoring rule | future pathing module
- Review status: implemented
- Notes: Run Context v0.2 adds optional `upcoming_elites` and path pressure fields for manual JSON inputs.

### Claim: Elite fights are predictable enough to draft for

- Claim: Because elite pools are limited and repeat in known ways, a player can draft cards and save potions for the specific elites still possible.
- Context: Act 1 elite preparation.
- Confidence: medium
- Source video: YT-003
- Timestamp: around `3:50` to `5:12`
- Creator: TBD
- Deckseer impact: Future advice should track region, fought elites, and remaining elite threats.
- Candidate implementation target: future pathing module | future card reward context
- Review status: proposed
- Notes: Needs more structured run context before implementation.

### Claim: Underdocks elites ask for block; Overgrowth elites ask for damage

- Claim: Region matters: Underdocks elite prep leans toward block and timing, while Overgrowth elite prep leans toward raw damage and efficiency.
- Context: Act 1 card rewards with known region.
- Confidence: high
- Source video: YT-003
- Timestamp: Underdocks around `6:43`; Overgrowth around `18:00`; summary around `27:34`
- Creator: TBD
- Deckseer impact: Add optional `region` or `upcoming_threats` to future run context so scoring can bias defense/frontload appropriately.
- Candidate implementation target: input schema extension | scoring rule | regression test
- Review status: implemented
- Notes: Run Context v0.2 adds optional `act_region` and `upcoming_elites`; scoring now biases Underdocks toward block and Overgrowth toward frontload.

### Claim: Some elites are timing puzzles, not just stat checks

- Claim: Fights like Terror Eel and Phrog Parasite can punish crossing thresholds or transforming enemies at the wrong time, even when the deck has enough nominal damage.
- Context: Future combat advice and elite-specific card reward caveats.
- Confidence: medium
- Source video: YT-003
- Timestamp: Terror Eel around `14:05`; Phrog Parasite around `18:33`
- Creator: TBD
- Deckseer impact: Future combat advice should recognize threshold fights and value retain, delayed burst, poison/doom-style delayed damage, and planning.
- Candidate implementation target: future combat module | card role
- Review status: proposed
- Notes: Needs enemy-specific metadata before implementation.

### Claim: Slow-style enemies reward sequencing small damage before large damage

- Claim: Against enemies whose damage taken increases as cards are played, attacks should generally be sequenced from least to most important damage.
- Context: Bygone Effigy-style combat sequencing.
- Confidence: medium
- Source video: YT-003
- Timestamp: around `25:55`
- Creator: TBD
- Deckseer impact: Future combat advice can include deterministic sequencing hints for known enemy mechanics.
- Candidate implementation target: future combat module
- Review status: proposed
- Notes: Not relevant to card reward scoring until combat state is modeled.

### Claim: Tier lists should become weak priors, not final answers

- Claim: Card tier lists can identify generally strong cards, but Deckseer should treat them as weak priors because run needs, act timing, deck direction, and current patch context can dominate raw tier placement.
- Context: Card reward scoring and hand-curated card data.
- Confidence: high
- Source video: TL-DEFECT-001, TL-IRONCLAD-001, TL-NECROBINDER-001, TL-REGENT-001, TL-SILENT-001
- Timestamp: N/A
- Creator: user-provided local tier lists
- Deckseer impact: Add an optional reviewed `quality_prior` or `tier_hint` later, but keep run-needs scoring as the main driver.
- Candidate implementation target: card data schema | scoring rule | regression test
- Review status: implemented
- Notes: Card Priors v0.1 adds optional `quality_prior`, `pick_context`, `source_patch`, and `source_notes`; priors are weak and do not override urgent run needs.

### Claim: Patch version must be attached to card-quality assumptions

- Claim: Tier-list claims can become stale when patches change card numbers or mechanics, so any imported quality prior should record its source patch/version.
- Context: User-curated card data and future tier-list intake.
- Confidence: high
- Source video: TL-IRONCLAD-001, TL-REGENT-001, TL-SILENT-001
- Timestamp: N/A
- Creator: user-provided local tier lists
- Deckseer impact: Future card metadata should distinguish stable roles from patch-sensitive quality priors.
- Candidate implementation target: card data schema | docs-only note
- Review status: implemented
- Notes: Card Priors v0.1 adds optional `source_patch`; Regent source uses `v0.103.0`, and Ironclad/Silent use `v0.102.0`.

### Claim: Regent tier data needs category normalization before scoring

- Claim: Regent's resource uses descriptive buckets such as overstatted, boss damage, niche uses, and skip in most cases rather than simple S/A/B/C/D tiers.
- Context: Tier-list intake and class-specific card priors.
- Confidence: medium
- Source video: TL-REGENT-001
- Timestamp: N/A
- Creator: user-provided local tier list
- Deckseer impact: Future import tooling should support qualitative bucket labels and map them to reviewed roles or priors manually.
- Candidate implementation target: future import helper | card role review
- Review status: proposed
- Notes: This is probably more informative than flattening Regent into generic S/A/B/C/D.

### Claim: Community win-rate data should inform priors with bias controls

- Claim: STS2.fun card and run stats can provide empirical signals such as pick rate, win rate, win-rate impact, by-act performance, and pairings, but these signals should be patch-filtered and treated as biased observational data.
- Context: Future empirical scoring support.
- Confidence: high
- Source video: STS2FUN-001
- Timestamp: N/A
- Creator: STS2.fun community stats
- Deckseer impact: Active empirical rows now track `pick_rate`, `win_rate`, `impact`, `sample_size`, `patch`, provenance, and review status, but they remain secondary to run-needs diagnosis.
- Candidate implementation target: empirical audit | scoring prior | docs-only note
- Review status: implemented
- Notes: STS2.fun Data Audit now includes manually reviewed active rows for all five classes. Do not equate high win rate with causal card strength; strong players and already-winning decks may pick certain cards more often.

### Claim: High-level run histories can teach sequencing and context, not just card value

- Claim: Reviewing top-player run histories can reveal when cards were picked, what route was chosen, which potions were held or spent, and how decisions compound across a run.
- Context: Strategy research and future run-history learning.
- Confidence: medium
- Source video: STS2FUN-001
- Timestamp: N/A
- Creator: STS2.fun community stats
- Deckseer impact: Future research should sample complete runs from strong players and extract context-aware examples, especially "why this pick now" scenarios.
- Candidate implementation target: strategy backlog | future run history module | regression scenarios
- Review status: proposed
- Notes: Prefer a small reviewed set of complete runs over bulk-imported aggregate stats at first.

### Claim: Patch-aware empirical data can challenge static tier lists

- Claim: Patch-filtered card stats can reveal when local tier lists are stale or when a card's performance depends heavily on act, ascension, or pairings.
- Context: Tier-list review and hand-curated data maintenance.
- Confidence: high
- Source video: STS2FUN-001
- Timestamp: N/A
- Creator: STS2.fun community stats
- Deckseer impact: Use empirical data to flag card roles and priors for review, not to auto-rewrite them.
- Candidate implementation target: future import helper | card data review report
- Review status: implemented
- Notes: Added `audit-card-priors` with local empirical-style fixtures and manually reviewed STS2.fun rows. Live STS2.fun ingestion remains future work.

### Claim: Ironclad tier list can seed a curated one-class data expansion

- Claim: The Ironclad `v0.102.0` tier list is useful for expanding Deckseer's first class dataset when imported as weak priors plus manually reviewed roles, not as direct recommendations.
- Context: Hand-curated card data coverage.
- Confidence: high
- Source video: TL-IRONCLAD-001
- Timestamp: N/A
- Creator: user-provided local tier list
- Deckseer impact: Ironclad now has a broader curated data slice spanning frontload, block, draw, energy, scaling, exhaust, AoE, and niche payoff cards.
- Candidate implementation target: card data schema | scoring prior | regression test
- Review status: implemented
- Notes: Imported cards still use simplified effects; future passes should check names/effects against current patch data before relying on exact numbers.
