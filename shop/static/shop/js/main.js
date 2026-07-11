document.addEventListener('DOMContentLoaded', function () {

    // ---------- Hero carousel ----------
    const banner = document.getElementById('heroBanner');
    if (banner) {
        const slides = banner.querySelectorAll('.hero-slide');
        const dots = banner.querySelectorAll('.hero-dots span');
        const prevBtn = banner.querySelector('.hero-arrow-left');
        const nextBtn = banner.querySelector('.hero-arrow-right');
        let current = 0;
        let timer = null;

        function goTo(index) {
            if (!slides.length) return;
            current = (index + slides.length) % slides.length;
            slides.forEach((slide, i) => slide.classList.toggle('active', i === current));
            dots.forEach((dot, i) => dot.classList.toggle('active', i === current));
        }

        function next() { goTo(current + 1); }
        function prev() { goTo(current - 1); }

        function startAutoplay() {
            stopAutoplay();
            timer = setInterval(next, 5000);
        }
        function stopAutoplay() {
            if (timer) clearInterval(timer);
        }

        if (prevBtn) prevBtn.addEventListener('click', () => { prev(); startAutoplay(); });
        if (nextBtn) nextBtn.addEventListener('click', () => { next(); startAutoplay(); });
        dots.forEach((dot, i) => dot.addEventListener('click', () => { goTo(i); startAutoplay(); }));

        banner.addEventListener('mouseenter', stopAutoplay);
        banner.addEventListener('mouseleave', startAutoplay);

        goTo(0);
        startAutoplay();
    }

    // ---------- Category menu scroll ----------
    const list = document.getElementById('categoryList');
    if (list) {
        const leftBtn = document.querySelector('.category-scroll-left');
        const rightBtn = document.querySelector('.category-scroll-right');
        const step = 220;

        function updateArrows() {
            if (!leftBtn || !rightBtn) return;
            leftBtn.classList.toggle('is-hidden', list.scrollLeft <= 0);
            rightBtn.classList.toggle(
                'is-hidden',
                list.scrollLeft + list.clientWidth >= list.scrollWidth - 1
            );
        }

        if (leftBtn) leftBtn.addEventListener('click', () => {
            list.scrollBy({ left: -step, behavior: 'smooth' });
        });
        if (rightBtn) rightBtn.addEventListener('click', () => {
            list.scrollBy({ left: step, behavior: 'smooth' });
        });

        list.addEventListener('scroll', updateArrows);
        window.addEventListener('resize', updateArrows);
        updateArrows();
    }

});
