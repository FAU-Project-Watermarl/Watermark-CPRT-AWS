import argparse
import os
import subprocess
import sys
import uuid
import Database
import ErrorHandling
import ExtractMedia
import MediaTransfer
import ValidateMedia

video_media = "video"
audio_media = "audio"

parser = argparse.ArgumentParser()

# output -> folder that it outputs to.
# Args: o, output
parser.add_argument("-o", "--output")

# manifest_url -> argument that accepts a manifest url, necessary to download the segments.
# Args: m, manifest_url
parser.add_argument("-u", "--manifest_url")

args = parser.parse_args()

# main, takes cli as arguments and inserts them into dash obj, also extracts the media content and then validates it.
def main():
    Database.open_db()

    dash_obj = {
        "manifest_path": None,
        "uuid_value": None,
        "root_folder": None,
        "manifest_root": None,
        "manifest_output_path": None,
        "manifest_output_nested_path": None,
        "bucket_path": "testbucket-watermarking/test_signal",
        "bucket_filename":"test_signal",
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
        "cprt_time_complexity": 0,
    }

    root = args.output
    url = args.manifest_url

    not_unique = True
    uuid_value = None

    while(not_unique == True):
       uuid_value = str(uuid.uuid4())
       not_unique = Database.check_stored_uuid(uuid_value)

    dash_obj["uuid_value"] = uuid_value
    
    if not root or not url:
        ErrorHandling.error_handling_format("Invalid args")

    dash_obj["root_folder"] = f"{root}"
    dash_obj["manifest_output_path"] = f"{root}/output_mpd.txt"

    dash_obj["manifest_path"] = url.rsplit("/", 1)[-1]
    dash_obj["manifest_root"] = url[: url.rindex("/")]

    dash_obj["manifest_output_path"] = f"{root}/{dash_obj['manifest_path']}"

    MediaTransfer.extract_media_into_folder(
        dash_obj["manifest_root"],
        dash_obj["manifest_path"],
        dash_obj["manifest_output_path"],
        True,
    )

    extracted_value = None
    
    ExtractMedia.parse_mpd(dash_obj)
    if(not dash_obj["edge_case_base_url"]):
        os.chdir(os.path.dirname(dash_obj["manifest_output_nested_path"]))

        for vid_quality_id in dash_obj["video_qualities"]:
            print(f"video_id: {vid_quality_id}")
            ExtractMedia.extract_media(dash_obj, vid_quality_id, video_media)
            ExtractMedia.apply_uuid(dash_obj, vid_quality_id, video_media)

        for aud_quality_id in dash_obj["audio_qualities"]:
            print(f"audio_id: {aud_quality_id}")

            ExtractMedia.extract_media(dash_obj, aud_quality_id, audio_media)
            ExtractMedia.apply_uuid(dash_obj, aud_quality_id, audio_media)

        extracted_value = ValidateMedia.extract_uuid(
            dash_obj, dash_obj["video_qualities"][0], video_media
        )

    else:
        os.chdir(os.path.dirname(dash_obj["manifest_output_path"]))
        for id in dash_obj["base_urls"]:
            ExtractMedia.extract_media(dash_obj, id, video_media)
            ExtractMedia.apply_uuid(dash_obj, id, video_media)
        
        extracted_value = ValidateMedia.extract_uuid(
            dash_obj, dash_obj["base_urls"][0], video_media
        )

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    Database.insert_uuid_value(
       uuid_value,
       dash_obj
       )

    ValidateMedia.validate_uuid(extracted_value)

    print(
      "Total elapsed time duration to apply UUID:",
      dash_obj["cprt_time_complexity"],
       "milliseconds",
    )
    
    Database.close_db()

    MediaTransfer.insert_media_into_aws(
       dash_obj,
       uuid_value,
    )

if __name__ == "__main__":
    main()

