#!/usr/bin/env python3

import sys
import json
import re
import xml.etree.ElementTree as ET

NOT_IMPLEMENTED_SECTIONS = set([
    "Tabs",
    "Entity and numeric character references",
    "HTML blocks",
    "Raw HTML",
    "Autolinks",
    "Indented code blocks",
    "Link reference definitions",
    "Block quotes",
])

DEVIATE_REASON = "intentional deviation from spec"
TEST_WRONG_REASON = "test case is incorrect"
UNSUPPORTED_REASON = "contains unsupported content"

SKIPPED_EXAMPLES = {
    18: UNSUPPORTED_REASON,
    20: UNSUPPORTED_REASON,
    23: TEST_WRONG_REASON,
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
    141: DEVIATE_REASON,
    145: DEVIATE_REASON,
    225: UNSUPPORTED_REASON,
    253: UNSUPPORTED_REASON,
    254: UNSUPPORTED_REASON,
    257: DEVIATE_REASON,
    259: UNSUPPORTED_REASON,
    260: UNSUPPORTED_REASON,
    263: UNSUPPORTED_REASON,
    264: UNSUPPORTED_REASON,
    266: DEVIATE_REASON,
    270: UNSUPPORTED_REASON,
    271: UNSUPPORTED_REASON,
    272: UNSUPPORTED_REASON,
    273: UNSUPPORTED_REASON,
    274: UNSUPPORTED_REASON,
    278: DEVIATE_REASON,
    280: DEVIATE_REASON,
    281: DEVIATE_REASON,
    283: DEVIATE_REASON,
    284: DEVIATE_REASON,
    286: UNSUPPORTED_REASON,
    287: UNSUPPORTED_REASON,
    288: UNSUPPORTED_REASON,
    289: DEVIATE_REASON,
    290: UNSUPPORTED_REASON,
    292: UNSUPPORTED_REASON,
    293: UNSUPPORTED_REASON,
    296: DEVIATE_REASON,
    300: DEVIATE_REASON,
    304: DEVIATE_REASON,
    309: UNSUPPORTED_REASON,
    312: DEVIATE_REASON,
    313: DEVIATE_REASON,
    315: DEVIATE_REASON,
    317: DEVIATE_REASON,
    318: TEST_WRONG_REASON,
    324: TEST_WRONG_REASON,
    342: DEVIATE_REASON,
    344: UNSUPPORTED_REASON,
    346: UNSUPPORTED_REASON,
    347: DEVIATE_REASON,
    352: DEVIATE_REASON,
    367: DEVIATE_REASON,
    368: DEVIATE_REASON,
    372: DEVIATE_REASON,
    379: DEVIATE_REASON,
    388: DEVIATE_REASON,
    391: DEVIATE_REASON,
    392: DEVIATE_REASON,
    393: DEVIATE_REASON,
    394: DEVIATE_REASON,
    398: DEVIATE_REASON,
    405: DEVIATE_REASON,
    406: DEVIATE_REASON,
    407: DEVIATE_REASON,
    409: DEVIATE_REASON,
    410: DEVIATE_REASON,
    411: DEVIATE_REASON,
    412: DEVIATE_REASON,
    414: DEVIATE_REASON,
    415: DEVIATE_REASON,
    417: DEVIATE_REASON,
    418: DEVIATE_REASON,
    424: DEVIATE_REASON,
    428: DEVIATE_REASON,
    431: DEVIATE_REASON,
    432: DEVIATE_REASON,
    441: DEVIATE_REASON,
    443: DEVIATE_REASON,
    444: DEVIATE_REASON,
    453: DEVIATE_REASON,
    455: DEVIATE_REASON,
    456: DEVIATE_REASON,
    466: DEVIATE_REASON,
    467: DEVIATE_REASON,
    470: DEVIATE_REASON,
    471: DEVIATE_REASON,
    472: DEVIATE_REASON,
    473: DEVIATE_REASON,
    474: UNSUPPORTED_REASON,
    475: UNSUPPORTED_REASON,
    476: UNSUPPORTED_REASON,
    477: UNSUPPORTED_REASON,
    478: DEVIATE_REASON,
    479: UNSUPPORTED_REASON,
    480: UNSUPPORTED_REASON,
    487: DEVIATE_REASON,
    489: DEVIATE_REASON,
    490: DEVIATE_REASON,
    491: UNSUPPORTED_REASON,
    492: UNSUPPORTED_REASON,
    493: UNSUPPORTED_REASON,
    496: DEVIATE_REASON,
    498: UNSUPPORTED_REASON,
    507: DEVIATE_REASON,
    509: DEVIATE_REASON,
    510: DEVIATE_REASON,
    512: DEVIATE_REASON,
    517: DEVIATE_REASON,
    518: DEVIATE_REASON,
    520: DEVIATE_REASON,
    523: UNSUPPORTED_REASON,
    524: DEVIATE_REASON,
    525: UNSUPPORTED_REASON,
    526: TEST_WRONG_REASON,
    527: TEST_WRONG_REASON,
    528: TEST_WRONG_REASON,
    529: TEST_WRONG_REASON,
    530: TEST_WRONG_REASON,
    531: TEST_WRONG_REASON,
    532: TEST_WRONG_REASON,
    533: TEST_WRONG_REASON,
    534: TEST_WRONG_REASON,
    535: UNSUPPORTED_REASON,
    536: DEVIATE_REASON,
    537: TEST_WRONG_REASON,
    538: TEST_WRONG_REASON,
    539: TEST_WRONG_REASON,
    540: TEST_WRONG_REASON,
    541: TEST_WRONG_REASON,
    542: TEST_WRONG_REASON,
    543: TEST_WRONG_REASON,
    544: TEST_WRONG_REASON,
    545: DEVIATE_REASON,
    546: DEVIATE_REASON,
    547: DEVIATE_REASON,
    548: DEVIATE_REASON,
    549: DEVIATE_REASON,
    550: DEVIATE_REASON,
    552: DEVIATE_REASON,
    553: DEVIATE_REASON,
    554: DEVIATE_REASON,
    555: DEVIATE_REASON,
    556: DEVIATE_REASON,
    557: DEVIATE_REASON,
    558: DEVIATE_REASON,
    559: DEVIATE_REASON,
    560: TEST_WRONG_REASON,
    561: TEST_WRONG_REASON,
    562: TEST_WRONG_REASON,
    563: DEVIATE_REASON,
    564: TEST_WRONG_REASON,
    565: TEST_WRONG_REASON,
    566: TEST_WRONG_REASON,
    567: TEST_WRONG_REASON,
    568: TEST_WRONG_REASON,
    569: TEST_WRONG_REASON,
    570: TEST_WRONG_REASON,
    572: TEST_WRONG_REASON,
    575: TEST_WRONG_REASON,
    576: TEST_WRONG_REASON,
    581: TEST_WRONG_REASON,
    582: TEST_WRONG_REASON,
    583: TEST_WRONG_REASON,
    584: TEST_WRONG_REASON,
    585: TEST_WRONG_REASON,
    586: TEST_WRONG_REASON,
    587: TEST_WRONG_REASON,
    588: TEST_WRONG_REASON,
    589: TEST_WRONG_REASON,
    590: TEST_WRONG_REASON,
    591: TEST_WRONG_REASON,
    592: TEST_WRONG_REASON,
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
    tokens.extend(link_ref_tokens(tc["markdown"]))

    tokens.sort(key=lambda x: x["start"])

    output = {
        "name": tc["section"].lower()+ " " + str(tc["example"]),
        "markdown": tc["markdown"],
        "tokens": tokens,
    }

    if tc["section"] in NOT_IMPLEMENTED_SECTIONS:
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
link_ref_re = re.compile("^[ ]{0,3}(\[.+\]):.*$")

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

        tokens = [{
            "role": tokenrole,
            "start": start_pos,
            "end": end_pos,
            "text": markdown[start_pos:end_pos],
        }]

        if tokenrole.startswith("List"):
            for child in xmlroot:
                tokens.extend(xml_to_tokens(child, markdown))

        return tokens

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
            tokstart = start + match.span(1)[0]
            tokend = start + match.span(1)[1]
            tokens.append({
                "role": "Link",
                "start": tokstart,
                "end": tokend,
                "text": markdown[tokstart:tokend],
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
