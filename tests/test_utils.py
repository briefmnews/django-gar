import pytest

from django_gar.utils import (
    remove_external_links_from_html,
)

pytestmark = pytest.mark.django_db


class TestRemoveExternalLinks:
    def test_remove_external_links_from_html(self, html_content):
        # GIVEN / WHEN
        response = remove_external_links_from_html(html_content)

        # THEN
        assert "https://www.dummy.io" in response
        assert "https://www.dictionnaire-academie.fr" not in response

    def test_remove_external_links_from_html_without_href(self):
        # GIVEN / WHEN
        response = remove_external_links_from_html("<a>Lorem Ipsum</a>")

        # THEN
        assert response == "<a>Lorem Ipsum</a>"
