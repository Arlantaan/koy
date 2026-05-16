document.addEventListener('DOMContentLoaded', () => {
  // Navigation links as tabs (single-section view)
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.menu-section');
  const searchInput = document.getElementById('menuSearch');
  const setActiveSection = (hash) => {
    const targetId = hash && hash.startsWith('#') ? hash : '#starters';
    sections.forEach(section => {
      section.classList.add('active');
      section.classList.remove('fade-in');
      void section.offsetWidth;
      section.classList.add('fade-in');
    });
    navLinks.forEach(link => {
      link.classList.toggle('active', link.getAttribute('href') === targetId);
    });
    if (history.replaceState) {
      history.replaceState(null, '', targetId);
    }
  };

  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const targetId = link.getAttribute('href');
      setActiveSection(targetId);
      const targetSection = document.querySelector(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  const applySearchFilter = () => {
    const query = (searchInput?.value || '').trim().toLowerCase();
    const cards = document.querySelectorAll('.menu-card');
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      card.closest('.col-12, .col-md-6, .col-lg-4')?.classList.toggle('d-none', query && !text.includes(query));
    });
  };

  if (searchInput) {
    searchInput.addEventListener('input', applySearchFilter);
  }

  const imageMap = {
    // Starters
    "arancini": "/images/aranchini.jpeg",
    "bao with shredded beef": "/images/Bao_buns_with_shredded_beef.jpeg",
    "mini burgers": "/images/mimib.jpeg",
    "cauliflower veloute with smoked salmon shavings": "https://images.pexels.com/photos/19367737/pexels-photo-19367737.jpeg?auto=compress&cs=tinysrgb&w=500",

    // Main courses
    "spicy garlic prawns": "/images/garlic.jpeg",
    "chicken supreme": "https://images.pexels.com/photos/33795738/pexels-photo-33795738.jpeg?auto=compress&cs=tinysrgb&w=500",
    "beef fillet with pepper sauce": "https://images.pexels.com/photos/34434635/pexels-photo-34434635.jpeg?auto=compress&cs=tinysrgb&w=500",
    "grilled maigre fish with sweet and sour tamarind sauce": "https://images.pexels.com/photos/6046671/pexels-photo-6046671.jpeg?auto=compress&cs=tinysrgb&w=500",
    "sea bream fillet with lemon beurre blanc": "https://images.pexels.com/photos/19615784/pexels-photo-19615784.jpeg?auto=compress&cs=tinysrgb&w=500",
    "penne with chicken and mushroom cream sauce": "https://images.pexels.com/photos/29160624/pexels-photo-29160624.jpeg?auto=compress&cs=tinysrgb&w=500",
    "pizza koya": "https://cdn.pixabay.com/photo/2020/08/17/14/16/pizza-5495544_1280.jpg",

    // Sharing mix
    "sharing mix for two": "https://images.pexels.com/photos/29253330/pexels-photo-29253330.jpeg?auto=compress&cs=tinysrgb&w=500",

    // Sides
    "mashed potatoes": "https://images.pexels.com/photos/7785366/pexels-photo-7785366.jpeg?auto=compress&cs=tinysrgb&w=500",
    "white rice": "https://images.pexels.com/photos/8423376/pexels-photo-8423376.png?auto=compress&cs=tinysrgb&w=500",
    "sauteed vegetables": "https://images.pexels.com/photos/5848483/pexels-photo-5848483.jpeg?auto=compress&cs=tinysrgb&w=500",
    "fries": "https://images.pexels.com/photos/14537711/pexels-photo-14537711.jpeg?auto=compress&cs=tinysrgb&w=500",
    "green salad": "https://images.pexels.com/photos/2750560/pexels-photo-2750560.jpeg?auto=compress&cs=tinysrgb&w=500",

    // Sauces
    "shallot sauce": "https://images.pexels.com/photos/18976994/pexels-photo-18976994.jpeg?auto=compress&cs=tinysrgb&w=500",
    "pepper sauce": "https://images.pexels.com/photos/8130681/pexels-photo-8130681.jpeg?auto=compress&cs=tinysrgb&w=500",
    "koya green sauce": "https://images.pexels.com/photos/5899677/pexels-photo-5899677.jpeg?auto=compress&cs=tinysrgb&w=500",
    "beurre blanc": "https://images.pexels.com/photos/19490391/pexels-photo-19490391.jpeg?auto=compress&cs=tinysrgb&w=500",

    // Desserts
    "profiteroles with chocolate sauce": "https://images.pexels.com/photos/16402076/pexels-photo-16402076.jpeg?auto=compress&cs=tinysrgb&w=500",
    "italian tiramisu": "https://images.pexels.com/photos/12916029/pexels-photo-12916029.jpeg?auto=compress&cs=tinysrgb&w=500",
    "french toast brioche": "https://images.pexels.com/photos/4623075/pexels-photo-4623075.jpeg?auto=compress&cs=tinysrgb&w=500",
    "lemon cheesecake": "https://images.pexels.com/photos/10754937/pexels-photo-10754937.jpeg?auto=compress&cs=tinysrgb&w=500",
    "chocolate lava cake": "https://images.pexels.com/photos/20377567/pexels-photo-20377567.jpeg?auto=compress&cs=tinysrgb&w=500"
  };

  const fallbackImages = [
    "https://images.pexels.com/photos/6046671/pexels-photo-6046671.jpeg?auto=compress&cs=tinysrgb&w=500",
    "https://images.pexels.com/photos/29160624/pexels-photo-29160624.jpeg?auto=compress&cs=tinysrgb&w=500",
    "https://cdn.pixabay.com/photo/2020/08/17/14/16/pizza-5495544_1280.jpg"
  ];

  // Use local images set in HTML src attributes
  const cardImages = document.querySelectorAll('.menu-card img');
  cardImages.forEach((img) => {
    img.loading = "lazy";
    img.decoding = "async";
  });

  // Lightbox for larger image preview
  const lightbox = document.getElementById('imageLightbox');
  const lightboxImage = document.getElementById('lightboxImage');
  if (lightbox && lightboxImage) {
    cardImages.forEach(img => {
      img.style.cursor = 'zoom-in';
      img.addEventListener('click', (event) => {
        event.preventDefault();
        lightboxImage.src = img.src;
        lightboxImage.alt = img.alt || 'Menu item image';
        lightbox.classList.add('open');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
      });
    });

    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox || event.target === lightboxImage) {
        lightbox.classList.remove('open');
        lightbox.setAttribute('aria-hidden', 'true');
        lightboxImage.src = '';
        document.body.style.overflow = '';
        document.documentElement.style.overflow = '';
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && lightbox.classList.contains('open')) {
        lightbox.classList.remove('open');
        lightbox.setAttribute('aria-hidden', 'true');
        lightboxImage.src = '';
        document.body.style.overflow = '';
        document.documentElement.style.overflow = '';
      }
    });
  }

  // Always start at top of page
  window.scrollTo(0, 0);

  // Initialize from URL hash or default
  setActiveSection(window.location.hash);
  applySearchFilter();

  // Scroll-reveal: animate each menu card as it enters the viewport
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.menu-card').forEach((card, i) => {
    card.classList.add('reveal');
    card.style.transitionDelay = `${(i % 6) * 55}ms`;
    revealObserver.observe(card);
  });
});
