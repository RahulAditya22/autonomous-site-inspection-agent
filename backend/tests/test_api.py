def test_api_module_imports():
    from app.api.routes import api
    assert api.name=='api'
