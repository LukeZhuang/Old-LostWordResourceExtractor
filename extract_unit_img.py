import os
import re
import wget
import UnityPy
from util import create_output_folder_if_not_exist

SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"

unit_square_pattern = r'^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/square.png$'
unit_costume_pattern = r'^assets/east/units/([0-9]+)/([0-9]+)/thumbnail/costume.png$'
unit_fullbody_pattern = r'^assets/east/units/([0-9]+)/([0-9]+)/g([0-9]+)/g([0-9]+).png$'

item_pattern = r'^([0-9]+)([a-zA-Z]+)$'


def match_asset_pattern(pattern, asset_path, cur_unit, items, item_name):
	g = re.findall(pattern, asset_path.lower())
	if len(g) > 0:
		unit_id = int(g[0][0])
		costume_id = g[0][1]
		assert cur_unit == None or cur_unit == unit_id
		cur_unit = unit_id
		items.append(costume_id + item_name)
		return cur_unit
	return cur_unit


def extract_costume_id_from_items(items):
	assert len(items) == 1
	g = re.findall(item_pattern, items[0])
	assert len(g) == 1 and len(g[0]) == 2
	return g[0][0]


def unit_square_name(unit_id, costume_id):
	return "S" + str(unit_id) + str(costume_id) + ".png"

def unit_costume_name(unit_id, costume_id):
	return "C" + str(unit_id) + str(costume_id) + ".png"

def unit_fullbody_name(unit_id, costume_id):
	return "G" + str(unit_id) + str(costume_id) + ".png"

def extract_unit_img(DOWNLOAD_PREFIX, asset_infos):
	create_output_folder_if_not_exist(SOURCE_DIR, "unit")
	unit_source_dir = os.path.join(SOURCE_DIR, "unit")
	create_output_folder_if_not_exist(OUTPUT_DIR, "unit")
	unit_output_dir = os.path.join(OUTPUT_DIR, "unit")

	create_output_folder_if_not_exist(unit_output_dir, "Square")
	create_output_folder_if_not_exist(unit_output_dir, "Costume")
	create_output_folder_if_not_exist(unit_output_dir, "FullBody")

	create_output_folder_if_not_exist(os.path.join(unit_output_dir, "Square"), "AltCostumes")
	create_output_folder_if_not_exist(os.path.join(unit_output_dir, "Costume"), "AltCostumes")
	create_output_folder_if_not_exist(os.path.join(unit_output_dir, "FullBody"), "AltCostumes")

	# read all unit info
	unit_dict = {}
	for asset_info in asset_infos:
		if "Units" not in str(asset_info):
			continue
		file_name = asset_info["Name"]
		asset_paths = asset_info["AssetPaths"]
		cur_unit = None
		items = []
		for asset_path in asset_paths:
			cur_unit = match_asset_pattern(unit_square_pattern, asset_path, cur_unit, items, "Square")
			cur_unit = match_asset_pattern(unit_costume_pattern, asset_path, cur_unit, items, "Costume")
			cur_unit = match_asset_pattern(unit_fullbody_pattern, asset_path, cur_unit, items, "FullBody")
		
		if cur_unit:
			items.sort()
			unit_dict.setdefault(cur_unit, [])
			unit_dict[cur_unit].append((file_name, items))
	
	sorted_units = sorted(list(unit_dict.items()), key=lambda x:x[0])

	for unit_id, unit_asset_infos in sorted_units:
		print('extracting image for unit', unit_id)
		for file_name, img_files in unit_asset_infos:
			unit_asset_file = os.path.join(unit_source_dir, "unit" + str(unit_id) + "_" + "-".join(img_files))
			
			# download file if needed
			if not os.path.exists(unit_asset_file):
				print("downloading:", unit_id, file_name)
				url = DOWNLOAD_PREFIX + file_name
				output = wget.download(url, unit_asset_file)

			# start extracing
			bundle = UnityPy.load(unit_asset_file)
			# objects = bundle.assets[0].objects
			# for obj in objects.values():
			# 	if obj.type.name in ["Texture2D"]:
			# 		data = obj.read()
			# 		dest = None
			# 		print(data.name, data.path)
			for path, obj in bundle.container.items():
				if obj.type.name in ["Texture2D", "Sprite"]:
					data = obj.read()
					cur_unit = None
					items = []
					dest = None
					if match_asset_pattern(unit_square_pattern, path, cur_unit, items, "Square"):
						costume_id = extract_costume_id_from_items(items)
						if costume_id == "01":
							dest = os.path.join(unit_output_dir, "Square", unit_square_name(unit_id, costume_id))
						else:
							dest = os.path.join(unit_output_dir, "Square", "AltCostumes", unit_square_name(unit_id, costume_id))
					elif match_asset_pattern(unit_costume_pattern, path, cur_unit, items, "Costume"):
						costume_id = extract_costume_id_from_items(items)
						if costume_id == "01":
							dest = os.path.join(unit_output_dir, "Costume", unit_costume_name(unit_id, costume_id))
						else:
							dest = os.path.join(unit_output_dir, "Costume", "AltCostumes", unit_costume_name(unit_id, costume_id))
					elif match_asset_pattern(unit_fullbody_pattern, path, cur_unit, items, "FullBody"):
						costume_id = extract_costume_id_from_items(items)
						if costume_id == "01":
							dest = os.path.join(unit_output_dir, "FullBody", unit_fullbody_name(unit_id, costume_id))
						else:
							dest = os.path.join(unit_output_dir, "FullBody", "AltCostumes", unit_fullbody_name(unit_id, costume_id))

					if dest:
						assert not os.path.exists(dest)
						data.image.save(dest)


if __name__ == "__main__":
	pass