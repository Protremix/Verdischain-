file_path = "/app/conversations/6a6cb8454bc0607c481bb5eb/verdis-landing.html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

responsive_addition = """@media (max-width: 1024px) {
      .features-grid { grid-template-columns: repeat(2,1fr); }
      .validators-grid { grid-template-columns: repeat(2,1fr); }
      .circle-grid { grid-template-columns: repeat(2,1fr); }
      .tokenomics-layout { grid-template-columns: 1fr; gap: 32px; }
      .footer-inner { grid-template-columns: 1fr 1fr; }
      .hero-title { font-size: 42px; }
      .hero-visual { transform: scale(0.9); transform-origin: center center; }
    }
    @media (max-width: 768px) {
      .nav-links { display: none; }
      .hero-container { flex-direction: column; min-height: auto; }
      .hero-left { padding: 100px 32px 40px; }
      .hero-right { padding: 20px; min-height: 500px; overflow: hidden; }
      .hero-visual { transform: scale(0.72); transform-origin: center center; }
      .hero-title { font-size: 32px; }
      .stats-grid { grid-template-columns: repeat(2,1fr); }
      .features-grid { grid-template-columns: 1fr; }
      .validators-grid { grid-template-columns: 1fr; }
      .circle-grid { grid-template-columns: repeat(2,1fr); }
      .arch-layer { flex-direction: column; align-items: flex-start; gap: 8px; }
      .arch-layer-name { min-width: auto; }
      .roadmap-track { flex-direction: column; gap: 24px; }
      .roadmap-track::before { display: none; }
      .cta-card { padding: 40px 24px; }
      .cta-card h2 { font-size: 24px; }
      .footer-inner { grid-template-columns: 1fr; gap: 24px; }
      .footer-bottom { flex-direction: column; gap: 8px; text-align: center; }
    }
    @media (max-width: 480px) {
      .hero-visual { transform: scale(0.55); transform-origin: center center; }
      .hero-right { min-height: 380px; }
      .stats-grid { grid-template-columns: 1fr; }
      .circle-grid { grid-template-columns: 1fr; }
      .hero-actions { flex-direction: column; }
    }"""

idx = text.find('@media (max-width: 1024px)')
style_end = text.find('</style>', idx)

text = text[:idx] + responsive_addition + '\n  ' + text[style_end:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Responsive CSS updated successfully!")
