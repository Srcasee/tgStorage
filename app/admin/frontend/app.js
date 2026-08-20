async function load(endpoint, target) {
  const response = await fetch(endpoint);
  const data = await response.json();
  document.getElementById(target).textContent = JSON.stringify(data, null, 2);
}

load('/api/v2/admin/accounts', 'accounts').catch(console.error);
load('/api/v2/admin/sources', 'sources').catch(console.error);
load('/api/v2/admin/resources', 'resources').catch(console.error);
