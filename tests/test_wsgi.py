def test_wsgi():
    from aurora.config.wsgi import application

    assert application
