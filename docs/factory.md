# Software Factory for maze

Selected mode: maximum-autonomy, scenario-driven development, following the StrongDM direction. The human specifies desired behavior and release boundaries. Agents plan, implement, verify, evaluate independently, repair, push, and create draft PRs without routine step approvals. Tests and CI remain the foundation; no human code review is required to finish the local development loop.

## Adopted from software-factory-mode-2026aki

Source: https://scrapbox.io/shokai/software-factory-mode-2026aki_skill
Original skill: https://github.com/shokai/agent-skills/blob/main/plugins/software-factory-mode/skills/software-factory-mode-2026aki/SKILL.md

This repository adapts the process; it does not claim to activate or install the original skill. The original requires an Opus-tier primary agent and a qualifying Codex consultant. It also depends on codex-consultation, sanity-review, conversation-context-export, and kuden skills. Those dependencies are not silently assumed installed here.

Use this development loop:

1. Turn a request into observable acceptance scenarios. Ask about product decisions that would change those scenarios; use established rules for routine implementation choices.
2. Plan one small, reviewable change on a feature branch.
3. Implement and run rules, rendering/input, and relevant browser checks.
4. Obtain independent fresh-context review, evaluate findings against evidence, fix concrete bugs, and repeat affected checks. Record review depth and whether code changed afterwards.
5. Update progress with evidence and remaining uncertainty. After relevant checks and independent evaluation pass, push the feature branch and create or update its draft PR automatically. This project explicitly overrides the source skill’s wait-for-push-instruction rule. Never force-push.
6. In the draft PR, include the requirements, validation, known limits, and a concise conversation handoff. Exclude secrets and unrelated private conversation. Keep evidence in the PR description. Do not post comments or request other people’s reviews without authorization.
7. Independently evaluate the final diff and acceptance evidence, resolve findings, and check CI on the latest commit. Repair CI failures and repeat evaluation after changes. Keep the PR draft while checks are incomplete; mark ready for review on instruction. No unrun CI is treated as green.
8. Merge on explicit instruction, then clean up only this task's development processes and branches.

The local commands automate verification. Within an active authorized task, the agent carries out the loop through push, draft PR, and CI repair. No background scheduler or unattended daemon has been installed; work does not continue after the active session ends. Merge and production deployment remain explicit release decisions.

## Scenario-driven acceptance

Start from `docs/game-spec.md` and a concrete user journey. A scenario passes only when its observable result matches the requirement, including failure recovery and actual browser behavior. Evaluate with fresh context and preserve evidence. Do not let the implementer revise the contract or erase a failing scenario just to pass. Current evaluators see the repository tests; no hidden holdout suite is claimed. A successful automated check does not certify untested physical-device behavior or whether the game is fun.

## Complementary loops

| Loop | What repeats | Use in maze |
| --- | --- | --- |
| Small story + persistent handoff (Ralph / long-running harness) | one acceptance item → implementation → checks → record progress → next item | Keep each feature small; resume from `progress.md`. Add a finite attempt/time budget before unattended operation. |
| Scenario evaluation (StrongDM) | user scenario → evaluate result independently → repair → replay | Complete a map, undo a multiplier, change direction, share the resulting image. Keep release-only device scenarios distinct from implementation unit tests. |
| Generator + evaluator (Anthropic) | generate UI → screenshot / play → evaluate fixed criteria → revise | Judge legibility, touch targets, route visibility, audio clarity, and game feel using a fixed rubric. Humans decide visual taste; a green test does not prove fun. |
| Failure → regression | real failure → minimal replay → fix → rerun | Save seed and action sequence for solver, undo, or scoring defects. Add a test that fails before the fix. |

Sources:
- https://github.com/snarktank/ralph
- https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
- https://www.anthropic.com/research/harness-design-long-running-apps
- https://factory.strongdm.ai/

## Evidence and stop conditions

A report names the acceptance item, commands and outcomes, screenshots, review findings, and unresolved limits. Stop a repeated repair loop when the same blocker returns three times or its agreed budget is exhausted; report the blocker rather than producing cosmetic changes or marking the item complete.

Before relaxing review gates, first measure: first-pass acceptance, regressions after release, number of repair cycles, and time/cost per accepted item. More agents are useful only when they improve those outcomes.
