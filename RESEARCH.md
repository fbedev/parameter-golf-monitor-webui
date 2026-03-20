---
name: parameter-golf-research
description: >
  Research papers and techniques relevant to the OpenAI Parameter Golf competition.
  Use when looking for novel architectural ideas, quantization methods, or training
  techniques to improve val_bpb under the 16MB/600s constraints. Trigger when the user
  asks about "what papers could help", "novel techniques", "research for parameter golf",
  or "find papers about" compression, quantization, small LMs, etc.
---

# Parameter Golf Research Guide

## How to Use This Skill

When looking for novel techniques to improve Parameter Golf scores, search for papers in these categories and evaluate them against our constraints:
- **16MB artifact** (code + compressed model)
- **600s training** on 8xH100
- **int6/int8 quantization** with zstd-22 compression
- **~11 layers, 512 dim, 1024 vocab**

## Key Research Areas

### 1. Attention Improvements
| Paper | Technique | Impact | Complexity |
|-------|-----------|--------|------------|
| [Differential Transformer](https://arxiv.org/abs/2410.05258) | Difference of two softmax maps | 35-40% param-equivalent | Medium |
| [Value Residual Learning](https://arxiv.org/abs/2410.17897) | Mix V_first into all layers | 16% param-equivalent | Very Low |
| [Low-Rank Q Factorization](https://github.com/openai/parameter-golf/pull/215) | Factor Q into rank-192 | -22% step time, 25% Q savings | Low |
| [Multi-Head Latent Attention](https://arxiv.org/abs/2405.04434) | Compress KV through bottleneck | Low at small scale | High |

### 2. Depth Efficiency / Weight Sharing
| Paper | Technique | Impact | Complexity |
|-------|-----------|--------|------------|
| [RingFormer](https://arxiv.org/abs/2502.13181) | Shared blocks + loop with level signals | 80% param reduction | Medium |
| [Relaxed Recursive Transformers](https://arxiv.org/abs/2410.20672) | LoRA per loop iteration | Similar to RingFormer | Medium |
| [Self-Compressing NNs](https://arxiv.org/abs/2301.13142) | Joint pruning + quantization loss | Low relevance (pruning) | High |

### 3. Quantization & Compression
| Paper | Technique | Impact | Complexity |
|-------|-----------|--------|------------|
| [Quant-Noise](https://arxiv.org/abs/2004.07320) | Stochastic partial quantization | Better int5/int6 STE | Low |
| [Entropy Penalized Reparam](https://arxiv.org/abs/1906.06624) | Entropy penalty in loss for compression | Save 0.5-1MB | Medium |
| [Soft Weight-Sharing](https://arxiv.org/abs/1702.04008) | Learned non-uniform quantization levels | Marginal over int6 | High |
| [k-means Quantization](https://arxiv.org/html/2602.15563) | Optimal quantization levels via clustering | Better than uniform | Low-Med |

### 4. Architecture
| Paper | Technique | Impact | Complexity |
|-------|-----------|--------|------------|
| [GhostNet](https://arxiv.org/abs/2509.12380) | Cheap linear transforms for feature expansion | Uncertain for LMs | Medium |
| [DynaMoE](https://arxiv.org/abs/2603.01697) | Dynamic token-level expert activation | Storage-constrained, risky | High |

### 5. Training Efficiency
| Paper | Technique | Impact | Complexity |
|-------|-----------|--------|------------|
| [FastCuRL](https://arxiv.org/abs/2502.12345) | Progressive context extension | 50% fewer steps needed | Low |
| [Muon Optimizer](https://kellerjordan.github.io/posts/muon/) | Newton-Schulz orthogonalization | Already using NorMuon | — |

## Evaluation Checklist for New Techniques

Before adding a technique, verify:
1. **Does it fit in 16MB?** — Extra parameters must be offset by compression savings
2. **Does it train in 600s?** — Extra compute per step must be offset by fewer needed steps
3. **Is it compatible with int6 STE?** — Must work with quantization-aware training
4. **Can AIDE2 implement it?** — Must fit in a single optimize.py file
5. **Is it novel vs existing PRs?** — Check the leaderboard first

## TO-EXPLORE: Recent Papers (2024-2026, unvalidated)

**IMPORTANT:** Leaderboard-proven techniques (11L, WD=0.04, BigramHash, SmearGate, SWA) should always take priority over paper techniques. These papers are for exploration when proven approaches plateau.

### BitNet / Extreme Low-Bit
| Paper | Technique | Caution |
|-------|-----------|---------|
| [BitNet b1.58](https://arxiv.org/abs/2402.17764) | Ternary weights {-1,0,1} | Competition BitNet PRs scored poorly (1.20+). 600s may be too short. |
| [BitNet Reloaded](https://arxiv.org/abs/2407.09527) | BitNet for small models | Validates small scale but untested in our setting |
| [PV-Tuning](https://arxiv.org/abs/2405.14852) | 1-2 bits per param | Extreme compression, unvalidated at 600s training |

### Rate-Distortion / Compression-Aware
| Paper | Technique | Relevance |
|-------|-----------|-----------|
| [BackSlash](https://arxiv.org/abs/2504.16968) | Train under bit budget constraint | Directly relevant — optimize for 16MB during training |
| [Radio](https://arxiv.org/abs/2505.03031) | Per-layer precision decisions | Could guide int5 vs int6 routing |

### Depth Recurrence / Weight Tying
| Paper | Technique | Relevance |
|-------|-----------|-----------|
| [Universal Transformers](https://arxiv.org/abs/1807.03819) | Same block applied repeatedly | Virtual depth at 1 layer's cost. Needs level signals. |
| [RingFormer](https://arxiv.org/abs/2502.13181) | Shared blocks + LoRA level signals | Modern take on weight tying. 20% params matches vanilla. |
| [Attention Residuals (2026)](https://arxiv.org/abs/2603.15031) | Optimized residual connections | Critical for stable deep recurrence |

### Test-Time Training
| Paper | Technique | Relevance |
|-------|-----------|-----------|
| [TTT Layers](https://arxiv.org/abs/2407.04153) | GD-updated weights during forward pass | Drop-in attention replacement. PR #77 showed +0.003 bpb. |

### Architecture / Signal Flow
| Paper | Technique | Relevance |
|-------|-----------|-----------|
| [Super Tiny LMs](https://arxiv.org/abs/2405.14159) | Tiny model training strategies | Directly about our scale |

## Search Strategy

When looking for new techniques, search for:
- `arxiv small language model efficiency 2024 2025`
- `arxiv transformer quantization aware training extreme`
- `arxiv weight sharing depth recurrence transformer`
- `arxiv parameter efficient attention mechanism`
- `alphaxiv.org` for curated paper recommendations
- Check `parameter-golf.github.io` for competition-specific resources
