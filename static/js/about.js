// 检查是否有任何自动隐藏或动画效果
document.addEventListener('DOMContentLoaded', function() {
    // 确保 hero section 保持可见
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        // 移除任何可能导致消失的类
        heroSection.classList.remove('fade-out', 'auto-hide');
        
        // 确保元素可见
        heroSection.style.opacity = '1';
        heroSection.style.visibility = 'visible';
        heroSection.style.display = 'block';
    }
    
    // 禁用任何可能导致元素消失的定时器
    const timers = window.setTimeout(function() {}, 0);
    for (let i = 0; i <= timers; i++) {
        window.clearTimeout(i);
    }
});

const fadeElements = document.querySelectorAll('.value-card, .timeline-item, .team-card');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

fadeElements.forEach(element => {
    element.classList.add('fade-in');
    observer.observe(element);
});

const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Thank you for your message! We will get back to you soon.');
        contactForm.reset();
    });
}
