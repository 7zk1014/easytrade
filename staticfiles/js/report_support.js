document.addEventListener('DOMContentLoaded', function() {
    // Ensure navbar is always visible
    const navbar = document.querySelector('.navbar');
    const mainContent = document.querySelector('main') || document.querySelector('#content') || document.querySelector('.container');
    
    if (navbar) {
        // Force navbar visibility
        navbar.style.opacity = '1';
        navbar.style.visibility = 'visible';
        navbar.style.display = 'flex';
        navbar.style.position = 'sticky';
        navbar.style.top = '0';
        navbar.style.zIndex = '1000';
        
        // Remove classes that might cause navbar to disappear
        navbar.classList.remove('fade-out', 'auto-hide');
        
        // Disable any animations that might affect the navbar
        navbar.style.animation = 'none';
        navbar.style.transition = 'none';
    }
    
    if (mainContent) {
        // Ensure main content is visible
        mainContent.style.opacity = '1';
        mainContent.style.visibility = 'visible';
        mainContent.style.display = 'block';
    }
    
    // Force all main sections to be visible
    document.querySelectorAll('section, .hero-section, .support-options, .faq-section, .report-form-section, .contact-section').forEach(section => {
        if (section) {
            section.style.opacity = '1';
            section.style.visibility = 'visible';
            section.style.display = 'block';
        }
    });
    
    // Disable timers that might cause elements to disappear
    const timers = window.setTimeout(function() {}, 0);
    for (let i = 0; i <= timers; i++) {
        window.clearTimeout(i);
    }
    
    // Smooth scroll to anchors
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Handle report form submission
    const reportForm = document.querySelector('.report-form');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Form validation logic can be added here
            
            // Simulate form submission
            alert('Thank you for your feedback! Our support team will address your issue as soon as possible.');
            this.reset();
        });
    }
    
    // Handle contact form submission
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Form validation logic can be added here
            
            // Simulate form submission
            alert('Your message has been sent! We will get back to you soon.');
            this.reset();
        });
    }
    
    // Add fade-in effects
    const fadeElements = document.querySelectorAll('.support-card, .accordion-item, .form-wrapper, .contact-form-wrapper');
    
    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    fadeElements.forEach(element => {
        element.classList.add('fade-in');
        fadeInObserver.observe(element);
    });
});

// Add fade-in animation CSS classes
document.head.insertAdjacentHTML('beforeend', `
    <style>
        .fade-in {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .fade-in-visible {
            opacity: 1;
            transform: translateY(0);
        }
    </style>
`);