import os
from flask import Flask
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='lksdj;as987q3908475ukjhfgklauy983475iuhdfkjghairutyh',
        MAX_CONTENT_LENGTH = 1000 * 1000 # 1mbyte upload size limit
    )
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import manager
    app.register_blueprint(manager.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app