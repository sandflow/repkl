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

import pathlib
import typing
import enum
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import logging

import repkl.assetmap
import repkl.pkl
import repkl.cpl


@dataclass(frozen=True)
class Instruction:

  class Operation(enum.Enum):
    COPY = 1
    MOVE = 2

  src_cpl_path: pathlib.Path
  operation: Operation
  dest_dir_path: pathlib.Path

ASSETMAP_FILENAME = "ASSETMAP.xml"

def process(ov: Instruction, sups: typing.Optional[typing.List[Instruction]], mapped_file_set_paths: typing.Optional[typing.List[pathlib.Path]]):

  # collect all mapped file sets

  if mapped_file_set_paths is not None and len(mapped_file_set_paths) > 0:
    # use the provided mapped file sets
    am_dir_paths = {e.resolve() for e in mapped_file_set_paths}

  else:
    # infer mapped file sets from CPL paths
    logging.info("Inferring mapped file sets from input CPL paths")

    am_dir_paths = set()
    am_dir_paths.add(ov.src_cpl_path.parent.resolve())
    if sups is not None:
      for sup in sups:
        am_dir_paths.add(sup.src_cpl_path.parent.resolve())

  # collect all assets

  path_resolver: typing.Mapping[str, pathlib.Path] = {}
  asset_resolver: typing.Mapping[str, repkl.pkl.Asset] = {}

  for p in am_dir_paths:
    am_doc = ET.parse(p.joinpath(ASSETMAP_FILENAME))
    am_assets = repkl.assetmap.collect_assets(am_doc.getroot())

    # TODO: detect duplicates
    path_resolver.update({a.id : p.joinpath(a.path) for a in am_assets.values()})

    for pkl_entry in filter(lambda x: x.is_pkl, am_assets.values()):
      pkl_doc = ET.parse(p.joinpath(pkl_entry.path))
      pkl_assets = repkl.pkl.collect_assets(pkl_doc.getroot())

      # TODO: detect duplicates
      asset_resolver.update(pkl_assets)


  # process OV

  ov_doc = ET.parse(ov.src_cpl_path)
  ov_resource_ids = set()
  ov_resource_ids.add(repkl.cpl.get_id(ov_doc.getroot()))
  ov_resource_ids.update(repkl.cpl.collect_resource_ids(ov_doc.getroot()))

  print([path_resolver[e] for e in ov_resource_ids])

if __name__ == "__main__":
  process(
    Instruction(
      pathlib.Path("src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml"),
      Instruction.Operation.COPY,
      "build/imp1"
      ),
      None,
      None
  )