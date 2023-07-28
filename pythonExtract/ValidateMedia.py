import subprocess
import re
import ExtractMedia 
import MediaTransfer
import time
import argparse
import ErrorHandling
import os
import Database

video_media = "video"
audio_media = "audio"
uuid_db = "uuid"

# extract uuid -> extracts the uuid, self explanatory. Looks into the given file and attempts to find the uuid inside the mp4dump value = 
# Args:
#  dash obj, dash dictionary containing all information associated with the extracted prased mpd file
# quality id, the video or audio quality id
# media type, either audio or video, whatever we are looking for.
def extract_uuid(dash_obj, quality_id, media_type):
    print('''--------------- Extracting uuid ---------------------
    ''')
    init_template = None
    if(dash_obj["edge_case_base_url"]):
        init_template = quality_id
    else:
        if(media_type == "video"):
            init_template = dash_obj["init_template_video"].replace('$RepresentationID$', str(quality_id))
        else:  
            init_template = dash_obj["init_template_audio"].replace('$RepresentationID$', str(quality_id))

    dump_mp4 = f"mp4dump {init_template}"

    result = subprocess.run(dump_mp4, shell=True, capture_output=True, text=True)
    output = result.stdout

    match = re.findall(r'value = (\S+)', output) 

    for extracted_value in match:
         if(len(extracted_value) == 36):
            print("UUID Successfully extracted, UUID:", extracted_value)
            return extracted_value
    print("No UUID has been found")
    return None

# validate uuid -> validates a given uuid, accepts uuid to validate as an optional argument otherwise it just looks inside the db.json file
# Args:
# extracted_value, its the value extracted from the init.
# uuid_to_validate, optional argument that is the uuid, not necessary
def validate_uuid(extracted_value, uuid_to_validate=None):
    
    print('''--------------- Validating uuid ---------------------
    ''')

    if(not uuid_to_validate):
        uuid_status = Database.check_stored_uuid(extracted_value) 
        if(uuid_status):
            print("UUID Successfully validated through the database, UUID:", extracted_value)
            subprocess.run(f'echo "{extracted_value}" > s3.txt', shell=True)
        else:
            print("The UUID has failed to validate inside of the database.")
        return

    if(extracted_value in uuid_to_validate):
        print("UUID Successfully internally validated, UUID:", extracted_value)
        subprocess.run(f'echo "{extracted_value}" > s3.txt', shell=True)
    else:
        print("The UUID has failed to internally validate.")

parser = argparse.ArgumentParser()
# output -> folder that it outputs to.
# Args:
# o, output
parser.add_argument(
    "-o",
    "--output",
)

# manifest_url -> arugment that accepts a manifest url, necessary to download the segments.
# Args:
# u or manifest_url 
parser.add_argument(
    "-u",
    "--manifest_url",
)
args = parser.parse_args()

# Main for validation
# Args: the cli args as stated in the comments
# Validates a given stream, looks for the uuid inside the init of the first id.
def main():
    
    Database.open_db()

    start_time = time.time()

    dash_obj = {
    'manifest_path' : None, 
    'uuid_value' : None, 
    'root_folder' : None,
    'manifest_root' : None,
    'manifest_output_path' : None,
    'manifest_output_nested_path' : None,
    'bucket_filename':"validated_signal",
    'bucket_path' : "testbucket-watermarking/validated_signal",
    "video_qualities": [],
    "audio_qualities": [],
    'video_time_segments': None,
    'audio_time_segments': None,
    "init_template_video": "",
    "segment_template_video": "",
    "start_number": None,
    "init_template_audio": "",
    "segment_template_audio": "",
    "edge_case_video_base_root": "",
    "edge_case_audio_base_root": "",
    "total_segments": None,
    "edge_case_base_url": False,
    "base_urls": [],
    "cprt_time_complexity": 0 }
    
    root = args.output
    url = args.manifest_url

    if(not root or not url):
        ErrorHandling.error_handling_format("Invalid args")

    dash_obj['root_folder'] = f"{root}"
    dash_obj['manifest_output_path'] = f"{root}/output_mpd.txt"

    dash_obj['manifest_path'] = url.rsplit('/', 1)[-1]
    dash_obj['manifest_root'] = url[:url.rindex('/')]

    dash_obj['manifest_output_path'] = f"{root}/{dash_obj['manifest_path']}"

    MediaTransfer.extract_media_into_folder(dash_obj["manifest_root"], dash_obj["manifest_path"], dash_obj["manifest_output_path"], True)
    
    ExtractMedia.parse_mpd(dash_obj)

    extracted_uuid = None

    if(not dash_obj["edge_case_base_url"]):
        os.chdir(os.path.dirname(dash_obj['manifest_output_nested_path']))
        
        ExtractMedia.extract_media(dash_obj, dash_obj["video_qualities"][0], video_media, True)

        extracted_uuid = extract_uuid(dash_obj, dash_obj["video_qualities"][0], video_media)
    else:
        extracted_uuid = extract_uuid(dash_obj, dash_obj["base_urls"][0], video_media)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)
    if(extracted_uuid != None):
        validate_uuid(extracted_uuid)
        MediaTransfer.insert_media_into_aws(dash_obj, True)
    
    end_time = time.time()
    total_time_ms = int((end_time - start_time) * 1000)

    print("Time duration to validate:", total_time_ms," milliseconds")

    Database.close_db()

if __name__ == "__main__":
    main()