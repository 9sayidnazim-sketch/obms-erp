/**
 * ========================================================
 * OBMS ERP - OCTAPUS SYSTEM: CLEAN SPLIT-SCREEN AUTH JS
 * ========================================================
 */
(function() {
  function applyOctapusAuthEnhancements() {
    const loginContainer = document.querySelector('.login-container');
    if (!loginContainer) return;

    // 1. Inject Left Hero Panel if not present
    if (!document.getElementById('octapus-hero-panel')) {
      const heroPanel = document.createElement('div');
      heroPanel.id = 'octapus-hero-panel';
      heroPanel.className = 'octapus-hero-panel';
      heroPanel.innerHTML = `
        <!-- Circular Back Button -->
        <button class="back-btn" title="Back" onclick="window.history.back()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
        </button>

        <!-- Full-Bleed Brand Asset Image -->
        <img
          src="/assets/auth-hero-asset.jpg"
          alt="OBMS ERP Growth Illustration"
          class="hero-img"
        />

        <!-- Floating Octapus Branding Pill -->
        <div class="hero-branding-pill">
          <span class="brand-dot"></span>
          <span>OBMS ERP &bull; Powered by Octapus System</span>
        </div>
      `;
      loginContainer.insertBefore(heroPanel, loginContainer.firstChild);
    }

    const loginWrapper = document.querySelector('.login-container .login-wrapper');
    if (!loginWrapper) return;

    // 2. Update Titles
    const titleEl = loginWrapper.querySelector('#title, .title');
    if (titleEl && titleEl.textContent !== 'Welcome Back') {
      titleEl.textContent = 'Welcome Back';
    }

    const subTitleEl = loginWrapper.querySelector('.sub-title');
    if (subTitleEl && !subTitleEl.querySelector('.signup-link')) {
      subTitleEl.innerHTML = `Don't have an account? <a class="signup-link" href="#/auth/register">Sign up</a>`;
    }

    const form = loginWrapper.querySelector('form');
    if (form) {
      // 3. Inject 1-Click Role Quick Access Box above form
      if (!document.getElementById('octapus-demo-bar')) {
        const demoBar = document.createElement('div');
        demoBar.id = 'octapus-demo-bar';
        demoBar.className = 'octapus-demo-bar';
        demoBar.innerHTML = `
          <div class="octapus-demo-bar-title">
            <span>Quick 1-Click Access</span>
            <span style="color:#2563EB; font-size:10.5px; font-weight:600;">Super Admin • Staff</span>
          </div>
          <div class="octapus-demo-pills">
            <div class="octapus-demo-pill" id="pill-super-admin" title="1-Click Login as Super Administrator">
              <span class="role-name">👑 Super Admin</span>
              <span class="role-hint">admin / admin123</span>
            </div>
            <div class="octapus-demo-pill" id="pill-org-admin" title="1-Click Login as Workspace Administrator">
              <span class="role-name">💼 Workspace Admin</span>
              <span class="role-hint">admin / admin123</span>
            </div>
            <div class="octapus-demo-pill" id="pill-employee" title="1-Click Login as Employee">
              <span class="role-name">👤 Staff Member</span>
              <span class="role-hint">employee / 12345678</span>
            </div>
          </div>
        `;

        form.parentNode.insertBefore(demoBar, form);

        function fillAndSubmit(emailVal, passVal, nativeBtnIndex) {
          const nativeBtns = document.querySelectorAll('.demo-credentials-buttons button');
          if (nativeBtns && nativeBtns[nativeBtnIndex]) {
            nativeBtns[nativeBtnIndex].click();
            return;
          }

          const emailInput = document.getElementById('input-email');
          const passInput = document.getElementById('input-password');
          if (emailInput && passInput) {
            emailInput.value = emailVal;
            emailInput.dispatchEvent(new Event('input', { bubbles: true }));
            emailInput.dispatchEvent(new Event('change', { bubbles: true }));

            passInput.value = passVal;
            passInput.dispatchEvent(new Event('input', { bubbles: true }));
            passInput.dispatchEvent(new Event('change', { bubbles: true }));

            const btn = form.querySelector('button.submit-btn');
            if (btn) {
              btn.removeAttribute('disabled');
              btn.click();
            }
          }
        }

        const pSuper = document.getElementById('pill-super-admin');
        const pAdmin = document.getElementById('pill-org-admin');
        const pEmp = document.getElementById('pill-employee');

        if (pSuper) {
          pSuper.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.octapus-demo-pill').forEach(p => p.classList.remove('active'));
            pSuper.classList.add('active');
            fillAndSubmit('admin', 'admin123', 0);
          });
        }

        if (pAdmin) {
          pAdmin.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.octapus-demo-pill').forEach(p => p.classList.remove('active'));
            pAdmin.classList.add('active');
            fillAndSubmit('admin', 'admin123', 1);
          });
        }

        if (pEmp) {
          pEmp.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.octapus-demo-pill').forEach(p => p.classList.remove('active'));
            pEmp.classList.add('active');
            fillAndSubmit('employee@ever.co', '12345678', 2);
          });
        }
      }

      // 4. Update Submit Button text to "Sign In" and style as solid black
      const submitBtn = form.querySelector('button.submit-btn');
      if (submitBtn) {
        if (submitBtn.textContent.trim() !== 'Sign In') {
          submitBtn.textContent = 'Sign In';
        }
        submitBtn.style.setProperty('background', '#000000', 'important');
        submitBtn.style.setProperty('background-color', '#000000', 'important');
        submitBtn.style.setProperty('border-color', '#000000', 'important');
        submitBtn.style.setProperty('color', '#FFFFFF', 'important');
      }

      // 5. Inject "or" Divider and Social Buttons (Google + GitHub)
      if (!document.getElementById('octapus-social-section')) {
        const socialSection = document.createElement('div');
        socialSection.id = 'octapus-social-section';
        socialSection.innerHTML = `
          <div class="octapus-or-divider">
            <span>or</span>
          </div>
          <div class="octapus-social-grid">
            <a class="octapus-social-btn" href="/api/auth/google">
              <svg viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continue with Google</span>
            </a>
            <a class="octapus-social-btn" href="/api/auth/github">
              <svg fill="#24292f" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <span>Continue with GitHub</span>
            </a>
          </div>
        `;
        form.appendChild(socialSection);
      }
    }
  }

  // Purge any demo account banner anywhere in the DOM
  function purgeDemoBanners() {
    const banners = document.querySelectorAll('.notification-header, [class*="notification-header"]');
    banners.forEach(b => b.remove());
  }

  // Observe DOM additions to react when Angular finishes rendering the login route or headers
  const observer = new MutationObserver(() => {
    applyOctapusAuthEnhancements();
    purgeDemoBanners();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });

  window.addEventListener('hashchange', () => {
    applyOctapusAuthEnhancements();
    purgeDemoBanners();
  });
  window.addEventListener('popstate', () => {
    applyOctapusAuthEnhancements();
    purgeDemoBanners();
  });
  window.addEventListener('DOMContentLoaded', () => {
    applyOctapusAuthEnhancements();
    purgeDemoBanners();
  });
  setInterval(() => {
    applyOctapusAuthEnhancements();
    purgeDemoBanners();
  }, 250);
})();
