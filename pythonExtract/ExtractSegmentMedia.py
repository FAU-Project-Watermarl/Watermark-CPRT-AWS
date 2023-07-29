import MediaTransfer
import ErrorHandling
import Mp4ContainerManip
import re

# extract media -> extracts the parsed media content be it the init or the segements or both.
# Args:
# dash_obj, contains all the information about the parsed mpd
# quality od, the id of what we are trying to extract
# media_type, audio or video
# init_only, optional value, true if we only want to extract the init false if we want the segments aswell.
def extract_media_segments(dash_obj, quality_id, media_type, init_only=False, apply_uuid=True):

    if(dash_obj["edge_case_base_url"]):
        print("Extracting File:", quality_id)
        MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], quality_id, quality_id)
        return

    init_template=""
    segment_template=""
    if(media_type == "video"):
        init_template = dash_obj["edge_case_video_base_root"] + dash_obj["init_template_video"].replace('$RepresentationID$', str(quality_id))
        segment_template = dash_obj["edge_case_video_base_root"] + dash_obj["segment_template_video"].replace('$RepresentationID$', str(quality_id))
    else:
        init_template = dash_obj["edge_case_audio_base_root"] + dash_obj["init_template_audio"].replace('$RepresentationID$', str(quality_id))
        segment_template = dash_obj["edge_case_audio_base_root"] +  dash_obj["segment_template_audio"].replace('$RepresentationID$', str(quality_id))

    print("Extracting File:", init_template)
    MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], init_template, init_template)
    if(apply_uuid):
        Mp4ContainerManip.apply_uuid(dash_obj, quality_id, media_type)

    if(init_only):
        return
    
    iterator = re.search(r'\$(.*?)\$', segment_template)
    if(not iterator.group(1)):
        ErrorHandling.error_handling_format("No iterator found")
    iterator = iterator.group(1)

    # true for number false for time, so u don't get confused manuel.
    iterator_type = None
    if("Number" in iterator):
        iterator_type = True
    if("Time" in iterator):
        iterator_type = False

    edge_case_iterator = False

    if("%0" in iterator):
        counter_edge_case = re.search(r'%(.*?)d', iterator)
        iterator = "%" + counter_edge_case.group(1) + "d"
        edge_case_iterator = True
        if(iterator_type):
            segment_template = segment_template.replace("Number", "")
        if(iterator_type == False):
            segment_template = segment_template.replace("Time", "")

    segment_template = segment_template.replace("$", "")

    num = 0 
    
    if(iterator_type == False):

        time_array = []
        if(media_type == "video"):
            time_array  = dash_obj['video_time_segments']
        else:
            time_array = dash_obj['audio_time_segments']

        for time_value in time_array:
            if(edge_case_iterator):
                temp_iterator = iterator % time_value
                segment = segment_template.replace(iterator, temp_iterator)
            else:
                segment = segment_template.replace(iterator, str(time_value))

            print("Extracting File:", segment)
            MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], segment, segment)
    elif (dash_obj['total_segments'] != None and iterator_type):
        for fragment_num in range(dash_obj['start_number'], dash_obj['start_number'] + dash_obj['total_segments']):
            num += 1
            if(edge_case_iterator):
                temp_iterator = iterator % fragment_num
                segment = segment_template.replace(iterator, temp_iterator)
            else:
                segment = segment_template.replace(iterator, str(fragment_num))
            print("Extracting File:", segment)
            MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], segment, segment)
    else:
        fragment_status = True
        current_fragment = dash_obj['start_number']
        while fragment_status:
            num += 1
            init = segment_template.replace(iterator, str(current_fragment))

            print("Extracting File:", init)
            fragment_status = MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], init, init)
            current_fragment = current_fragment + 1
