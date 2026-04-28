<!-- COMPONENT: go-no-go | applies to: feasibility-analysis -->

## ⟨N⟩. Go / No-Go Criteria

**Intro-Summary**: ⟨1-2 sentences: the criteria-based decision framework⟩

> Decision framework: a "go" verdict is conditional on **named numeric thresholds**. A "no-go" or "conditional" verdict spells out what would change the decision in the future.

| Criterion | Threshold for **GO** | Current status | Verdict on this criterion |
|---|---|---|---|
| ⟨e.g. "POC throughput ≥ 1k req/s"⟩ | ≥ 1,000 req/s | ⟨measured / expected⟩ | ✓ / ✗ / pending V1 |
| ⟨e.g. "Cost ≤ $X/mo at target traffic"⟩ | ≤ $⟨X⟩/mo at ⟨traffic⟩ | ⟨measured / projected⟩ | ✓ / ✗ / pending V2 |
| ⟨e.g. "P99 latency under SLA at full traffic"⟩ | < ⟨SLA value⟩ | ⟨measured / unknown⟩ | ✓ / ✗ / pending V2 |
| ⟨e.g. "Risk register has no Critical un-mitigated risks"⟩ | All Critical risks mitigated | ⟨per Sec. risk register⟩ | ✓ / ✗ |

**Overall verdict**: **GO** / **NO-GO** / **CONDITIONAL on ⟨X, Y⟩**

**Decision-reversal triggers** (if "GO" is granted): if any of the following becomes true post-launch, reopen the feasibility decision:
- ⟨specific condition, e.g. "Traffic 2× target with no scaling path"⟩
- ⟨specific condition, e.g. "Maintenance burden > 20% of team capacity"⟩

**Takeaway**: ⟨1 sentence stating the verdict and the most fragile assumption it depends on⟩
