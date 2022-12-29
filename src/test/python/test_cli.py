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

import unittest
import shutil
import pathlib

import repkl.cli

class CLITest(unittest.TestCase):

  def _prep_dir(self, path: pathlib.Path):
    if path.exists():
      shutil.rmtree(path)

    path.mkdir(parents=True)

  def test_ov(self):

    TEST_DIR = pathlib.Path("build/ov-imp")

    self._prep_dir(TEST_DIR)

    repkl.cli.main([
      "--action",
      "copy",
      "src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml",
      str(TEST_DIR)
    ])

  def test_vf(self):

    TEST_DIR = pathlib.Path("build/vf-imp")

    self._prep_dir(TEST_DIR)

    repkl.cli.main([
      "--action",
      "copy",
      "--ov",
      "src/test/resources/imp/countdown/CPL_bb2ce11c-1bb6-4781-8e69-967183d02b9b.xml",
      "src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml",
      str(TEST_DIR)
    ])

  def test_dryrun(self):

    TEST_DIR = pathlib.Path("build/vf-imp")

    self._prep_dir(TEST_DIR)

    repkl.cli.main([
      "--action",
      "dryrun",
      "--ov",
      "src/test/resources/imp/countdown/CPL_bb2ce11c-1bb6-4781-8e69-967183d02b9b.xml",
      "src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml",
      str(TEST_DIR)
    ])

  def test_symlinks(self):

    TEST_DIR = pathlib.Path("build/symlink-imp")

    self._prep_dir(TEST_DIR)

    try:
      test_src = TEST_DIR.joinpath("src.txt")
      test_dest = TEST_DIR.joinpath("dst.txt")
      test_dest.symlink_to(test_src)
    except OSError as e:
      raise unittest.SkipTest("Cannot create symlinks") from e

    self._prep_dir(TEST_DIR)

    repkl.cli.main([
      "--action",
      "symlink",
      "src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml",
      str(TEST_DIR)
    ])

  def test_move(self):

    SRC_DIR = pathlib.Path("build/move-src-imp")

    self._prep_dir(SRC_DIR)

    repkl.cli.main([
      "--action",
      "copy",
      "src/test/resources/imp/countdown-audio/CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml",
      str(SRC_DIR)
    ])

    TEST_DIR = pathlib.Path("build/move-imp")

    self._prep_dir(TEST_DIR)

    repkl.cli.main([
      "--action",
      "move",
      str(SRC_DIR.joinpath("CPL_0b976350-bea1-4e62-ba07-f32b28aaaf30.xml")),
      str(TEST_DIR)
    ])
