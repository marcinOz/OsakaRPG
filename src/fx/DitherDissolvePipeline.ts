import Phaser from 'phaser';

const ditherFrag = `
#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D uMainSampler;
uniform vec2 uResolution;
uniform float uProgress; // 0.0 to 1.0
uniform int uMode; // 0=bayer dissolve, 1=iris, 2=datamosh, 3=filmBurn
uniform float uPixelScale;

varying vec2 outTexCoord;

// Bayer 8x8 matrix normalized 0.0 to 1.0
float bayer8(vec2 uv) {
    vec2 p = floor(uv);
    int x = int(mod(p.x, 8.0));
    int y = int(mod(p.y, 8.0));

    // 4x4 recursive bayer reconstructed
    int m[16];
    // We compute 4x4 bayer and tile
    int bx = int(mod(float(x), 4.0));
    int by = int(mod(float(y), 4.0));

    float val = 0.0;
    if (by == 0) {
        if (bx == 0) val = 0.0; else if (bx == 1) val = 8.0; else if (bx == 2) val = 2.0; else val = 10.0;
    } else if (by == 1) {
        if (bx == 0) val = 12.0; else if (bx == 1) val = 4.0; else if (bx == 2) val = 14.0; else val = 6.0;
    } else if (by == 2) {
        if (bx == 0) val = 3.0; else if (bx == 1) val = 11.0; else if (bx == 2) val = 1.0; else val = 9.0;
    } else {
        if (bx == 0) val = 15.0; else if (bx == 1) val = 7.0; else if (bx == 2) val = 13.0; else val = 5.0;
    }
    return val / 16.0;
}

void main(void) {
    vec2 uv = outTexCoord;
    vec2 pixelCoord = floor((uv * uResolution) / max(1.0, uPixelScale));

    if (uMode == 0) {
        // Bayer 8x8 threshold dissolve
        float threshold = bayer8(pixelCoord);
        if (uProgress < threshold) {
            gl_FragColor = vec4(0.0);
            return;
        }
        gl_FragColor = texture2D(uMainSampler, uv);
        return;
    }
    else if (uMode == 1) {
        // Iris circular wipe with dithered edge
        vec2 center = vec2(0.5, 0.5);
        vec2 aspect = vec2(uResolution.x / uResolution.y, 1.0);
        float dist = length((uv - center) * aspect);
        float maxR = 0.72; // Full coverage
        float targetR = uProgress * maxR;

        float dither = (bayer8(pixelCoord) - 0.5) * 0.06;
        if ((dist + dither) > targetR) {
            gl_FragColor = vec4(0.0);
            return;
        }
        gl_FragColor = texture2D(uMainSampler, uv);
        return;
    }
    else if (uMode == 2) {
        // Datamosh glitch (blocky slice displacement + chromatic aberration)
        float blockY = floor(uv.y * 32.0);
        float sliceNoise = fract(sin(blockY * 141.2 + uProgress * 23.4) * 43758.5);

        vec2 glitchUv = uv;
        if (sliceNoise > 0.65 && uProgress < 0.8) {
            float shift = (fract(sliceNoise * 10.0) - 0.5) * 0.12 * (1.0 - uProgress);
            glitchUv.x += shift;
        }

        float r = texture2D(uMainSampler, glitchUv + vec2(0.006 * (1.0 - uProgress), 0.0)).r;
        float g = texture2D(uMainSampler, glitchUv).g;
        float b = texture2D(uMainSampler, glitchUv - vec2(0.006 * (1.0 - uProgress), 0.0)).b;
        float a = texture2D(uMainSampler, glitchUv).a;

        gl_FragColor = vec4(r, g, b, a * clamp(uProgress * 1.5, 0.0, 1.0));
        return;
    }
    else if (uMode == 3) {
        // Film burn (white flash overexposure into warm vintage color)
        vec4 col = texture2D(uMainSampler, uv);
        float burn = clamp((1.0 - uProgress) * 1.8, 0.0, 1.0);
        col.rgb += vec3(burn * 1.1, burn * 0.8, burn * 0.4);
        gl_FragColor = col;
        return;
    }

    gl_FragColor = texture2D(uMainSampler, uv);
}
`;

export class DitherDissolvePipeline extends Phaser.Renderer.WebGL.Pipelines.PostFXPipeline {
  public progress = 1.0;
  public mode = 0;
  public pixelScale = 2.0;

  constructor(game: Phaser.Game) {
    super({
      game,
      fragShader: ditherFrag,
    });
  }

  override onPreRender(): void {
    this.set1f('uProgress', this.progress);
    this.set1i('uMode', this.mode);
    this.set1f('uPixelScale', this.pixelScale);
    this.set2f('uResolution', this.renderer.width, this.renderer.height);
  }
}
