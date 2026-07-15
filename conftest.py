import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """
    Returns a helper that authenticates the given client as a
    specific user by generating a real JWT, exactly like a real
    login would produce.
    """
    from rest_framework_simplejwt.tokens import RefreshToken

    def _authenticate(user):
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return api_client

    return _authenticate