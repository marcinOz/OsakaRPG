import Phaser from 'phaser';

const livingPaintingFrag = `
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D uMainSampler;
uniform vec2 uResolution;
uniform float uTime;
uniform int uMode; // 0=water, 1=sway, 2=swirl, 3=haze
uniform float uPixelScale;
uniform vec4 uParams; // [amp, freq, speed, extra]
uniform vec2 uCenter; // in screen pixels

varying vec2 outTexCoord;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void main(void) {
    vec2 uv = outTexCoord;
    vec2 pixelStep = vec2(max(1.0, uPixelScale) / uResolution.x, max(1.0, uPixelScale) / uResolution.y);

    if (uMode == 0) {
        // Water wave displacement (horizontal ripple quantized to art-pixel grid)
        float wave = sin(uv.y * uParams.y + uTime * uParams.z);
        float rawDisp = wave * (uParams.x / uResolution.x);
        float quantDisp = floor(rawDisp / pixelStep.x + 0.5) * pixelStep.x;
        vec2 sampleCoord = vec2(uv.x + quantDisp, uv.y);

        vec4 col = texture2D(uMainSampler, sampleCoord);
        if (col.a <= 0.01) {
            gl_FragColor = vec4(0.0);
            return;
        }

        // Water specular sparkle
        if (uParams.w > 0.05) {
            vec2 gridCell = floor(uv / pixelStep);
            float h = hash(gridCell + floor(uTime * 4.0));
            if (h > (1.0 - uParams.w * 0.15)) {
                col.rgb += vec3(0.25, 0.35, 0.4);
            }
        }

        gl_FragColor = col;
        return;
    }
    else if (uMode == 1) {
        // Foliage / reeds sway (anchored at base, stronger at top)
        float swayFactor = clamp(1.0 - uv.y, 0.0, 1.0);
        float rawDisp = sin(uTime * uParams.z + uv.x * uParams.y) * swayFactor * (uParams.x / uResolution.x);
        float quantDisp = floor(rawDisp / pixelStep.x + 0.5) * pixelStep.x;

        vec4 col = texture2D(uMainSampler, vec2(uv.x + quantDisp, uv.y));
        gl_FragColor = col;
        return;
    }
    else if (uMode == 2) {
        // Vortex swirl (cosmic dimensional rift)
        vec2 centerNorm = uCenter / uResolution;
        vec2 offset = uv - centerNorm;
        // Correct aspect ratio for circular swirl
        offset.x *= (uResolution.x / uResolution.y);
        float r = length(offset);
        float angle = atan(offset.y, offset.x);

        float twist = uParams.x / (1.0 + r * r * uParams.y);
        angle += uTime * uParams.z * twist;

        vec2 swirled;
        swirled.x = cos(angle) * r * (uResolution.y / uResolution.x);
        swirled.y = sin(angle) * r;
        vec2 targetUv = centerNorm + swirled;

        // Quantize back to pixel grid
        targetUv = floor(targetUv / pixelStep + 0.5) * pixelStep;

        vec4 col = texture2D(uMainSampler, targetUv);
        gl_FragColor = col;
        return;
    }
    else if (uMode == 3) {
        // Heat haze / smoke shimmer (vertical rising oscillation)
        float rawDispX = sin(uv.y * uParams.y - uTime * uParams.z) * (uParams.x / uResolution.x);
        float rawDispY = cos(uv.x * uParams.y - uTime * uParams.z) * (uParams.x / uResolution.y);
        float qx = floor(rawDispX / pixelStep.x + 0.5) * pixelStep.x;
        float qy = floor(rawDispY / pixelStep.y + 0.5) * pixelStep.y;

        vec4 col = texture2D(uMainSampler, vec2(uv.x + qx, uv.y + qy));
        gl_FragColor = col;
        return;
    }

    // Default passthrough
    gl_FragColor = texture2D(uMainSampler, uv);
}
`;

export class LivingPaintingPipeline extends Phaser.Renderer.WebGL.Pipelines.PostFXPipeline {
  private time = 0;
  public mode = 0;
  public pixelScale = 2.0;
  public params = [2.0, 24.0, 0.5, 0.0];
  public center = [512.0, 288.0];

  constructor(game: Phaser.Game) {
    super({
      game,
      fragShader: livingPaintingFrag,
    });
  }

  override onPreRender(): void {
    this.time += 0.016;
    this.set1f('uTime', this.time);
    this.set1i('uMode', this.mode);
    this.set1f('uPixelScale', this.pixelScale);
    this.set4f('uParams', this.params[0], this.params[1], this.params[2], this.params[3]);
    this.set2f('uCenter', this.center[0], this.center[1]);
    this.set2f('uResolution', this.renderer.width, this.renderer.height);
  }
}
