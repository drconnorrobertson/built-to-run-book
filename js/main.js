// Built to Run - Main JS
document.addEventListener('DOMContentLoaded', function() {
  // Mobile nav toggle
  const toggle = document.querySelector('.mobile-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', function() {
      nav.classList.toggle('active');
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', !expanded);
    });
    document.addEventListener('click', function(e) {
      if (!e.target.closest('.site-header')) {
        nav.classList.remove('active');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Header scroll effect
  const header = document.querySelector('.site-header');
  if (header) {
    window.addEventListener('scroll', function() {
      header.style.boxShadow = window.scrollY > 10
        ? '0 1px 8px rgba(0,0,0,0.06)' : 'none';
    });
  }

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Intersection Observer for fade-in
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.framework-card, .testimonial-card, .chapter-item, .blog-card, .resource-card, .framework-full-card').forEach(function(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // Contact form handler
  const form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.textContent = 'Message Sent!';
      btn.style.background = '#16a34a';
      setTimeout(function() {
        btn.textContent = 'Send Message';
        btn.style.background = '';
        form.reset();
      }, 3000);
    });
  }
});
