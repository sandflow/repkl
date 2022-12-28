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
import xml.etree.ElementTree as ET

import repkl.assetmap

class AssetMapTest(unittest.TestCase):

  def test_collect_assets(self):

    tree = ET.parse("src/test/resources/imp/countdown-audio/ASSETMAP.xml")

    assets = repkl.assetmap.collect_assets(tree.getroot())

    self.assertEqual(len(assets), 4)

    pkl = assets["urn:uuid:e8aa8652-f9de-4d8d-b337-53123066605e"]
    self.assertEqual(pkl.id, "urn:uuid:e8aa8652-f9de-4d8d-b337-53123066605e")
    self.assertTrue(pkl.is_pkl)
    self.assertEqual(pkl.path, "PKL_e8aa8652-f9de-4d8d-b337-53123066605e.xml")

    wav = assets["urn:uuid:d01bc6be-ae2f-436b-9705-c402e1d92212"]
    self.assertEqual(wav.id, "urn:uuid:d01bc6be-ae2f-436b-9705-c402e1d92212")
    self.assertFalse(wav.is_pkl)
    self.assertEqual(wav.path, "WAV_d01bc6be-ae2f-436b-9705-c402e1d92212.mxf")
