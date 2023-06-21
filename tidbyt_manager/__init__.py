import os
from flask import Flask
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='lksdj;as987q3908475ukjhfgklauy983475iuhdfkjghairutyh',
    )
    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)
    # # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import manager
    app.register_blueprint(manager.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app