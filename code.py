from bs4 import BeautifulSoup
import csv
import re
import time

start_time = time.time()

# Open and read the HTML file
with open('total_source.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Define the fields to extract from the HTML tables
fields = [
    ("對象：", lambda td: re.sub(r'\s*\([^)]*\)', '', td.text.strip()), "對象"),
    ("項目：", lambda td: td.text.split(' ')[-1].strip('()'), "YMcode"),
    ("子項目：", lambda td: td.text.split(' ')[-1].strip('()'), "Mcode"),
    ("課程／項目管理：", lambda td: td.text.split(' ')[-1].strip('()'), "CURcode"),
    ("課程／項目管理狀態：", lambda td: td.text.strip(), "CUR狀態"),
    ("時間：", lambda td: td.text.strip().split(' ', 1)[0], "ADcode"),
    ("活動／課節狀態：", lambda td: td.text.strip(), "AD狀態"),
    ("時間：", lambda td: re.search(r'\d{4}-\d{2}-\d{2}', td.text.strip()).group() if re.search(r'\d{4}-\d{2}-\d{2}', td.text.strip()) else None, "日期"),
    ("時間：", lambda td: re.search(r'\d{2}:\d{2}至\d{2}:\d{2}', td.text.strip()).group() if re.search(r'\d{2}:\d{2}至\d{2}:\d{2}', td.text.strip()) else None, "時間"),
    ("課程／項目管理：", lambda td: td.text.split('(')[0].strip('項目管理'), "地點")
]

# Prepare the CSV file header
header = [label for _, __, label in fields]
header.append("建立日期")

# Find all tables in the HTML content
tables = soup.find_all('table')

# List to store the rows of data
data_rows = []
seen_rows = set()  

# Process each table
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        if row.find('td'):
            row_data = []
            for field, func, label in fields:
                td_element = row.find(text=re.compile(field))
                if td_element:
                    td_element = td_element.find_next("td")
                    result = func(td_element) if td_element else None
                else:
                    result = None
                row_data.append(result)

            # Extract the "建立日期" dynamically for each row
            created_date_text = row.find(text=re.compile("建立日期"))
            if created_date_text:
                created_date = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', created_date_text)
                created_date = created_date.group() if created_date else None
            else:
                created_date = None
            row_data.append(created_date)

            row_tuple = tuple(row_data)
            if row_tuple not in seen_rows and not all(item is None or item == '' for item in row_data):
                seen_rows.add(row_tuple)
                meaningful_field_count = sum(1 for item in row_data if item is not None and item.strip() != '')
                if meaningful_field_count >= len(row_data) / 2:
                    data_rows.append(row_data)

# Write the data rows to a CSV file
csv_filename = 'output.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='|')
    writer.writerow(header)
    for data_row in data_rows:
        writer.writerow(data_row)

end_time = time.time()
runtime_seconds = end_time - start_time

# Print a message to the console
print(f"Data has been written to '{csv_filename}'")
print(f"Runtime: {runtime_seconds:.2f} seconds")

# type: ignore