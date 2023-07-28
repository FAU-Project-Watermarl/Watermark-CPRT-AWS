import subprocess
import os
import requests
import ErrorHandling
import shutil

# extract file -> extracts the file to the current dir
# Args:
# manifest_root, manifest_path, root and path to the file
#  manifest_output_file, outputted file name
# is_root, optional value, false if we don't want to exit on extraction failure, true if we do.
def extract_file(manifest_root, manifest_path, is_root=False):

    status = path_status(manifest_root, manifest_path, is_root)

    if not status:
        return 

    extract_mpd = f"curl {manifest_root}/{manifest_path} > {manifest_path}"
    subprocess.run(extract_mpd, shell=True)

# extract media into folder -> extracts media into a given folder.
# Args:
# manifest_root, media_file, root and path for the curl
# file output, the nested folder path it outputs to.
# is_root, optional value, false if we don't want to exit on extraction failure, true if we do.
def extract_media_into_folder(manifest_root, media_file, folder_path_output, is_root=False):
    status = path_status(manifest_root, media_file, is_root)

    if not status:
        return False 
    
    if("/" in folder_path_output):
        output_directory = os.path.dirname(folder_path_output)
        os.makedirs(output_directory, exist_ok=True)
    else:
        folder_path_output = f"./{folder_path_output}"

    extract_mpd_segments = f"curl {manifest_root}/{media_file} --output {folder_path_output}"
    subprocess.run(extract_mpd_segments, shell=True)
    return True

# insert_media_into_aws -> insert media into an aws bucket path
# Args:
# file path, the path of the folder or file that is going to be moved to the s3 bucker
# bucket path, the aws bucket path.
def insert_media_into_aws(dash_obj, uuid):

    temp_dir = f"./temp_dir/{uuid}/"
    os.makedirs(temp_dir, exist_ok=True)
    subprocess.run(f"mkdir -p {temp_dir}", shell=True)

    subprocess.run(f"pwd",shell=True)
    subprocess.run(f"cp -r {dash_obj['root_folder']}/ ./{temp_dir}", shell=True)

    insert_media_folder = f"aws s3 sync ./temp_dir/  s3://{dash_obj['bucket_path']}/"
    subprocess.run(insert_media_folder, shell=True)
    subprocess.run(f"rm -rf ./{temp_dir}", shell=True)

    subprocess.run(f"echo 'https://d6p5bgq5sl2je.cloudfront.net/{dash_obj['bucket_filename']}/{uuid}/{dash_obj['manifest_output_nested_path']}' > {dash_obj['bucket_filename']}.txt", shell=True)

# path status -> checks if a given request is valid or not
# Args:
# manifest_root, path, the root and the path.
# is_root, optional value, false if we don't want to exit on extraction failure, true if we do.
def path_status(manifest_root, manifest_path, is_root):
    url = f"{manifest_root}/{manifest_path}"
    response = requests.head(url)
    if(response.status_code == 429):
        ErrorHandling.error_handling_format("Trafic limit exceeded")

    if(response.status_code != 200):
        ErrorHandling.error_handling_format("unable to find path", is_root)
        return False

    return True

