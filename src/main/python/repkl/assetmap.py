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
from typing import List, Optional
from dataclasses import dataclass, field

from repkl.utils import get_ns

@dataclass(frozen=True)
class Asset:
  id: str
  path: str
  is_pkl: bool

  @staticmethod
  def from_element(asset_elem: ET.Element):
    ns = { "am": get_ns(asset_elem)}

    is_pkl_element = asset_elem.find("am:PackingList", ns)

    return Asset(
      asset_elem.find("am:Id", ns).text.lower(),
      asset_elem.find(".//am:Path", ns).text,
      is_pkl_element is not None and is_pkl_element.text.lower() in ("true", "1")
      )


@dataclass
class AssetMap:
  creator: str
  issuer: str
  id: str
  issue_date: str
  assets: List[Asset] = field(default_factory=list)
  creator_lang: Optional[str] = None
  issuer_lang: Optional[str] = None
  annotation: Optional[str] = None
  annotation_lang: Optional[str] = None

  @staticmethod
  def from_element(am_elem: ET.Element):
    ns = { "am": get_ns(am_elem)}

    am = AssetMap(
      creator=am_elem.find("am:Creator", ns).text,
      creator_lang=am_elem.find("am:Creator", ns).attrib.get("language"),
      issuer=am_elem.find("am:Issuer", ns).text,
      issuer_lang=am_elem.find("am:Issuer", ns).attrib.get("language"),
      id=am_elem.find("am:Id", ns).text,
      issue_date=am_elem.find("am:IssueDate", ns).text
    )

    annotation_elem = am_elem.find("am:AnnotationText", ns)
    if annotation_elem is not None:
      am.annotation = annotation_elem.text
      am.annotation_lang = annotation_elem.attrib.get("language")

    am.assets = [Asset.from_element(e) for e in am_elem.findall(".//am:Asset", ns)]

    return am
