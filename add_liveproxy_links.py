#!/usr/bin/python3
import base64

source_stream_urls = {
    'ATV': 'https://www.atv.com.tr/canli-yayin',
    'KANAL D': 'https://www.kanald.com.tr/canli-yayin'}

liveproxy_urls = {name: 'http://localhost:53422/base64/' + base64.b64encode(
    f'streamlink {url} best'.encode(
        "utf8")).decode("ascii")
    for name, url in source_stream_urls.items()}

with open('tr.m3u', 'r', encoding='utf8') as f:
    lines = f.readlines()

for name, url in liveproxy_urls.items():
    for index, line in enumerate(lines):
        if f'",{name}\n' in line:
            print(lines[index + 1].strip(), 'replaced with')
            lines[index + 1] = url + '\n'
            print(lines[index + 1].strip(), end='\n\n')
            break

for name, url in liveproxy_urls.items():
    for index, line in enumerate(lines):
        if f'",{name}\n' in line:
            print(line.strip())
            print(lines[index + 1].strip())

with open('tr.m3u', 'w', encoding='utf8') as f:
    f.writelines(lines)
