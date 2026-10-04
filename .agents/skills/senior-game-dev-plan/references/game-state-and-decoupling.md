# Game State Management & Decoupling Reference

This reference demonstrates the Senior Game Dev architectural pattern: **Sim vs. View Decoupling** with **Headless Testability**.

---

## 1. Simulation vs. Presentation Decoupling

Keep game rules, math, and state completely free of engine imports (no Phaser, Unity, Godot, or DOM references in the core simulation).

### Example: Pure Simulation Layer (`Combatant.ts`)
```typescript
export interface CombatantConfig {
  maxHp: number;
  attackPower: number;
}

export type CombatState = 'idle' | 'attacking' | 'hurt' | 'dead';

export class Combatant {
  private _hp: number;
  private _state: CombatState = 'idle';

  constructor(public readonly id: string, public readonly config: CombatantConfig) {
    this._hp = config.maxHp;
  }

  get hp(): number { return this._hp; }
  get state(): CombatState { return this._state; }
  get isAlive(): boolean { return this._hp > 0; }

  takeDamage(amount: number): number {
    if (!this.isAlive) return 0;
    const actualDamage = Math.max(1, Math.min(this._hp, amount));
    this._hp -= actualDamage;
    this._state = this._hp === 0 ? 'dead' : 'hurt';
    return actualDamage;
  }

  resetState(): void {
    if (this.isAlive) this._state = 'idle';
  }
}
```

### Presentation Layer (`CombatantView.ts` - Phaser Example)
```typescript
import Phaser from 'phaser';
import { Combatant } from './Combatant';

export class CombatantView extends Phaser.GameObjects.Container {
  constructor(scene: Phaser.Scene, x: number, y: number, private model: Combatant) {
    super(scene, x, y);
    // Visuals observe or respond to model state, never mutate business logic directly
  }

  playHurtEffect(): void {
    this.scene.tweens.add({
      targets: this,
      alpha: 0.3,
      yoyo: true,
      duration: 80,
      repeat: 2,
    });
  }
}
```

---

## 2. Minimal Deterministic State Machine (FSM)

Avoid loose boolean flags (`isAttacking`, `canMove`, `isStunned`). Use an explicit state pattern to prevent invalid transitions:

```typescript
export type StateKey = 'IDLE' | 'MOVING' | 'ATTACKING' | 'DEAD';

export interface StateHandler {
  enter?(): void;
  update?(deltaMs: number): void;
  exit?(): void;
}

export class FiniteStateMachine {
  private currentState?: StateKey;
  private handlers = new Map<StateKey, StateHandler>();

  register(key: StateKey, handler: StateHandler): this {
    this.handlers.set(key, handler);
    return this;
  }

  transitionTo(next: StateKey): boolean {
    if (this.currentState === next) return false;
    this.handlers.get(this.currentState!)?.exit?.();
    this.currentState = next;
    this.handlers.get(next)?.enter?.();
    return true;
  }

  update(deltaMs: number): void {
    if (this.currentState) {
      this.handlers.get(this.currentState)?.update?.(deltaMs);
    }
  }
}
```

---

## 3. Headless Vitest Verification

Because the simulation layer does not depend on Canvas or WebGL, unit tests execute instantly in Vitest without browser mocks:

```typescript
import { describe, it, expect } from 'vitest';
import { Combatant } from './Combatant';

describe('Combatant Simulation', () => {
  it('correctly calculates lethal damage and transitions to dead', () => {
    const hero = new Combatant('hero-1', { maxHp: 100, attackPower: 20 });
    const dmg = hero.takeDamage(150);

    expect(dmg).toBe(100);
    expect(hero.hp).toBe(0);
    expect(hero.isAlive).toBe(false);
    expect(hero.state).toBe('dead');
  });
});
```

---

## 4. Hot Path Memory Hygiene (Tick Loop)

- **Zero allocation in `update(delta)`**: Do not instantiate objects (`new Vector2()`, `{...state}`), arrays (`[...items]`), or lambdas inside the per-frame update loop.
- **Preallocate & Reuse**: Preallocate temp vectors/scratch buffers at class instantiation.
- **Unsubscribe on Destroy**: Always clear listeners, tweens, and timers when entities or scenes are shut down.
