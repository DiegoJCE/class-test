# PLAN

Stack: plain `index.html` + `style.css` + `app.js` (vanilla JS, no build, no dependencies).
Run: `python -m http.server 8000` then open http://localhost:8000 (or just double-click `index.html`).

- [x] 1. Build the working calculator: `index.html` with a title and form (bill input, tip buttons 15/18/20, custom tip % input, people input, results area), plus `app.js` with a pure `calculate(bill, tipPercent, people)` function returning `{tip, total, perPerson}`, wired so results (tip, total, per-person) update live on every keystroke (`input` events) and the selected tip button is highlighted; verify: bill 50 + 20% shows tip $10.00, total $60.00; bill 90, custom 10%, 3 people shows per-person $33.00; changing any field updates results without clicking anything.
- [ ] 2. Handle bad input: empty, negative, non-numeric, or zero people show a friendly message / "$0.00" instead of NaN or Infinity, and never throw; verify: clearing fields or typing -5 shows no NaN and no console errors.
- [ ] 3. Add `style.css` for a clean, centered card layout with readable results that looks decent for a demo; verify: page looks good on desktop and narrow (mobile-width) windows.
