// constellationSpawner.js
export class ConstellationSpawner {
  constructor(ctx, width, height, backgroundParticles = []) {
    this.meteors = [];
    this.nextMeteorTime = performance.now() + 10000 + Math.random() * 10000;
    this.ctx = ctx;
    this.width = width;
    this.height = height;
    this.backgroundParticles = backgroundParticles;

    // add extra galaxy stars drifting in the background
    this.galaxyStars = Array.from({ length: 100 }, () => ({
      x: Math.random() * this.width,
      y: Math.random() * this.height,
      size: 0.5 + Math.random() * 1.5,
      speedX: -0.05 + Math.random() * 0.1,
      speedY: -0.02 + Math.random() * 0.05,
      alpha: 0.15 + Math.random() * 0.25,
    }));

    this.activeConstellations = [];

    // timing settings (ms)
    this.pauseAfterArrival = 2000; // how long particles stay at constellation
    this.lineFadeDelay = 1000; // fade lines start after departure begins
    this.lineFadeDuration = 1000; // duration of line fade

    this.animationStarted = false;
    this.FRAME_MS = 1000 / 60; // 60fps reference
  }

  startBackground() {
    if (!this.animationStarted) {
      this.animationStarted = true;
      requestAnimationFrame(this.animate.bind(this));
    }
  }

  randomRefPoint(margin = 100) {
    const x = margin + Math.random() * Math.max(0, this.width - 2 * margin);
    const y = margin + Math.random() * Math.max(0, this.height - 2 * margin);
    return { x, y };
  }

  spawnConstellation(helper, options = {}) {
    // Prevent overlap: skip spawn if another is forming or formed
    const blocking = this.activeConstellations.some(
      (c) => c.state === "spawning" || c.state === "formed"
    );
    if (blocking) return;

    const ref = options.refPoint || this.randomRefPoint();
    const angle = options.angle ?? Math.random() * Math.PI * 2;

    // Pick a random constellation (ignore helper functions)
    const constellationKeys = Object.keys(helper).filter(
      (k) => !["drawConstellation", "getRandomConstellation"].includes(k)
    );
    const randomKey =
      constellationKeys[Math.floor(Math.random() * constellationKeys.length)];
    const selectedConstellation = helper[randomKey];

    const result = helper.drawConstellation(
      this.ctx,
      selectedConstellation,
      ref.x,
      ref.y,
      angle
    );

    const now = performance.now();
    const startYOffset = 50 + Math.random() * 120;

    const tempParticles = result.particles.map((p) => {
      const bg = this.backgroundParticles[
        Math.floor(Math.random() * Math.max(1, this.backgroundParticles.length))
      ] || { speedY: 0.35 };

      const startY = this.height + startYOffset + Math.random() * 40;
      const speedY = bg.speedY || 0.35;

      const distance = startY - p.y;
      const travelTimeMs = distance / Math.max(speedY, 0.0001); // ms

      return {
        x: p.x,
        y: startY, // invisible offscreen start
        targetX: p.x,
        targetY: p.y,
        speedY,
        size: 2 + Math.random() * 3,
        alpha: 0.3,
        twinkleSpeed: 0.02 + Math.random() * 0.03,
        twinklePhase: Math.random() * Math.PI * 2,
        maxTwinkle: 0.6 + Math.random() * 0.4,
        arrived: false,
        departureStarted: false,
        launchTimestamp: now, // will adjust below
        arrivalTime: now + travelTimeMs,
      };
    });

    // Compute max arrival time for simultaneous arrival
    const maxArrival = Math.max(...tempParticles.map((p) => p.arrivalTime));
    tempParticles.forEach((p) => {
      p.launchTimestamp = maxArrival - (p.y - p.targetY) / p.speedY;
    });

    const constellation = {
      name: randomKey || "Unknown",
      particles: tempParticles,
      connections: result.connections,
      ref,
      state: "waiting",
      formedAt: null,
      departureAt: null,
      lineFadeStart: null,
      lineAlpha: 1,
    };

    this.activeConstellations.push(constellation);
    this.startBackground();
  }

  animate() {
    if (!this.animationStarted) return;
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.width, this.height);
    const now = performance.now();

    // --- Galaxy background layer ---
    for (let g of this.galaxyStars) {
      g.x += g.speedX;
      g.y += g.speedY;
      if (g.x < 0) g.x = this.width;
      if (g.x > this.width) g.x = 0;
      if (g.y < 0) g.y = this.height;
      if (g.y > this.height) g.y = 0;

      ctx.fillStyle = `rgba(220,220,255,${g.alpha * 2})`;
      ctx.beginPath();
      ctx.arc(g.x, g.y, g.size, 0, Math.PI * 10);
      ctx.fill();
    }

    // --- Background particles ---
    for (let p of this.backgroundParticles) {
      if (!p) continue;
      const twinkle = (Math.sin(p.twinklePhase || 0) + 1) / 2;
      const glowIntensity = twinkle * 0.7;
      const currentAlpha = (p.alpha ?? 0.3) + twinkle * (p.maxTwinkle ?? 0.6);

      if (glowIntensity > 0.2) {
        const glowSize = (p.size ?? 2) + glowIntensity * 10;
        const gradient = ctx.createRadialGradient(
          p.x,
          p.y,
          (p.size ?? 2) * 0.5,
          p.x,
          p.y,
          glowSize
        );
        gradient.addColorStop(0, `rgba(255,245,150,${glowIntensity * 0.8})`);
        gradient.addColorStop(0.3, `rgba(255,220,100,${glowIntensity * 0.5})`);
        gradient.addColorStop(1, `rgba(255,200,50,0)`);
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(p.x, p.y, glowSize, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.fillStyle = `rgba(255,${255 - glowIntensity * 40},${
        255 - glowIntensity * 155
      },${currentAlpha})`;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size ?? 2, 0, Math.PI * 2);
      ctx.fill();
    }

    // --- Active constellations ---
    for (let ci = 0; ci < this.activeConstellations.length; ci++) {
      const c = this.activeConstellations[ci];
      let allArrived = true;

      for (let p of c.particles) {
        if (c.state === "waiting") {
          if (now >= p.launchTimestamp) c.state = "spawning";
          else {
            allArrived = false;
            continue;
          }
        }

        if (c.state === "spawning") {
          if (!p.arrived) {
            p.y -= p.speedY;
            if (p.y <= p.targetY) {
              p.y = p.targetY;
              p.arrived = true;
              p.arrivalTime = now;
            } else allArrived = false;
          }
        } else if (c.state === "departing") {
          p.y -= p.speedY; // resume normal upward motion
        }
      }

      // State transitions
      if (c.state === "spawning" && allArrived) {
        c.state = "formed";
        c.formedAt = now;
        c.lineAlpha = 1;
      }

      if (c.state === "formed" && now - c.formedAt >= this.pauseAfterArrival) {
        c.state = "departing";
        c.departureAt = now;
        c.lineFadeStart = now + this.lineFadeDelay;
      }

      if (
        c.state === "departing" &&
        c.lineFadeStart &&
        now >= c.lineFadeStart
      ) {
        const fadeElapsed = now - c.lineFadeStart;
        c.lineAlpha = Math.max(0, 1 - fadeElapsed / this.lineFadeDuration);
      }

      // Draw lines only if formed or departing
      if (
        (c.state === "formed" || c.state === "departing") &&
        c.lineAlpha > 0
      ) {
        ctx.save();
        ctx.strokeStyle = `rgba(255,215,0,${c.lineAlpha})`;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = "rgba(255,255,200,0.5)";
        ctx.shadowBlur = 6;
        ctx.beginPath();
        for (let [a, b] of c.connections) {
          const pa = c.particles[a];
          const pb = c.particles[b];
          ctx.moveTo(pa.targetX, pa.targetY);
          ctx.lineTo(pb.targetX, pb.targetY);
        }
        ctx.stroke();
        ctx.restore();

        // --- Show constellation name when fully formed ---
        if (c.state === "formed") {
          ctx.save();
          ctx.fillStyle = `rgba(255,255,230,${c.lineAlpha})`;
          ctx.font = "16px sans-serif";
          ctx.fillText(c.name || "Unknown", c.ref.x + 10, c.ref.y - 10);
          ctx.restore();
        }
      }

      // Draw particles only if launched
      for (let p of c.particles) {
        if (now < p.launchTimestamp) continue;

        p.twinklePhase += p.twinkleSpeed;
        const tw = (Math.sin(p.twinklePhase) + 1) / 2;
        const glowIntensity = tw * 0.7;
        const currentAlpha = p.alpha + tw * p.maxTwinkle;

        if (glowIntensity > 0.2) {
          const glowSize = p.size + glowIntensity * 10;
          const gradient = ctx.createRadialGradient(
            p.x,
            p.y,
            p.size * 0.5,
            p.x,
            p.y,
            glowSize
          );
          gradient.addColorStop(0, `rgba(255,245,150,${glowIntensity * 0.8})`);
          gradient.addColorStop(
            0.3,
            `rgba(255,220,100,${glowIntensity * 0.5})`
          );
          gradient.addColorStop(1, `rgba(255,200,50,0)`);
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(p.x, p.y, glowSize, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.fillStyle = `rgba(255,${255 - glowIntensity * 40},${
          255 - glowIntensity * 155
        },${currentAlpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      // Cleanup
      const offscreen = c.particles.every((p) => p.y + p.size < 0);
      if (c.state === "departing" && c.lineAlpha <= 0 && offscreen) {
        this.activeConstellations.splice(ci, 1);
        ci--;
      }
    }

    // --- Meteor streaks ---
    const meteorNow = performance.now();
    if (meteorNow > this.nextMeteorTime) {
      // spawn new meteor
      this.meteors.push({
        x: Math.random() * this.width,
        y: Math.random() * (this.height * 0.5),
        vx: 4 + Math.random() * 3,
        vy: 2 + Math.random() * 1.5,
        life: 0,
      });
      this.nextMeteorTime = meteorNow + 10000 + Math.random() * 20000;
    }

    for (let i = this.meteors.length - 1; i >= 0; i--) {
      const m = this.meteors[i];
      m.x += m.vx;
      m.y += m.vy;
      m.life += this.FRAME_MS;
      const alpha = Math.max(0, 1 - m.life / 800);
      ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(m.x, m.y);
      ctx.lineTo(m.x - m.vx * 8, m.y - m.vy * 8);
      ctx.stroke();
      if (alpha <= 0) this.meteors.splice(i, 1);
    }

    if (this.animationStarted) requestAnimationFrame(this.animate.bind(this));
  }
}
