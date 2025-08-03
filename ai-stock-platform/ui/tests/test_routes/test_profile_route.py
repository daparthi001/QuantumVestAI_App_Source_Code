from fastapi import status


def test_profile_requires_authentication(client):
    """Unauthenticated access to profile should redirect to login."""
    response = client.get("/profile/", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert "/login" in response.headers["location"]
