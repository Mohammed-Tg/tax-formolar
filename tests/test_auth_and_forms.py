from flask import url_for


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_index_redirects(client):
    resp = client.get('/')
    # index redirects to login
    assert resp.status_code in (301, 302)


def test_login_and_dashboard_access(client, db):
    from tests.conftest import create_user
    # create user
    user = create_user(db, username='tester', email='tester@example.com', password='secret')

    resp = login(client, 'tester', 'secret')
    assert resp.status_code == 200
    # After login should contain dashboard text (check decoded text)
    text = resp.get_data(as_text=True)
    assert ('Übersicht' in text) or ('Willkommen' in text)


def test_protected_create_form_requires_login(client):
    # without login, access to create_form should redirect to login
    resp = client.get('/create_form')
    assert resp.status_code in (301, 302)


def test_delete_form(client, db):
    from tests.conftest import create_user
    from app.models.form import Form

    user = create_user(db, username='deleter', email='deleter@example.com', password='pw')

    # create a form for this user
    f = Form(title='T1', description='Desc', user_id=user.id)
    db.session.add(f)
    db.session.commit()

    # login
    login_resp = login(client, 'deleter', 'pw')
    assert login_resp.status_code == 200

    # delete via POST
    del_resp = client.post(f'/delete/{f.id}', follow_redirects=True)
    assert del_resp.status_code == 200
    # check flash message or absence of form in db
    remaining = Form.query.filter_by(id=f.id).first()
    assert remaining is None
