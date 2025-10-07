// constellation.js

export const ConstellationHelper = {
  // Example constellations with approximate relative layouts
  Orion: {
    scaleRange: [1.0, 2.0],
    particles: [
      { x: 0, y: 0 },
      { x: 30, y: -50 },
      { x: 60, y: 0 },
      { x: 90, y: -20 },
      { x: 120, y: -60 },
      { x: 150, y: 0 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
    ],
  },

  UrsaMajor: {
    scaleRange: [1.0, 1.5],
    particles: [
      { x: 0, y: 0 },
      { x: 40, y: -10 },
      { x: 80, y: -20 },
      { x: 120, y: 0 },
      { x: 160, y: 20 },
      { x: 200, y: 40 },
      { x: 240, y: 30 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
    ],
  },

  Cassiopeia: {
    scaleRange: [1.0, 1.7],
    particles: [
      { x: 0, y: 0 },
      { x: 40, y: -30 },
      { x: 80, y: 0 },
      { x: 120, y: -30 },
      { x: 160, y: 0 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },

  Cygnus: {
    scaleRange: [1.0, 1.4],
    particles: [
      { x: 0, y: 0 },
      { x: 0, y: -60 },
      { x: 0, y: -120 },
      { x: -40, y: -60 },
      { x: 40, y: -60 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [1, 3],
      [1, 4],
    ],
  },

  Scorpius: {
    scaleRange: [1.0, 1.3],
    particles: [
      { x: 0, y: 0 },
      { x: 20, y: -20 },
      { x: 40, y: -40 },
      { x: 60, y: -20 },
      { x: 80, y: 10 },
      { x: 100, y: 40 },
      { x: 120, y: 80 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 6],
    ],
  },

  Leo: {
    scaleRange: [1.0, 1.5],
    particles: [
      { x: 0, y: 0 },
      { x: 30, y: -20 },
      { x: 60, y: -40 },
      { x: 90, y: -20 },
      { x: 120, y: 0 },
      { x: 150, y: 20 },
    ],
    connections: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
    ],
  },

  /**
   * Draw constellation relative to reference point with rotation and scaling
   * @param {CanvasRenderingContext2D} ctx - canvas context (can be dummy for particle calculation)
   * @param {Object} constellation - constellation object (particles + connections + scaleRange)
   * @param {number} refX - reference point X
   * @param {number} refY - reference point Y
   * @param {number} angle - rotation in radians
   * @returns {Object} - { particles: [{x,y}], connections }
   */
  drawConstellation(ctx, constellation, refX, refY, angle = 0) {
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);

    // Choose scale within constellation's defined range
    const [minScale, maxScale] = constellation.scaleRange || [1, 2];
    const scale = minScale + Math.random() * (maxScale - minScale);

    const particles = constellation.particles.map((p) => {
      const sx = p.x * scale;
      const sy = p.y * scale;
      const x = sx * cos - sy * sin + refX;
      const y = sx * sin + sy * cos + refY;
      return { x, y };
    });

    return {
      particles,
      connections: constellation.connections,
    };
  },
};
