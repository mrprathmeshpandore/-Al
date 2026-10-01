import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Optional
import urllib.request

from app.services.current_affairs.base_source import BaseCurrentAffairsSource, CurrentAffairCandidate


class RSSFeedSource(BaseCurrentAffairsSource):
    """RSS / Atom feed current affairs source provider."""

    def __init__(self, source_name: str, feed_url: str, default_category: str = "NATIONAL"):
        super().__init__(source_name=source_name)
        self.feed_url = feed_url
        self.default_category = default_category

    def fetch_latest(self, limit: int = 20) -> List[CurrentAffairCandidate]:
        candidates: List[CurrentAffairCandidate] = []
        try:
            req = urllib.request.Request(self.feed_url, headers={'User-Agent': 'PrashasakAI/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()

            root = ET.fromstring(xml_data)
            # Find RSS items or Atom entries
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')

            for item in items[:limit]:
                title = self._get_child_text(item, ['title', '{http://www.w3.org/2005/Atom}title'])
                link = self._get_child_text(item, ['link', '{http://www.w3.org/2005/Atom}link'])
                desc = self._get_child_text(item, ['description', 'summary', '{http://www.w3.org/2005/Atom}summary', 'content'])
                pub_date_str = self._get_child_text(item, ['pubDate', 'published', 'updated'])

                if not title or not desc:
                    continue

                pub_date = self._parse_date(pub_date_str)

                candidates.append(
                    CurrentAffairCandidate(
                        title=title.strip(),
                        source_name=self.source_name,
                        source_url=link.strip() if link else None,
                        content=desc.strip(),
                        published_at=pub_date,
                        category=self.default_category,
                    )
                )
        except Exception:
            # Safe fallthrough if network/feed error occurs
            pass

        return candidates

    def _get_child_text(self, element: ET.Element, tags: List[str]) -> Optional[str]:
        for tag in tags:
            child = element.find(tag)
            if child is not None:
                if child.text:
                    return child.text
                elif 'href' in child.attrib:
                    return child.attrib['href']
        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        # Try standard RFC 822 / ISO formats
        for fmt in [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]:
            try:
                return datetime.strptime(date_str.strip(), fmt).astimezone(timezone.utc)
            except ValueError:
                continue
        return None
