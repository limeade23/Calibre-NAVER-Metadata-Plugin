from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import json
import re

from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import Source


class NAVER(Source):

    name = "NAVER OpenAPI"
    description = "Downloads metadata and covers from NAVER Open API."
    author = "Limeade23 <https://github.com/limeade23>"
    version = (0, 0, 1)
    minimum_calibre_version = (6, 10, 0)

    NAVER_ID: str = "naver"
    API_ID: str = ""
    API_KEY: str = ""
    API_URL: str = "https://openapi.naver.com/v1/search/book.json"

    capabilities = frozenset(["identify", "cover"])
    touched_fields = frozenset(
        [
            "title",
            "authors",
            "identifier:" + NAVER_ID,
            "identifier:isbn",
            "comments",
            "publisher",
            "pubdate",
            "languages",
            "tags",
        ]
    )

    def identify(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers={},
        timeout=30,
    ):
        search_keyword = title
        if title and authors:
            authors_str = ",".join(authors)
            search_keyword = f"{title} {authors_str}"
        books = self._search(search_keyword)
        for book in books:
            metadata = self._to_metadata(book)
            if isinstance(metadata, Metadata):
                mi = metadata.identifiers[self.NAVER_ID]
                if metadata.cover_url:
                    self.cache_identifier_to_cover_url(mi, metadata.cover_url)
                self.clean_downloaded_metadata(metadata)
                result_queue.put(metadata)

    def _search(self, title: str = "", timeout: int = 30):
        params = {"query": title}
        query_string = urlencode(params)
        url = f"{self.API_URL}?{query_string}"

        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Naver-Client-Id": self.API_ID,
                "X-Naver-Client-Secret": self.API_KEY,
            },
        )

        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            if response.status != 200:
                raise Exception(f"failed to search: {body.decode()}")

        results = json.loads(body).get("items", [])

        if len(results) > 0:
            return results

        return None

    def _to_metadata(self, data: dict) -> Metadata:
        authors = data.get("author", "").split("^")

        metadata = Metadata(data.get("title", ""), authors)
        metadata.comments = data.get("description", "")
        identifiers = re.search(r"\d+", data.get("link")).group()
        metadata.set_identifier(self.NAVER_ID, str(identifiers))
        metadata.isbn = data.get("isbn", "")

        date_string = data.get("pubdate")
        formatted_date = datetime.strptime(date_string, "%Y%m%d")
        metadata.pubdate = formatted_date
        metadata.publisher = data.get("publisher", "")
        metadata.language = "kor"
        metadata.cover_url = data.get("image", "")

        return metadata

    def get_cached_cover_url(self, identifiers):

        url = None
        mi = identifiers.get(self.NAVER_ID, None)
        if mi is not None:
            url = self.cached_identifier_to_cover_url(mi)
        return url

    def download_cover(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers={},
        timeout=30,
        get_best_cover=False,
    ):
        cover_url = self.get_cached_cover_url(identifiers)
        if cover_url:
            log.info("Downloading cover from: %s", cover_url)
            try:
                with urlopen(cover_url, timeout=timeout) as response:
                    cover = response.read()
                    result_queue.put((self, cover))
            except Exception as e:
                log.exception("Failed to download cover from: %s", cover_url)
        else:
            log.info("No cover found")
