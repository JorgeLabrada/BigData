/**
 * Vinyl – Autocomplete Enhancement (Enhancement C)
 * Author: Jorge Alfonso Labrada Ramos (vape)
 *
 * Features:
 *  - Debounced API calls to /api/autocomplete
 *  - Keyboard navigation (↑ ↓ Enter Escape)
 *  - Click-to-fill
 *  - Highlights matching prefix in suggestions
 */

(function () {
  const input = document.getElementById('searchInput');
  const list  = document.getElementById('autocompleteList');
  const wrap  = document.getElementById('searchWrap');

  if (!input || !list) return;

  let activeIndex = -1;
  let debounceTimer = null;
  let currentSuggestions = [];

  /* ── Debounce helper ── */
  function debounce(fn, delay) {
    return function (...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fn(...args), delay);
    };
  }

  /* ── Fetch suggestions from backend ── */
  async function fetchSuggestions(prefix) {
    if (!prefix || prefix.trim().length < 2) {
      hideSuggestions();
      return;
    }
    // Only autocomplete the LAST word the user is typing
    const words  = prefix.trim().split(/\s+/);
    const lastWord = words[words.length - 1];
    if (lastWord.length < 2) { hideSuggestions(); return; }

    try {
      const res = await fetch(`/api/autocomplete?q=${encodeURIComponent(lastWord)}&limit=8`);
      const data = await res.json();
      currentSuggestions = data.suggestions || [];
      renderSuggestions(lastWord, words.slice(0, -1));
    } catch (e) {
      hideSuggestions();
    }
  }

  /* ── Highlight the matching prefix inside a suggestion ── */
  function highlightPrefix(suggestion, prefix) {
    if (!prefix) return suggestion;
    const idx = suggestion.toLowerCase().indexOf(prefix.toLowerCase());
    if (idx === -1) return suggestion;
    return (
      suggestion.slice(0, idx) +
      '<strong>' + suggestion.slice(idx, idx + prefix.length) + '</strong>' +
      suggestion.slice(idx + prefix.length)
    );
  }

  /* ── Render the dropdown ── */
  function renderSuggestions(lastWord, prevWords) {
    list.innerHTML = '';
    activeIndex = -1;

    if (!currentSuggestions.length) { hideSuggestions(); return; }

    currentSuggestions.forEach((sug, i) => {
      const li = document.createElement('li');
      li.innerHTML = highlightPrefix(sug, lastWord);
      li.setAttribute('role', 'option');
      li.dataset.index = i;

      li.addEventListener('mousedown', (e) => {
        e.preventDefault(); // don't blur the input
        selectSuggestion(sug, prevWords);
      });

      list.appendChild(li);
    });

    list.classList.add('visible');
  }

  /* ── Fill input with the chosen suggestion ── */
  function selectSuggestion(suggestion, prevWords) {
    const newVal = prevWords.length
      ? prevWords.join(' ') + ' ' + suggestion
      : suggestion;
    input.value = newVal + ' ';
    input.focus();
    hideSuggestions();
  }

  /* ── Hide dropdown ── */
  function hideSuggestions() {
    list.classList.remove('visible');
    list.innerHTML = '';
    activeIndex = -1;
    currentSuggestions = [];
  }

  /* ── Keyboard navigation ── */
  input.addEventListener('keydown', (e) => {
    const items = list.querySelectorAll('li');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % items.length;
      updateActive(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + items.length) % items.length;
      updateActive(items);
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      const words = input.value.trim().split(/\s+/);
      const prevWords = words.slice(0, -1);
      selectSuggestion(currentSuggestions[activeIndex], prevWords);
    } else if (e.key === 'Escape') {
      hideSuggestions();
    }
  });

  function updateActive(items) {
    items.forEach((li, i) => {
      li.classList.toggle('active', i === activeIndex);
    });
    if (activeIndex >= 0) {
      items[activeIndex].scrollIntoView({ block: 'nearest' });
    }
  }

  /* ── Input event: trigger debounced fetch ── */
  const debouncedFetch = debounce(fetchSuggestions, 180);
  input.addEventListener('input', () => debouncedFetch(input.value));

  /* ── Hide on outside click ── */
  document.addEventListener('mousedown', (e) => {
    if (!wrap.contains(e.target)) hideSuggestions();
  });

  /* ── Hide on form submit ── */
  input.closest('form')?.addEventListener('submit', () => hideSuggestions());
})();
