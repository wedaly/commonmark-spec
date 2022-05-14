#!/usr/bin/env python3

import sys
import json
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
        "markdown": tc["markdown"],
        "tokens": tokens,
    }


TAG_TO_TOKEN = {
    "{http://commonmark.org/xml/1.0}code_block": "codeblock",
    "{http://commonmark.org/xml/1.0}emph": "emph",
    "{http://commonmark.org/xml/1.0}strong": "strong",
}


def xml_to_tokens(xmlroot, markdown):
    if xmlroot.tag in TAG_TO_TOKEN:
        tokentype = TAG_TO_TOKEN[xmlroot.tag]
        sourcepos = xmlroot.attrib['sourcepos']
        start, end = sourcepos.split('-')
        start_pos = resolve_pos(start, markdown)
        end_pos = resolve_pos(end, markdown)
        return [{
            "type": tokentype,
            "start": start_pos,
            "end": end_pos,
        }]
    else:
        tokens = []
        for child in xmlroot:
            tokens.extend(xml_to_tokens(child, markdown))
        return tokens


if __name__ == "__main__":
    main()
