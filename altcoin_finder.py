from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from tabulate import tabulate
import sys, getopt

if __name__ == "__main__":
   # parse command line arguments
   # we're setting the max market cap and min number of events
   # default to a market cap of 100 million and a min number of 4 events
   max_market_cap = 10000000
   min_num_events = 4
   if len(sys.argv) > 1:
      optlist, sys.argv = getopt.getopt(sys.argv[1:], 'm:e:', ['market_cap=', 'num_events='])
      for opt in optlist:
         if opt[0] == '-m' or opt[0] == '--market_cap':
            max_market_cap = opt[1]
         if opt[0] == '-e' or opt[0] == '--num_events':
            min_num_events = opt[1]

   print(f"Max market cap: {max_market_cap}")
   print(f"Min number of events: {min_num_events}")
   print("Fetching data...")

   url = 'https://coinmarketcal.com/en/coin-ranking?page=1&orderBy=&show_all=true'
   
   # Prevent the webpage from returning a 403 by making it think we're a real browser
   req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   
   # Fetch the data and parse it with soup
   uClient = urlopen(req)
   page_soup = BeautifulSoup(uClient.read(), "html.parser")
   uClient.close()
   
   list_wrapper = page_soup.find(id="coin-list-wrapper")
   list_header = list_wrapper.find("thead").find("tr")
   
   # used to keep track of column locations
   column_loc = 0
   
   # the columns aren't well labeled in the body of the list
   # use the header to make sure we're scraping from the correct columns
   name_col = 0
   market_cap_col = 0
   event_count_col = 0
   for column in list_header.children:
      if column.name == "th":
         if 'data-field' in column.attrs.keys():
            field = column["data-field"]
            if field == "full_name":
               name_col = column_loc
            if field == "market_cap_usd":
               market_cap_col = column_loc
            if field == "upcoming_event_count":
               event_count_col = column_loc
         column_loc += 1
   
   # this will store our list of potential altcoins
   viable_altcoins = []
   
   list_body = list_wrapper.find("tbody").find_all("tr")
   
   for row in list_body:
      column_loc = 0
      name = ""
      market_cap = 0
      event_count = 0
      events_url = ""
      for column in row.children:
         if column.name == "td":
   
            if column_loc == name_col:
               name = column["data-value"]
               events_url = "https://coinmarketcal.com" + column.a["href"]
   
            if column_loc == market_cap_col:
               market_cap_str = column["data-value"]
               if len(market_cap_str) > 0:
                  market_cap = int(market_cap_str)
   
            if column_loc == event_count_col:
               event_count_str = column["data-value"]
               if len(event_count_str) > 0:
                  event_count = int(event_count_str)
   
            column_loc += 1
   
      if market_cap > 0 and market_cap < 100000000 and event_count > 3:
         viable_altcoins.append([name, market_cap, event_count, events_url])
         #print(name.encode('utf-8'), ", ", market_cap, ", ", event_count, ", ", events_url)

   print(tabulate(viable_altcoins, headers=['Coin', 'Market Cap', 'Event Count', 'Calender URL'], tablefmt='orgtbl'))
