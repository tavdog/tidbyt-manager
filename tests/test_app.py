def test_register(client):
    response = client.get("/auth/register")
    assert response.status_code == 200

def test_unauth_index(client):
    response = client.get("/")
    assert response.status_code != 200

def test_login(client):
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    #assert response.status_code == 200
    response = client.get("/")
    assert response.status_code == 200


# def test_logout(client):
#     response = client.get("/auth/logout")
#     assert response.status_code == )
    

# def test_home_with_query(client):
#     response = client.get("/?q=test")
#     assert response.status_code == 200

