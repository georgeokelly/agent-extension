<!-- COMPONENT: experiment-setup | applies to: research-findings, technical-evaluation -->

## ⟨N⟩. Experiment Setup

**Intro-Summary**: ⟨what enables readers to "verify" the results — 1-2 sentences⟩

### ⟨N⟩.1 Hardware / Software / Dataset / Input scale
### ⟨N⟩.2 Measurement protocol (warm-up / repetitions / statistic)
### ⟨N⟩.3 Baseline description (comparison target + fairness conditions)

> 📌 **Benchmark 7-item disclosure** (this component appears in `research-findings` and `technical-evaluation` manifest sequences; non-measurement reports do not include this component because the manifest type-routing already excludes it):

<!-- DEMO from [examples.md Sec. B.7.4 Benchmark 7-item disclosure filling](../../examples.md#b74-benchmark-7-item-disclosure-filling) — REPLACE -->
> 1. **Hardware**：A100-SXM4-40GB；NVLink；1 node
> 2. **Software**：Ubuntu 22.04，driver 535.129.03，CUDA 12.4，nvcc -O3 -arch=sm_80
> 3. **Workload**：sum-reduce 1M float32 (4 MB) device-to-device

> Fill in the remaining 4 items per the skeleton:
> 4. **Configuration**：⟨blockDim / gridDim / launch config⟩
> 5. **Sampling**：⟨runs / warm-up / outlier-rejection rule⟩
> 6. **Statistics**：median + IQR (long-tail robust)
> 7. **Baseline**：⟨same input / same compile options / same thread count / same statistic⟩

> If your report is `technical-evaluation`, the **Baseline** row MUST list ALL competing methods (≥ 2 alternatives), not just one. Each baseline gets identical 7-item disclosure rigor.

**Takeaway**: ⟨1 sentence on the validity boundary under the experimental conditions⟩
