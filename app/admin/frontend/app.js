async function loadJson(endpoint, target) {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`${endpoint}: ${response.status}`);
  }
  const data = await response.json();
  document.getElementById(target).textContent = JSON.stringify(data, null, 2);
}

async function sendJson(endpoint, method, body) {
  const response = await fetch(endpoint, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`${endpoint}: ${response.status}`);
  }

  return response.json();
}

function showError(error) {
  console.error(error);
  alert(error.message);
}

async function loadAccounts() {
  return loadJson('/api/v2/admin/accounts', 'accounts');
}

async function loadSources() {
  return loadJson('/api/v2/admin/sources', 'sources');
}

async function loadResources() {
  return loadJson('/api/v2/admin/resources', 'resources');
}

async function createAccount() {
  try {
    await sendJson('/api/v2/admin/accounts', 'POST', {
      name: document.getElementById('account-name').value,
      session_path: document.getElementById('account-session').value,
    });
    clearAccountForm();
    await loadAccounts();
  } catch (error) {
    showError(error);
  }
}

async function createSource() {
  try {
    await sendJson('/api/v2/admin/sources', 'POST', {
      account_id: Number(document.getElementById('source-account').value),
      chat_id: Number(document.getElementById('source-chat').value),
      title: document.getElementById('source-title').value,
    });
    clearSourceForm();
    await loadSources();
  } catch (error) {
    showError(error);
  }
}

function clearAccountForm() {
  document.getElementById('account-name').value = '';
  document.getElementById('account-session').value = '';
}

function clearSourceForm() {
  document.getElementById('source-account').value = '';
  document.getElementById('source-chat').value = '';
  document.getElementById('source-title').value = '';
}

loadAccounts().catch(console.error);
loadSources().catch(console.error);
loadResources().catch(console.error);
