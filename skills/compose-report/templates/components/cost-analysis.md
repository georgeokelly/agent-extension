<!-- COMPONENT: cost-analysis | applies to: feasibility-analysis -->

## ⟨N⟩. Cost Analysis

**Intro-Summary**: ⟨1-2 sentences: total cost ballpark + cost type breakdown⟩

> Quantify ALL cost types: development (engineer-months / hourly rate), infrastructure (monthly run-rate), opportunity (other features deferred), maintenance (steady-state engineer time / on-call burden), and migration (one-time switching cost if applicable).

| Cost type | One-time | Recurring (monthly / annual) | Notes / assumptions |
|---|---|---|---|
| Development | ⟨engineer-months × $rate = $⟩ | — | ⟨team size + duration assumption⟩ |
| Infrastructure | ⟨setup cost⟩ | ⟨$X/mo⟩ | ⟨traffic / scale assumption⟩ |
| Opportunity | — | ⟨feature deferred + estimated value⟩ | ⟨what else this team could do⟩ |
| Maintenance | — | ⟨engineer hours / mo⟩ | ⟨on-call rotation / SLA target⟩ |
| Migration | ⟨switching cost⟩ | — | ⟨downtime / data-migration risk⟩ |

**Sensitivity analysis**: ⟨if cost projection assumes traffic = X, show cost at 0.5X and 2X scenarios; if cost depends on team velocity, show ±20% range⟩

**Cost-benefit verdict**: ⟨ROI / payback period in months / break-even traffic level⟩

**Takeaway**: ⟨the dominant cost dimension and its dependency on a key uncertainty⟩
