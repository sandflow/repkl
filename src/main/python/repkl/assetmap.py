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

from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import List, Optional, IO
from dataclasses import dataclass, field

from repkl.utils import get_ns, make_text_element, make_uuid, make_iso_ts, pretty_print

AM2007_NS = "http://www.smpte-ra.org/schemas/429-9/2007/AM"

@dataclass(frozen=True)
class Asset:
  id: str
  path: str
  is_pkl: bool

  @staticmethod
  def from_element(asset_elem: ET.Element) -> Asset:
    ns = { "am": get_ns(asset_elem)}

    is_pkl_element = asset_elem.find("am:PackingList", ns)

    return Asset(
      asset_elem.find("am:Id", ns).text.lower(),
      asset_elem.find(".//am:Path", ns).text,
      is_pkl_element is not None and is_pkl_element.text.lower() in ("true", "1")
      )

  def to_element(self) -> ET.Element:
    asset_elem = ET.Element(f"{{{AM2007_NS}}}Asset")

    asset_elem.append(make_text_element(f"{{{AM2007_NS}}}Id", self.id))

    if self.is_pkl:
      asset_elem.append(make_text_element(f"{{{AM2007_NS}}}PackingList", "true"))

    path_elem = make_text_element(f"{{{AM2007_NS}}}Path", self.path)

    chunk_elem = ET.Element(f"{{{AM2007_NS}}}Chunk")
    chunk_elem.append(path_elem)

    chunklist_elem = ET.Element(f"{{{AM2007_NS}}}ChunkList")
    chunklist_elem.append(chunk_elem)

    asset_elem.append(chunklist_elem)

    return asset_elem

@dataclass
class AssetMap:
  creator: str = "n/a"
  issuer: str = "n/a"
  id: str = field(default_factory=make_uuid)
  issue_date: str = field(default_factory=make_iso_ts)
  assets: List[Asset] = field(default_factory=list)
  creator_lang: Optional[str] = None
  issuer_lang: Optional[str] = None
  annotation: Optional[str] = None
  annotation_lang: Optional[str] = None

  @staticmethod
  def from_element(am_elem: ET.Element) -> AssetMap:
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

  def to_element(self) -> ET.ElementTree:

    am_element = ET.Element(f"{{{AM2007_NS}}}AssetMap")

    am_element.append(make_text_element(f"{{{AM2007_NS}}}Id", self.id))
    if self.annotation is not None:
      am_element.append(make_text_element(f"{{{AM2007_NS}}}AnnotationText", self.annotation, self.annotation_lang))
    am_element.append(make_text_element(f"{{{AM2007_NS}}}Creator", self.creator, self.creator_lang))
    am_element.append(make_text_element(f"{{{AM2007_NS}}}VolumeCount", "1"))
    am_element.append(make_text_element(f"{{{AM2007_NS}}}IssueDate",self.issue_date))
    am_element.append(make_text_element(f"{{{AM2007_NS}}}Issuer", self.issuer, self.issuer_lang))

    asset_list = ET.Element(f"{{{AM2007_NS}}}AssetList")

    for asset in self.assets:
      asset_list.append(asset.to_element())

    am_element.append(asset_list)

    return ET.ElementTree(am_element)

  def write(self, fp: IO):
    doc = self.to_element()
    pretty_print(doc)
    doc.write(fp, encoding="utf-8")