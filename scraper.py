
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
import requests
import json


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

# ------------------------------------------------------------------------ #


def main():

    urls = [
        'https://www.airbnb.co.uk/rooms/14531512?s=51',
        'https://www.airbnb.co.uk/rooms/19278160?s=51',
        'https://www.airbnb.co.uk/rooms/19292873?s=51',
    ]

    for url in urls:
        try:
            # Use requests to retrieve web page data
            response = requests.get(url)

            if response.status_code != 200:
                print('Failed to retrieve page, URL: {0}, error: {1}\n'.format(url, response.status_code))
                continue

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

    return


if __name__ == '__main__':
    main()
