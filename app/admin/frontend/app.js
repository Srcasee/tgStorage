async function loadJson(endpoint, target) {
  const response = await fetch(endpoint);
  if (!response.ok) throw new Error(`${endpoint}: ${response.status}`);
  const data = await response.json();
  document.getElementById(target).textContent = JSON.stringify(data, null, 2);
}

async function sendJson(endpoint, method, body = null) {
  const response = await fetch(endpoint, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) throw new Error(`${endpoint}: ${response.status}`);
  return response.status === 204 ? null : response.json();
}

function showError(error) {
  console.error(error);
  alert(error.message);
}

async function loadAccounts() { return loadJson('/api/v2/admin/accounts', 'accounts'); }
async function loadSources() { return loadJson('/api/v2/admin/sources', 'sources'); }
async function loadResources() { return loadJson('/api/v2/admin/resources', 'resources'); }

async function createAccount() {
  try {
    await sendJson('/api/v2/admin/accounts', 'POST', {
      name: document.getElementById('account-name').value,
      session_path: document.getElementById('account-session').value,
    });
    await loadAccounts();
  } catch (error) { showError(error); }
}

async function updateAccount(id, enabled) {
  try {
    await sendJson(`/api/v2/admin/accounts/${id}`, 'PATCH', { enabled });
    await loadAccounts();
  } catch (error) { showError(error); }
}

async function deleteAccount(id) {
  try {
    await sendJson(`/api/v2/admin/accounts/${id}`, 'DELETE');
    await loadAccounts();
  } catch (error) { showError(error); }
}

async function createSource() {
  try {
    await sendJson('/api/v2/admin/sources', 'POST', {
      account_id: Number(document.getElementById('source-account').value),
      chat_id: Number(document.getElementById('source-chat').value),
      title: document.getElementById('source-title').value,
    });
    await loadSources();
  } catch (error) { showError(error); }
}

async function updateSource(id, enabled) {
  try {
    await sendJson(`/api/v2/admin/sources/${id}`, 'PATCH', { enabled });
    await loadSources();
  } catch (error) { showError(error); }
}

async function deleteSource(id) {
  try {
    await sendJson(`/api/v2/admin/sources/${id}`, 'DELETE');
    await loadSources();
  } catch (error) { showError(error); }
}

loadAccounts().catch(console.error);
loadSources().catch(console.error);
loadResources().catch(console.error);
