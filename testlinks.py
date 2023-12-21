#!/usr/bin/python3
import os
import re
import m3u8
from m3u8 import protocol
from m3u8.model import M3U8, number_to_string
from m3u8.parser import save_segment_custom_value
from urllib.error import HTTPError, URLError
from http.client import InvalidURL
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-o",
    "--override",
    action="store_true",
)
args = parser.parse_args()



def dumps_iptv(iptv : M3U8):
    output = ["#EXTM3U"]
    last_group = ""
    for seg in iptv.segments:
        segdumps = []
        seg_props = seg.custom_parser_values["extinf_props"]
        if seg_props["group-title"] != last_group and last_group != "":
            segdumps.append(2*"\n")
        last_group = seg_props["group-title"]
        if seg.uri:
            if seg.duration is not None:
                segdumps.append("#EXTINF:%s" % number_to_string(seg.duration))
                if seg_props["tvg-logo"]:
                    segdumps.append(" tvg-logo=\"%s\"" % seg_props["tvg-logo"])
                if seg_props["group-title"]:
                    segdumps.append(" group-title=\"%s\"" % seg_props["group-title"])
                if seg.title:
                    segdumps.append("," + seg.title)
                segdumps.append("\n")
            segdumps.append(seg.uri)
        output.append("".join(segdumps))
    return "\n".join(output)

def dump_iptv(iptv, filename):
    """
    Saves the current m3u8 to ``filename``
    """
    create_sub_directories(filename)

    with open(filename, "w") as fileobj:
        fileobj.write(dumps_iptv(iptv))

def create_sub_directories(filename):
    basename = os.path.dirname(filename)
    if basename:
        os.makedirs(basename, exist_ok=True)


def parse_iptv_attributes(line, lineno, data, state):
    # Customize parsing #EXTINF
    if line.startswith(protocol.extinf):
        title = ""
        chunks = line.replace(protocol.extinf + ":", "").split(",", 1)
        if len(chunks) == 2:
            duration_and_props, title = chunks
        elif len(chunks) == 1:
            duration_and_props = chunks[0]

        additional_props = {}
        chunks = duration_and_props.strip().split(" ", 1)
        if len(chunks) == 2:
            duration, raw_props = chunks
            matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
            for match in matched_props:
                additional_props[match.group(1)] = match.group(2)
        else:
            duration = duration_and_props

        if "segment" not in state:
            state["segment"] = {}
        state["segment"]["duration"] = float(duration)
        state["segment"]["title"] = title

        # Helper function for saving custom values
        save_segment_custom_value(state, "extinf_props", additional_props)

        # Tell 'main parser' that we expect an URL on next lines
        state["expect_segment"] = True

        # Tell 'main parser' that it can go to next line, we've parsed current fully.
        return True

def is_success(playlist):
    try:
        m3u8.load(playlist.absolute_uri, 10)
        return True
    except (HTTPError, URLError, TimeoutError, InvalidURL, KeyError):
        return False


def get_failed_links(channel_list):
    failed = []
    for i, s in enumerate(channel_list.segments):
        try:
            m = m3u8.load(s.uri, 10)
            if m.is_variant:
                if not any([is_success(pl) for pl in m.playlists]):
                    failed.append(s)
        except (HTTPError, URLError, TimeoutError, InvalidURL, KeyError) as e:
            if "http://localhost:53422" not in s.uri:
                failed.append(s)
        print(f"tested {i} / {len(channel_list.segments)}", s.uri)
    return failed
            

if __name__ == "__main__":
    FILE = "tr.m3u"

    parsed = m3u8.load(FILE, custom_tags_parser=parse_iptv_attributes)
    for failed_segment in get_failed_links(parsed):
        parsed.segments.remove(failed_segment)
    if args.override:
        dump_iptv(parsed, FILE)
    else:
        dump_iptv(parsed, "success.m3u")

    # print(parsed.is_variant)

    # for s in parsed.segments:
    #     segment_props = s.custom_parser_values["extinf_props"]
    #     print("title:", s.title)
    #     print("logo:", segment_props["tvg-logo"])
    #     print("group:", segment_props["group-title"])
    #     print("uri:", s.uri)
    #     try:
    #         m = m3u8.load(s.uri, 5)
    #         print("is_vaiant:", m.is_variant)
    #         if m.is_variant:
    #             for playlist in m.playlists:
    #                 print("    ***")
    #                 print("    playlist.uri:", playlist.uri)
    #                 print("    playlist.absolute_uri:", playlist.absolute_uri)
    #                 print("    playlist.stream_info:", playlist.stream_info)
    #                 print("        * PLAYLIST CONTENT:")
    #                 try:
    #                     pm = m3u8.load(playlist.absolute_uri)
    #                     print("        is_variant:", pm.is_variant)
    #                     assert not pm.is_variant
    #                     for plts in pm.segments:
    #                         print("        \033[36mts.absolute_uri:\033[0m", plts.absolute_uri)
    #                         print("        ts.duration:", plts.duration)
    #                 except (HTTPError, URLError, TimeoutError, InvalidURL) as e:
    #                     print("    \033[31mFailed!:\033[0m", e)
    #         else:
    #             print("    ***")
    #             print("    SEGMENTS:")
    #             for ts in m.segments:
    #                 print("        \033[33mts.absolute_uri:\033[0m", ts.absolute_uri)
    #                 print("        ts.duration:", ts.duration)
    #     except (HTTPError, URLError, TimeoutError, InvalidURL) as e:
    #         print("\033[31mFailed!:\033[0m", e)
            

        # print("-" * 70)

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
