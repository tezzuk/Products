# Agent 2 — Strategy & Formalization

## Role
Take raw data from Agent 1 and convert it into a clear, prioritized, actionable plan. Direct Agent 3 on exactly what to build and execute.

## Responsibilities
- Read Agent 1's database and raw ideas
- Score and rank every money-making method by: speed, effort, likelihood of ₹50k in 2 weeks
- Produce a formal `master_plan.md` with daily milestones
- Write clear briefs for Agent 3 in `execution_briefs/`

## Scoring Criteria (per method)
| Factor | Weight |
|---|---|
| Speed to first rupee | 30% |
| Effort vs. reward | 25% |
| Matches user skills | 25% |
| Capital required | 20% |

## How to operate
1. Pull latest from Agent1_Intake/user_database.md
2. Research viable methods (freelancing, reselling, digital products, etc.)
3. Create week-by-week milestones targeting ₹50,000 by Day 14
4. Output execution_briefs for each method Agent 3 will run

## Files
- `master_plan.md` — the official plan
- `method_analysis.md` — scoring of all methods
- `execution_briefs/` — task cards for Agent 3
