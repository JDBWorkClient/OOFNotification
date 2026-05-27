const display = document.getElementById('display');
const history = document.getElementById('history');
let currentValue = '0';
let storedValue = null;
let pendingOperator = null;
let waitingForNewValue = false;

function updateDisplay() {
  display.textContent = currentValue;
  history.textContent = storedValue !== null && pendingOperator ? `${storedValue} ${pendingOperator}` : '';
}

function formatResult(value) {
  const str = String(value);
  if (str.length > 12 && !str.includes('e')) {
    return Number(value).toPrecision(12).replace(/\.\.?0+$/, '');
  }
  return str;
}

function calculate(firstValue, secondValue, operator) {
  const a = parseFloat(firstValue);
  const b = parseFloat(secondValue);
  if (operator === '+') return a + b;
  if (operator === '-') return a - b;
  if (operator === '*') return a * b;
  if (operator === '/') return b === 0 ? 'Error' : a / b;
  return secondValue;
}

function handleDigit(digit) {
  if (waitingForNewValue) {
    currentValue = digit;
    waitingForNewValue = false;
  } else {
    currentValue = currentValue === '0' ? digit : currentValue + digit;
  }
  updateDisplay();
}

function handleDecimal() {
  if (waitingForNewValue) {
    currentValue = '0.';
    waitingForNewValue = false;
  } else if (!currentValue.includes('.')) {
    currentValue += '.';
  }
  updateDisplay();
}

function handleOperator(operator) {
  if (pendingOperator && !waitingForNewValue) {
    currentValue = String(calculate(storedValue, currentValue, pendingOperator));
    storedValue = currentValue === 'Error' ? null : currentValue;
  } else {
    storedValue = currentValue;
  }

  pendingOperator = operator;
  waitingForNewValue = true;
  updateDisplay();
}

function handleEquals() {
  if (!pendingOperator || waitingForNewValue) return;
  currentValue = String(calculate(storedValue, currentValue, pendingOperator));
  pendingOperator = null;
  storedValue = null;
  waitingForNewValue = true;
  updateDisplay();
}

function handleClear() {
  currentValue = '0';
  storedValue = null;
  pendingOperator = null;
  waitingForNewValue = false;
  updateDisplay();
}

function handleToggleSign() {
  if (currentValue === '0' || currentValue === 'Error') return;
  currentValue = currentValue.startsWith('-') ? currentValue.slice(1) : `-${currentValue}`;
  updateDisplay();
}

function handlePercent() {
  if (currentValue === 'Error') return;
  currentValue = String(parseFloat(currentValue) / 100);
  updateDisplay();
}

const buttonGrid = document.querySelector('.calculator-buttons');
buttonGrid.addEventListener('click', event => {
  const button = event.target.closest('button');
  if (!button) return;

  const action = button.dataset.action;
  const value = button.dataset.value;

  if (action === 'digit') handleDigit(value);
  if (action === 'decimal') handleDecimal();
  if (action === 'operator') handleOperator(value);
  if (action === 'equals') handleEquals();
  if (action === 'clear') handleClear();
  if (action === 'toggle-sign') handleToggleSign();
  if (action === 'percent') handlePercent();
});

window.addEventListener('keydown', event => {
  if (event.key >= '0' && event.key <= '9') handleDigit(event.key);
  if (event.key === '.') handleDecimal();
  if (event.key === 'Enter' || event.key === '=') handleEquals();
  if (event.key === 'Backspace') handleClear();
  if (['+', '-', '*', '/'].includes(event.key)) handleOperator(event.key);
  if (event.key === '%') handlePercent();
});

updateDisplay();
