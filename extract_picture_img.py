import os
import re
import wget
import UnityPy

SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"

picture_asset_pattern = r'^Assets/East/Pictures/([0-9]+)/(.*).png$'

def extract_picture_img(DOWNLOAD_PREFIX, asset_infos, do_extract_picture, extract_thumbsquare, extract_thumblarge, extract_efuda):
	if not do_extract_picture:
		return

	picture_source_dir = os.path.join(SOURCE_DIR, "picture")
	if not os.path.exists(picture_source_dir):
		os.makedirs(picture_source_dir)

	picture_dict = {}
	for asset_info in asset_infos:
		if "Pictures" not in str(asset_info):
			continue
		file_name = asset_info["Name"]
		asset_paths = asset_info["AssetPaths"]
		cur_picture = None
		imgs = []
		for asset_path in asset_paths:
			g = re.findall(picture_asset_pattern, asset_path)
			assert len(g) == 1
			pic_id = int(g[0][0])
			img_name = g[0][1]
			assert cur_picture == None or cur_picture == pic_id
			cur_picture = pic_id
			imgs.append(img_name)
		picture_dict.setdefault(cur_picture, [])
		picture_dict[cur_picture].append((file_name, imgs))
	
	sorted_pictures = sorted(list(picture_dict.items()), key=lambda x:x[0])

	for picture_id, pic_asset_infos in sorted_pictures:
		for file_name, img_files in pic_asset_infos:
			picture_asset_file = os.path.join(picture_source_dir, "picture" + str(picture_id) + "_" + "-".join(img_files))

			# download file if needed
			if not os.path.exists(picture_asset_file):
				print("downloading:", picture_id, file_name)
				url = DOWNLOAD_PREFIX + file_name
				output = wget.download(url, picture_asset_file)

			pass




if __name__ == "__main__":
	pass