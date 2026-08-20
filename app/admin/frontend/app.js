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
  await sendJson('/api/v2/admin/accounts', 'POST', {
    name: document.getElementById('account-name').value,
    session_path: document.getElementById('account-session').value,
  });
  await loadAccounts();
}

async function createSource() {
  await sendJson('/api/v2/admin/sources', 'POST', {
    account_id: Number(document.getElementById('source-account').value),
    chat_id: Number(document.getElementById('source-chat').value),
    title: document.getElementById('source-title').value,
  });
  await loadSources();
}

loadAccounts().catch(console.error);
loadSources().catch(console.error);
loadResources().catch(console.error);
