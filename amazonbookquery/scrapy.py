import requests
import re
from bs4 import BeautifulSoup

class Scrapy(object):
    def scrape(self, url):
        # url = "https://www.amazon.com/Your-Mind-Can-Heal-You/dp/1163201189?SubscriptionId=AKIAI43JB5HRRQCS6TXQ&tag=archivetestac&linkCode=xm2&camp=2025&creative=165953&creativeASIN=1163201189"
        # print(url)
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
        lowest_new_price = lowest_used_price = lowest_collectible_price = -1

        versions = content.select('.swatchElement')

        if versions:
            for version in versions:
                version_name = version.select('.a-list-item .a-button-inner a span')[0].get_text().strip()
                links = version.select('.a-list-item .tmm-olp-links .olp-link .a-size-mini')

                # if version_name == 'Kindle':
                #     total_new = total_new + 1

                data = self.processContent(links)
                total_new = total_new + data['count_new']
                total_used = total_used + data['count_used']
                total_collectible = total_collectible + data['count_collectible']

                if lowest_new_price == -1:
                    lowest_new_price = data['price_new']
                elif (data['price_new'] != -1 and lowest_new_price != -1 and data['price_new'] < lowest_new_price):
                    lowest_new_price = data['price_new']

                if lowest_used_price == -1:
                    lowest_used_price = data['price_used']
                elif (data['price_used'] != -1 and lowest_used_price != -1 and data['price_used'] < lowest_used_price):
                    lowest_used_price = data['price_used']

                if lowest_collectible_price == -1:
                    lowest_collectible_price = data['price_collectible']
                elif (data['price_collectible'] != -1 and lowest_collectible_price != -1 and data['price_collectible'] < lowest_collectible_price):
                    lowest_collectible_price = data['price_collectible']

        choices = content.find('div', {'id': 'mediaOlp'})

        if choices:
            links = choices.select('.a-row .a-section .olp-padding-right')

            data = self.processContent(links)
            total_new = total_new + data['count_new']
            total_used = total_used + data['count_used']
            total_collectible = total_collectible + data['count_collectible']

            if lowest_new_price == -1:
                lowest_new_price = data['price_new']
            elif (data['price_new'] != -1 and lowest_new_price != -1 and data['price_new'] < lowest_new_price):
                lowest_new_price = data['price_new']

            if lowest_used_price == -1:
                lowest_used_price = data['price_used']
            elif (data['price_used'] != -1 and lowest_used_price != -1 and data['price_used'] < lowest_used_price):
                lowest_used_price = data['price_used']

            if lowest_collectible_price == -1:
                lowest_collectible_price = data['price_collectible']
            elif (data['price_collectible'] != -1 and lowest_collectible_price != -1 and data[
                'price_collectible'] < lowest_collectible_price):
                lowest_collectible_price = data['price_collectible']

        ret = {
            'total_new' : total_new,
            'total_used' : total_used,
            'total_collectible' : total_collectible,
            'lowest_new_price' : lowest_new_price if lowest_new_price != -1 else "",
            'lowest_used_price' : lowest_used_price if lowest_used_price != -1 else "",
            'lowest_collectible_price' : lowest_collectible_price if lowest_collectible_price != -1 else ""
        }

        return ret

    def processContent(self, links):
        count_new = count_used = count_collectible = 0
        price_new = price_used = price_collectible = -1

        for link in links:
            content = link.get_text()
            match_new = re.search(r'(\d*)(\sNew)', content)
            match_used = re.search(r'(\d*)(\sUsed)', content)
            match_collectible = re.search(r'(\d*)(\sCollectible)', content)
            match_price = re.search(r'(from\s\$)(\d*.\d*)', content)

            if match_new:
                count_new = int(match_new.groups()[0])
                price_new = float(match_price.groups()[1])
            elif match_used:
                count_used = int(match_used.groups()[0])
                price_used = float(match_price.groups()[1])
            elif match_collectible:
                count_collectible = int(match_collectible.groups()[0])
                price_collectible = float(match_price.groups()[1])

        return {
            'count_new' : count_new,
            'count_used' : count_used,
            'count_collectible' : count_collectible,
            'price_new' : price_new,
            'price_used' : price_used,
            'price_collectible' : price_collectible
        }