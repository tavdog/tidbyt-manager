import pytest
from tidbyt_manager import create_app

@pytest.fixture()
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['path'] = './data'
    # from tidbyt_manager import auth
    # app.register_blueprint(auth.bp)

    # from tidbyt_manager import manager
    # app.register_blueprint(manager.bp)
    # app.add_url_rule('/', endpoint='index')

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()