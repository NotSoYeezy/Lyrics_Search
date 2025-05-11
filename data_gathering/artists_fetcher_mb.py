import musicbrainzngs
import time
import logging
from data_gathering.descriptors import NonEmptyString, PositiveInteger


class ArtistsFetcherMB:
    """
    Class to fetch artists from the MusicBrainz API.

    Args:
        limit_per_page (int): The number of artists to fetch per page.
        max_artists_to_fetch (int): The maximum number of artists to fetch.
        app_name (str): The name of the application.
        app_version (str): The version of the application.
        contact_info (str): Contact information for the application.
        artists_country_code (str): The country code to filter artists by.
        verbose (bool): Flag to enable verbose mode.

    Methods:
        save_to_file(file_name): Saves fetched artist data to a file.
        fetch_artists(): Fetches artist data from the MusicBrainz API.
    """
    _limit_per_page = PositiveInteger("limit_per_page")
    _max_artists_to_fetch = PositiveInteger("max_artists_to_fetch")
    _app_name = NonEmptyString("app_name")
    _app_version = NonEmptyString("app_version")
    _contact_info = NonEmptyString("contact_info")
    _artists_country_code = NonEmptyString("artists_country_code")

    def __init__(self, limit_per_page: int, max_artists_to_fetch: int, *,
                 app_name: str = "MyApp", app_version: str = "1.0", contact_info="example@example.com",
                 verbose: bool = True, artists_country_code: str = "PL"):
        if not isinstance(verbose, bool):
            raise Exception("`verbose` should be of type bool")
        self._limit_per_page = limit_per_page
        self._max_artists_to_fetch = max_artists_to_fetch
        self._app_name = app_name
        self._app_version = app_version
        self._contact_info = contact_info
        self._artists_country_code = artists_country_code
        self._verbose = verbose
        self._all_artist_names = set()
        self._set_up()

    def _set_up(self):
        self._log(f"Setting User-Agent for MusicBrainz API: {self._app_name}/{self._app_version} ({self._contact_info})")
        musicbrainzngs.set_useragent(
            self._app_name, self._app_version, contact=self._contact_info
        )

    def _log(self, message, warning: bool = False):
        if self._verbose and not warning:
            print(message)
            return
        logging.warning(message)

    def save_to_file(self, file_name):
        try:
            sorted_artists = sorted(self._all_artist_names)
            with open(file_name, 'w', encoding="UTF-8") as f:
                f.write("\n".join(sorted_artists))
            self._log(f"Artist list saved to file: {file_name}")
        except Exception as e:
            self._log(f"Error during saving to file: {e}", True)

    def fetch_artists(self):
        fetched_count = 0
        current_offset = 0
        while fetched_count < self._max_artists_to_fetch:
            try:
                result = self._query_artists(current_offset)
                artist_list = self._extract_artist_list(result)
                if not artist_list:
                    self._log("No more results found...")
                    break
                fetched_count = self._process_artist_list(artist_list, fetched_count)
                current_offset += self._limit_per_page
                self._log_progress(fetched_count)
            except musicbrainzngs.WebServiceError as exc:
                self._handle_web_service_error(exc)
            except Exception as e:
                self._log(f"Unexpected error: {e}", True)
                self._log("Stopping...")
                break
        return self

    def _query_artists(self, offset):
        return musicbrainzngs.search_artists(
            query=f"country:{self._artists_country_code}",
            limit=self._limit_per_page,
            offset=offset
        )

    def _extract_artist_list(self, result):
        return result.get('artist-list', [])

    def _process_artist_list(self, artist_list, fetched_count):
        page_fetched_count = 0
        for artist_info in artist_list:
            artist_name = artist_info.get('name')
            if artist_name:
                self._all_artist_names.add(artist_name)
                fetched_count += 1
                page_fetched_count += 1
            if fetched_count >= self._max_artists_to_fetch:
                break
        self._log(f"Found {len(artist_list)} results on that page, added {page_fetched_count} new artists.")
        return fetched_count

    def _log_progress(self, fetched_count):
        self._log(f"Currently {len(self._all_artist_names)} artists.")
        if fetched_count >= self._max_artists_to_fetch:
            self._log(f"Found max number of artists - {self._max_artists_to_fetch}")
        self._log("Waiting 1 sec for another query")
        time.sleep(1.1)

    def _handle_web_service_error(self, exc):
        self._log(f"MusicBrainz Web Service exception: {exc}")
        self._log("There might be a problem with query limit. Waiting 10 secs....")
        time.sleep(10)
