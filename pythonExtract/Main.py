import argparse
import os
import Database
import ExtractSegmentMedia
import MediaTransfer
import ValidateMedia
import Mp4ContainerManip
import ParseMpd

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

    root = args.output
    url = args.manifest_url
    extracted_value = None

    dash_obj = ParseMpd.parse_mpd(root, url, True)

    if(not dash_obj["edge_case_base_url"]):
        os.chdir(os.path.dirname(dash_obj["manifest_output_nested_path"]))

        for vid_quality_id in dash_obj["video_qualities"]:
            print(f"video_id: {vid_quality_id}")
            ExtractSegmentMedia.extract_media_segments(dash_obj, vid_quality_id, video_media, False, True)

        for aud_quality_id in dash_obj["audio_qualities"]:
            print(f"audio_id: {aud_quality_id}")
            ExtractSegmentMedia.extract_media_segments(dash_obj, aud_quality_id, audio_media, False, True)

        extracted_value = Mp4ContainerManip.extract_uuid(
            dash_obj, dash_obj["video_qualities"][0], video_media
        )
    else:
        os.chdir(os.path.dirname(dash_obj["manifest_output_path"]))
        for id in dash_obj["base_urls"]:
            ExtractSegmentMedia.extract_media_segments(dash_obj, id, video_media)
            Mp4ContainerManip.apply_uuid(dash_obj, id, video_media)
        
        extracted_value =  Mp4ContainerManip.extract_uuid(
            dash_obj, dash_obj["base_urls"][0], video_media
        )

    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)
    
    Database.insert_uuid_value(
       dash_obj
       )
    
    uuid_status = Database.check_stored_uuid(extracted_value) 

    ValidateMedia.validate_uuid(extracted_value,uuid_status)

    print(
      "Total elapsed time duration to apply UUID:",
      dash_obj["cprt_time_complexity"],
       "milliseconds",
    )
    
    Database.close_db()

    MediaTransfer.insert_media_into_aws(
       dash_obj,
    )

if __name__ == "__main__":
    main()

