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
import uuid

import repkl.assetmap
import repkl.pkl
import repkl.cpl

CREATOR_STRING = "repkl"

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("repkl")

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
    LOGGER.info("Inferring mapped file sets from input CPL paths")

    am_dir_paths = set()
    am_dir_paths.add(ov.src_cpl_path.parent.resolve())
    if sups is not None:
      for sup in sups:
        am_dir_paths.add(sup.src_cpl_path.parent.resolve())

  # collect all assets

  path_resolver: typing.Mapping[str, pathlib.Path] = {}
  pkl_asset_resolver: typing.Mapping[str, repkl.pkl.Asset] = {}
  am_asset_resolver: typing.Mapping[str, repkl.assetmap.Asset] = {}

  for p in am_dir_paths:
    am_doc = ET.parse(p.joinpath(ASSETMAP_FILENAME))
    am = repkl.assetmap.AssetMap.from_element(am_doc.getroot())

    # TODO: detect duplicates
    am_asset_resolver.update({a.id: a for a in am.assets})
    path_resolver.update({a.id : p.joinpath(a.path) for a in am.assets})

    for pkl_entry in filter(lambda x: x.is_pkl, am.assets):
      pkl_doc = ET.parse(p.joinpath(pkl_entry.path))
      pkl = repkl.pkl.PackingList.from_element(pkl_doc.getroot())

      # TODO: detect duplicates
      pkl_asset_resolver.update({a.id: a for a in pkl.assets})


  # collect assets for the OV

  ov_cpl = repkl.cpl.Composition.from_element(ET.parse(ov.src_cpl_path).getroot())
  ov_resource_ids = set()
  ov_resource_ids.add(ov_cpl.id)
  ov_resource_ids.update(ov_cpl.resource_ids)

  # create PKL for the OV

  ov_pkl = repkl.pkl.PackingList(
    assets=[pkl_asset_resolver[i] for i in ov_resource_ids],
    creator=CREATOR_STRING,
    issuer=ov_cpl.issuer,
    issuer_lang=ov_cpl.issuer_lang,
    annotation=ov_cpl.content_title,
    annotation_lang=ov_cpl.content_title_lang
  )

  pkl_fn = f"PKL_{str(uuid.UUID(ov_pkl.id))}.xml"

  ov_pkl.write(ov.dest_dir_path.joinpath(pkl_fn))

  LOGGER.info("OV PackingList written (%s)", pkl_fn)

  # build Asset Map for the OV

  ov_am = repkl.assetmap.AssetMap(
    assets=[am_asset_resolver[i] for i in ov_resource_ids],
    creator=CREATOR_STRING,
    issuer=ov_cpl.issuer,
    issuer_lang=ov_cpl.issuer_lang,
    annotation=ov_cpl.content_title,
    annotation_lang=ov_cpl.content_title_lang
  )

  ov_am.assets.append(repkl.assetmap.Asset(
    id=ov_pkl.id,
    path=pkl_fn,
    is_pkl=True
  ))

  ov_am.write(ov.dest_dir_path.joinpath("ASSETMAP.xml"))

  LOGGER.info("OV AssetMap written")

  # process assets

  for i in ov_resource_ids:
    am_asset = am_asset_resolver[i]

    src_path = ov.src_cpl_path.joinpath(am_asset.path)
    dst_path = ov.dest_dir_path.joinpath(am_asset.path)

    if ov.operation == Instruction.Operation.COPY:
      LOGGER.info("Copying %s to %s", am_asset.path, dst_path)
    else:
      LOGGER.info("Moving %s to %s", am_asset.path, dst_path)

if __name__ == "__main__":

  ov_path = pathlib.Path("build/imp1")
  ov_path.mkdir(parents=True, exist_ok=True)

  process(
    Instruction(
      pathlib.Path("src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml"),
      Instruction.Operation.COPY,
      ov_path
      ),
      None,
      None
  )
