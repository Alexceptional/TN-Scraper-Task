# TN Scraper Coding Task
---
## Overview
A simple web scraper to retrieve details from an Airbnb property overview web page. Retrieves property name & type, number of bedrooms & bathrooms, list of amenities.

All code for this task is included in the file `scraper.py`.

### Asynchronous Scraping
The scraper is capable of running asynchronously with a specified number of threads using the `threading` module. The number of threads can be set to the number of URLs to scrape, or can be set to a lower number which will split the weoklist down accoringly into chunks and iterate through these chunks of URLs.

There are a number of alternatives to the threading module, such as `asyncio`/`aiohttp` and `concurrent.futures`, neither of which offered any major improvement in performance compared to threading + requests in this particular case.

### Parser
One major performance bottleneck for this scraper is `html5lib`, which is somewhat slower than `lxml`. The latter is awkward to install on Windows however. If you wish to run this on Linux you may want to consider lxml as an alternative parser.

## Running the Code
Simply run `python scraper.py` in the top-level directory.

## Requirements
This program was written using Python 3.4.3. Install requirements by running
  `pip install -r requirements.txt`
