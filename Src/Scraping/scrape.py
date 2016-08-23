import requests
import re
import itertools
import random
import bs4


olympic_html_file = "Data/scrape/Olympic Results - Official Records.html"
test_event_file = "Data/Beijing 2008 1500m men - Olympic Beijing 2008 Athletics.html"


def get_olympic_year_strings():
    reader = open(olympic_html_file, "rb")
    text = str(reader.read())
    matches = re.findall('summergames"> <a href="https://www.olympic.org/.{1,20}"', text)
    return [x[x.rfind("/") + 1:-1] for x in matches]


def get_olympic_event_strings():
    reader = open(olympic_html_file, "rb")
    text = str(reader.read())
    matches = re.findall('<option value="/.{1,30}/athletics/.{1,30}men"', text)
    return [x[x.rfind("/") + 1:-1] for x in matches]


def separate_athlete_county(table_columns):
    a_and_c = table_columns[1]
    athlete = a_and_c[:a_and_c.find("\n")]
    country = a_and_c[a_and_c.rfind("\n") + 1:]
    table_columns[1] = athlete
    table_columns.insert(2, country)
    return table_columns


def parse_html_results(html):
    has_place = lambda row: len(row) > 0 and (row[0] in ['G', 'S', 'B'] or row[0][:-1].isdigit())
    bs = bs4.BeautifulSoup(html, "html.parser")
    table = bs.find(lambda tag: tag.name == 'table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols = [ele for ele in cols if ele]
        if(has_place(cols)):
            data.append(cols)

    return [x for x in map(separate_athlete_county, data)]

data = parse_html_results(open(test_event_file, "rb").read())


#years = get_olympic_year_strings()
#events = get_olympic_event_strings()

#urls = ["https://www.olympic.org/%s/athletics/%s" % (year, event) for year, event in itertools.product(*[years, events])]

#url_subset = random.sample(urls, 5)
#for url in url_subset:
#    response = requests.get(url)
#    text = str(response.text)
#    print(url, response.status_code)
#    print(url, "table4" in text)
#    #print(url, "<h2>Ranking</h2>" in text)
#    #print(url, "<h2>Final</h2>" in text)
