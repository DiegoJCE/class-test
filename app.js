function calculate(bill, tipPercent, people) {
  const ok = n => typeof n === 'number' && isFinite(n);
  if (!ok(bill) || bill < 0 || !ok(tipPercent) || tipPercent < 0) {
    return { tip: 0, total: 0, perPerson: 0 };
  }
  const tip = bill * tipPercent / 100;
  const total = bill + tip;
  const perPerson = ok(people) && people >= 1 ? total / Math.floor(people) : 0;
  return { tip, total, perPerson };
}

function validate(bill, tipPercent, people) {
  const bad = n => !isFinite(n);
  if (bad(bill)) return 'Enter a bill amount to get started.';
  if (bill < 0) return 'Bill amount cannot be negative.';
  if (bad(tipPercent)) return 'Enter a valid tip percentage.';
  if (tipPercent < 0) return 'Tip percentage cannot be negative.';
  if (bad(people) || people < 1) return 'Number of people must be at least 1.';
  return '';
}

if (typeof module !== 'undefined') module.exports = { calculate, validate };

if (typeof document !== 'undefined') {
  const billEl = document.getElementById('bill');
  const customEl = document.getElementById('custom-tip');
  const peopleEl = document.getElementById('people');
  const buttons = document.querySelectorAll('#tip-buttons button');
  let selectedTip = 15;

  const fmt = n => '$' + n.toFixed(2);

  function highlight() {
    buttons.forEach(b => b.classList.toggle('selected',
      customEl.value === '' && Number(b.dataset.tip) === selectedTip));
    customEl.classList.toggle('selected', customEl.value !== '');
  }

  function update() {
    const tipPercent = customEl.value !== '' ? parseFloat(customEl.value) : selectedTip;
    const bill = parseFloat(billEl.value);
    const people = parseFloat(peopleEl.value);
    const r = calculate(bill, tipPercent, people);
    document.getElementById('message').textContent = validate(bill, tipPercent, people);
    document.getElementById('tip').textContent = fmt(r.tip);
    document.getElementById('total').textContent = fmt(r.total);
    document.getElementById('per-person').textContent = fmt(r.perPerson);
    highlight();
  }

  buttons.forEach(b => b.addEventListener('click', () => {
    selectedTip = Number(b.dataset.tip);
    customEl.value = '';
    update();
  }));
  [billEl, customEl, peopleEl].forEach(el => el.addEventListener('input', update));
  update();
}
