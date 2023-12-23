#!/usr/bin/python3

with open('all.m3u', 'r', encoding='utf8') as f:
    lines = f.readlines()

first_line = lines[0]
tr_title_lines = []

for index, line in enumerate(lines):
    if 'group-title="|TR|' in line:
        tr_title_lines.append(index)

for index, line in enumerate(lines):
    if index > tr_title_lines[len(tr_title_lines) - 1] and line == '\n':
        last_empty_line = index
        break

del lines[last_empty_line:]
del lines[:tr_title_lines[0]]


first_title_line = tr_title_lines[0]
new_lines = []

search_text = 'group-title="|TR|'
for index, line in enumerate(lines):
    if "#EXTINF:0" in line:
        if search_text in line:
            group_start = line.find(search_text) + len(search_text) + 3
            group_end = line.find('",')
            group = line[group_start:group_end]
            line = line[:group_start - 7] + line[group_start:]
        else:
            insert_location = line.find('",') + 1
            line = line[:insert_location] + ' group-title="' + \
                group + '"' + line[insert_location:]
    new_lines.append(line)

# for index, line in enumerate(new_lines):
#     print(index + 1, line.strip())

with open('tr.m3u', 'w', encoding='utf8') as f:
    f.write(first_line)
    f.writelines(new_lines)
