import io
import re
import sys
import requests
import zipfile
import webbrowser
from urllib import parse
from bs4 import BeautifulSoup

core_package = sys.argv[1]

dependency_dict = dict()


def get_requirements(package_name: str):
    if not package_name in dependency_dict:
        dependency_dict[package_name] = []
    else:
        return
    page = requests.get('https://pypi.org/simple/' + package_name)

    data = page.text
    soup = BeautifulSoup(data, features='html.parser')

    last_ver = None

    for link in soup.find_all('a'):
        if '.whl' in link.get('href'):
            last_ver = link.get('href')
    if last_ver is None:
        return
    r = requests.get(last_ver).content
    file = zipfile.ZipFile(io.BytesIO(r))

    for dist in list(line for line in file.open(list(meta_data for meta_data in file.namelist()
                    if meta_data.find('METADATA') != -1)[0]).readlines()
                    if line.decode().find('Requires-Dist:') != -1 and line.decode().find('extra ==') == -1):
        req_name = re.match(r'Requires-Dist:\s[\w\-.]+', dist.decode()).group().split()[1]
        # if req_name in dependency_dict[package_name]:
        #     print(req_name)
        if req_name not in dependency_dict[package_name]:
            dependency_dict[package_name].append(req_name)
            get_requirements(req_name)
    file.close()


def make_graphviz_code(dep_dict: dict):
    edge_list = 'digraph G {\n'
    for parent in dep_dict:
        for dep in dep_dict[parent]:
            edge_list += '\t"' + parent + '" -> "' + dep + '";\n'
    edge_list += '}'
    return edge_list


get_requirements(core_package)
code = make_graphviz_code(dependency_dict)
print(code)
webbrowser.open('https://dreampuf.github.io/GraphvizOnline/#' + parse.quote(code), new=2)