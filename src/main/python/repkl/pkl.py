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
from typing import Optional, List
from dataclasses import dataclass, field

from repkl.utils import get_ns, make_text_element, make_uuid, make_iso_ts

PKL2016_NS = "http://www.smpte-ra.org/schemas/2067-2/2016/PKL"

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

  @staticmethod
  def from_element(asset_element: ET.Element) -> Asset:
    ns = {"pkl": get_ns(asset_element)}

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
      id=asset_element.find("pkl:Id", ns).text.lower(),
      annotation_text=annotation_text,
      annotation_text_lang=annotation_text_lang,
      hash=asset_element.find("pkl:Hash", ns).text,
      size=int(asset_element.find("pkl:Size", ns).text),
      type=asset_element.find("pkl:Type", ns).text,
      original_filename=original_filename,
      original_filename_lang=original_filename_lang,
      hash_algorithm=hash_algorithm
      )

  def to_element(self) -> ET.Element:
    asset_elem = ET.Element(f"{{{PKL2016_NS}}}Asset")

    asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Id", self.id))
    if self.annotation_text is not None:
      asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Type", self.annotation_text, self.annotation_text_lang))
    asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Hash", self.hash))
    asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Size", str(self.size)))
    asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Type", self.type))
    if self.original_filename is not None:
      asset_elem.append(make_text_element(f"{{{PKL2016_NS}}}Type", self.original_filename, self.original_filename_lang))

    hash_element = ET.Element(f"{{{PKL2016_NS}}}HashAlgorithm")
    hash_element.attrib["Algorithm"] = self.hash_algorithm
    asset_elem.append(hash_element)

    return asset_elem

@dataclass
class PackingList:
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
  def from_element(pkl_element: ET.Element) -> PackingList:
    ns = { "pkl": get_ns(pkl_element)}

    pkl = PackingList(
      creator=pkl_element.find("pkl:Creator", ns).text,
      creator_lang=pkl_element.find("pkl:Creator", ns).attrib.get("language"),
      issuer=pkl_element.find("pkl:Issuer", ns).text,
      issuer_lang=pkl_element.find("pkl:Issuer", ns).attrib.get("language"),
      id=pkl_element.find("pkl:Id", ns).text,
      issue_date=pkl_element.find("pkl:IssueDate", ns).text
    )

    annotation_elem = pkl_element.find("pkl:AnnotationText", ns)
    if annotation_elem is not None:
      pkl.annotation = annotation_elem.text
      pkl.annotation_lang = annotation_elem.attrib.get("language")

    pkl.assets = [Asset.from_element(e) for e in pkl_element.findall(".//pkl:Asset", ns)]

    return pkl

  def to_element(self) -> ET.ElementTree:

    pkl_element = ET.Element(f"{{{PKL2016_NS}}}PackingList")

    pkl_element.append(make_text_element(f"{{{PKL2016_NS}}}Id", self.id))
    pkl_element.append(make_text_element(f"{{{PKL2016_NS}}}IssueDate",self.issue_date))
    pkl_element.append(make_text_element(f"{{{PKL2016_NS}}}Issuer", self.issuer, self.issuer_lang))
    pkl_element.append(make_text_element(f"{{{PKL2016_NS}}}Creator", self.creator, self.creator_lang))

    asset_list = ET.Element(f"{{{PKL2016_NS}}}AssetList")

    for asset in self.assets:
      asset_list.append(asset.to_element())

    pkl_element.append(asset_list)

    return ET.ElementTree(pkl_element)
