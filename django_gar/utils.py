import re
import ast

from bs4 import BeautifulSoup

from django.conf import settings

GAR_ALLOWED_EXTERNAL_LINKS = getattr(settings, "GAR_ALLOWED_EXTERNAL_LINKS", [])


def remove_external_links_from_html(html_content):
    """
    Given a html content, remove external a tags.
    a tags with starting urls found in GAR_ALLOWED_EXTERNAL_LINKS won't be removed.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for link in soup.find_all("a"):
        if not link.has_attr("href"):
            continue

        # Strip html a tags
        external_links_to_keep = any(
            link["href"].startswith(excluded) for excluded in GAR_ALLOWED_EXTERNAL_LINKS
        )
        if "http" in link["href"] and not external_links_to_keep:
            link.unwrap()

    return str(soup)


def remove_external_links_from_json(json_content):
    """
    Given a json content, remove external a tags and 'http://' and 'https://'
    a tags, 'http://' and 'https://' with starting urls found in GAR_ALLOWED_EXTERNAL_LINKS won't be removed.
    """
    data = remove_external_links_from_html(str(json_content))
    regex = f"(?!{'|'.join(excluded for excluded in GAR_ALLOWED_EXTERNAL_LINKS)})"
    regex = f"{regex}(http[s]?://)([^']*)"
    data = re.sub(regex, "", data)
    return ast.literal_eval(data)
