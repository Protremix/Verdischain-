/**
 * Verdis Web3 Animation Engine v2.0
 * Full eco-animation suite: particles, gradient orbs, scroll reveal, glassmorphism
 */
(function() {
  "use strict";

  // === PARTICLE CANVAS (floating leaves + glowing nodes) ===
  function initParticles() {
    // Skip if page already has its own bg-canvas
    if (document.getElementById('bg-canvas')) return;

    const canvas = document.createElement("canvas");
    canvas.id = "verdis-particles";
    canvas.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-2;opacity:0.6;";
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext("2d");
    let particles = [];
    let mouse = { x: -1000, y: -1000, radius: 130 };

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    document.addEventListener("mousemove", function(e) {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    });
    document.addEventListener("mouseleave", function() {
      mouse.x = -1000;
      mouse.y = -1000;
    });

    const PARTICLE_COUNT = Math.min(70, Math.floor(window.innerWidth / 20));
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: -(Math.random() * 0.4 + 0.1),
        r: Math.random() * 2.5 + 1,
        opacity: Math.random() * 0.5 + 0.2,
        angle: Math.random() * Math.PI * 2,
        angVel: (Math.random() - 0.5) * 0.02,
        isLeaf: Math.random() > 0.7
      });
    }

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(function(p) {
        p.y += p.vy;
        p.x += p.vx + Math.sin(p.angle) * 0.3;
        p.angle += p.angVel;

        // Mouse repulsion
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          const ang = Math.atan2(dy, dx);
          p.x += Math.cos(ang) * force * 2;
          p.y += Math.sin(ang) * force * 2;
        }

        // Reset when off top
        if (p.y < -20) {
          p.y = canvas.height + 20;
          p.x = Math.random() * canvas.width;
        }
        if (p.x < -20) p.x = canvas.width + 20;
        if (p.x > canvas.width + 20) p.x = -20;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.angle);
        ctx.globalAlpha = p.opacity;

        if (p.isLeaf) {
          // Draw stylized leaf
          ctx.fillStyle = "#00ff88";
          ctx.shadowColor = "#00ff88";
          ctx.shadowBlur = 6;
          ctx.beginPath();
          ctx.ellipse(0, 0, p.r * 1.8, p.r * 0.7, 0, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Glowing node
          ctx.fillStyle = "#10B981";
          ctx.shadowColor = "#00ff88";
          ctx.shadowBlur = 5;
          ctx.beginPath();
          ctx.arc(0, 0, p.r, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.restore();
      });

      // Connect nearby particles
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.globalAlpha = (1 - dist / 120) * 0.12;
            ctx.strokeStyle = "#00ff88";
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(animate);
    }
    animate();
  }

  // === GRADIENT ORBS ===
  function initGradientOrbs() {
    // Skip if page already has orbs
    if (document.querySelector('.orb') || document.getElementById('verdis-orbs')) return;

    const orbContainer = document.createElement("div");
    orbContainer.id = "verdis-orbs";
    orbContainer.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:-1;overflow:hidden;";
    document.body.insertBefore(orbContainer, document.body.firstChild);

    const orbs = [
      { color: "rgba(0,255,136,0.10)", size: 500, x: "10%", y: "15%", delay: "0s" },
      { color: "rgba(45,212,191,0.08)", size: 400, x: "70%", y: "55%", delay: "-7s" },
      { color: "rgba(16,185,129,0.06)", size: 600, x: "35%", y: "75%", delay: "-14s" }
    ];

    orbs.forEach(function(orb) {
      const div = document.createElement("div");
      div.style.cssText = "position:absolute;border-radius:50%;filter:blur(100px);opacity:0.6;" +
        "width:" + orb.size + "px;height:" + orb.size + "px;" +
        "left:" + orb.x + ";top:" + orb.y + ";" +
        "background:radial-gradient(circle," + orb.color + ",transparent 70%);" +
        "animation:verdis-orb-float 20s ease-in-out infinite alternate;" +
        "animation-delay:" + orb.delay + ";";
      orbContainer.appendChild(div);
    });
  }

  // === SCROLL REVEAL ===
  function initScrollReveal() {
    // Add reveal class to key content elements if not already present
    const selectors = [
      'section', '.card', '.glass-card', '.panel', '.feature',
      '.stat-card', '.eco-tile', '.download-card', '.info-section',
      'table', '.hero-content'
    ];

    // Don't auto-add to elements that already have reveal
    document.querySelectorAll(selectors.join(',')).forEach(function(el) {
      if (!el.classList.contains('reveal') && !el.classList.contains('no-reveal')) {
        el.classList.add('verdis-reveal');
      }
    });

    // Add CSS for reveal animation
    const style = document.createElement("style");
    style.textContent = `
      .verdis-reveal {
        opacity: 0;
        transform: translateY(28px);
        transition: opacity 0.7s cubic-bezier(0.22,1,0.36,1), transform 0.7s cubic-bezier(0.22,1,0.36,1);
      }
      .verdis-reveal.verdis-visible {
        opacity: 1;
        transform: translateY(0);
      }
      @media (prefers-reduced-motion: reduce) {
        .verdis-reveal { opacity: 1; transform: none; transition: none; }
      }
    `;
    document.head.appendChild(style);

    // IntersectionObserver for scroll reveal
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('verdis-visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

      document.querySelectorAll('.verdis-reveal').forEach(function(el) {
        observer.observe(el);
      });
    } else {
      // Fallback: just show everything
      document.querySelectorAll('.verdis-reveal').forEach(function(el) {
        el.classList.add('verdis-visible');
      });
    }
  }

  // === GLASSMORPHISM HOVER EFFECTS ===
  function initGlassmorphism() {
    const style = document.createElement("style");
    style.textContent = `
      .glass-card, .panel, .stat-card, .eco-tile, .card, .download-card, .info-section {
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s ease, border-color 0.3s ease;
      }
      .glass-card:hover, .panel:hover, .stat-card:hover, .eco-tile:hover, .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0,255,136,0.08), 0 0 1px rgba(0,255,136,0.15);
      }
      @media (max-width: 768px) {
        .glass-card:hover, .panel:hover, .stat-card:hover, .eco-tile:hover, .card:hover {
          transform: none;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // === NAVBAR GLASS EFFECT ===
  function initNavGlass() {
    const style = document.createElement("style");
    style.textContent = `
      header, .header, nav, .navbar {
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
      }
    `;
    document.head.appendChild(style);
  }

  // === ORB FLOAT KEYFRAME ===
  function injectKeyframes() {
    const style = document.createElement("style");
    style.textContent = `
      @keyframes verdis-orb-float {
        0% { transform: translate(0,0) scale(1); }
        50% { transform: translate(50px,70px) scale(1.1); }
        100% { transform: translate(-40px,40px) scale(0.95); }
      }
    `;
    document.head.appendChild(style);
  }

  // === INIT ===
  function init() {
    try {
      injectKeyframes();
      initParticles();
      initGradientOrbs();
      initGlassmorphism();
      initNavGlass();
      // Delay scroll reveal slightly so DOM is fully ready
      setTimeout(initScrollReveal, 50);
      console.log("%c🌿 Verdis Web3 Animation Engine v2.0 loaded", "color:#00ff88;font-weight:bold");
    } catch(e) {
      console.warn("Verdis animation init error:", e);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
