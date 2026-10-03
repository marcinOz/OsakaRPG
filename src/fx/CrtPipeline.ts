import Phaser from 'phaser';

const CRT_STORAGE_KEY = 'thepack.crt';

const fragShader = `
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D uMainSampler;
uniform vec2 uResolution;
uniform float uTime;
varying vec2 outTexCoord;

void main(void) {
    vec2 uv = outTexCoord;

    // Subtle barrel curvature
    vec2 cc = uv - 0.5;
    float dist = dot(cc, cc);
    uv = uv + cc * (dist * 0.04);

    if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }

    // Chromatic aberration (tuned for 1024x576)
    float ca = 0.0008;
    float r = texture2D(uMainSampler, vec2(uv.x + ca, uv.y)).r;
    float g = texture2D(uMainSampler, uv).g;
    float b = texture2D(uMainSampler, vec2(uv.x - ca, uv.y)).b;
    vec3 color = vec3(r, g, b);

    // Scanlines (based on 576 vertical pixel rows)
    float scanline = sin(uv.y * 576.0 * 3.14159) * 0.5 + 0.5;
    color *= (0.92 + 0.08 * scanline);

    // Subtle vignette
    float vig = 16.0 * uv.x * uv.y * (1.0 - uv.x) * (1.0 - uv.y);
    color *= clamp(pow(vig, 0.08), 0.0, 1.0);

    gl_FragColor = vec4(color, 1.0);
}
`;

export class CrtPipeline extends Phaser.Renderer.WebGL.Pipelines.PostFXPipeline {
  private time = 0;

  constructor(game: Phaser.Game) {
    super({
      game,
      fragShader,
    });
  }

  override onPreRender(): void {
    this.time += 0.016;
    this.set1f('uTime', this.time);
    this.set2f('uResolution', this.renderer.width, this.renderer.height);
  }
}

export function isCrtEnabled(): boolean {
  const val = localStorage.getItem(CRT_STORAGE_KEY);
  return val === null ? true : val === 'true'; // Enabled by default for retro aesthetic
}

export function setCrtEnabled(scene: Phaser.Scene, enabled: boolean): void {
  localStorage.setItem(CRT_STORAGE_KEY, String(enabled));
  applyCrtToCamera(scene, enabled);
}

export function applyCrtToCamera(scene: Phaser.Scene, enabled?: boolean): void {
  const active = enabled ?? isCrtEnabled();
  try {
    const cam = scene.cameras?.main;
    if (!cam) return;
    if (active) {
      if (!(cam as any).hasPostPipeline?.('Crt')) {
        cam.setPostPipeline(CrtPipeline);
      }
    } else {
      cam.removePostPipeline('Crt');
    }
  } catch {
    // Canvas mode / WebGL pipeline fallback
  }
}

export function registerCrt(game: Phaser.Game): void {
  if (game.renderer instanceof Phaser.Renderer.WebGL.WebGLRenderer) {
    const pipelines = (game.renderer as any).pipelines;
    if (pipelines && !pipelines.has('Crt')) {
      pipelines.addPostPipeline('Crt', CrtPipeline);
    }
  }
}
