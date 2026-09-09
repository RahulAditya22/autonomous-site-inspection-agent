from __future__ import annotations
from pathlib import Path

def create_app():
    from flask import Flask, jsonify
    from flask_cors import CORS
    from app.models.db import init_db
    from app.database.seed import seed
    from app.api.routes import api
    from app.config import settings
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=settings.max_upload_mb*1024*1024
    CORS(app,resources={r'/api/*':{'origins':'*'}})
    Path('data').mkdir(exist_ok=True)
    import logging
    logging.basicConfig(level=getattr(logging,settings.log_level.upper(),logging.INFO),format='%(asctime)s | %(levelname)s | %(message)s')
    init_db(); seed(); app.register_blueprint(api)
    @app.errorhandler(413)
    def too_large(_): return jsonify({'error':'Upload exceeds configured size limit'}),413
    return app
