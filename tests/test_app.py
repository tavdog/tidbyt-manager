from tidbyt_manager import db
import os

def test_register_and_login(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    response = client.post("/auth/register", data={"username": "testuser", "password": "password"})
    # assert user.config file exists
    assert os.path.exists(os.path.join("tests", "users", "testuser", "testuser.json"))

    response = client.post("/auth/login",    data={"username": "testuser", "password": "password"})
    response = client.get("/")
    assert response.status_code == 200

def test_login_with_wrong_password(client):
    response = client

def test_unauth_index(client):
    response = client.get("/")
    assert response.status_code != 200

# def test_login(client):


# def test_logout(client):
#     response = client.get("/auth/logout")
#     assert response.status_code == )
    

# def test_home_with_query(client):
#     response = client.get("/?q=test")
#     assert response.status_code == 200

