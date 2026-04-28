<!-- COMPONENT: validation-path | applies to: feasibility-analysis -->

## ⟨N⟩. Validation Path

**Intro-Summary**: ⟨1-2 sentences: how the feasibility claim will be tested before full commitment⟩

> Every assumption in the feasibility verdict MUST have a validation step. List validation activities in the order they would run, with measurable success criteria and expected duration.

| Step | Validation activity | Measurable success criterion | Expected duration | Cost (if non-trivial) |
|---|---|---|---|---|
| V1 | ⟨e.g. "POC: implement core path on synthetic data"⟩ | ⟨quantified, e.g. "single-machine throughput ≥ 1k req/s"⟩ | ⟨2 weeks⟩ | ⟨1 engineer⟩ |
| V2 | ⟨e.g. "Pilot: run on production-sample"⟩ | ⟨quantified, e.g. "tail latency P99 < SLA at 50% target traffic"⟩ | ⟨4 weeks⟩ | ⟨2 engineers + infra⟩ |
| V3 | ⟨e.g. "User study: 10 internal users"⟩ | ⟨quantified, e.g. "Adoption rate ≥ 70%, NPS ≥ 30"⟩ | ⟨2 weeks⟩ | ⟨1 PM + UX hours⟩ |

**Failure-stop conditions**: ⟨if V_i fails, what triggers stopping vs. iterating? Be specific.⟩

**Total validation duration**: ⟨weeks⟩ before go-no-go decision can be made.

**Takeaway**: ⟨the assumption most worth validating early because its failure invalidates the rest⟩
