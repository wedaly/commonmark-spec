#!/usr/bin/env python3

import sys
import json
import re
import xml.etree.ElementTree as ET


def main():
    results = []
    with open("commonmark_0.3_testcases.json") as f:
        for testcase in json.load(f):
            results.append(munge(testcase))
    print(json.dumps(results, indent=2))


def munge(tc):
    xmlroot = ET.fromstring(tc["xml"])
    tokens = xml_to_tokens(xmlroot, tc["markdown"])
    return {
        "name": tc["section"].lower().replace(" ", "_") + "_" + str(tc["example"]),
        "markdown": tc["markdown"],
        "tokens": tokens,
    }


TAG_TO_TOKEN = {
    "{http://commonmark.org/xml/1.0}code_block": "codeblock",
    "{http://commonmark.org/xml/1.0}emph": "emph",
    "{http://commonmark.org/xml/1.0}strong": "strong",
    "{http://commonmark.org/xml/1.0}heading": "heading",
    "{http://commonmark.org/xml/1.0}block_quote": "blockquote",
    "{http://commonmark.org/xml/1.0}link": "link",
    "{http://commonmark.org/xml/1.0}image": "image",
    "{http://commonmark.org/xml/1.0}item": "listitem",
}

list_item_number_re = re.compile("^\d+\.")
list_item_bullet_re = re.compile("^(-|\*)")

def xml_to_tokens(xmlroot, markdown):
    if xmlroot.tag in TAG_TO_TOKEN:
        tokentype = TAG_TO_TOKEN[xmlroot.tag]
        sourcepos = xmlroot.attrib['sourcepos']
        start, end = sourcepos.split('-')
        start_pos = resolve_pos(start, markdown)
        end_pos = resolve_pos(end, markdown) + 1

        if tokentype == "listitem":
            match = list_item_number_re.search(markdown[start_pos:end_pos])
            if match is not None:
                end_pos = start_pos + match.span()[1]
            else:
                match = list_item_bullet_re.search(markdown[start_pos:end_pos])
                if match is not None:
                    end_pos = start_pos + match.span()[1]

        return [{
            "type": tokentype,
            "start": start_pos,
            "end": end_pos,
            "text": markdown[start_pos:end_pos],
        }]
    else:
        tokens = []
        for child in xmlroot:
            tokens.extend(xml_to_tokens(child, markdown))
        return tokens


def resolve_pos(linecol, markdown):
    line, col = linecol.split(':')
    line = int(line)
    col = int(col)
    return sum(len(x) for x in markdown.split('\n')[0:line-1]) + col - 1


if __name__ == "__main__":
    main()
