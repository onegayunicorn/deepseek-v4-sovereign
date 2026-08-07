# SOVEREIGN AI — Brand Kit

Version 1.0 · Built by onegayunicorn (OGU) · Connected to the Quantum Lineage Bridge and the Mocking Jay Universal Digital Twin

---

## 1. Identity

| Field | Value |
|---|---|
| Brand name | SOVEREIGN AI (short: SOVEREIGN) |
| Mission | Own your intelligence. |
| Category | Sovereign (self-hosted, privacy-preserving) AI product family |
| Core architecture | DeepSeek-V4, self-hosted, orchestrated locally |
| Product family | Sovereign Orchestrator · Sovereign Ring · Sovereign Buds · Sovereign OS |
| Parent lineage | Built by onegayunicorn (OGU); connected to the Quantum Lineage Bridge and the Mocking Jay Universal Digital Twin |

### Mission
**Own your intelligence.**

Every model, every memory, every inference stays on hardware you control. SOVEREIGN exists for the person who refuses to rent their mind to someone else's cloud.

### What we are
A sovereign AI family. The Sovereign Orchestrator is the monorepo that runs your agents. Sovereign OS is the operating layer that binds device, model, and identity. Sovereign Ring is a BCI neural ring. Sovereign Buds are AI earbuds with on-device inference. All of it lives on your hardware, behind your firewall, answerable to you.

### What we are not
We are not a SaaS wrapper. We are not another chatbot subscription. We are not "cloud AI with a privacy sticker." If it cannot run without our servers, it is not SOVEREIGN.

---

## 2. Positioning statement

For self-hosting developers, privacy-first individuals, and compliance-bound enterprises who believe their intelligence should belong to them, SOVEREIGN AI is the self-hosted AI product family that runs entirely on hardware you own. Unlike cloud AI platforms that store your data, decisions, and biometric signals on someone else's servers, SOVEREIGN keeps inference, memory, and identity local — orchestrated by you, bound only by your rules.

---

## 3. Personality — 5 adjectives

1. **Sovereign** — answers to its users, not to ad models or data brokers.
2. **Precise** — says the exact thing, the first time, in the fewest words.
3. **Direct** — no hedging, no hype, no press-release padding.
4. **Quietly powerful** — does not shout; the capability speaks for itself.
5. **Uncompromising** — privacy is not a setting to negotiate; it is the architecture.

---

## 4. Color system

| Token | Hex | Role |
|---|---|---|
| Background | `#0A0A10` | Foundation — near-black with a blue cast. All surfaces sit on this. |
| Primary accent | `#00E5FF` | Cyan — the sovereign signal. Actions, links, focus, active states, key data. |
| Secondary | `#00FFCC` | Mint — confirmation, growth, success, device "on" states. |
| Text | `#E0E0E0` | Primary text on dark surfaces. |

### Usage rules
- Background `#0A0A10` covers at least 70% of any screen or printed surface.
- Cyan `#00E5FF` is the single action color. One cyan element per view; never two competing cyan CTAs.
- Mint `#00FFCC` marks success and the "on" state of devices. Never used for destructive actions.
- Body text is always `#E0E0E0`. Never render body copy in cyan or mint.
- Cyan and mint are accents, not fills. No large accent blocks behind body text.
- On light surfaces (print, white docs), text flips to `#0A0A10`; cyan darkens to `#00838F`-class for contrast.

See `palette.md` for the full token table and contrast notes.

---

## 5. Typography

Suggested stack (self-hosted ethos — no proprietary font CDNs, all open families):

- **Display / Headlines:** Space Grotesk — geometric, technical, a little sharp. Fallback: system-ui.
- **Body / UI:** Inter — neutral, legible at small sizes. Fallback: system-ui.
- **Mono / Code / Telemetry:** JetBrains Mono — for anything that runs or computes: CLIs, logs, agent output.

Rules:
- Headlines: tight tracking (-0.02em), sentence case. No all-caps for long strings.
- Body: 16–18px on dark, line-height 1.6.
- One typeface role per surface. Mono is reserved for machine speech — logs, outputs, specs.

---

## 6. Taglines (5)

1. **Own your intelligence.**
2. **Your mind, your hardware.**
3. **The last AI you hand over.**
4. **Inference is local. Sovereignty is the default.**
5. **Run it yourself. Keep it yours.**

---

## 7. Logo concept (text description)

A single glyph: a **ring**, open at one point like a circuit break rather than a closed loop, orbiting a **quantum glyph** at its center — a small core with three orbital traces. A **circuit path** threads from the ring's gap through the core and out the far side.

- Geometry: the ring is a thin annulus (stroke ~2.5% of diameter); the core is a dot with three elliptical orbit lines; the circuit is one broken trace entering the gap and exiting opposite.
- Color: ring and circuit in primary cyan `#00E5FF`; core dot in mint `#00FFCC`; on background `#0A0A10`.
- Meaning: the ring is the Sovereign Ring (BCI) and the closed orbit of your own data; the gap is the sovereign choice to open the loop to your own integrations; the circuit is hardware, grounded, real; the quantum glyph is the DeepSeek-V4 inference core.
- Usage: glyph alone at or below 48px (favicons, device bezels); glyph + wordmark ("SOVEREIGN" in Space Grotesk, letterspaced +0.08em) above that size. The wordmark is always text color, never cyan.

---

## 8. Brand architecture

**Master brand: SOVEREIGN AI**

One system, one promise — "Own your intelligence" — delivered across four product lines:

```
SOVEREIGN AI
├── Sovereign Orchestrator   — agent orchestration monorepo (developer platform)
├── Sovereign OS             — operating layer binding device + model + identity
├── Sovereign Ring           — BCI neural ring (intent, presence, bio-signal context)
└── Sovereign Buds           — AI earbuds (private on-device audio intelligence)
```

Rules:
- All products carry the SOVEREIGN name; the master brand owns the mission.
- Each product line speaks in its own register (Orchestrator = developer; Ring/Buds = personal and health; OS = systems), but every piece of copy passes the mission test: does it return control to the user?
- The lineage line ("by OGU · Quantum Lineage Bridge · Mocking Jay Universal Digital Twin") appears in the footer of brand surfaces. It is provenance, not marketing copy.

---

## 9. Do / Don't

**Do:**
- State facts with numbers.
- Address the user as the owner of the system.
- Default to "you control" language.

**Don't:**
- Use hype adjectives (see `brand_voice.md` forbidden list).
- Claim the cloud is evil — claim that ownership is better.
- Promise features that are not yet in the repo or on the device.
