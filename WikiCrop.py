import re
import bs4


price_re = re.compile(r"\n*(\d+(\.\d+)?)g")
harvest_re = re.compile(r"(Total|Regrowth):\s?(\d+|every) days?")
gold_per_day_re = re.compile(r"")


# TODO: get gold_per_day
# TODO: get harvest time
class WikiCrop:
    def __init__(self, name, season):
        self.name = name
        self.gold_per_day = []
        self.buy = {"Pierre's": 0, "JojaMart": 0}
        self.sell = {"normal": 0, "silver": 0, "gold": 0}
        self.harvest = 0
        self.season = season
        self.regrowth = False
        self.regrowth_rate = 0

    def parse_sell_price_cell(self, cell_tag):
        prices = cell_tag.find_all(text=price_re)
        prices = [price_re.match(price).group(1) for price in prices]
        prices = [int(price) for price in prices]  # convert to int
        self.sell["normal"] = prices[0]
        self.sell["silver"] = prices[1]
        self.sell["gold"] = prices[2]

    def parse_buy_price_cell(self, cell_tag):
        pierres_tag = cell_tag.find_next(text=re.compile(r"Pierre's"))
        pierre_price = "0g"
        jojamart_price = "0g"
        if pierres_tag:
            pierre_price = pierres_tag.find_next(text=price_re)
        jojamart_tag = cell_tag.find_next(text=re.compile(r"JojaMart"))
        if jojamart_tag:
            jojamart_price = jojamart_tag.find_next(text=price_re)
        self.buy["Pierre's"] = int(price_re.match(pierre_price).group(1))
        self.buy["JojaMart"] = int(price_re.match(jojamart_price).group(1))

    def parse_harvest_data(self, harvest_tag):
        total_tag = harvest_tag
        if self.regrowth:
            regrowth_tag = total_tag
            total_tag = regrowth_tag.find_previous("td")
            regrowth_text = harvest_re.match(regrowth_tag.text).group(2)
            if regrowth_text == "every":
                regrowth_text = 1
            self.regrowth_rate = int(regrowth_text)
        total_text = harvest_re.match(total_tag.text).group(2)
        self.harvest = int(total_text)

    def table_to_data(self, table_tag: bs4.element.Tag):
        table_data = []
        rows = table_tag.find_all("tr", recursive=False)
        self.parse_buy_price_cell(rows[1].find_next("td"))
        ix = 0

        def get_sell_col_num():
            col_tags = rows[0].find_all("th", recursive=False)
            cols_text = [col.text.strip() for col in col_tags]
            padding = 0
            for col_tag in col_tags:
                col_text = col_tag.text.strip()
                if col_text == "Harvest" \
                        and 'colspan' in col_tag.attrs \
                        and int(col_tag['colspan']) == 2:
                    padding = 1
                    self.regrowth = True
                    break
            return cols_text.index("Sells For") + padding

        sell_column = get_sell_col_num()
        for row in rows[1:]:  # skip header
            cols = row.find_all("td", recursive=False)  # skip last 2
            if ix == 0:
                cols = cols[1:sell_column+1]
            ix += 1
            cols = [elem for elem in cols]  # get only stripped text
            table_data.append([elem for elem in cols])
        self.parse_sell_price_cell(table_data[0][sell_column-1])
        self.parse_harvest_data(table_data[1][sell_column-2])
        sell_tag = table_data[1][sell_column-1]
        for sell_match in price_re.finditer(sell_tag.text):
            self.gold_per_day.append(float(sell_match.group(1)))

    def __str__(self):
        text = "{}\n  season: {}\n  sell: {}\n  gold_per_day: {}\n  buy: {}\n  harvest: {}".format(
            self.name, self.season, self.sell, self.gold_per_day, self.buy, self.harvest)
        if self.regrowth:
            text += "\n  regrowth: {}".format(self.regrowth_rate)
        return text
