
"""
  Airbnb Web Scraper -- TravelNest Assignment
  - - - - - - - - - - - - - - - - - - - - - -

  This is a simple web scraper, intended to analyse the web page of an Airbnb property and return the
  following information:

  * Property name
  * Property type
  * Number of bedrooms
  * Number of bathrooms
  * Amenities

  This scraper loops through a list of URLs (as defined in the assignment) and produces a basic report
  for each which is printed to screen. The URLs are defined as a list in the main function.

  The 'print_report' function could be replaced/supplemented by further methods of producing a report e.g.
  writing to a file or database table, as a potential improvement.

  - - -

  This module requires BeautifulSoup, requests, json and a HTML/XML parser, e.g. html5lib.

"""

from bs4 import BeautifulSoup
from threading import Thread
import requests
import json
import time


# ------------------------------------------------------------------------ #

# Define headers for HTTP GET request. This ensures the request appears to be a valid request from a browser,
# rather than an automated crawler which some sites may block or throttle.

headers = {
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/60.0.3112.90 Safari/537.36'
}

# Define a persistent session for requests, apply headers to this session:
session = requests.Session()
session.headers.update(headers)

# ------------------------------------------------------------------------ #


def get_json_data(page_content, parser='html5lib'):

    """ Scrape content from Airbnb property details pages, return page data as a
    a Python dictionary.

    :param page_content: str
        web page content, as a string
    :param parser: str
        specify the parser for BeautifulSoup to use, or set None to use system default
    :return: dict
        scraped page data
    """

    page_data = BeautifulSoup(page_content, parser)

    # Find the script tag containing the bootstrap data JSON string
    data = page_data.find(
        'script',
        attrs={"data-hypernova-key": "p3indexbundlejs", "type": "application/json"}
    )

    # Extract tag contents, remove comment tags and convert to dict. using json module
    tag_content = str(data.contents[0]).replace('<!--', '').replace('-->', '')
    content_dict = json.loads(tag_content)

    return content_dict


def generate_report(data):

    """ Process the property data from the web page, build summary dictionary containing:

     * 'property_name' - Name of property
     * 'property_type' - Type of property e.g. 'Apartment'
     * 'room_type' - Type or number of bedrooms
     * 'room_number' - Number of bedrooms
     * 'bathrooms' - Number of bathrooms
     * 'general_amenities' - List of general amenities
     * 'family_amenities' - List of family amenities
     * 'safety_feats' - List of safety amenities

    :param data: dict
        Web page data, derived from 'bootstrapData' JSON string
    :return: dict
        Summarised property information (see above)
    """

    listing = data['bootstrapData']['listing']

    # Initialise summary data dictionary. Some values have been assigned default values of 'Not found'
    # in the event that the data is not present in the web page data

    summary_data = {
        'property_name': listing['name'],
        'property_type': 'Not found',
        'rooms': 'Not found',
        'bathrooms': 'Not found',
        'general_amenities': [],
        'family_amenities': [],
        'safety_feats': []
    }

    # Iterate through 'Space' section to build room details

    for detail in listing['space_interface']:

        if detail.get('label') == 'Property type:' and detail['value']:
            summary_data['property_type'] = detail['value']

        if detail.get('label') == 'Bedrooms:' and detail['value']:
            summary_data['rooms'] = detail['value']

        if detail.get('label') == 'Bathrooms:' and detail['value']:
            summary_data['bathrooms'] = detail['value']

    # Iterate through amenities to build list of amenities grouped by category

    for amenity in listing['listing_amenities']:
        if amenity['is_present']:

            if amenity['category'] == 'family':
                summary_data['family_amenities'].append(amenity['name'])

            elif amenity['category'] == 'general' and amenity['is_safety_feature']:
                summary_data['safety_feats'].append(amenity['name'])

            else:
                summary_data['general_amenities'].append(amenity['name'])

    return summary_data


def print_report(report_data):

    """ Report generator - prints report to screen.

    :param report_data: dict
        summary dictionary of property details
    :return: None

    """

    header = '\nPROPERTY SUMMARY FOR "{}"\n'.format(report_data['property_name'])
    print('* ' * (len(header) // 2))
    print(header)

    print('Property Type:'.ljust(25), report_data['property_type'])
    print('Number of Bedrooms:'.ljust(25), report_data['rooms'])
    print('Number of Bathrooms:'.ljust(25), report_data['bathrooms'])

    not_found = ['n/a']  # Print this if nothing found for category

    print('\nAMENITIES:')

    for amenity in report_data['general_amenities']:
        print(' * ', amenity)

    print('\nFAMILY AMENITIES:')

    for amenity in report_data['family_amenities'] or not_found:
        print(' * ', amenity)

    print('\nSAFETY FEATURES:')

    for amenity in report_data['safety_feats'] or not_found:
        print(' * ', amenity)

    print('\n')

    return


def divide_list(input_list, n):

    """ Split a list into 'n' number of chunks of approximately equal length.

    Based on example given here:
        https://stackoverflow.com/questions/2130016/splitting-a-list-of-into-n-parts-of-approximately-equal-length

    :param input_list: list
        list to be split
    :param n: int
        number of chunks to split list into
    :return: list
        list of lists (chunks)
    """

    avg = len(input_list) / float(n)
    last = 0.0
    divided = []

    while last < len(input_list):
        divided.append(input_list[int(last):int(last + avg)])
        last += avg

    return divided

# ------------------------------------------------------------------------ #


class Scraper(Thread):

    """ Subclass of Thread :-
    Defines a thread worker for running the scraper. Spawn one Scraper instance per
    thread to be executed - each thread can accept either a URL or a list of URLs to
    iterate through.

    """

    def __init__(self, urls):

        super(Scraper, self).__init__()

        # Ensure URL list is of list type:
        if type(urls) is str:
            self.urls = [urls]

        else:
            self.urls = urls

    def run(self):

        """ Iterate through URLs supplied, parse and print report.

        :return: None
        """

        for url in self.urls:
            try:
                # Use requests to retrieve web page data
                print(url)
                response = session.get(url, )  # allow_redirects=True)

                if response.status_code != 200:
                    print('Failed to retrieve page, URL: {0}, error: {1}\n'.format(url, response.status_code))
                    return

                # Get web page data from HTML response
                content = get_json_data(response.text)

                # Compile data into dictionary to be used for reporting
                summary_data = generate_report(content)

                # Generate/print report
                print_report(summary_data)

            except Exception as error:
                print('Scraper failed to run for URL {0}, error: {1}, {2}\n'.format(
                    url, type(error).__name__, error
                ))

            # time.sleep(1)  # for load concerns

# ------------------------------------------------------------------------ #


def main():
    start_time = time.time()

    with open('sample_data.txt', 'r') as f:
        data = f.read()

    urls = data.split('\n')

    # Number of threads
    no_threads = 6

    # Split URL list down into equal number of chunks to number of threads:
    chunks = divide_list(urls, no_threads)

    # Create list of thread workers
    threads = [Scraper(chunks[x])for x in range(no_threads)]

    # Start threads, wait for threads to complete before function returns
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print('Execution time: ', time.time() - start_time)

    return


if __name__ == '__main__':
    main()
