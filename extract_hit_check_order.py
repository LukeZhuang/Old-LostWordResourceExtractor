import csv
import os
import re
import wget
import UnityPy

SOURCE_DIR = "./source"
OUTPUT_DIR = "./output"
absent_file = "./hit_check_order_absent.csv"

timeline_asset_pattern = r'^Assets/East/Units/([0-9]+)/Timeline/Barrage[12347][0123].asset$'
barrage_file_pattern = r'Barrage([12347][0123])'

barrage_ids = ['1', '2', '3', '4' ,'7']
boost_ids = ['0', '1', '2', '3']

def extract_hit_check_order(DOWNLOAD_PREFIX, asset_infos, do_extract_hit_check_order):
	if not do_extract_hit_check_order:
		return

	timeline_source_dir = os.path.join(SOURCE_DIR, "timeline")
	if not os.path.exists(timeline_source_dir):
		os.makedirs(timeline_source_dir)

	# read all timeline info
	unit_timeline = {}
	for asset_info in asset_infos:
		if "Timeline" not in str(asset_info):
			continue
		file_name = asset_info["Name"]
		asset_paths = asset_info["AssetPaths"]
		cur_unit = None
		for asset_path in asset_paths:
			g = re.findall(timeline_asset_pattern, asset_path)
			assert len(g) == 1
			assert cur_unit == None or cur_unit == int(g[0])
			cur_unit = int(g[0])
		assert cur_unit not in unit_timeline
		unit_timeline[cur_unit] = file_name

	sorted_units = sorted(list(unit_timeline.items()), key=lambda x:x[0])
	hit_check_order_result = []

	for unit, file_name in sorted_units:
		timeline_file = os.path.join(timeline_source_dir, "timeline" + str(unit))

		# download file if needed
		if not os.path.exists(timeline_file):
			print("downloading:", unit, file_name)
			url = DOWNLOAD_PREFIX + file_name
			output = wget.download(url, timeline_file)

		# start extracing
		bundle = UnityPy.load(timeline_file)
		objects = bundle.assets[0].objects
		obj_file_dict = {}
		barrage_files = []
		for obj in objects.values():
			if 'MonoBehaviour' in str(obj.type):
				game_object = obj.read()
				obj_file_dict[game_object.path_id] = game_object
				if game_object.name.startswith("Barrage"):
					g = re.findall(barrage_file_pattern, game_object.name)
					assert len(g) == 1
					barrage_id = int(g[0][0])
					boost_id = int(g[0][1])
					barrage_files.append((barrage_id, boost_id, game_object))
		barrage_files.sort()
		for barrage_id, boost_id, game_object in barrage_files:
			assert hasattr(game_object, 'm_ordrlist')
			hit_check_order = ''
			for order in game_object.m_ordrlist:
				assert order.path_id in obj_file_dict
				order_object = obj_file_dict[order.path_id]
				if hasattr(order_object, 'm_mgznid'):
					hit_check_order += str(int(order_object.m_mgznid)+1)
			hit_check_order_result.append((unit, barrage_id, boost_id, hit_check_order))

	# add absent unit hit check order info
	with open(absent_file) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			hit_check_order_result.append((int(row["unit_id"]), int(row["barrage_id"]), int(row["boost_id"]), row["hit_check_order"]))

	hit_check_order_result.sort()

	# print output to file
	with open(os.path.join(OUTPUT_DIR, "HitCheckOrderTable.csv"), 'w') as fo:
		fo.write("id,unit_id,barrage_id,boost_id,hit_check_order\n")
		uniq_id = 1
		for unit_id, barrage_id, boost_id, hit_check_order in hit_check_order_result:
			fo.write(','.join([str(uniq_id), str(unit_id), str(barrage_id), str(boost_id), hit_check_order if len(hit_check_order) > 0 else "(empty)"]) + "\n")
			uniq_id += 1


if __name__ == "__main__":
	# testing code
	pass
