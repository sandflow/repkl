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
from typing import AbstractSet, Optional
from dataclasses import dataclass

from repkl.utils import get_ns

@dataclass(frozen=True)
class Composition:
  resource_ids: AbstractSet[str]
  id: str
  creator: Optional[str] = None
  issuer: Optional[str] = None
  creator_lang: Optional[str] = None
  issuer_lang: Optional[str] = None
  annotation: Optional[str] = None
  annotation_lang: Optional[str] = None
  content_title: Optional[str] = None
  content_title_lang: Optional[str] = None

  @staticmethod
  def from_element(cpl_elem: ET.Element) -> Composition:
    ns = { "cpl": get_ns(cpl_elem)}

    annot_element = cpl_elem.find("cpl:AnnotationText", ns)
    ct_element = cpl_elem.find("cpl:ContentTitle", ns)
    creator_element = cpl_elem.find("cpl:Creator", ns)
    issuer_element = cpl_elem.find("cpl:Issuer", ns)

    return Composition(
      resource_ids={e.text.lower() for e in cpl_elem.findall(".//cpl:Resource/cpl:TrackFileId", ns)},
      id=cpl_elem.find("cpl:Id", ns).text.lower(),
      creator=creator_element.text if creator_element is not None else None,
      creator_lang=creator_element.attrib.get("language") if creator_element is not None else None,
      issuer=issuer_element.text if issuer_element is not None else None,
      issuer_lang=issuer_element.attrib.get("language") if issuer_element is not None else None,
      annotation=annot_element.text if annot_element is not None else None,
      annotation_lang=annot_element.attrib.get("language") if annot_element is not None else None,
      content_title=ct_element.text if ct_element is not None else None,
      content_title_lang=ct_element.attrib.get("language") if ct_element is not None else None
    )
