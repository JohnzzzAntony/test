/**
 * premium_ui.js
 * Handle luxury animations, 3D visuals, and interactive micro-interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    initCustomCursor();
    initMagneticElements();
    initThreeJS();
    initScrollAnimations();
});

/**
 * 1. Custom Follower Cursor
 */
function initCustomCursor() {
    if (!designTokens.effects.cursor) return;

    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    const dot = document.createElement('div');
    dot.className = 'custom-cursor-dot';
    
    document.body.appendChild(cursor);
    document.body.appendChild(dot);

    window.addEventListener('mousemove', (e) => {
        gsap.to(cursor, {
            x: e.clientX - 16,
            y: e.clientY - 16,
            duration: 0.5,
            ease: "power3.out"
        });
        gsap.to(dot, {
            x: e.clientX - 3,
            y: e.clientY - 3,
            duration: 0.1,
            ease: "power3.out"
        });
    });

    // Hover effects
    document.querySelectorAll('a, button, .interactive').forEach(el => {
        el.addEventListener('mouseenter', () => {
            gsap.to(cursor, { scale: 1.5, borderColor: designTokens.accent, duration: 0.3 });
            gsap.to(dot, { scale: 0, duration: 0.3 });
        });
        el.addEventListener('mouseleave', () => {
            gsap.to(cursor, { scale: 1, borderColor: designTokens.primary, duration: 0.3 });
            gsap.to(dot, { scale: 1, duration: 0.3 });
        });
    });
}

/**
 * 2. Magnetic Buttons
 */
function initMagneticElements() {
    document.querySelectorAll('.magnetic').forEach(el => {
        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            gsap.to(el, {
                x: x * 0.3,
                y: y * 0.3,
                duration: 0.4,
                ease: "power3.out"
            });
        });
        el.addEventListener('mouseleave', () => {
            gsap.to(el, { x: 0, y: 0, duration: 0.6, ease: "elastic.out(1, 0.3)" });
        });
    });
}

/**
 * 3. Three.js Background Visuals
 */
function initThreeJS() {
    const container = document.getElementById('hero-canvas');
    if (!container || designTokens.effects.threejs === 'none') return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Fluid Abstract Geometry
    let geometry;
    if (designTokens.effects.threejs === 'fluid') {
        geometry = new THREE.IcosahedronGeometry(2, 20);
    } else {
        geometry = new THREE.TorusKnotGeometry(1, 0.3, 100, 16);
    }

    const material = new THREE.MeshNormalMaterial({ 
        wireframe: false,
        transparent: true,
        opacity: 0.3
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
    
    camera.position.z = 5;

    // Animation Loop
    const animate = () => {
        requestAnimationFrame(animate);
        mesh.rotation.x += 0.005;
        mesh.rotation.y += 0.005;
        
        // Mouse reaction
        const targetX = (window.mouseX || 0) * 0.0005;
        const targetY = (window.mouseY || 0) * 0.0005;
        mesh.rotation.x += targetY;
        mesh.rotation.y += targetX;

        renderer.render(scene, camera);
    };

    window.addEventListener('mousemove', (e) => {
        window.mouseX = e.clientX - window.innerWidth / 2;
        window.mouseY = e.clientY - window.innerHeight / 2;
    });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    animate();
}

/**
 * 4. Scroll Reveal Animations
 */
function initScrollAnimations() {
    if (!designTokens.effects.animations) return;
    
    gsap.registerPlugin(ScrollTrigger);

    document.querySelectorAll('.reveal').forEach(el => {
        gsap.from(el, {
            scrollTrigger: {
                trigger: el,
                start: "top 85%",
                toggleActions: "play none none none"
            },
            y: 50,
            opacity: 0,
            duration: 1,
            ease: "power4.out"
        });
    });
}
