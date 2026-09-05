// A single overlay avoids clipping inside horizontally scrolling tables.
(() => {
  const tooltip = document.getElementById('context-help');
  let active = null;
  let hideTimer;
  let pinned = false;

  function hide() {
    clearTimeout(hideTimer);
    active?.removeAttribute('aria-describedby');
    active = null;
    pinned = false;
    tooltip.hidden = true;
  }

  function show(trigger) {
    clearTimeout(hideTimer);
    const definition = document.getElementById(`definition-${trigger.dataset.help}`);
    if (!definition) return;
    if (active !== trigger) hide();
    active = trigger;
    tooltip.textContent = definition.textContent;
    tooltip.hidden = false;
    trigger.setAttribute('aria-describedby', tooltip.id);
    const rect = trigger.getBoundingClientRect();
    const left = Math.max(12, Math.min(rect.left, innerWidth - tooltip.offsetWidth - 12));
    const below = rect.bottom + 8;
    const top = below + tooltip.offsetHeight <= innerHeight - 12 ? below : Math.max(12, rect.top - tooltip.offsetHeight - 8);
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  }

  document.addEventListener('pointerover', e => {
    if (e.pointerType === 'touch') return;
    if (tooltip.contains(e.target)) clearTimeout(hideTimer);
    const trigger = e.target.closest('[data-help]');
    if (trigger && !pinned) show(trigger);
  });
  document.addEventListener('pointerout', e => {
    if (pinned || e.pointerType === 'touch' || active === document.activeElement) return;
    if (active?.contains(e.relatedTarget) || tooltip.contains(e.relatedTarget)) return;
    if (active?.contains(e.target) || tooltip.contains(e.target)) hideTimer = setTimeout(hide, 150);
  });
  document.addEventListener('focusin', e => {
    const trigger = e.target.closest('[data-help]');
    if (trigger) show(trigger);
    else hide();
  });
  document.addEventListener('click', e => {
    const trigger = e.target.closest('[data-help]');
    if (trigger) {
      if (active === trigger && pinned) hide();
      else { show(trigger); pinned = true; }
    } else if (!tooltip.contains(e.target)) hide();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') hide(); });
  document.addEventListener('scroll', hide, true);
  window.addEventListener('resize', hide);
})();
