function calculate(bill, tipPercent, people) {
  const tip = bill * tipPercent / 100;
  const total = bill + tip;
  const perPerson = total / people;
  return { tip, total, perPerson };
}

if (typeof module !== 'undefined') module.exports = { calculate };

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
    const r = calculate(parseFloat(billEl.value), tipPercent, parseFloat(peopleEl.value));
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
