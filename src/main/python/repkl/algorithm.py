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
import xml.etree.ElementTree as ET
import logging
import uuid
import shutil

import repkl.assetmap
import repkl.pkl
import repkl.cpl

CREATOR_STRING = "repkl"

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("repkl")

class Action(enum.Enum):
  COPY = "copy"           # copy assets
  MOVE = "move"           # move assets
  DRYRUN = "dryrun"       # do not write anything
  SKIP = "skip"           # skip writing assets and only write the new PackingList and AssetMap
  SYMLINK = "symlink"     # create symlinks to assets

ASSETMAP_FILENAME = "ASSETMAP.xml"

def process(target_cpl_path: pathlib.Path,
            dest_dir_path: pathlib.Path,
            action: Action,
            base_cpl_path: typing.Optional[pathlib.Path] = None,
            mapped_file_set_paths: typing.Optional[typing.List[pathlib.Path]] = None
  ):

  # collect all mapped file sets

  if mapped_file_set_paths is not None and len(mapped_file_set_paths) > 0:
    # use the provided mapped file sets
    am_dir_paths = {e.resolve() for e in mapped_file_set_paths}

  else:
    # infer mapped file sets from CPL paths
    LOGGER.info("Inferring mapped file sets from input CPL paths")

    am_dir_paths = set()
    am_dir_paths.add(target_cpl_path.parent.resolve())
    if base_cpl_path is not None:
      am_dir_paths.add(base_cpl_path.parent.resolve())

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

  # collect assets for the Target

  target_cpl = repkl.cpl.Composition.from_element(ET.parse(target_cpl_path).getroot())
  target_asset_ids = set()
  target_asset_ids.add(target_cpl.id)
  target_asset_ids.update(target_cpl.resource_ids)

  # subtract assets already present in the base

  if base_cpl_path is not None:
    base_cpl = repkl.cpl.Composition.from_element(ET.parse(base_cpl_path).getroot())
    target_asset_ids = target_asset_ids.difference(base_cpl.resource_ids)


  # create PKL for the Target

  target_pkl = repkl.pkl.PackingList(
    assets=[pkl_asset_resolver[i] for i in target_asset_ids],
    creator=CREATOR_STRING,
    issuer=target_cpl.issuer,
    issuer_lang=target_cpl.issuer_lang,
    annotation=target_cpl.content_title,
    annotation_lang=target_cpl.content_title_lang
  )

  pkl_fn = f"PKL_{str(uuid.UUID(target_pkl.id))}.xml"

  if action != Action.DRYRUN:
    target_pkl.write(dest_dir_path.joinpath(pkl_fn))

  LOGGER.info("Target PackingList written (%s)", pkl_fn)

  # build Asset Map for the Target

  target_am = repkl.assetmap.AssetMap(
    assets=[am_asset_resolver[i] for i in target_asset_ids],
    creator=CREATOR_STRING,
    issuer=target_cpl.issuer,
    issuer_lang=target_cpl.issuer_lang,
    annotation=target_cpl.content_title,
    annotation_lang=target_cpl.content_title_lang
  )

  target_am.assets.append(repkl.assetmap.Asset(
    id=target_pkl.id,
    path=pkl_fn,
    is_pkl=True
  ))

  if action != Action.DRYRUN:
    target_am.write(dest_dir_path.joinpath("ASSETMAP.xml"))

  LOGGER.info("Target AssetMap written")

  # process assets

  for i in target_asset_ids:

    src_path = path_resolver[i]
    am_asset = am_asset_resolver[i]
    dst_path = dest_dir_path.joinpath(am_asset.path)

    if action == Action.COPY:
      LOGGER.info("Copying %s to %s", am_asset.path, dst_path)
      shutil.copy(src_path, dst_path)
    elif action == Action.MOVE:
      LOGGER.info("Moving %s to %s", am_asset.path, dst_path)
      shutil.move(src_path, dst_path)
    elif action == Action.SYMLINK:
      LOGGER.info("Symlink from %s to %s", am_asset.path, dst_path)
      dst_path.symlink_to(src_path)
    else:
      LOGGER.info("Skipping copying %s to %s", am_asset.path, dst_path)

if __name__ == "__main__":

  target_path = pathlib.Path("build/imp1")
  target_path.mkdir(parents=True, exist_ok=True)

  process(
      target_cpl_path=pathlib.Path("src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml"),
      base_cpl_path=pathlib.Path("src/test/resources/imp/countdown/CPL_bb2ce11c-1bb6-4781-8e69-967183d02b9b.xml"),
      dest_dir_path=target_path,
      action=Action.COPY
  )
