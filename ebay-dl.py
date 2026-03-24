import argparse
import csv
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# download browser and run html

def download_html_and_run_javascript(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=60000)
        html = page.content()
        browser.close()
    return html

def parse_itemssold(text):
    '''
    Extracts the number of items sold from a string.

    >>> parse_itemssold('127 sold')
    127
    >>> parse_itemssold('15 watchers')
    0
    >>> parse_itemssold('Almost gone')
    0
    '''
    if 'sold' not in text:
        return 0
    digits = ''
    for char in text:
        if char.isdigit():
            digits += char
    if digits:
        return int(digits)
    else:
        return 0

def parse_price(text):
    '''
    Converts a price string into an integer number of cents and returns as an integer.

    >>> parse_price('$15.99')
    1599
    >>> parse_price('$1,299.00')
    129900
    >>> parse_price('$20.00 to $30.00')
    2000
    '''
    if 'to' in text:
        text = text.split(' to ')[0]
    cleaned = ''
    for char in text:
        if char.isdigit() or char == '.':
            cleaned += char
    if cleaned:
        if '.' in cleaned:
            # separate the dollars and cents to combine into one integer at the end
            dollars, cents = cleaned.split('.')
            return int(dollars) * 100 + int(cents)
        else:
            return int(cleaned) * 100
    return None

def parse_shipping(text):
    '''
    Converts a shipping string into an integer number of cents, if there is a shipping cost.

    >>> parse_shipping('Free delivery')
    0
    >>> parse_shipping('+$4.99 delivery')
    499
    '''
    text = text.strip()
    if 'free' in text.lower():
        return 0
    if '+$' in text:
        cleaned = ''
        for char in text:
            if char.isdigit() or char == '.':
                cleaned += char
        if '.' in cleaned:
            dollars, cents = cleaned.split('.')
            return int(dollars) * 100 + int(cents)
        else:
            return int(cleaned) * 100
    return None

# only runs the code below if the python file is run "normally"
# AKA not being run in doctests
if __name__ == '__main__':

    # get command line arguments
    parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON.')
    parser.add_argument('search_term')
    parser.add_argument('--num_pages', type=int, default=10)
    parser.add_argument('--csv', action='store_true', help='Save output as CSV instead of JSON')
    args = parser.parse_args()

    # list of all items found in all webpages
    items = []

    # loop over ebay webpages
    for page_number in range(1, args.num_pages + 1):    

        # build url
        url = 'https://www.ebay.com/sch/i.html?_nkw='
        url += args.search_term
        url += '&_sacat=0&_from=R40&_pgn='
        url += str(page_number)
        url += '&rt=nc'
        print('url=', url)

        # download the html
        html = download_html_and_run_javascript(url)

        # process the html 
        soup = BeautifulSoup(html, 'html.parser')
        tags_items = soup.select('.su-card-container__content')
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(html)

        # loop over items in the page
        for tag_item in tags_items:

            # extract name of item 
            name = None 
            tags_name = tag_item.select('.s-card__title span.su-styled-text')
            for tag_name in tags_name:
                title = tag_name.text
                if title == "Shop on eBay":
                    continue
                name = title

            # skip over items with no name
            if name is None: 
                continue

            # extract price of item 
            price = None
            tags_price = tag_item.select('.s-card__price')
            for tag_price in tags_price:
                price = parse_price(tag_price.text)

            # extract status of item
            status = None 
            tags_status = tag_item.select('.su-styled-text.secondary.default')
            for tag_status in tags_status:
                status = tag_status.text

            # extract shipping price of item 
            shipping = None
            tags_shipping = tag_item.select('.su-styled-text.secondary.large')
            for tag_shipping in tags_shipping:
                if 'delivery' in tag_shipping.text.lower() or 'shipping' in tag_shipping.text.lower():
                    shipping = parse_shipping(tag_shipping.text)

            # extract items with free returns 
            free_returns = False
            tags_freereturns = tag_item.select('.su-styled-text.secondary.large')
            for tag_freereturns in tags_freereturns:
                if 'free returns' in tag_freereturns.text.lower():
                    free_returns = True

            # extract the number of items sold  
            items_sold = 0
            tags_itemssold = tag_item.select('.su-styled-text.primary.bold.large')
            for tag_itemssold in tags_itemssold:
                if 'sold' in tag_itemssold.text.lower():
                    items_sold = parse_itemssold(tag_itemssold.text)


            # create dictionary for each item and add it to the list
            item = {
                'name': name,
                'price': price,
                'status': status,
                'shipping': shipping,
                'free_returns': free_returns,
                'items_sold': items_sold,
            }
            items.append(item)

    print('total items=', len(items))

    # replace any spaces with a '_' to eliminate syntax errors
    filename = args.search_term.replace(' ', '_')  

    if args.csv:
        with open(filename + '.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'status', 'shipping', 'free_returns', 'items_sold'])
            writer.writeheader()
            writer.writerows(items)
        print('saved to', filename + '.csv')
    else:
        with open(filename + '.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
        print('saved to', filename + '.json')



        
        
        
        
        
        
        
        
        
        
