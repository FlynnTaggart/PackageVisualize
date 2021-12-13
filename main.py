import io
import re
import sys
import requests
import zipfile
from bs4 import BeautifulSoup

page = requests.get('https://pypi.org/simple/' + sys.argv[1])

data = page.text
soup = BeautifulSoup(data, features='html.parser')

last_ver = None

for link in soup.find_all('a'):
    if '.whl' in link.get('href'):
        last_ver = link.get('href')

r = requests.get(last_ver).content
file = zipfile.ZipFile(io.BytesIO(r))

for dist in list(line for line in file.open(list(meta_data for meta_data in file.namelist()
        if meta_data.find('METADATA') != -1)[0]).readlines() if line.decode().find('Requires-Dist:') != -1):
    print(re.match(r'Requires-Dist:\s[\w\-.]+', dist.decode()).group().split()[1])
