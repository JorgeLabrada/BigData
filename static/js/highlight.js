/**
 * Vinyl – Term Highlighting & Expand/Collapse
 * Author: Jorge Alfonso Labrada Ramos (vape)
 */

(function () {
  /* ── Highlight query terms in snippets ── */
  document.querySelectorAll('.result-snippet[data-terms]').forEach((el) => {
    const terms = el.dataset.terms.trim().split(/\s+/).filter(Boolean);
    if (!terms.length) return;

    let html = el.innerHTML;
    terms.forEach((term) => {
      // Escape regex special chars
      const safe = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const re = new RegExp(`(${safe})`, 'gi');
      html = html.replace(re, '<mark>$1</mark>');
    });
    el.innerHTML = html;
  });

  /* ── Expand / Collapse full text ── */
  window.toggleExpand = function (btn) {
    const snippet = btn.closest('.result-card').querySelector('.result-snippet');
    const expanded = snippet.classList.toggle('expanded');
    btn.textContent = expanded ? 'Show less' : 'Show full text';
  };
})();
