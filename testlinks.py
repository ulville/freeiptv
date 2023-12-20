#!/usr/bin/python3
from subprocess import run
import re
import m3u8
from m3u8 import protocol
from m3u8.parser import save_segment_custom_value
from urllib.error import HTTPError, URLError


def parse_iptv_attributes(line, lineno, data, state):
    # Customize parsing #EXTINF
    if line.startswith(protocol.extinf):
        title = ''
        chunks = line.replace(protocol.extinf + ':', '').split(',', 1)
        if len(chunks) == 2:
            duration_and_props, title = chunks
        elif len(chunks) == 1:
            duration_and_props = chunks[0]

        additional_props = {}
        chunks = duration_and_props.strip().split(' ', 1)
        if len(chunks) == 2:
            duration, raw_props = chunks
            matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
            for match in matched_props:
                additional_props[match.group(1)] = match.group(2)
        else:
            duration = duration_and_props

        if 'segment' not in state:
            state['segment'] = {}
        state['segment']['duration'] = float(duration)
        state['segment']['title'] = title

        # Helper function for saving custom values
        save_segment_custom_value(state, 'extinf_props', additional_props)

        # Tell 'main parser' that we expect an URL on next lines
        state['expect_segment'] = True

        # Tell 'main parser' that it can go to next line, we've parsed current fully.
        return True


if __name__ == '__main__':
    FILE = "tr.m3u"

    parsed = m3u8.load(FILE, custom_tags_parser=parse_iptv_attributes)
    print(parsed.is_variant)

    for s in parsed.segments:
        segment_props = s.custom_parser_values['extinf_props']
        print("title:", s.title)
        print("logo:", segment_props["tvg-logo"])
        print("group:", segment_props['group-title'])
        print("uri:", s.uri)
        try:
            m = m3u8.load(s.uri, 5)
            print("is_vaiant:", m.is_variant)
            if m.is_variant:
                for playlist in m.playlists:
                    print("    ***")
                    print("    playlist.uri:", playlist.uri)
                    print("    playlist.absolute_uri:", playlist.absolute_uri)
                    print("    playlist.stream_info:", playlist.stream_info)
        except (HTTPError, URLError, TimeoutError) as e:
            print("\033[31mFailed!:\033[0m", e)
        
        print("-"*70)
    # print(first_segment_props['catchup-type'])  # 'flussonic'

# with open('tr.m3u', 'r', encoding='utf8') as f:
#     lines = f.readlines()

# for index, line in enumerate(lines):
#     if line[0:9] == '#EXTINF:0':
#         link = lines[index + 1].strip()
#         print(line + link)

#         try:
#             playlist = m3u8.load(link)
#             print('✅')
#             with open('success.txt', 'a', encoding='utf8') as f:
#                 f.writelines([line, link + '\n'])
#         except:
#             print('❌')
#             with open('failed.txt', 'a', encoding='utf8') as f:
#                 f.writelines([line, link + '\n'])

        # print(playlist.dumps())
        # print(playlist.segments)
        # print(playlist.target_duration)

        # try:
        #     p = run(['mpv', '--network-timeout=9', link], timeout=32)
        #     print("GALİBA FAILED:", p.returncode)
        #     with open('failed.txt', 'a', encoding='utf8') as f:
        #         f.writelines([line, link + '\n'])
        # except:
        #     print("GALİBA SUCCESS:")
        #     with open('success.txt', 'a', encoding='utf8') as f:
        #         f.writelines([line, link + '\n'])
