"""Markdown transformations shared by snapshot generation and its checks."""
import re

FENCES = re.compile(r'(^```[^\n]*\n.*?^```[^\n]*$)', re.M | re.S)


def map_prose(source, transform):
    parts = FENCES.split(source)
    return ''.join(part if index % 2 else transform(part)
                   for index, part in enumerate(parts))
