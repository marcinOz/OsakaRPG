---
name: senior-game-dev-plan
description: >-
  Use this skill when creating an implementation plan (/plan) for game development features, mechanics, architecture refactors, or gameplay systems. Enforces a Senior Game Dev lens: clean game state management, decoupling simulation from presentation, hot-path memory hygiene, and headless testability without overloading context.
---

# Senior Game Dev Planning Skill

This skill guides the creation of high-quality, architecture-first technical implementation plans (`/plan`) for games. It ensures games remain performant, modular, and easy to maintain as complexity grows.

For concrete code patterns and state machine examples, see:
[Game State & Decoupling Reference](./references/game-state-and-decoupling.md)

---

## The 4 Senior Game Dev Pillars

When planning any game feature or refactor, evaluate it through these 4 pillars:

1. **Decoupled Simulation (Sim vs. View)**
   - Game rules, formulas, and state must exist in pure, engine-agnostic classes/modules.
   - Presentation layers (sprites, animations, sounds, particle emitters) merely observe or react to state changes. Never let rendering code drive gameplay truth.

2. **Deterministic State Management**
   - Use explicit state transitions (Finite State Machines or State pattern).
   - Eliminate hidden booleans or scattered flags (`isJumping`, `canAttack`, `isHurt`).
   - Keep state serializable for save/load or network sync where applicable.

3. **Hot-Path Memory & Tick Hygiene**
   - **Zero Allocation in Update**: Never allocate memory (`new Object()`, `[...spread]`, inline closures) inside `update(time, delta)` or per-frame hot paths.
   - **Preallocate & Pool**: Reuse scratch objects/vectors and pool transient entities (bullets, damage numbers, particles).
   - **Teardown Lifecycle**: Explicitly clean up tweens, event listeners, and timers on entity destruction or scene transitions to prevent memory leaks.

4. **Headless Testability First**
   - If game logic cannot be unit-tested without launching a WebGL/Canvas renderer or full game window, the architecture is too tightly coupled.
   - Core mechanics (combat math, inventories, dialog trees, turn order) must have fast, headless unit tests.

---

## Senior Game Dev `/plan` Blueprint

When generating an implementation plan artifact for a game task, format it using the standard Antigravity plan sections enriched with game architecture checkpoints:

### 1. Goal Description
- **Mechanical & Design Intent**: Clear statement of the feature, player interaction, and expected behavior.
- **Architecture Role**: Clarifies which layer this belongs to (Simulation, View/Presentation, Controller/Input, or Data/Config).

### 2. User Review Required
- Highlight critical design choices, breaking changes to save data/schemas, or performance-sensitive tradeoffs.

### 3. Open Questions
- Technical spikes, asset dependencies, or gameplay balance ambiguities that need input.

### 4. Proposed Changes
Organize by architectural layer:
- **Simulation Layer (Pure Logic)**:
  - New models, state machines, math formulas, and event definitions.
- **Presentation / Scene Layer (Engine Specific)**:
  - Game object views, sprite animations, audio cues, particle triggers, tweening.
- **Data / Config Layer**:
  - Balancing tables, JSON configs, or static data files (separating numbers from logic).

*(For all files, use `#### [NEW]`, `#### [MODIFY]`, or `#### [DELETE]` with precise diffs/signatures).*

### 5. Verification Plan
Split verification into two distinct tracks:
- **Automated Headless Tests**:
  - Exact Vitest/unit test commands covering edge cases, state transitions, and damage/stat calculations without DOM/Canvas.
- **Manual Playtest Checklist**:
  - Input responsiveness & boundary tests (e.g. hitting walls, rapid button presses).
  - State edge cases (e.g. pause/resume mid-animation, opening menus during combat).
  - Visual & audio polish check (tween cleanup, sound effect triggering).
