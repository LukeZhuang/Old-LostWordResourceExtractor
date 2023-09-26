import os

def create_output_folder_if_not_exist(root, sub_dir):
	sub_dir_path = os.path.join(root, sub_dir)
	if not os.path.exists(sub_dir_path):
		os.makedirs(sub_dir_path)