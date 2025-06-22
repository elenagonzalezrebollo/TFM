document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const body = document.body;
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

    function setTheme(theme) {
        body.classList.toggle('dark-mode', theme === 'dark');
        if (themeToggleButton) {
            const icon = themeToggleButton.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
        localStorage.setItem('theme', theme);

        const loadingSpinnerElement = document.getElementById('loading-spinner');
        if (loadingSpinnerElement) {
            const loader = loadingSpinnerElement.querySelector('l-grid');
            if (loader) {
                loader.color = theme === 'dark' ? 'white' : 'black';
            }
            
            const loaderText = loadingSpinnerElement.querySelector('p');
            if (loaderText) {
                loaderText.style.color = theme === 'dark' ? 'white' : 'black';
            }
            
            const logoImg = loadingSpinnerElement.querySelector('img');
            if (logoImg && logoImg.src.includes('icon.svg')) {
                const currentSrc = logoImg.src.split('?')[0];
                logoImg.src = `${currentSrc}?theme=${theme}`;
            }
        }
    }

    let currentTheme = localStorage.getItem('theme');
    if (!currentTheme) {
        currentTheme = prefersDarkScheme.matches ? 'dark' : 'light';
    }
    setTheme(currentTheme); 

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const newTheme = body.classList.contains('dark-mode') ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }

    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
});
