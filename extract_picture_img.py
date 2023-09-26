import os
import re
import wget
import UnityPy
from util import create_output_folder_if_not_exist

SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"

picture_asset_pattern = r'^Assets/East/Pictures/([0-9]+)/(.*).png$'


def picture_thumbsquare_name(picture_id):
	return "PTS" + str(picture_id) + ".png"

def picture_thumblarge_name(picture_id):
	return "PTL" + str(picture_id) + ".png"

def picture_efuda_name(picture_id):
	return "PE" + str(picture_id) + ".png"


def extract_picture_img(DOWNLOAD_PREFIX, asset_infos):
	create_output_folder_if_not_exist(SOURCE_DIR, "picture")
	picture_source_dir = os.path.join(SOURCE_DIR, "picture")
	create_output_folder_if_not_exist(OUTPUT_DIR, "picture")
	picture_output_dir = os.path.join(OUTPUT_DIR, "picture")

	create_output_folder_if_not_exist(picture_output_dir, "ThumbSquare")
	create_output_folder_if_not_exist(picture_output_dir, "ThumbLarge")
	create_output_folder_if_not_exist(picture_output_dir, "Efuda")

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
		print('extracting image for picture', picture_id)
		for file_name, img_files in pic_asset_infos:
			picture_asset_file = os.path.join(picture_source_dir, "picture" + str(picture_id) + "_" + "-".join(img_files))

			# download file if needed
			if not os.path.exists(picture_asset_file):
				print("downloading:", picture_id, file_name)
				url = DOWNLOAD_PREFIX + file_name
				output = wget.download(url, picture_asset_file)

			# start extracing
			bundle = UnityPy.load(picture_asset_file)
			objects = bundle.assets[0].objects
			for obj in objects.values():
				if obj.type.name in ["Texture2D"]:
					data = obj.read()
					dest = None
					if data.name.lower() == "ThumbSquare".lower():
						dest = os.path.join(picture_output_dir, "ThumbSquare", picture_thumbsquare_name(picture_id))
					elif data.name.lower() == "ThumbLarge".lower():
						dest = os.path.join(picture_output_dir, "ThumbLarge", picture_thumblarge_name(picture_id))
					elif data.name.lower() == "Efuda".lower():
						dest = os.path.join(picture_output_dir, "Efuda", picture_efuda_name(picture_id))

					if dest and not os.path.exists(dest):
						data.image.save(dest)


if __name__ == "__main__":
	pass