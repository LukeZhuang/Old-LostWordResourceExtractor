import os
import re
import wget
import UnityPy

SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"

unit_square_pattern = r'^Assets/East/Units/([0-9]+)/([0-9]+)/Thumbnail/Square.png$'
unit_costume_pattern = r'^Assets/East/Units/([0-9]+)/([0-9]+)/Thumbnail/Costume.png$'
unit_fullbody_pattern = r'^Assets/East/Units/([0-9]+)/([0-9]+)/G([0-9]+)/G([0-9]+).png$'


def match_asset_pattern(pattern, asset_path, cur_unit, items, item_name):
	g = re.findall(pattern, asset_path)
	if len(g) > 0:
		unit_id = int(g[0][0])
		costume_id = g[0][1]
		assert cur_unit == None or cur_unit == unit_id
		cur_unit = unit_id
		items.append(costume_id + item_name)
		return cur_unit
	return cur_unit


def extract_unit_img(DOWNLOAD_PREFIX, asset_infos, do_extract_unit, all_costumes, extract_square, extract_costume, extract_fullbody):
	if not do_extract_unit:
		return

	unit_source_dir = os.path.join(SOURCE_DIR, "unit")
	if not os.path.exists(unit_source_dir):
		os.makedirs(unit_source_dir)

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
		for file_name, img_files in unit_asset_infos:
			unit_asset_file = os.path.join(unit_source_dir, "unit" + str(unit_id) + "_" + "-".join(img_files))
			
			# download file if needed
			if not os.path.exists(unit_asset_file):
				print("downloading:", unit_id, file_name)
				url = DOWNLOAD_PREFIX + file_name
				output = wget.download(url, unit_asset_file)




if __name__ == "__main__":
	pass