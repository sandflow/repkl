#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2022, Sandflow Consulting LLC
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import xml.etree.ElementTree as ET
from typing import Optional, Mapping
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Asset:
  id: str
  annotation_text: Optional[str]
  annotation_text_lang: Optional[str]
  hash: str
  size: int
  type: str
  original_filename: Optional[str]
  original_filename_lang: Optional[str]
  hash_algorithm: str

def make_asset(asset_element: ET.Element, ns: dict) -> Asset:

  orig_fn_element = asset_element.find("pkl:OriginalFileName", ns)
  if orig_fn_element is not None:
    original_filename = orig_fn_element.text
    original_filename_lang = orig_fn_element.attrib.get("language")
  else:
    original_filename = None
    original_filename_lang = None

  annot_element = asset_element.find("pkl:AnnotationText", ns)
  if annot_element is not None:
    annotation_text = annot_element.text
    annotation_text_lang = annot_element.attrib.get("language")
  else:
    annotation_text = None
    annotation_text_lang = None

  algo_element = asset_element.find("pkl:HashAlgorithm", ns)
  hash_algorithm = algo_element.attrib["Algorithm"] if algo_element is not None else "http://www.w3.org/2000/09/xmldsig#sha1"

  return Asset(
    asset_element.find("pkl:Id", ns).text.lower(),
    annotation_text,
    annotation_text_lang,
    asset_element.find("pkl:Hash", ns).text,
    int(asset_element.find("pkl:Size", ns).text),
    asset_element.find("pkl:Type", ns).text,
    original_filename,
    original_filename_lang,
    hash_algorithm
    )

NS_RE = re.compile(r"{([^}]+)")

def collect_assets(pkl: ET.Element) -> Mapping[str, Asset]:

  ns = { "pkl": NS_RE.match(pkl.tag).group(1)}

  assets = [make_asset(e, ns) for e in pkl.findall(".//pkl:Asset", ns)]

  return {e.id: e for e in assets}
