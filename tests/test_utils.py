import pytest

from django_gar.utils import remove_external_links

pytestmark = pytest.mark.django_db


class TestRemoveExternalLinks:
    def test_remove_external_links(self, html_content):
        # GIVEN / WHEN
        response = remove_external_links(html_content)

        # THEN
        assert "https://www.dummy.io" in response
        assert "https://www.dictionnaire-academie.fr" not in response

    def test_remove_external_links_without_href(self):
        # GIVEN / WHEN
        response = remove_external_links("<a>Lorem Ipsum</a>")

        # THEN
        assert response == "<a>Lorem Ipsum</a>"
