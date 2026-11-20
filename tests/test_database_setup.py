def test_database_connection(session):
    result = session.exec(
        __import__("sqlmodel").text("SELECT 1")
    ).scalar_one()
    
    assert result == 1