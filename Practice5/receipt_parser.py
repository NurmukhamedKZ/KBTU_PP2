import re
# Prices
pattern = r"Стоимость\n\b\d{1,3}(?:\s\d{3})*,\d{2}\b"

with open("Practice5/raw.txt", "r") as f:
    text = f.read()
results = re.findall(pattern=pattern, string=text)

final_prices = []
for result in results:
    final_prices.append(result.replace("Стоимость\n", ""))
final_prices

# Names
pattern = r"\d{1,}\.\n[^\n]+"
names = [name[name.find("\n")+1:] for name in re.findall(pattern=pattern, string=text)]

# Full price
full_price = sum(float(price.replace(",",".").replace(" ","")) for price in final_prices)

# Date and time
pattern = r"Время:\s*(\d{2}\.\d{2}\.\d{4})\s*(\d{2}:\d{2}:\d{2})"

date_time = re.search(pattern, text)

date_obj = date_time.group(1)
time_obj = date_time.group(2)

# Payment method
pattern = r"([^\n]+)([^:]+\nИТОГО:)"

payment = re.search(pattern, text).group(1)

# JSON file
json_file = {
    "product_names": names,
    "product_prices": final_prices,
    "date": date_obj,
    "time": time_obj,
    "full_price": full_price,
    "payment_method": payment
}

print(json_file)