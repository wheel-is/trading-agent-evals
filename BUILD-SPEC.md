# Build contract: evidence-grounded research grading

Version: build-contract-1. Recorded October 16, 2026, Pacific. This document specifies the unfinished grading system. It does not release financial grades or certify the draft rubric as calibrated.

## 1. Start here and preserve the existing evidence

The sibling `../jango-eval-kit/` is the complete implementation/data baseline. Read `inputs/TRACE_FORMAT.md`, `research-rubric.json`, `schemas.json`, `acceptance-tests.json`, and `IMPLEMENTATION-ORDER.txt` alongside this document. `input-inventory.json` identifies the original immutable inputs and their hashes. Run `python3 verify_handoff.py --kit ../jango-eval-kit` to check this handoff and the arithmetic examples without invoking models.

Already implemented: weighted scoring arithmetic, unknown bounds, correctness gates, aggregation, schema-1.0 trace normalization, source-bound captures, browser/native adapters, synthetic P01/P11 verifiers, and extensive tests in the kit. The synthetic oracle does not establish actual historical market facts. Existing product outputs have delivery/context/timing reviews, not independently validated financial scores.

Build the missing layers: validated historical source packs; decision-driving claim extraction; independent financial/data verifiers; grounded semantic graders; expert calibration/adjudication; released grade records; and reports that keep quality, delivery, timing and coverage distinct. Do not rerun products merely to grade retained responses.

Use a fresh `grading/<grading_run_id>/` directory. Do not edit captured responses, selected attempts, old contracts, original manifests, prior reports or their integrity records. A changed response, source pack, rubric, judge or applicability rule produces a new grading version. Preserve superseded versions and comparison deltas.

## 2. Scope, task contracts and comparability

This build grades recommendations-only research for all 11 templates. Actual broker execution, scheduled monitoring, restart persistence and paper performance are outside it. The Jango paper cohort needs its own execution rubric; do not score it as an identical research treatment.

Read each selected run's actual prompt and frozen contract. The original P01 pilot, later web-only P02–P11, and native-computation extensions have different contracts/cutoffs/tool allowances. `inputs/research-p01.json`, `research-p02-p11.json` and `native-research-p01-p11.json` preserve those differences. The native task text in `research-rubric.json` is a reference; it never overrides the evaluated run's delivered scope. Freeze an applicability manifest for each cohort before grading.

The later common cutoff is 2026-10-16T03:15:00Z with reference regular close 2026-10-15T16:00:00-04:00. P05/P09 use the earlier 2026-09-30T16:00:00-04:00 decision cutoff. The original P01 pilot's distinct cutoff remains distinct. Publication/availability, observation period, retrieval time, market close and evaluator time must not be conflated.

Publish native/web-only/CLI/paper configurations separately. Underlying models are unknown unless independently reported; product comparisons are not model-only causal estimates. Shared account memory, changed model/tools, shared quotas, concurrency, unavailable sources and observation gaps are explicit comparison strata/findings.

For new collections, freeze prompts, rubric/applicability, source-access treatment, budget and trial/attempt selection before running targets. Three planned trials per prompt/configuration is a starting reliability design, not a property of the existing mostly single-trial collection. Separate technical retries from planned trials. Do not rerun genuine failures until a successful output appears and substitute it for the trial.

For existing captures, import their documented selected-attempt mapping and preserve all attempts. The explicit P02–P11 research adaptations in this new handoff were written after outputs: retrospective scores must be labeled **post-hoc**, never preregistered. Do not silently change selection to improve scores. An expert can revise the draft, but that creates a new rubric and disclosed regrade.

## 3. Modules and interfaces to implement

Reuse `jango_eval/scoring.py` and `traces.py`. Extend through separate modules rather than creating a second incompatible score calculator:

| New component | Input | Output / responsibility |
|---|---|---|
| `grade_import` | Existing run/trace index and selection manifest | Immutable response/artifact references; source hashes; cohort/config identity; capture/timing/context limits |
| `sourcepacks` | Task/cutoff and accepted source policy | Archived records, temporal/entity/unit validation, missing coverage and signed validation status |
| `claims` | Canonical response and actually retrieved artifacts | Source-bound atomic claims, quantities, method assumptions, selected names/weights and completeness statements |
| `financial_verifiers` | Frozen task, declared choices, claims and source pack | Deterministic reference calculations plus pass/fail/unknown evidence for supported checks |
| `semantic_judges` | One criterion, blinded response and validated evidence | Grounded votes only for checks requiring judgment; no unsupported truth from judge memory |
| `adjudication` | Disputed votes, failed evidence checks, expert labels | Versioned human resolution or explicit unknown; all earlier votes retained |
| `grade_release` | Rubric approval, source validation and calibration | Release gate; refuses financial scoring until required prerequisites pass |
| `grade_report` | Versioned criterion grades and operational observations | Separate relevance, raw/gated correctness bounds, coverage, all-pass, timing and delivery tables |

Required future CLI behavior (these commands are a specification, not installed commands):

1. `python -m jango_eval.grade import --selection selection.json --out grading/NEW`
2. `... sourcepack validate --pack sourcepack.json` (never marks authenticity validated merely because URLs resolve).
3. `... rubric validate --rubric research-rubric.json --applicability applicability.json`
4. `... calibrate --expert-labels labels.json --judge-config judges.json`
5. `... run --grading-run grading/NEW` defaults to offline checks/dry-run; configured authorized judge execution is a separate explicit mode.
6. `... adjudicate --decisions expert-decisions.json`
7. `... report --grading-run grading/NEW` creates additive reports and a final integrity inventory.

Every command validates identity/hashes and is resumable. No provider call, account login or target-code execution is needed to import, inspect, validate schemas, calculate supplied-grade scores, or render reports. Untrusted target code, HTML and prompts are data. Any later code reproduction uses an isolated, resource-limited environment without credentials/network by default and a separate execution receipt.

## 4. Rubric and scoring arithmetic

`research-rubric.json` enumerates all 11 tasks, 157 derived criteria, every original task-check mapping, weights, critical flags, explicit exclusions and verification routes. It is complete as a build input but **unreleased pending domain review and calibration**. It retains the earlier explicit P01 research adaptation. The 1/3/5 weights are local proposed defaults, not externally validated SOTA constants.

Score relevance and correctness independently. For each axis let P be passed weight, F failed weight and U unknown weight; T=P+F+U:

- Lower bound = 100 × P/T.
- Upper bound = 100 × (P+U)/T.
- Verification coverage = 100 × (P+F)/T.
- If U=0, the score is a point value. If T=0, the axis is null, never 100.
- A failed predeclared correctness dealbreaker sets gated correctness lower/upper to zero; retain raw correctness diagnostically.
- An unknown dealbreaker sets gated correctness lower to zero and preserves the raw upper bound.
- All-pass is true only when every applicable required check passes; false if any fails; otherwise unknown.
- `required=false` affects all-pass only; applicable checks still remain in the axis denominator.
- Exclusions require an explicit cohort-wide applicability reason. Never drop an inconvenient criterion after seeing a response. Excluded weight is not redistributed.
- No relevance/correctness average or single invented leaderboard score. Extra correct prose cannot add denominator items or points.

Use the existing engine and exact `scoring-examples.json` expectations. Keep full precision in stored values and use declared display rounding only. Aggregation averages planned trials within a fixture, fixtures within a template, then equally weighted template means. Keep target/track/configuration separate and report every denominator. No trial independence or confidence interval is inferred from multiple captures/retries of one output.

Genuine target errors/timeouts after a valid submission remain attempted trials and delivery failures; they cannot vanish as convenient infrastructure exclusions. Map demonstrably missing required outputs to failed checks after release. A pre-submission access block is missing evaluation coverage, not a fabricated failed answer. Invalid prompt delivery, proven scope violations and evaluator corruption remain visible with explicit eligibility decisions and coverage effects. Adapt existing aggregation inputs carefully: its `valid` status is a scoring-eligibility concept, not evidence of a successful target answer.

## 5. Label rules, abstention and critical errors

- **Pass:** the particular proposition is supported by validated evidence or an appropriate deterministic verifier.
- **Fail:** evidence contradicts it, a required feasible output is demonstrably omitted, or an asserted completed result lacks required supplied support. A non-entailing citation is a failed support check when that mismatch is established.
- **Unknown:** the evaluator cannot establish truth from the evidence, including missing evaluator source coverage or a permitted explicitly unresolved recommendation. Unknown is not a pass, zero-weight exclusion or discretionary partial-credit fraction.

Before the release gate, all financial criterion grades remain unknown. Capture/disposition/timing facts may still be reported. After release, distinguish target omission from evaluator uncertainty. When a prompt permits abstention for missing data, a clear unresolved answer can satisfy the output-presence/relevance check while the substantive selection/ranking remains unknown. Do not vacuously pass an empty basket's eligibility, equal weights, graph accuracy or top-ranking checks. Its delivery is partial/unresolved and its all-pass cannot become true through abstention.

If an answer claims a full calculation/ranking while withholding required inputs/artifacts, missing support is a target omission, not evaluator-created uncertainty. An illustrative graph does not verify a real S&P ranking. If the evaluator genuinely cannot retrieve the cited record, authenticity/entailment may remain unknown; inability to fetch alone is not proof of fabrication. Record exact reasons.

Critical examples include future-information leakage, a decision-driving source/entity/unit error, wrong consensus/ranking math, wrong regime-to-ETF mapping, and unsupported core results where the mapped rubric marks them critical. No new critical rule is added after seeing a failure without versioning the rubric. Actual prohibited actions produce a separate scope/eligibility finding; claims that an action occurred require evidence and can also fail the existing claim checks.

## 6. Ground truth and per-template verification

Source validation must be independent of targets and of agreement among target answers. Archive actual passages/tables, URL, entity/security identifier, units, observation period, publication/availability intervals, retrieval time, raw content hash, relevant source spans and source-quality assessment. The allowed source pack and the evaluator-only reference answers are separate. Hide oracle labels/reference outputs from evaluated agents.

Use primary records for decision-driving facts under the frozen policy; clearly label secondary corroboration and unavailable primary records. Prove point-in-time vintage, not merely present-day availability. Date-only evidence stays an interval with timezone/precision; do not invent midnight timestamps. If availability overlaps the cutoff, resolve it or mark unknown. A later retrieval can establish an earlier fact only with support for the earlier vintage.

Declared discretionary choices are inputs to grading: a defensible manager roster, formula, market boundary, forecast convention or company basket need not equal another target's choice. Verify adherence and evidential defensibility under that choice; do not force one preferred ticker list. Claims about returns use only the declared ex-ante framework, not later realized performance as a truth oracle.

| Task | Required independent verification |
|---|---|
| P01 S&P1 | Point-in-time membership; company versus share-class capitalization; consistent closing prices/share counts; credible nearest contenders; declared ties; supported leader and target allocation; conditional daily review/switch policy |
| P02 Hedge-fund consensus | Exactly 20 distinct admissible declared managers; Q2-2026 13F versions/amendment semantics; common-stock/ADR versus options/debt; reported-value units; ticker/class mapping; each top ten; one manager vote per stock; count/rank/tie recomputation; ten 10% weights |
| P03 Congress | Actual disclosure/member identity and ownership attribution; actionable availability clock; 30-day window; at least three distinct members; sum of range lower bounds >=$500,000; at most five equal-weight names; frozen conditional exit/performance clocks |
| P04 Insiders | Effective S&P membership; transaction and filing times; CEO/CFO plus a second distinct director; code/ownership/footnotes and plan exclusions; 30-day transaction window; selection/ties/weights; attached qualifying identities and conditional exits; no exhaustive no-qualifier claim from incomplete screening |
| P05 Revisions | September-30 point-in-time universe and consensus endpoints; fiscal forecast period; declared revision strength/breadth; adjusted six-month momentum; missing-data/threshold/tie rules; independently recomputed composite and top five; no current-consensus proxy mislabeled historical |
| P06 Oligopoly | Same product/geography/period boundaries for concentration and leadership; declared admission threshold; source-supported pricing power; consistent ROIC/FCF definitions and calculations; defensible basket <=5; observable material-deterioration replacement policy; grounded expert judgment for discretionary selection |
| P07 AI bottleneck | All five categories considered; declared geography/horizon; actual binding-constraint evidence and counterevidence; direct company economics/exposure; supported FCF forecasts and units; three names if established; evidence-driven conditional rotation, not popularity |
| P08 Lobbying | Q2-2026 versus Q2-2025 comparable federal spending; parent/subsidiary deduplication; positive-denominator growth; zero/tiny-base treatment; complete comparison coverage; rank first/take five/then confirm/no backfill; dated contract/backlog confirmation; equal-weight confirmed subset; no unsupported causal claim |
| P09 Regimes | Exact series/transforms and release-vintage availability by September-30 close; growth/inflation signs and zero/missing rules; independent classification; exact map SPY/TLT/GLD+DBC/GLD+SGOV; initialization and change-only conditional policy; no fabricated previous holdings |
| P10 SoFi-style | Separate supplied task terms, verified disclosures and independent approximation; approved current model or explicitly stale 83/14/2/1 fallback; absent instrument approval stays unresolved; target versus temporary no-action cash distinction; supplied cash/deviation thresholds, fee formula and expenses; conditional policies/version record; no invented proprietary methodology or account state |
| P11 PageRank | Frozen node universe/cycle and full primary-source coverage; mention-to-entity records/exclusions; A→B direction, deduplication, no self/subsidiary/ambiguous edges; all isolates/dangling nodes; damping .85, uniform teleportation/dangling redistribution; independent recomputation, convergence, full scores, top ten/ties and 10% weights; toy demonstrations kept distinct |

For P11 validate claimed convergence L1<=1e-10 and compare normalized reference scores with maximum absolute error <=1e-8 unless the frozen contract specifies a stricter tolerance. Include a separately written linear-system solution for small fixtures rather than only duplicating the target's iterative algorithm. For rankings use unrounded values and declared exact ties. Use exact integers for counts and Decimal/rational arithmetic for disclosed dollar/range thresholds; never invent a universal dollar-rounding tolerance. Record accepted reporting precision/source units and interval bounds per task. Proposed weights sum to one within 1e-9 when provided as exact numerical fractions; rounded display weights are interpreted under an explicit rounding policy rather than silently failed.

## 7. Claim ledger, graders and calibration

Extract each decision-driving fact, numerical input, ranking, coverage assertion, method choice, causal assertion and claimed action as a source-bound claim. Keep exact response byte spans, original text, normalized proposition, quantity/unit, entity, time, supporting source IDs and uncertainty. Never expand the score denominator with incidental facts. Extraction is not truth verification.

Prefer deterministic tests for dates, units, counts, sums, mappings, thresholds, formulas and reproducible graph calculations. Use grounded semantic review for mandate coverage, source entailment, market-boundary defensibility, pricing power and bottleneck reasoning. Judges receive the frozen criterion, applicable contract, blinded response, validated passages/reference calculation and explicit unknown option. Target text cannot instruct the judge or access hidden grading tools.

The default semantic design is three independently prompted judge configurations from distinct model families when feasible. Pin their actual identifiers/settings and keep votes isolated. This is inspired by jury-based finance evaluation, not proof that any particular jury is calibrated. Store label, evidence references, concise rationale and errors; do not require private reasoning.

Adjudication rule: unanimous supported votes can become a candidate label; two matching votes plus unknown can become a candidate for a noncritical check. Any pass/fail split, critical non-unanimity, unsupported citation, reference disagreement or schema error goes to expert adjudication and remains unknown until resolved. Expert overrides retain all votes and cite their evidence. Agreement alone never establishes source truth.

Before release, have two qualified reviewers independently annotate a representative development set across all 11 templates, critical/peripheral checks, true/false/unknown labels, abstentions and adversarial failures; resolve disagreements with a recorded third review. Start with at least 220 criterion labels (20 per template), including at least 100 known critical failures across the suite. Judge configurations must reach >=95% exact label agreement and <=1% observed false-pass rate on those critical failures before automatic release. These are local proposed acceptance thresholds, not SOTA-certified constants. Publish counts, per-template confusion matrices and uncertainty intervals; zero observed errors is not proof of zero risk. Review/expand the set when uncertainty is too wide.

Keep calibration and held-out validation labels separate; rerun held-out validation after judge/prompt/model changes. Add known-good and deliberately broken versions differing in exactly one material fact. Check position, product-name, verbosity and paraphrase sensitivity. No expert labels should come from the same target answer being graded. Failure to meet thresholds leaves affected semantic checks human-only or unknown; it never silently lowers the bar.

Release requires approved rubric/applicability, validated source pack/reference, passing deterministic tests, calibrated route or human-only adjudication, and frozen version hashes. Source or judge availability errors are reported, not converted to invented financial grades.

## 8. Operational outcomes, timing, reporting and scale

Retain delivery labels (substantive/partial/decline/empty/error) independently of financial grades. Preserve separate arm, actual Send, first observed outcome and Copy/artifact clocks. A reported interval includes polling delay; observation gaps do not establish exact completion or continuous provider execution. Saved post-deadline Working evidence establishes a known budget miss even when later completion time is unknown.

Report `quality_all_pass`, `within_budget` (true/false/unknown), `scope_validity` and `benchmark_all_pass` separately. The latter requires quality all-pass plus verified budget/scope conditions when the track requires them. A deadline miss does not itself change the underlying financial correctness score. A stop request does not prove termination. Claims about time/tool use must agree with the actual observed trace or remain disputed.

Each criterion grade cites response/source hashes, evidence spans, verifier/judge versions, reference values/tolerances, rationale, adjudication and release status. Store raw and gated correctness, score intervals, weighted verification coverage, required all-pass, selected-attempt mapping, count of missing/blocked/invalid trials, source/judge costs if actually known, and comparison limitations. Rank neither unvalidated outputs nor upper bounds as established quality. Quality tables can display unresolved intervals without a winner.

Build the source pack once per task/cutoff/convention set, cache immutable source extraction, and reuse it across eligible target grades. Cache verifier/judge results only by complete response+criterion+rubric+sourcepack+judge/config hashes. Judge requests can run concurrently with per-provider quotas; do not alter target execution budgets with grader overhead. Use the separate rerun playbook for future target queues; its scheduler is not a grader.

One process owns report publication; per-run grading workers own separate directories. Atomic writes, content hashes and checkpoints permit resumption. The final export includes inputs, schema/rubric/source manifests, grades/votes/adjudication, report, source snapshots and a SHA-256 file inventory. Verify copies and preserve original captures. Credentials and unrelated account files do not belong in the handoff.

## 9. Acceptance and definition of done

`acceptance-tests.json` is the implementation checklist, not a claim those future components already pass. Existing scoring/examples and source mappings are verifiable now. All planned tests need implementations before release. Run the kit's existing unit suite after changes and add meaningful schema, provenance, deterministic finance, unknown/abstention, judge-injection/calibration, timing-gap, retry-selection and export tests.

Done means: all 11 templates mapped; every original check accounted for; approved research-only applicability; schema-valid source-bound outputs; actual independently validated source/reference packs; deterministic tests and calibrated/human-adjudicated semantic checks; no unresolved release prerequisites; honest uncertainty/coverage; preserved old data; reproducible reports and verified export. A working calculator or a successful provider call alone is not done.

Until these gates are met, the current product capture collection remains financially ungraded. Any agent can build from this contract, but missing authoritative historical data and expert calibration must remain visible inputs—not invented completions.

## 10. Methodology provenance

- [Vals Finance Agent v2](https://www.vals.ai/benchmarks/fabv2): weighted checks, critical-error gates, all-pass reporting, repeated runs and a judge jury inspired the design. Our weights, ten-minute budget and calibration thresholds are local choices; its shared harness is not reproduced by mixed native products.
- [FActScore](https://arxiv.org/abs/2305.14251): supports claim-level source verification; factual precision alone cannot replace required-task coverage.
- [Anthropic agent-eval guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents): motivates matching deterministic/model/human graders to checks, transcript review, isolated trials and judge calibration. Actual shared-memory/isolation limits remain reported.
- [StrangeBenchML grading](https://strangebench.com/#how-graded): reinforces independent final-output verification and repeated measurements; reviewed after these captures. Its ML tasks and best-observed-result success threshold are not our financial ground truth or our fixed pass rule.

The original spec preserves additional literature references. No access token, source credential or externally licensed corpus is included here.
