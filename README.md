# Project 2: eBay Webscraper 

This project contains a file, titled `ebay-dl.py`, that scrapes search results from eBay and saves the extracted information in a JSON file. 

## How it Works:

The `ebay-dl.py` file parses through the first 10 pages of eBay search results for the term you search, extracting key pieces of information. 

Each item contains the following keys: 
1. **name**: the name of the item
2. **price**: the price of the item in cents (in integer form)
3. **status**: the ownership status of the item (e.g. `"Brand New"`, `"Pre-owned"`, `"Refurbished"`)
4. **shipping**: the price of the shipping in cents (in integer form)
5. **free_returns**: whether or not there are free returns for the item 
6. **items_sold**: the number of items sold (as an integer)

## How to Run the File: 

First, set up the virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install playwright beautifulsoup4
playwright install chromium
```

To generate the JSON files, run the following command in your terminal with a search term of your choice. Wrap the search term in quotes if it contains spaces. 
```bash
python3 ebay-dl.py typewriter
python3 ebay-dl.py "pink typewriter"
python3 ebay-dl.py "film camera"
```

To generate the CSV files, run a slightly modified version of the previous command. The same wrapping requirement applies here for search terms containing spaces. 
```bash
python3 ebay-dl.py typewriter --csv
python3 ebay-dl.py "pink typewriter" --csv
python3 ebay-dl.py "film camera" --csv
```

## Course Project:

This is the link the [course project](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping). 