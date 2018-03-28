import requests
import re
from bs4 import BeautifulSoup

class Scrapy(object):
    def scrape(self, url):
        url = "https://www.amazon.com/Your-Mind-Can-Heal-You/dp/1163201189?SubscriptionId=AKIAI43JB5HRRQCS6TXQ&tag=archivetestac&linkCode=xm2&camp=2025&creative=165953&creativeASIN=1163201189"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'})
        content = BeautifulSoup(r.text, 'html.parser')
        if r.status_code == 502:
            return self.scrape(url)

        bad_gate_way = content.select('body center h1')
        if bad_gate_way:
            if bad_gate_way.get_text() == "502 Bad Gateway":
                return self.scrape(url)

        captcha = content.find('input', {'id': 'captchacharacters'})
        if captcha:
            return self.scrape(url)

        return self.parse(content)

    def parse(self, content):
        total_new = 0
        total_used = 0
        total_collectible = 0

        versions = content.select('.swatchElement')

        if versions:
            for version in versions:
                version_name = version.select('.a-list-item .a-button-inner a span')[0].get_text().strip()
                links = version.select('.a-list-item .tmm-olp-links .olp-link .a-size-mini')

                if version_name == 'Kindle':
                    total_new = total_new + 1

                data = self.processContent(links)
                total_new = total_new + data['count_new']
                total_used = total_used + data['count_used']
                total_collectible = total_collectible + data['count_collectible']

        choices = content.find('div', {'id': 'mediaOlp'})

        if choices:
            links = choices.select('.a-row .a-section span a')

            data = self.processContent(links)
            total_new = total_new + data['count_new']
            total_used = total_used + data['count_used']
            total_collectible = total_collectible + data['count_collectible']

        if total_new == 0 and total_used == 0:
            print("empty count detected")

        ret = {
            'total_new' : total_new,
            'total_used' : total_used,
            'total_collectible' : total_collectible
        }

        return ret

    def processContent(self, links):
        count_new = 0
        count_used = 0
        count_collectible = 0

        for link in links:
            content = link.get_text()
            match_new = re.search(r'(\d*)(\sNew)', content)
            match_used = re.search(r'(\d*)(\sUsed)', content)
            match_collectible = re.search(r'(\d*)(\sCollectible)', content)

            if match_new:
                count_new = int(match_new.groups()[0])
            elif match_used:
                count_used = int(match_used.groups()[0])
            elif match_collectible:
                count_collectible = int(match_collectible.groups()[0])

        return {
            'count_new' : count_new,
            'count_used' : count_used,
            'count_collectible' : count_collectible
        }