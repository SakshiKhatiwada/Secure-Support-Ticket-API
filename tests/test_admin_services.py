from app.utils.db import get_all_users_from_db


def test_get_all_users_from_db(session, add_commit_refresh, make_user):
    # Arrange: create some users
    user1 = make_user(
        username="testuser1"
    )
    user2 = make_user(username="testuser2")
    
    user1 = add_commit_refresh(user1)
    user2 = add_commit_refresh(user2)
    
    # Act: calling the service function
    users = get_all_users_from_db(session)
    
    # Assert: verify the returned users
    assert len(users)==2
    
    usernames = {user.username for user in users}
    
    assert usernames == {"testuser1", "testuser2"}
    
def test_get_all_users_from_db_empty(session):
    users = get_all_users_from_db(session)
    
    assert users == []