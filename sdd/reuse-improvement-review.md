# Reuse Improvement Review

Project: `4 - stroke-signal-demo`

## Review points

- [x] after scaffold
- [x] after architecture decision
- [x] after first working slice
- [x] after benchmark result
- [x] before publication

## Findings

| Finding | Classification | Kit Area | Action | Status |
|---|---|---|---|---|
| Synthetic fixture generator pattern (numpy-based, seed-controlled) is reusable across ML projects | `patch_now` | `templates` | document the pattern as a recommended approach for deterministic ML benchmarks | recorded |
| BenchmarkResult schema is consistent with other portfolio projects | `patch_now` | `contracts` | keep the shared schema stable for cross-project comparison | recorded |
| Dockerfile structure follows established portfolio pattern | `reject` | `templates` | project-specific dependencies and entrypoint should remain local | rejected |

## Patch-now decisions

- The project uses the existing portfolio benchmark JSON shape from other projects.
- The synthetic fixture pattern is documented and ready for reuse by other ML projects.

## Backlog decisions

- Add a shared synthetic data generator to portfolio-reuse-kit when two or more projects use the same pattern.

## Rejected improvements

- No external dataset, GPU, or model serving was added; it would increase complexity without improving the reproducibility claim.

## Final gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects the synthetic fixture benchmark contract.
