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

import argparse
import pathlib

import repkl.algorithm

def main(argv=None):
  parser = argparse.ArgumentParser(description="Repackages an IMF CPL into a new Mapped File Set.")
  parser.add_argument('target', help="Path of the target CPL that will be repackaged.")
  parser.add_argument('dest', help="Path of the directory where the new Mapped File Set is created")
  parser.add_argument('--delivery', action='append', type=str,
    help="""Path to an Mapped File Set where the assets of the target CPL are found.
            If omitted, the target and OV CPLs are assumed to be at the root of a mapped file set.""")
  parser.add_argument('--ov', help="Path to an OV CPL. If omitted, the target CPL is an OV CPL.")
  parser.add_argument('--action', choices=[e.value for e in repkl.algorithm.Action],
    default=repkl.algorithm.Action.COPY.value,
    help="Indicates whether assets will be copied or moved to the new Mapped File Set.")

  args = parser.parse_args(argv)

  action = repkl.algorithm.Action(args.action)

  target_cpl_path = pathlib.Path(args.target)
  if not target_cpl_path.is_file():
    raise ValueError("Target path is not to a file.")

  dest_path = pathlib.Path(args.dest)
  if action is not repkl.algorithm.Action.DRYRUN:
    if not dest_path.is_dir():
      raise ValueError("Destination path is not to a directory.")
    if len(list(dest_path.iterdir())) > 0:
      raise ValueError("Destination directory is not empty.")

  if args.delivery is not None:
    delivery_paths = [pathlib.Path(e) for e in args.delivery]
    if not all(e.is_dir() for e in delivery_paths):
      raise ValueError("Not all deliveries point to a directory.")
  else:
    delivery_paths = None

  if args.ov is not None:
    ov_path =  pathlib.Path(args.ov)
    if not ov_path.is_file():
      raise ValueError("OV path is not to a file.")
  else:
    ov_path = None

  repkl.algorithm.process(
    target_cpl_path=target_cpl_path,
    dest_dir_path=dest_path,
    mapped_file_set_paths=delivery_paths,
    base_cpl_path=ov_path,
    action=repkl.algorithm.Action(args.action)
  )

if __name__ == "__main__":
  import sys
  main(sys.argv[1:])
