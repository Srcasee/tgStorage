async function loadJson(endpoint, target) {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`${endpoint}: ${response.status}`);
  }
  const data = await response.json();
  document.getElementById(target).textContent = JSON.stringify(data, null, 2);
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

loadAccounts().catch(console.error);
loadSources().catch(console.error);
loadResources().catch(console.error);
