import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from ..helpers import cache_file, get_cache_dir, get_file_content, convert_to_num


class CoronaModel:
    NO = 0
    COUNTRY = 1
    TOTALCASES = 2
    NEWCASES = 3
    TOTALDEATHS = 4
    NEWDEATHS = 5
    TOTALRECOVERED = 6
    NEWRECOVERED = 7
    ACTIVECASES = 8
    SERIOUS = 9
    TOTALCASESPER1M = 10
    DEATHSPER1M = 11
    TOTALTESTS = 12
    TESTSPER1M = 13
    POPULATION = 14

    def __init__(self, *args: str):
        """
        The CoronaModel class represents data related to the Covid-19 virus. This data is scraped from
        https://worldometers.info/coronavirus/.

        Parameters
        ----------
        args: str
            String arguments of countries that will be filtered.

        Examples
        --------

        >>> corona = CoronaModel("USA", "World", "Spain", "Japan", "India")
        """
        self.countries = args

    def get_data(
            self,
            sort_by: int = NO,
            no_cache: bool = False,
            get_all: bool = False) -> list[tuple[int | str | float]]:
        """
        Gets data filtered based on the countries given in the constructor. For most cases, this should be the main
        entrypoint for getting data.

        Parameters
        ----------
        sort_by: int
            Sorts the filtered result based on the given key in ascending order. Defaults to CoronaModel.NO
        no_cache: bool
            Bypasses retrieving data from cache and fetches new data if True. Defaults to False
        get_all: bool
            Bypasses filtering and retrieves data of all countries. Defaults to False

        Returns
        -------
        list[tuple]
            A list of tuples containing data of countries.
        """
        raw_data_path = get_cache_dir("raw")
        clean_data_path = get_cache_dir("clean")

        result = []
        # Using cache
        if not no_cache:
            # If clean cache exists and it's not empty
            if os.path.exists(clean_data_path) and get_file_content(clean_data_path):
                clean_data = get_file_content(clean_data_path)
                result = self.parse_clean_data(clean_data)

            # If raw cache exists and it's not empty
            elif os.path.exists(raw_data_path) and get_file_content(raw_data_path):
                raw_data = get_file_content(raw_data_path)

                clean_data = self.parse_raw_data(raw_data)
                clean_data_as_str = self.convert_data_as_str(clean_data)
                cache_file("clean", clean_data_as_str)

                clean_data = get_file_content(clean_data_path)
                result = self.parse_clean_data(clean_data)

            else:
                # For when there is literally no cache, so must fetch data
                no_cache = not no_cache

        # If bypass cache or there is literally no cache
        if no_cache:
            raw_data = self.fetch_data()
            cache_file("raw", raw_data)

            clean_data = self.parse_raw_data(raw_data)
            clean_data_as_str = self.convert_data_as_str(clean_data)
            cache_file("clean", clean_data_as_str)

            clean_data = get_file_content(clean_data_path)
            result = self.parse_clean_data(clean_data)

        if not get_all:
            result = filter(lambda country_data: country_data[1] in self.countries, result)

        result = sorted(result, key=lambda country_data: country_data[sort_by])
        return result

    def get_table_headers(self) -> list[str]:
        """
        Gets the table headers of the data.

        Returns
        -------
        list[str]
            A list of strings of table headers.

        """
        headers = [
            "No.",
            "Country",
            "Total Cases",
            "New Cases",
            "Total Deaths",
            "New Deaths",
            "Total Recovered",
            "New Recovered",
            "Active Cases",
            "Serious",
            "Total Cases/1M",
            "Deaths/1M",
            "Total Tests",
            "Tests/1M",
            "Population"
        ]

        return headers

    def fetch_data(self) -> str:
        """
        Fetches raw html data from https://worldometers.info/coronavirus/ and parses it to get the table that
        displays data from the current date.

        Returns
        -------
        str
            A string of the raw html table body data.
        """
        url = "https://www.worldometers.info/coronavirus/"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        # Find the 'today' table
        table = soup.find(id="main_table_countries_today")
        table_body = table.find("tbody")

        result = str(table_body)
        return result

    def parse_raw_data(self, html_content: str = None) -> map:
        """
        Parses raw html table body for data. The numbers in the returned data will still be strings rather than int
        or float.

        Parameters
        ----------
        html_content: str | None
            A string that will be parsed for data.

        Returns
        -------
        list[tuple]
            A list of tuples which contain the sanitised data of all available countries.
        """

        def sanitise_value(i: int, value: str):
            # For numbers with commas in them (thousands, millions, etc.)
            clean_value = value.replace(",", "").strip()

            # For World, "No." is just nothing, so this is to assign it 0
            if i == 0 and not clean_value:
                clean_value = "0"
            # For New Whatever values which have a + at the start
            if len(clean_value) > 0 and clean_value[0] == "+":
                clean_value = clean_value[1:]

            result = convert_to_num(clean_value)
            return result

        def sanitise_data(data: Tag):
            country_data = data.find_all("td")[:15]
            sanitised_data = map(
                lambda enum_data: sanitise_value(enum_data[0], enum_data[1].text),
                enumerate(country_data)
            )

            result = tuple(sanitised_data)
            return result

        soup = BeautifulSoup(html_content, "html.parser")
        countries = soup.find_all("tr")[7:]
        result = map(lambda country: sanitise_data(country), countries)

        return result

    def parse_clean_data(self, csv_content: str = None, delimiter: str = "\n") -> map:
        r"""
        Parses csv-like file for data.

        Parameters
        ----------
        csv_content: str | None
            A string that will be parsed for data.

        delimiter: str
            The delimiter that will be used to split the data. Defaults to '\n'

        Returns
        -------
        list[tuple]
            A list of tuples which contain clean data of all available countries.
        """
        countries_data = csv_content.split(delimiter)

        # Using map() here cause it's significantly faster, by like 100 times.
        # (In practice, this isn't really noticeable tho lmao)
        str_to_list = map(lambda row: row.split(","), countries_data)
        result = map(lambda row: tuple(convert_to_num(data) for data in row), str_to_list)

        return result

    def convert_data_as_str(self, clean_data: list[tuple]) -> str:
        """
        Converts the given clean data as string.

        Parameters
        ----------
        clean_data: list[tuple]
            The list of tuples of clean data that will be converted as a string.

        Returns
        -------
        str
            A string of the clean data.
        """
        tuples_to_str = []
        for country_data in clean_data:
            data_to_str = ",".join(str(data) for data in country_data)
            tuples_to_str.append(data_to_str)
        result = "\n".join(tuples_to_str)

        return result


if __name__ == "__main__":
    corona = CoronaModel("Russia", "Malaysia", "China")
