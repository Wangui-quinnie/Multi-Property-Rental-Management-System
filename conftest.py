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

        # --- TEMPORARY DIAGNOSTIC (remove once the random 401 flakiness
        # is root-caused): print the full response body whenever a
        # request through this client comes back 401, so we can see
        # DRF's actual `detail` message instead of just the status code.
        original_generic = api_client.generic

        def _generic_with_diagnostic(method, path, *args, **kwargs):
            response = original_generic(method, path, *args, **kwargs)
            if response.status_code == 401:
                print(
                    f"\n[401 DIAGNOSTIC] {method} {path} user={user.email} "
                    f"role={user.role} -> {getattr(response, 'data', response.content)}"
                )
            return response

        api_client.generic = _generic_with_diagnostic
        # --- END TEMPORARY DIAGNOSTIC ---

        return api_client

    return _authenticate