import json
import os
import sys
import wget

from extract_hit_check_order import extract_hit_check_order
from extract_unit_img import extract_unit_img
from extract_picture_img import extract_picture_img

VER = "4009"
DOWNLOAD_PREFIX = "https://thcdn.gggamedownload.com/source/Assetbundle_Android_v" + VER + "/"
SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"

# control vars
do_extract_hit_check_order = False
do_extract_unit = True
do_extract_picture = False

if not os.path.exists(SOURCE_DIR):
	os.makedirs(SOURCE_DIR)
if not os.path.exists(OUTPUT_DIR):
	os.makedirs(OUTPUT_DIR)

manifest_file_path = os.path.join(SOURCE_DIR, "manifest_assetbundle_v{ver}.json".format(ver = VER))
if not os.path.exists(manifest_file_path):
	print("downloading manifest:")
	url = DOWNLOAD_PREFIX + "manifest.json"
	try:
	    output = wget.download(url, manifest_file_path)
	except:
		print("download manifest failed, exiting")
		sys.exit(1)


manifest_file = open(manifest_file_path)
data = json.load(manifest_file)
asset_infos = data['AssetInfos']


if do_extract_hit_check_order:
	extract_hit_check_order(DOWNLOAD_PREFIX, asset_infos)
if do_extract_unit:
	extract_unit_img(DOWNLOAD_PREFIX, asset_infos)
if do_extract_picture:
	extract_picture_img(DOWNLOAD_PREFIX, asset_infos)