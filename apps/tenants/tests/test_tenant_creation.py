import pytest

from apps.accounts.models import User
from apps.accounts.tests.factories import AdminUserFactory, LandlordUserFactory
from apps.tenants.models import Tenant
from apps.tenants.tests.factories import TenantFactory

pytestmark = pytest.mark.django_db


class TestTenantCreation:
    def test_admin_creates_tenant_and_linked_user(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/tenants/",
            {
                "email": "newtenant@example.com",
                "first_name": "John",
                "last_name": "Kamau",
                "national_id": "12345678",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 201

        user = User.objects.get(email="newtenant@example.com")
        assert user.role == User.Role.TENANT
        assert user.check_password("SecurePass123!")

        tenant = Tenant.objects.get(user=user)
        assert tenant.national_id == "12345678"
        assert tenant.status == Tenant.Status.ACTIVE

    def test_duplicate_email_rejected(self, authenticated_client):
        admin = AdminUserFactory()
        existing_tenant = TenantFactory()

        client = authenticated_client(admin)
        response = client.post(
            "/api/tenants/",
            {
                "email": existing_tenant.user.email,
                "first_name": "Duplicate",
                "national_id": "99999999",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 400
        assert "email" in response.data

    def test_landlord_cannot_create_tenant(self, authenticated_client):
        landlord = LandlordUserFactory()
        client = authenticated_client(landlord)

        response = client.post(
            "/api/tenants/",
            {
                "email": "blocked@example.com",
                "national_id": "11111111",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 403

    def test_username_auto_generated_when_not_provided(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/tenants/",
            {
                "email": "autouser@example.com",
                "national_id": "22222222",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 201
        user = User.objects.get(email="autouser@example.com")
        assert user.username == "autouser"

    def test_password_is_hashed_not_stored_plaintext(self, authenticated_client):
        admin = AdminUserFactory()
        client = authenticated_client(admin)

        response = client.post(
            "/api/tenants/",
            {
                "email": "hashcheck@example.com",
                "national_id": "33333333",
                "password": "SecurePass123!",
            },
        )

        user = User.objects.get(email="hashcheck@example.com")
        assert user.password != "SecurePass123!"
        assert user.password.startswith("pbkdf2_")  # Django's default hasher