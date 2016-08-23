import requests
import re
import itertools
import random
import bs4
import traceback


olympic_html_file = "Data/scrape/Olympic Results - Official Records.html"
test_event_file = "Data/test/Beijing 2008 1500m men - Olympic Beijing 2008 Athletics.html"
race_results_file = "Data/scrape/race_results/race_results.txt"


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


def get_all_result_urls():
    years = get_olympic_year_strings()
    events = get_olympic_event_strings()

    return ["https://www.olympic.org/%s/athletics/%s" % (year, event) for year, event in itertools.product(*[years, events])]


def separate_athlete_county(table_columns):
    a_and_c = table_columns[1]
    athlete = a_and_c[:a_and_c.find("\n")]
    country = a_and_c[a_and_c.rfind("\n") + 1:]
    table_columns[1] = athlete
    table_columns.insert(2, country)
    return table_columns


def parse_html_results(html):
    has_place = lambda row: len(row) > 0 and (row[0] in ['G', 'S', 'B'] or row[0][:-1].isdigit())
    trim_place = lambda place: place if not place[0].isdigit() else place[:-1]
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
            cols[0] = trim_place(cols[0])
            data.append(cols)

    return [x for x in map(separate_athlete_county, data)]


def get_race_title(html):
    bs = bs4.BeautifulSoup(html, "html.parser")
    title = bs.find(lambda tag: tag.name == 'title')
    return title.text


def save_race_results(result_urls):
    writer = open(race_results_file, "w", encoding='utf-8')
    for url in result_urls:
        response = requests.get(url)
        if(response.status_code == 200):
            try:
                html = response.text
                title = get_race_title(html)
                data = parse_html_results(html)
                writer.write(title + "\n")
                for line in data:
                    writer.write(",".join(x for x in line) + "\n")
                writer.write("\n")
            except:
                print(title)
                traceback.print_exc()
        else:
            print(url, response.status_code)


urls = get_all_result_urls()
save_race_results(urls)
