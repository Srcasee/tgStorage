from pathlib import Path


def test_admin_frontend_assets_exist():
    frontend = Path('app/admin/frontend')

    assert (frontend / 'index.html').exists()
    assert (frontend / 'app.js').exists()
    assert (frontend / 'style.css').exists()


def test_admin_frontend_contains_api_contracts():
    js = (Path('app/admin/frontend') / 'app.js').read_text()

    assert '/api/v2/admin/accounts' in js
    assert '/api/v2/admin/sources' in js
    assert '/api/v2/admin/resources' in js

    assert 'createAccount' in js
    assert 'createSource' in js
    assert 'updateAccount' in js
    assert 'deleteAccount' in js
    assert 'updateSource' in js
    assert 'deleteSource' in js
