import subprocess
import ExtractSegmentMedia 
import MediaTransfer
import time
import argparse
import ErrorHandling
import os
import Mp4ContainerManip
import Database
import ParseMpd

video_media = "video"
audio_media = "audio"
uuid_db = "uuid"

# validate uuid -> validates a given uuid, accepts uuid to validate as an optional argument otherwise it just looks inside the db.json file
# Args:
# extracted_value, its the value extracted from the init.
# uuid_to_validate, optional argument that is the uuid, not necessary
def validate_uuid(extracted_value, uuid_status, uuid_to_validate=None):
    
    print('''--------------- Validating uuid ---------------------
    ''')

    if(not uuid_to_validate):
        if(uuid_status):
            print("UUID Successfully validated through the database, UUID:", extracted_value)
            subprocess.run(f'echo "{extracted_value}" > s3.txt', shell=True)
        else:
            ErrorHandling.error_handling_format("The UUID has failed to validate inside of the database.")
        return

    if(extracted_value in uuid_to_validate):
        print("UUID Successfully internally validated, UUID:", extracted_value)
        subprocess.run(f'echo "{extracted_value}" > s3.txt', shell=True)
    else:
        ErrorHandling.error_handling_format("The UUID has failed to internally validate.")

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

    root = args.output
    url = args.manifest_url

    dash_obj = ParseMpd.parse_mpd(root, url, False)

    extracted_uuid = None

    if(not dash_obj["edge_case_base_url"]):
        os.chdir(os.path.dirname(dash_obj['manifest_output_nested_path']))
        
        ExtractSegmentMedia.extract_media_segments(dash_obj, dash_obj["video_qualities"][0], video_media, True, False)
        extracted_uuid = Mp4ContainerManip.extract_uuid(dash_obj, dash_obj["video_qualities"][0], video_media)
    else:
        extracted_uuid = Mp4ContainerManip.extract_uuid(dash_obj, dash_obj["base_urls"][0], video_media)

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)
    if(extracted_uuid != None):
        uuid_status = Database.check_stored_uuid(extracted_uuid) 
        validate_uuid(extracted_uuid, uuid_status)
        MediaTransfer.insert_media_into_aws(dash_obj)
    
    end_time = time.time()
    total_time_ms = int((end_time - start_time) * 1000)

    print("Time duration to validate:", total_time_ms," milliseconds")

    Database.close_db()

if __name__ == "__main__":
    main()