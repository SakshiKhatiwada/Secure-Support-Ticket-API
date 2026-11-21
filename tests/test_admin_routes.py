def test_admin_can_get_all_users(client, admin_headers):
    response = client.get(
        "/admin/users",
         headers=admin_headers
        )
    assert response.status_code == 200
    
def test_user_not_get_all_users(client, normal_user_headers):
    response = client.get(
        "/admin/users",
         headers=normal_user_headers
    )
    assert response.status_code == 403
    
def test_staff_not_get_all_users(client, staff_headers):
    response = client.get(
        "/admin/users",
         headers=staff_headers
    )
    assert response.status_code == 403