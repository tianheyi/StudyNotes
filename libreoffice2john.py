#!/usr/bin/env python

# The libreoffice2john.py utility processes OpenOffice / LibreOffice files into
# a format suitable for use with JtR.
#
# This utility was previously named odf2john.py.

# Output Format:
#
#   filename:$odf*cipher type*checksum type*iterations*key-size*checksum*...
#     ...iv length*iv*salt length*salt*unused*content.xml data
#
# This software is Copyright (c) 2012, Dhiru Kholia <dhiru at openwall.com> and
# it is hereby released to the general public under the following terms:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted.

from xml.etree.ElementTree import ElementTree
import zipfile
import sys
import base64
import binascii
import os


def process_file(filename):
    try:
        zf = zipfile.ZipFile(filename)
    except zipfile.BadZipfile:
        sys.stderr.write("%s is not an OpenOffice file!\n" % filename)
        return 2
    try:
        mf = zf.open("META-INF/manifest.xml")
    except KeyError:
        sys.stderr.write("%s is not an OpenOffice file!\n" % filename)
        return 3
    tree = ElementTree()
    tree.parse(mf)
    r = tree.getroot()

    # getiterator() is deprecated but 2.6 does not have iter()
    try:
        elements = list(r.iter())
    except:
        elements = list(r.getiterator())

    is_encrypted = False
    key_size = 16
    for i in range(0, len(elements)):
        element = elements[i]
        if element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}full-path") == "content.xml":
            for j in range(i + 1, i + 1 + 3):

                element = elements[j]
                #print element.items()
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}checksum")
                if data:
                    is_encrypted = True
                    checksum = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}checksum-type")
                if data:
                    checksum_type = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}initialisation-vector")
                if data:
                    iv = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}salt")
                if data:
                    salt = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}algorithm-name")
                if data:
                    algorithm_name = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}iteration-count")
                if data:
                    iteration_count = data
                data = element.get("{urn:oasis:names:tc:opendocument:xmlns:manifest:1.0}key-size")
                if data:
                    key_size = data

    if not is_encrypted:
        sys.stderr.write("%s is not an encrypted OpenOffice file!\n" % filename)
        return 4

    checksum = base64.b64decode(checksum)
    checksum = binascii.hexlify(checksum).decode("ascii")
    iv = binascii.hexlify(base64.b64decode(iv)).decode("ascii")
    salt = binascii.hexlify(base64.b64decode(salt)).decode("ascii")

    try:
        content = zf.open("content.xml").read(1024)
    except KeyError:
        sys.stderr.write("%s is not an encrypted OpenOffice file, " \
                "content.xml missing!\n" % filename)
        return 5

    if algorithm_name.find("Blowfish CFB") > -1:
        algorithm_type = 0
    elif algorithm_name.find("aes256-cbc") > -1:
        algorithm_type = 1
    else:
        sys.stderr.write("%s uses un-supported encryption!\n" % filename)
        return 6

    if checksum_type.upper().find("SHA1") > -1:
        checksum_type = 0
    elif checksum_type.upper().find("SHA256") > -1:
        checksum_type = 1
    else:
        sys.stderr.write("%s uses un-supported checksum algorithm!\n" % \
                filename)
        return 7

    meta_data_available = True
    gecos = ""
    try:
        meta = zf.open("meta.xml")
        meta_tree = ElementTree()
        meta_tree.parse(meta)
        meta_r = meta_tree.getroot()
        for office_meta in meta_r:
            for child in office_meta:
                if "subject" in child.tag:
                    gecos += child.text
                elif "keyword" in child.tag:
                    gecos += child.text
                elif "title" in child.tag:
                    gecos += child.text
                elif "description" in child.tag:
                    gecos += child.text
        gecos = gecos.replace("\n","").replace("\r","").replace(":","")
    except:
        meta_data_available = False

    if meta_data_available:
        sys.stdout.write("%s:$odf$*%s*%s*%s*%s*%s*%d*%s*%d*%s*%d*%s:::%s::%s\n" % \
                (os.path.basename(filename), algorithm_type, checksum_type,
                iteration_count, key_size, checksum, len(iv) / 2, iv,
                len(salt) / 2, salt, 0, binascii.hexlify(content).decode("ascii"),
                gecos, filename))
    else:
        sys.stdout.write("%s:$odf$*%s*%s*%s*%s*%s*%d*%s*%d*%s*%d*%s:::::%s\n" % \
                (os.path.basename(filename), algorithm_type, checksum_type,
                iteration_count, key_size, checksum, len(iv) / 2, iv,
                len(salt) / 2, salt, 0, binascii.hexlify(content).decode("ascii"),
                filename))

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     sys.stderr.write("Usage: %s <OpenOffice / LibreOffice files>\n" % sys.argv[0])
    #     sys.exit(-1)
    #
    # for k in range(1, len(sys.argv)):
    #     process_file(sys.argv[k])
    a = "4b22b15a8ce48c9eaec4cbb29fc050c42f96e3b5d91d049e31ba2f9e9b1f1b488c8901f8d28796456ad9e436accfd7e547cf834e4c8aada307a42b2d5e485456431ff4d47693d6360ede2d62be7711cb070d714fc6fa31fa370d4d488cc3a427d83e0bc8bf9bc0854a39ecdad5563d9944da1718be1c3c5dd48bb1232af8871b34e8df5c71e0d92d07da43d283f82ebf69215bbcfa3ed7d9554bdb1ce23b4a33667bf4196b595261299f50bdc18041400b5a876d83196b54572ea5bc5d19542f676d562792b0fae15ffad0d37b0bc717925129f1eead6bbe6ce230d96bbcacd5caa7785c10894172fb2f31c77a4291ae269ad406e23392327bfa4e85498126d025506981f2a68e00dc6439737e94c3a0197bbc533fac8055e1cc212e6f6af1466f8199dc55df3c080741f9f311d78cb9e7b384f76110f75a3448b7f9b1ef3ccaf006e2985da412d4f2700731bac0eead4f9672060a32f654cd9b63474069075259456c13422a1975d6aef400f596481815fb2591fd36e32213ca7a77093f910d277247512fff80f49c89630adc191cb236dab1fcb9f3b10d132e908485c44275fe2c2b83ebb93eb9ffd27239c20c8851097d2a9fdd0d65c71cf48274b8837b06cd6f350e11dfa283cac31dea129847497b2a7b0a32dd08d6ca57c0e405ac4aa10322276a5375227beacfec912b1a93194f1808a036f8afd2ba394aac198b0f0e9a22da81c24e75be6f4028eaeb94949d5bf952637a7ec1efc594bfcdebf4c9d967cf7cb6963971b6986cf402681ecdaf5fd440116abb24ef58235b62264d47b8b41d19247666db4a16e64795f3c36b87df8f5f1f13afbdbd6e0c2f762d33726d52c3a6d68f5321ff381d6a61b79eca7ccff5c35eaf91abf7f5a1bc3c0b9fadd23f5150a22c15f4276acedd8af3d23ee26533635626a043fa02c517009e5a2016bddb5b8b59aff1445a9aadc8c908dc80ea342dbde2d807c95f58baf4d8d9eef8a949f94beb1d6c1abb40255336b42f64efc2e237579c8b2afedb5a33a33332afc56e503b68bdd99ed7353b57ccaea0fb21980b262f9b3137da214d229e3dddf379b7a91c47984c5006799d84b2a233f2d63b55f96e6b9fd524e1068acef4ca260d954a7dc0e2937539830ac23143b50cf53b9fda20e000e123a97639b640d4485c678857e898de25b18213f592b4e79a8a5150cd59ec760ea0acc11abf61115d4166834a608c663e2a392fc07616456860dd9386734e6dc8d8172dcf0a099439b72c2e6fcffa8c221aca1b314ac489880f2f11d48b62df75087bb84999495359bbe57863522ef4c784beb86ac3a9fb4d5b0ceaee8f3570231d7fa6fd7a485dd9fc14a99a864002f2acb416ef8ebf6da7a2cd62b1b9456f68"
    print(len(a)/2)
    print(len(a.split("*")))