document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.range-field').forEach(field => {
    const input = field.querySelector('input[type="range"]');
    const output = field.querySelector('output');
    const sync = () => output.textContent = input.value;
    input.addEventListener('input', sync);
    sync();
  });

  const dateInput = document.getElementById('record_date');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }
});
