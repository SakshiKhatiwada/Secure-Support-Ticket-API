def test_database_connection(session): # INFO yii parameter lai dekhera pytest le fixtures with those names aafai search garxa
    result = session.exec(
        __import__("sqlmodel").text("SELECT 1")
    ).scalar_one()
    
    assert result == 1