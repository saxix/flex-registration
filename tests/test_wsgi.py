def test_wsgi():
    from smart_register.config.wsgi import application

    assert application
