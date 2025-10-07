// Splash particle effect with twinkle and yellowish glow
export function ParticleEffects() {
  const canvas = document.getElementById("splashParticles");
  const ctx = canvas.getContext("2d");
  let particles = [];
  const particleCount = 50;
  let w, h, animationFrame;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        size: 2 + Math.random() * 3,
        speedY: 0.2 + Math.random() * 0.15, // px/frame
        alpha: 0.2 + Math.random() * 0.3,
        twinkleSpeed: 0.02 + Math.random() * 0.03,
        twinklePhase: Math.random() * Math.PI * 2,
        maxTwinkle: 0.6 + Math.random() * 0.4,
      });
    }
  }

  function updateParticles() {
    particles.forEach((p) => {
      p.y -= p.speedY;
      if (p.y < -p.size) {
        p.y = h + p.size;
        p.x = Math.random() * w;
      }
      // twinkle phase keeps updating so spawner sees twinkling motion
      p.twinklePhase += p.twinkleSpeed;
    });
    requestAnimationFrame(updateParticles);
  }

  //   function drawParticles() {
  //     ctx.clearRect(0, 0, w, h);

  //     particles.forEach((p) => {
  //       // Twinkle effect
  //       p.twinklePhase += p.twinkleSpeed;
  //       const twinkle = (Math.sin(p.twinklePhase) + 1) / 2;
  //       const glowIntensity = twinkle * 0.7;
  //       const currentAlpha = p.alpha + twinkle * p.maxTwinkle;

  //       // Glow halo
  //       if (glowIntensity > 0.2) {
  //         const glowSize = p.size + glowIntensity * 10;
  //         const gradient = ctx.createRadialGradient(
  //           p.x,
  //           p.y,
  //           p.size * 0.5,
  //           p.x,
  //           p.y,
  //           glowSize
  //         );
  //         gradient.addColorStop(0, `rgba(255,245,150,${glowIntensity * 0.8})`);
  //         gradient.addColorStop(0.3, `rgba(255,220,100,${glowIntensity * 0.5})`);
  //         gradient.addColorStop(1, `rgba(255,200,50,0)`);
  //         ctx.fillStyle = gradient;
  //         ctx.beginPath();
  //         ctx.arc(p.x, p.y, glowSize, 0, Math.PI * 2);
  //         ctx.fill();
  //       }

  //       // Main particle
  //       ctx.fillStyle = `rgba(255,${255 - glowIntensity * 40},${
  //         255 - glowIntensity * 155
  //       },${currentAlpha})`;
  //       ctx.beginPath();
  //       ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
  //       ctx.fill();

  //       // Glowing border
  //       if (glowIntensity > 0.2) {
  //         ctx.strokeStyle = `rgba(255,235,100,${glowIntensity * 0.6})`;
  //         ctx.lineWidth = 1 + glowIntensity * 1.2;
  //         ctx.beginPath();
  //         ctx.arc(p.x, p.y, p.size + 0.5, 0, Math.PI * 2);
  //         ctx.stroke();
  //       }

  //       // Movement
  //       p.y -= p.speedY;
  //       if (p.y < -p.size) {
  //         p.y = h + p.size;
  //         p.x = Math.random() * w;
  //       }
  //     });

  //     animationFrame = requestAnimationFrame(drawParticles);
  //   }

  initParticles();
  // drawParticles(); commented out because in newer changes logic is moved out from this script in the spawner.
  updateParticles(); // keep particles moving, but don't draw

  // Auto-stop if splash element is removed
  const splash = document.getElementById("splash");
  if (splash) {
    const observer = new MutationObserver(() => {
      if (!document.body.contains(splash)) {
        cancelAnimationFrame(animationFrame);
        ctx.clearRect(0, 0, w, h);
      }
    });
    observer.observe(document.body, { childList: true });
  }

  // Expose particles array (with their speedY) for constellation spawner
  return { particles };
}
