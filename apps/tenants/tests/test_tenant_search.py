# Covers the TenantViewSet.search_fields fix - ?search= was previously a
# silent no-op (advertised in the OpenAPI schema via the project-wide
# SearchFilter backend, but the view never set search_fields for it to
# read). Added to support the frontend's tenant search box (Phase 3).
import pytest

from apps.accounts.tests.factories import AdminUserFactory
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestTenantSearch:
    def test_search_matches_first_name(self, authenticated_client):
        admin = AdminUserFactory()
        match = TenantFactory(user__first_name="Wanjiru", user__last_name="Kariuki")
        TenantFactory(user__first_name="Otieno", user__last_name="Odhiambo")

        client = authenticated_client(admin)
        response = client.get("/api/tenants/?search=Wanjiru")

        assert response.status_code == 200
        returned_ids = [row["id"] for row in response.data["results"]]
        assert str(match.id) in returned_ids
        assert len(response.data["results"]) == 1

    def test_search_matches_email(self, authenticated_client):
        admin = AdminUserFactory()
        match = TenantFactory(user__email="findme@example.com")
        TenantFactory(user__email="other@example.com")

        client = authenticated_client(admin)
        response = client.get("/api/tenants/?search=findme")

        returned_ids = [row["id"] for row in response.data["results"]]
        assert str(match.id) in returned_ids
        assert len(response.data["results"]) == 1

    def test_search_matches_national_id(self, authenticated_client):
        admin = AdminUserFactory()
        match = TenantFactory(national_id="UNIQUE99")
        TenantFactory(national_id="OTHER11")

        client = authenticated_client(admin)
        response = client.get("/api/tenants/?search=UNIQUE99")

        returned_ids = [row["id"] for row in response.data["results"]]
        assert str(match.id) in returned_ids
        assert len(response.data["results"]) == 1

    def test_no_search_param_returns_all(self, authenticated_client):
        admin = AdminUserFactory()
        TenantFactory()
        TenantFactory()

        client = authenticated_client(admin)
        response = client.get("/api/tenants/")

        assert len(response.data["results"]) == 2