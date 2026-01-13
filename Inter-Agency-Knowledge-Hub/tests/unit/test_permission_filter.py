"""Unit tests for PermissionFilter."""

import pytest

from src.core.permission_filter import PermissionFilter
from src.models.user import UserPermissions
from src.models.enums import Agency, DocumentClassification


@pytest.fixture
def permission_filter():
    """Create permission filter."""
    return PermissionFilter()


@pytest.fixture
def admin_user():
    """Create admin user."""
    return UserPermissions.from_groups(
        user_id="admin-001",
        email="admin@oti.ny.gov",
        groups=["AllAgencies_Admin"],
    )


@pytest.fixture
def dmv_staff_user():
    """Create DMV staff user."""
    return UserPermissions.from_groups(
        user_id="dmv-001",
        email="staff@dmv.ny.gov",
        groups=["DMV_Staff"],
    )


@pytest.fixture
def public_user():
    """Create public user."""
    return UserPermissions.from_groups(
        user_id="public-001",
        email="citizen@example.com",
        groups=[],
    )


class TestPermissionFilter:
    """Tests for PermissionFilter."""

    def test_admin_has_no_filter(self, permission_filter, admin_user):
        """Test admin users have no security filter."""
        filter_str = permission_filter.build_security_filter(admin_user)
        assert filter_str == ""

    def test_staff_has_agency_filter(self, permission_filter, dmv_staff_user):
        """Test staff users are filtered by agency."""
        filter_str = permission_filter.build_security_filter(dmv_staff_user)
        assert "dmv" in filter_str.lower()

    def test_public_user_sees_public_only(self, permission_filter, public_user):
        """Test public users only see public documents."""
        filter_str = permission_filter.build_security_filter(public_user)
        assert "public" in filter_str.lower()

    def test_admin_can_access_all_documents(self, permission_filter, admin_user):
        """Test admin can access any document."""
        can_access = permission_filter.check_document_access(
            permissions=admin_user,
            agency=Agency.DMV,
            classification=DocumentClassification.CONFIDENTIAL,
            allowed_groups=["DMV_Admin"],
        )
        assert can_access is True

    def test_staff_can_access_own_agency_internal(self, permission_filter, dmv_staff_user):
        """Test staff can access internal documents in their agency."""
        can_access = permission_filter.check_document_access(
            permissions=dmv_staff_user,
            agency=Agency.DMV,
            classification=DocumentClassification.INTERNAL,
            allowed_groups=["DMV_Staff"],
        )
        assert can_access is True

    def test_staff_cannot_access_other_agency(self, permission_filter, dmv_staff_user):
        """Test staff cannot access other agency documents."""
        can_access = permission_filter.check_document_access(
            permissions=dmv_staff_user,
            agency=Agency.DOL,
            classification=DocumentClassification.INTERNAL,
            allowed_groups=["DOL_Staff"],
        )
        assert can_access is False

    def test_staff_cannot_access_restricted(self, permission_filter, dmv_staff_user):
        """Test staff cannot access restricted documents."""
        can_access = permission_filter.check_document_access(
            permissions=dmv_staff_user,
            agency=Agency.DMV,
            classification=DocumentClassification.RESTRICTED,
            allowed_groups=["DMV_Manager"],
        )
        assert can_access is False

    def test_public_can_access_public_documents(self, permission_filter, public_user):
        """Test public users can access public documents."""
        can_access = permission_filter.check_document_access(
            permissions=public_user,
            agency=Agency.DMV,
            classification=DocumentClassification.PUBLIC,
            allowed_groups=[],
        )
        assert can_access is True

    def test_public_cannot_access_internal(self, permission_filter, public_user):
        """Test public users cannot access internal documents."""
        can_access = permission_filter.check_document_access(
            permissions=public_user,
            agency=Agency.DMV,
            classification=DocumentClassification.INTERNAL,
            allowed_groups=["DMV_Staff"],
        )
        assert can_access is False

    def test_permission_caching(self, permission_filter, dmv_staff_user):
        """Test permission caching works."""
        permission_filter.cache_permissions(dmv_staff_user.user_id, dmv_staff_user)

        cached = permission_filter.get_cached_permissions(dmv_staff_user.user_id)
        assert cached is not None
        assert cached.user_id == dmv_staff_user.user_id

    def test_cache_invalidation(self, permission_filter, dmv_staff_user):
        """Test cache invalidation."""
        permission_filter.cache_permissions(dmv_staff_user.user_id, dmv_staff_user)
        permission_filter.invalidate_cache(dmv_staff_user.user_id)

        cached = permission_filter.get_cached_permissions(dmv_staff_user.user_id)
        assert cached is None

    def test_get_accessible_agencies_admin(self, permission_filter, admin_user):
        """Test admin has access to all agencies."""
        agencies = permission_filter.get_accessible_agencies(admin_user)
        assert len(agencies) == len(Agency)

    def test_get_accessible_agencies_staff(self, permission_filter, dmv_staff_user):
        """Test staff only has access to their agency."""
        agencies = permission_filter.get_accessible_agencies(dmv_staff_user)
        assert Agency.DMV in agencies
        assert Agency.DOL not in agencies
