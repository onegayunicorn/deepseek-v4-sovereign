# SOVEREIGN AI — Market Plan

Version 1.0

---

## 1. Market segments

### Segment A — Self-hosting AI developers
The people already running DeepSeek, Llama, Qwen, and Mistral on their own hardware: homelab operators, ML engineers, indie hackers, and platform teams who read the cloud bill and flinched. They want multi-agent orchestration without surrendering the stack. Pain: orchestration tooling assumes cloud; self-hosting means wiring five tools together yourself. Sovereign Orchestrator is the monorepo that replaces the wiring.

### Segment B — BCI health-tech early adopters
Quantified-self users and neurotech early adopters (25–45, urban, privacy-sensitive) who already wear rings, bands, and earbuds. They track sleep, stress, and focus — and increasingly refuse to let biometric data sync to a brand's cloud. Pain: "smart" wearables are thin clients for someone else's data pipeline. Sovereign Ring and Buds keep inference and biometric events on-device.

### Segment C — Enterprise privacy / compliance teams
CISOs, data-protection officers, and platform leads in regulated industries — health, finance, legal, public sector — where data residency and auditability are non-negotiable. They cannot use cloud AI for sensitive workloads. Pain: deploying private LLMs is a consulting project. Sovereign OS plus Orchestrator is a repeatable, self-hosted deployment with compliance documentation.

## 2. TAM / SAM / SOM

| Layer | A — Developers | B — Health-tech DTC | C — Enterprise B2B | Total |
|---|---|---|---|---|
| **TAM** | $600M | $1.5B | $8.0B | ~$10.1B |
| **SAM** | $105M | $300M | $1.6B | ~$2.0B |
| **SOM (3-yr)** | $4.5M | $10.0M | $10.8M | **~$25.3M/yr run-rate** |

### Reasoning

**Segment A:** Cumulative downloads of leading open-weight model families exceed 60M. Applying a conservative 3–4% conversion to active self-hosting yields ~2.0M developers. Average tool and hardware spend of ~$300/yr per developer gives a TAM of ~$600M. SAM narrows to the ~350K developers who need multi-agent orchestration beyond a single model (~$105M at the same spend). SOM: 15K developers on the Orchestrator by Year 3 — free self-host with a paid managed tier — at ~$300 blended ARPU yields ~$4.5M annual run-rate.

**Segment B:** The consumer wellness and neurotech wearables market sits near $1.5B and is growing at roughly 18–22% CAGR. The privacy-forward slice — buyers who reject cloud sync of biometrics — is estimated at ~20% of that, ~$300M SAM. SOM: 40K Ring + Buds units over three years at a blended ~$250 device price yields ~$10M.

**Segment C:** Private/sovereign AI deployment plus data-residency and compliance software totals roughly $8B TAM. Regulated industries requiring on-prem AI with data residency represent ~20%, ~$1.6B SAM. SOM: 60 enterprise deployments over three years at ~$180K average contract value yields ~$10.8M.

Combined SOM of ~$25M annual run-rate by Year 3 — before any platform expansion beyond the four initial products.

## 3. Channels (4)

1. **Open-source distribution** — GitHub (Orchestrator monorepo) + HuggingFace Spaces (one-click self-host demo). Top of funnel; lowest CAC; feeds the waitlist.
2. **Developer communities** — X, Hacker News, r/LocalLLaMA, Discord, developer conferences. Technical credibility and word of mouth.
3. **Health-tech DTC** — Xiaohongshu, TikTok, wellness creators, DTC store. Owns Ring + Buds consumer demand and the launch waitlist.
4. **Enterprise direct** — security and compliance buyer channels, infosec events, partner-led pilots. High ACV, longer cycle, seeded by the open-source reputation.

## 4. Three-phase launch

| Phase | Timing | Objective | Key metrics |
|---|---|---|---|
| **Pre-launch** | T-21 → T-1 | Demand signaling and list building | Waitlist size, opt-in rate, CPA per lead |
| **Launch day** | T-0 | Conversion velocity | Sell-through rate, hourly revenue, CAC |
| **Post-launch** | T+1 → T+30 | Momentum and social proof | Review velocity, repeat purchase rate |

Tiered access on launch day: VIP (top 5–10% by LTV) at T-24h-equivalent 08:00, waitlist at 10:00, public at 12:00. Full day-by-day calendar in `launch_plan.md`.

## 5. Benchmarks

| Metric | Good | Great |
|---|---|---|
| Waitlist conversion | 10% | 25% |
| Launch-day revenue vs. daily average | 3x | 10x |
| Day-1 sell-through | 20% | 50% |
| Review rate | 2% | 8% |

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Waitlist growth stalls (<1% teaser CTR) | Swap creative to "waitlist-only discount" or "exclusive gift for first 100 buyers" |
| Inventory oversell on launch day | Track quantity, disable "continue selling when out of stock," live restock waitlist button |
| Checkout load spike | Disable non-essential scripts (pixels, chat) for first 2 hours of launch |
| Enterprise pilots stall | Offer 30-day self-host pilot with compliance pack included; no hardware dependency |
