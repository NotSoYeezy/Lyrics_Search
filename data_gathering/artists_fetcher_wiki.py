"""
This module provides a class to fetch artist names from Wikipedia category pages.
It is designed to extract cleaner datasets by directly querying Wikipedia instead of
using other APIs that may return noisy or irrelevant data.
"""

from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import re


class ArtistFetcherWiki:
    """
    A class to fetch artist names from a Wikipedia category page.
    `https://pl.wikipedia.org/wiki/Kategoria:Polscy_raperzy` - this is an example
    page that this fetcher works with.

    Args:
        wiki_url (str): The URL of the Wikipedia category page.

    Attributes:
        wiki_url (str): The URL of the Wikipedia category page.
        artists (list): A list of extracted artist names.
    """

    def __init__(self, wiki_url: str):
        """
        Initializes the ArtistFetcherWiki with a Wikipedia category URL.

        Args:
            wiki_url (str): The URL of the Wikipedia category page.
        """
        self._url = wiki_url
        self._extracted_artists = []
        self._next_url = ""

    @property
    def artists(self):
        """
        Returns the list of extracted artist names.

        Returns:
            list: A list of artist names.
        """
        return self._extracted_artists

    @property
    def wiki_url(self):
        return self._url

    @wiki_url.setter
    def wiki_url(self, new_url: str):
        self._url = new_url

    def save_to_file(self, file_path: str):
        """
        Saves the extracted artist names to a file.

        Args:
            file_path (str): The path to the file where artist names will be saved.
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("\n".join(self._extracted_artists))

    def _clean_data(self):
        """
        Cleans the extracted artist names by removing unnecessary text,
        such as "(rapper)" or similar annotations.
        """
        self._extracted_artists = [
            re.sub(r'\s*\(.*?\)', '', artist).strip() for artist in self._extracted_artists
        ]

    def _next_page(self, soup_obj: BeautifulSoup) -> str | None:
        """
        Finds the URL of the next page in the category, if it exists.

        Args:
            soup_obj (BeautifulSoup): The BeautifulSoup object of the current page.

        Returns:
            str | None: The URL of the next page, or None if no next page exists.
        """
        next_page_url = None
        pages_div = soup_obj.find('div', id='mw-pages')

        if pages_div:
            next_links = pages_div.find_all('a', href=lambda href: href and 'pagefrom=' in href)
            if next_links:
                relative_url = next_links[-1]['href']
                next_page_url = urljoin(self._url, relative_url)

        self._next_url = next_page_url
        return next_page_url

    def fetch_artists(self):
        """
        Fetches artist names from the Wikipedia category page and its subsequent pages.

        Returns:
            list: A list of extracted artist names.
        """
        current_url = self._next_url or self._url
        response = requests.get(current_url)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.text, 'html.parser')

        pages_container = soup.find('div', id='mw-pages')
        if pages_container:
            category_groups = pages_container.find_all('div', class_='mw-category-group')
            for group in category_groups:
                list_items = group.find_all('li')
                for item in list_items:
                    link_tag = item.find('a')
                    if link_tag and link_tag.get('href'):
                        href = link_tag.get('href')
                        content = link_tag.text
                        if href.startswith('/wiki/') and not href.startswith('/wiki/Wikiprojekt:'):
                            self._extracted_artists.append(content)

            if self._next_page(soup_obj=soup):
                self.fetch_artists()

            self._clean_data()
        return self._extracted_artists


if __name__ == "__main__":
    # Example usage
    url = "https://pl.wikipedia.org/wiki/Kategoria:Polscy_raperzy"
    af = ArtistFetcherWiki(url)
    artists = af.fetch_artists()
    af.save_to_file("outputs/artists_wiki.txt")
