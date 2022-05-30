#!/usr/bin/env python3

import sys
import json
import re
import xml.etree.ElementTree as ET

ENABLED_SECTIONS = set([
    "Thematic breaks",
    "ATX headings",
    "Setext headings",
    "Fenced code blocks",
    "Lists",
    "List items",
])

DEVIATE_REASON = "intentional deviation from spec"
TEST_WRONG_REASON = "test case is incorrect"
UNSUPPORTED_REASON = "contains unsupported block type"

SKIPPED_EXAMPLES = {
    48: DEVIATE_REASON,
    49: DEVIATE_REASON,
    59: TEST_WRONG_REASON,
    61: DEVIATE_REASON,
    69: DEVIATE_REASON,
    70: DEVIATE_REASON,
    85: DEVIATE_REASON,
    87: DEVIATE_REASON,
    91: DEVIATE_REASON,
    92: DEVIATE_REASON,
    92: UNSUPPORTED_REASON,
    93: UNSUPPORTED_REASON,
    96: TEST_WRONG_REASON,
    100: UNSUPPORTED_REASON,
    101: UNSUPPORTED_REASON,
    128: UNSUPPORTED_REASON,
    138: DEVIATE_REASON,
}


def main():
    results = []
    with open("commonmark_0.3_testcases.json") as f:
        for testcase in json.load(f):
            results.append(munge(testcase))
    print(json.dumps(results, indent=2))


def munge(tc):
    if tc["markdown"].endswith('\n'):
        tc["markdown"] = tc["markdown"][:-1]

    xmlroot = ET.fromstring(tc["xml"])
    tokens = xml_to_tokens(xmlroot, tc["markdown"])

    if "link reference" in tc["section"].lower():
        tokens.extend(link_ref_tokens(tc["markdown"]))

    tokens.sort(key=lambda x: x["start"])

    output = {
        "name": tc["section"].lower()+ " " + str(tc["example"]),
        "markdown": tc["markdown"],
        "tokens": tokens,
    }

    if tc["section"] not in ENABLED_SECTIONS:
        output["skipReason"] = "not implemented"
    elif tc["example"] in SKIPPED_EXAMPLES:
        output["skipReason"] = SKIPPED_EXAMPLES[tc["example"]]

    return output


TAG_TO_TOKEN_ROLE = {
    "{http://commonmark.org/xml/1.0}code_block": "CodeBlock",
    "{http://commonmark.org/xml/1.0}code": "CodeSpan",
    "{http://commonmark.org/xml/1.0}emph": "Emphasis",
    "{http://commonmark.org/xml/1.0}strong": "StrongEmphasis",
    "{http://commonmark.org/xml/1.0}heading": "Heading",
    #"{http://commonmark.org/xml/1.0}block_quote": "BlockQuote",
    "{http://commonmark.org/xml/1.0}link": "Link",
    "{http://commonmark.org/xml/1.0}image": "Link",
    "{http://commonmark.org/xml/1.0}item": "ListItem",
    #"{http://commonmark.org/xml/1.0}html_block": "HtmlBlock",
    "{http://commonmark.org/xml/1.0}thematic_break": "ThematicBreak",
}

list_item_number_re = re.compile("^\d+(\.|\))")
list_item_bullet_re = re.compile("^(-|\*|\+)")
link_ref_re = re.compile("^[ ]{0,3}\[.+\]:.*$")

def xml_to_tokens(xmlroot, markdown):
    if xmlroot.tag in TAG_TO_TOKEN_ROLE:
        tokenrole = TAG_TO_TOKEN_ROLE[xmlroot.tag]
        sourcepos = xmlroot.attrib['sourcepos']
        start, end = sourcepos.split('-')
        start_pos = resolve_pos(start, markdown)
        end_pos = resolve_pos(end, markdown) + 1

        if tokenrole == "ListItem":
            match = list_item_number_re.search(markdown[start_pos:end_pos])
            if match is not None:
                end_pos = start_pos + match.span()[1]
                tokenrole = "ListNumber"
            else:
                match = list_item_bullet_re.search(markdown[start_pos:end_pos])
                if match is not None:
                    end_pos = start_pos + match.span()[1]
                    tokenrole = "ListBullet"

        elif tokenrole == "CodeSpan":
            while start_pos > 0:
                if markdown[start_pos-1] == '`':
                    start_pos -= 1
                else:
                    break

            while end_pos < len(markdown):
                if markdown[end_pos] == '`':
                    end_pos += 1
                else:
                    break
        elif tokenrole == "CodeBlock":
            while start_pos > 0:
                if markdown[start_pos-1] == ' ' or markdown[start_pos-1] == '\t':
                    start_pos -= 1
                else:
                    break
            if end_pos < len(markdown) and markdown[end_pos-1] != '\n' and markdown[end_pos] == '\n':
                end_pos += 1

        elif tokenrole == "Heading":
            while start_pos > 0:
                if markdown[start_pos-1] == ' ' or markdown[start_pos-1] == '\t':
                    start_pos -= 1
                else:
                    break

            while end_pos < len(markdown):
                if markdown[end_pos-1] != '\n':
                    end_pos += 1
                else:
                    break

        elif tokenrole == "ThematicBreak":
            while start_pos > 0:
                if markdown[start_pos-1] == ' ' or markdown[start_pos-1] == '\t':
                    start_pos -= 1
                else:
                    break

            if end_pos < len(markdown) and markdown[end_pos-1] != '\n' and markdown[end_pos] == '\n':
                end_pos += 1

        return [{
            "role": tokenrole,
            "start": start_pos,
            "end": end_pos,
            "text": markdown[start_pos:end_pos],
        }]
    else:
        tokens = []
        for child in xmlroot:
            tokens.extend(xml_to_tokens(child, markdown))
        return tokens


def link_ref_tokens(markdown):
    tokens = []
    start = 0
    for line in markdown.splitlines(keepends=True):
        match = link_ref_re.match(line)
        if match is not None:
            end = start + len(line)
            tokens.append({
                "role": "LinkRef",
                "start": start,
                "end": end,
                "text": markdown[start:end],
            })
        start += len(line)
    return tokens


def resolve_pos(linecol, markdown):
    line, col = linecol.split(':')
    line = int(line)
    col = int(col)
    return sum(len(x) for x in markdown.splitlines(keepends=True)[0:line-1]) + col - 1


if __name__ == "__main__":
    main()
