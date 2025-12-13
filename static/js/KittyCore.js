/* ===============================
 MODAL STUFF FOR ACOUSTIC AND ELECTRIC KITTY
================================= */

document.addEventListener('DOMContentLoaded', () => {
  const helpBtn = document.getElementById('helpBtn');
  const dropdown = helpBtn?.parentElement;
  const dropdownMenu = document.getElementById('dropdownMenu');
  const modal = document.getElementById('helpModal');
  const guideModal = document.getElementById('guideModal');
  const closeModal = document.getElementById('closeModal');
  const closeGuide = document.getElementById('closeGuide');
  const closeGuideBottom = document.getElementById('closeGuideBottom');
  const openGuideBtn = document.getElementById('openGuideBtn');
  const floatingBackToTop = document.getElementById('floatingBackToTop');

  // ================================== BACK TO TOP ==================================
  const showBackToTop = () => {
    if (floatingBackToTop) {
      floatingBackToTop.classList.add('visible');
    }
  };

  const hideBackToTop = () => {
    if (floatingBackToTop) {
      floatingBackToTop.classList.remove('visible');
    }
  };

  if (floatingBackToTop && guideModal) {
    const guideContent = guideModal.querySelector('.modal-content');
    
    floatingBackToTop.onclick = () => {
      if (guideContent) {
        guideContent.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      }
    };

    if (guideContent) {
      guideContent.addEventListener('scroll', () => {
        if (guideContent.scrollTop > 150) {
          showBackToTop();
        } else {
          hideBackToTop();
        }
      });
    }
  }

  // ================================== DROP DOWN ==================================
  if (helpBtn && dropdown) {
    helpBtn.onclick = (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('active');
    };

    document.addEventListener('click', () => {
      dropdown.classList.remove('active');
    });

    if (dropdownMenu) {
      dropdownMenu.onclick = (e) => e.stopPropagation();
    }
  }

  // ================================== MAIN MODAL ==================================
  const openMainHelp = document.getElementById('openMainHelp');
  if (openMainHelp && modal) {
    openMainHelp.onclick = () => {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      if (dropdown) dropdown.classList.remove('active');
    };
  }

  if (closeModal && modal) {
    closeModal.onclick = () => {
      modal.style.display = 'none';
      document.body.style.overflow = 'auto';
    };

    modal.onclick = (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
      }
    };
  }

  // ================================== GUIDE MODAL ==================================
  const openGuide = document.getElementById('openGuide');
  if (openGuide && guideModal) {
    openGuide.onclick = () => {
      guideModal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
      if (dropdown) dropdown.classList.remove('active');
      showBackToTop();
    };
  }

  if (openGuideBtn && modal && guideModal) {
    openGuideBtn.onclick = () => {
      modal.style.display = 'none';
      guideModal.style.display = 'flex';
      showBackToTop();
    };
  }

  const closeGuideFn = () => {
    if (guideModal) {
      guideModal.style.display = 'none';
      document.body.style.overflow = 'auto';
      hideBackToTop();
    }
  };

  if (closeGuide) closeGuide.onclick = closeGuideFn;
  if (closeGuideBottom) closeGuideBottom.onclick = closeGuideFn;

  if (guideModal) {
    guideModal.onclick = (e) => {
      if (e.target === guideModal) closeGuideFn();
    };
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (modal) modal.style.display = 'none';
      if (guideModal) guideModal.style.display = 'none';
      document.body.style.overflow = 'auto';
      hideBackToTop();
    }
  });


// ==================== LEFT DROPDOWN MENU ====================
    const menuTrigger = document.querySelector('.menu-trigger');
    const leftDropdown = document.querySelector('.left-dropdown');

    if (menuTrigger && leftDropdown) {
        menuTrigger.onclick = (e) => {
            e.stopPropagation();
            leftDropdown.classList.toggle('active');
        };

        document.addEventListener('click', () => {
            leftDropdown.classList.remove('active');
        });

        document.querySelector('.left-menu')?.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

});



