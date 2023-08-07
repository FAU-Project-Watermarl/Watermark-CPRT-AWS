import re
import os
import isodate
import uuid
import MediaTransfer
import Database
import shutil
import ErrorHandling

# parse mpd -> We parse the mpd and assign all the parsed data to the dash_obj
# args -> 
# root: root folder
# url: a url path to the manifest
# parse_type: whether or not we are trying to parse the main or validation script, boolean value.
# return: dictionary value containing the mapped values for the parsed content
def parse_mpd(root, url, parse_type):

    bucket_path = None
    bucket_filename = None
    uuid_value = None

    if(not ".mpd" in  url):
        ErrorHandling.error_handling_format("invalid url, must be a reference to an mpd file")

    if(parse_type):
        bucket_path = "testbucket-watermarking/test_signal"
        bucket_filename = "test_signal"

        not_unique = True
        while(not_unique == True):
            uuid_value = str(uuid.uuid4())
            not_unique = Database.check_stored_uuid(uuid_value)
    else:
        bucket_path = "testbucket-watermarking/validate_signal"
        bucket_filename = "validate_signal"

    dash_obj = {
        "manifest_path": None,
        "uuid_value": None,
        "root_folder": None,
        "manifest_root": None,
        "manifest_output_path": None,
        "manifest_output_nested_path": None,
        "bucket_path": f"{bucket_path}",
        "bucket_filename": f"{bucket_filename}",
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

    with open(dash_obj['manifest_output_path'], 'r') as file:
        in_adaptation = False
        lines = file.readlines()
        media_type = None
        audio_init_template = None
        video_init_template = None
        segment_counter = False
        audio_segments = None
        video_segments = None
        compact_type = None
        bandwidth_as_id = False
        extracted_init_template = None
        extracted_segment_template = None

        is_base_url_edge_case = extract_base_url(dash_obj)
        if(is_base_url_edge_case):
            return dash_obj

        for line in lines:
            if(audio_init_template != None and video_init_template != None and audio_segments != None and video_segments != None):
                break
            
            if("<Adaptation" in line):
                in_adaptation = True
                
            if(in_adaptation == True):

                if("video" in line and media_type == None):
                    media_type = "video"

                if("audio" in line and media_type == None):
                    media_type = "audio"
                
                if("<S t=" in line or "<S d=" in line):
                    segment_counter = True

                if("initialization=" in line):
                    extracted_init_template = re.search(r'initialization="(.*?)"', line)
                    extracted_init_template = extracted_init_template.group(1)

                if("media=" in line):
                    extracted_segment_template = re.search(r'media="(.*?)"', line)
                    extracted_segment_template = extracted_segment_template.group(1)

                if("</AdaptationSet" in line):
                    if(media_type == "video"):
                        video_init_template = extracted_init_template
                        video_segments = extracted_segment_template
                    else:
                        audio_init_template = extracted_init_template
                        audio_segments = extracted_segment_template

                    media_type = None
                    in_adaptation = False
                    extracted_init_template = None
                    extracted_init_template = None

    if(video_init_template == None or video_segments == None or audio_init_template == None or audio_segments == None):
        ErrorHandling.error_handling_format("Unable to parse manifest, critical data not found")

    dash_obj['init_template_video'] += video_init_template
    dash_obj['segment_template_video'] += video_segments
    dash_obj['init_template_audio'] += audio_init_template
    dash_obj['segment_template_audio']+= audio_segments

    if("$RepresentationID$" in video_init_template):
        compact_type = True
    else:
        compact_type = False
    if("$Bandwidth$" in video_init_template):
        bandwidth_as_id = True

    mpd_file_path = f"{os.getcwd()}/{dash_obj['manifest_output_path']}"
    if("../" in dash_obj['init_template_video']):
        split_template_array = dash_obj['init_template_video'].split("/")
        updated_path_array = []

        for delim in split_template_array:
            if delim == "..":
                updated_path_array.append(f"{dash_obj['root_folder']}")

            updated_path = "/".join(updated_path_array)
            final_path = [dash_obj['root_folder'], updated_path, dash_obj['manifest_path']]

        dash_obj['manifest_output_nested_path']  = "/".join(final_path)

        output_directory = os.path.dirname( dash_obj['manifest_output_nested_path'])
        os.makedirs(output_directory, exist_ok=True)

        shutil.copy(mpd_file_path, output_directory )
        os.remove(mpd_file_path)
    else:
        dash_obj['manifest_output_nested_path'] = dash_obj['manifest_output_path']
    
    parse_segment_template(dash_obj, compact_type, bandwidth_as_id)
    
    get_segment_count(dash_obj, segment_counter)

    get_media_representations(dash_obj, compact_type, bandwidth_as_id)

    return dash_obj

#extract_base_url -> checks for edge case scenario where there is an associated base url in the manifest
# args ->
# dash_obj: dictionary value containing the mapped values for the parsed content
# return: boolean value, whether or not there is an base value edge case
def extract_base_url(dash_obj):
    with open(dash_obj['manifest_output_path'], 'r') as file:
            lines = file.readlines()
            base_urls = []
            in_adaptation = False
            is_path = False
            temp_base_video_found = False
            temp_base_audio_found = False
            base_url_path = None
            root_url_found = False
            url_found = False
            media_type = None

            for line in lines:
                if(temp_base_audio_found and temp_base_audio_found):
                    break
                if(in_adaptation == False and root_url_found == False):
                     base_url = re.search(r'<BaseURL>(.*?)</BaseURL>', line)
                     if(base_url != None):
                        root_url_found = True
                        dash_obj["edge_case_video_base_root"] += base_url.group(1)
                        dash_obj["edge_case_audio_base_root"] += base_url.group(1)

                if("<Adaptation" in line):
                    in_adaptation = True

                if(in_adaptation == True):

                    if("video" in line and media_type == None):
                        media_type = "video"

                    if("audio" in line and media_type == None):
                        media_type = "audio"

                    url = re.search(r'<BaseURL>(.*?)</BaseURL>', line)
                    if(url != None):
                        url_found = True
                        if(not ".m" in url.group(1)):
                            base_url_path = url.group(1)
                            is_path = True
                        base_urls.append(url.group(1))

                if("</AdaptationSet" in line):
                    if(base_url_path != None):
                        if(media_type == "video" and not temp_base_video_found):
                            temp_base_video_found = True
                            dash_obj["edge_case_video_base_root"] += base_url_path
                        else:
                            if(not temp_base_audio_found):
                                temp_base_audio_found = True
                                dash_obj["edge_case_audio_base_root"] += base_url_path

                    in_adaptation = False

    if(not root_url_found and not temp_base_video_found and not temp_base_audio_found and not url_found):
        return False
    
    if(is_path):

        dash_obj['init_template_video'] = dash_obj["edge_case_video_base_root"]
        return False
    else:
        dash_obj["base_urls"] = base_urls
        dash_obj["edge_case_base_url"] = True
        return True

# parse_segment_template -> formats the segment template and some minor string manipulation
# args ->
# dash_obj: dictionary value containing the mapped values for the parsed content
# compact_type: whether or not the manifest is compact, boolean value.
# bandwidth_as_id: edgecase if there is a bandwidth as an id representation, boolean value
def parse_segment_template(dash_obj, compact_type, bandwidth_as_id):

    layout_type_temp = dash_obj["segment_template_video"] 
    replace_id = ['segment_template_video', 'segment_template_audio', 'init_template_audio', 'init_template_video']
    if(bandwidth_as_id):
        for id in range(0, len(replace_id)):
            dash_obj[replace_id[id]].replace("$Bandwidth$", "$RepresentationID$")    
    elif(compact_type == False):
            
            temp_seg_video_template = dash_obj["segment_template_video"]
            temp_seg_audio_template = dash_obj["segment_template_audio"]

            values_after_seg_video_m = None
            values_after_seg_audio_m = None
            inconsistent_container = False

            index_video = temp_seg_video_template.rfind(".m")
            index_audio = temp_seg_audio_template.rfind(".m")
            if index_video  != -1 and index_audio != -1:
                values_after_seg_video_m = temp_seg_video_template[index_video:]
                values_after_seg_audio_m = temp_seg_audio_template[index_audio:]
            
            if(values_after_seg_video_m != values_after_seg_audio_m):
                inconsistent_container = True
                temp_seg_video_template = temp_seg_video_template[:index_video]
                temp_seg_audio_template = temp_seg_audio_template[:index_audio]
                
            custom_segment_id = custom_string(temp_seg_video_template,temp_seg_audio_template,"$RepresentationID$") 
            if(inconsistent_container):
                dash_obj["segment_template_video"] = custom_segment_id + values_after_seg_video_m
                dash_obj["segment_template_audio"] = custom_segment_id + values_after_seg_audio_m
            else:
                dash_obj["segment_template_video"] = custom_segment_id
                dash_obj["segment_template_audio"] = custom_segment_id

            for id in range(0, len(replace_id)):
                template_index = dash_obj[replace_id[id]].find("?")
                if template_index != -1:
                    dash_obj[replace_id[id]] = dash_obj[replace_id[id]][:template_index]

            custom_init_id = custom_string(dash_obj["init_template_video"],dash_obj["init_template_audio"],"$RepresentationID$") 
            dash_obj["init_template_video"] = custom_init_id
            dash_obj["init_template_audio"] = custom_init_id

    if("Time" in layout_type_temp): #The player substitutes this identifier with the value of the SegmentTimeline@t attribute for the Segment. You can use either $Number$ or $Time$, but not both at the same time.
        if(compact_type):
                ErrorHandling.error_handling_format("Unable to parse time format")
        with open(dash_obj['manifest_output_nested_path'], 'r') as file:
            lines = file.readlines()
            t_string = "t="
            media_type = None
            time_segments_video = []
            time_segments_audio = []
            in_adaptation = False
            video_adaptation_set_complete = False
            audio_adaptation_set_complete = False

            for line in lines:
                if(time_segments_video != None and time_segments_audio != None and video_adaptation_set_complete and audio_adaptation_set_complete):
                    break

                if("<Adaptation" in line):
                    in_adaptation = True
                
                if(in_adaptation == True):  
                    if("video" in line):
                        if(video_adaptation_set_complete):
                            continue
                        media_type = "video"

                    if("audio" in line):
                        if(audio_adaptation_set_complete):
                            continue
                        media_type = "audio"

                    if(media_type == "audio" and t_string in line):
                        if(not "<S" in line):
                            continue
                        t_value = re.search(r't="(.*?)"', line)
                        time_segments_audio.append(int(t_value.group(1)))
                    
                    if(media_type == "video" and t_string in line):
                        if(not "<S" in line):
                            continue
                        t_value = re.search(r't="(.*?)"', line)
                        time_segments_video.append(int(t_value.group(1)))

                    if("</AdaptationSet>" in line):
                        media_type = None
                        in_adaptation = False
                        if(media_type == "video"):
                            video_adaptation_set_complete = True
                        else:
                            audio_adaptation_set_complete = True
                
            if(time_segments_video == []):
                time_segments_video.append(0)
            if(time_segments_audio== []):
                time_segments_audio.append(0)

            dash_obj['video_time_segments'] = time_segments_video
            dash_obj['audio_time_segments'] = time_segments_video
        
        return

    if("Number" in layout_type_temp): 
        line = locate_line(dash_obj['manifest_output_nested_path'], "startNumber=")
        if("startNumber=" in line):
            start_number = re.search(r'startNumber="(.*?)"', line)
            start_number = int(start_number.group(1))

        if(start_number == None):
            ErrorHandling.error_handling_format("Unable to parse, start number not found")

        dash_obj['start_number'] = start_number
        return
        
    ErrorHandling.error_handling_format("Unable to find iterative format")

# get_segment_count -> 
# args ->
# dash_obj: dictionary value containing the mapped values for the parsed content
# segment_counter: type of iteration based on what was initially parsed, boolean value
def get_segment_count(dash_obj, segment_counter):
    if(not segment_counter):
        target_text = "<MPD"
        desired_line = locate_line(dash_obj['manifest_output_nested_path'], target_text)
        presentation = re.search(r'mediaPresentationDuration="(.*?)"', desired_line)
        presentation = presentation.group(1)
        
        presentation_parse = isodate.parse_duration(presentation)
        presentation_seconds = presentation_parse.total_seconds()

        #OPTIMIZE WITH FUNC, REFACTOR
        with open(dash_obj['manifest_output_nested_path'], 'r') as file:

            in_adaptation = False
            lines = file.readlines()

            for line in lines:
                if("<Adaptation" in line):
                    in_adaptation = True
                    
                if(in_adaptation == True):
                    
                    if('duration=' in line):
                        duration = re.search(r'duration="(.*?)"', line)
                        duration = int(duration.group(1))

                    if("timescale="in line):
                        timescale = re.search(r'timescale="(.*?)"', line)
                        timescale = int(timescale.group(1))

                    if("</AdaptationSet" in line):
                        break

        sec = duration / timescale
        if(sec < 1 or sec > 120):
            ErrorHandling.error_handling_format("Unable to parse fragment duration, estimated value:", sec)

        frag = presentation_seconds / sec

        if(frag > int(frag)):
            frag = frag + 1
        
        dash_obj['total_segments'] = int(frag)
    else:
        with open(dash_obj['manifest_output_nested_path'], 'r') as file:
            lines = file.readlines()
            segment_timeline_text = "SegmentTimeline"
            segment_timeline_iteration = 0
            s_string ="<S "
            r_string = "r="
            s_count = 0
            r_count = 0

            for line in lines:
                if segment_timeline_text in line and segment_timeline_iteration > 1:
                    break
                if(segment_timeline_text in line):
                    segment_timeline_iteration += 1
                if(r_string in line and segment_timeline_iteration == 1):
                    r_value = re.search(r'r="(.*?)"', line)
                    if(int(r_value.group(1)) > 0):
                        r_count = r_count + int(r_value.group(1))
                
                if(s_string in line and segment_timeline_iteration == 1):
                    s_count += 1
            
            dash_obj['total_segments'] = r_count + s_count

# custom_string -> used for string manipulation, finds where two strings have different values and then inserts a custom value so that the strings match,
# used primarily to insert the $RepresentationID$ between two different media templates, very useful for regular expression searches.
# args ->
# str1: first string
# str2: second string
# custom_string: custom string we want to insert
# return:
def custom_string(str1, str2, custom_string):
    str1_len = len(str1)
    str2_len = len(str2)
    
    max_len = max(str1_len, str2_len)
    
    if(str1_len != str2_len):
        additional_character_value = 0
        if(str1_len > str2_len):
            additional_character_value = str1_len - str2_len
            str2 = ("#" * additional_character_value ) + str2
        else:
            additional_character_value = str2_len - str1_len
            str1 = ("#" * additional_character_value ) + str1

    for i in range(max_len)[::-1]:
        if (str1[i] != str2[i]):
            backward_difference = i
            break
    
    backward = str1[backward_difference + 1:]
    return custom_string + backward
    
# get media representations -> gets the ids of the audio and video representations
# Args:
# dash_obj, contains all the information about the parsed mpd
# compact: whether or not the manifest of compact or not, boolean value
# bandwith_as_id: edge case scenario where the bandwidth is used as the represenation
def get_media_representations(dash_obj, compact=False, bandwidth_as_id=False):
    with open(dash_obj['manifest_output_nested_path'], 'r') as file:
        if(bandwidth_as_id): 
            lines = file.readlines()
            in_adaptation = False
            media_type = None
            for line in lines:
                if("<Adaptation" in line):
                    in_adaptation = True

                if(in_adaptation == True):
                    if("video" in line):
                        media_type = "video"

                    if("audio" in line):
                        media_type = "audio"

                    if(media_type == "audio" and "bandwidth=" in line):
                        bandwith_value = re.search(r'bandwidith="(.*?)"', line)
                        dash_obj['audio_qualities'].append(str(bandwith_value.group(1)))

                    if(media_type == "video" and "bandwidth=" in line):
                        bandwith_value = re.search(r'bandwidth="(.*?)"', line)
                        dash_obj['video_qualities'].append(str(bandwith_value.group(1)))

                    if("</AdaptationSet>" in line):
                        media_type = None
                        in_adaptation = False
            return

        if(not compact):
            idVideo=""
            idAudio=""

            segment_template_video_escaped = re.escape(dash_obj["segment_template_video"])
            segment_template_audio_escaped = re.escape(dash_obj["segment_template_audio"])

            reg_ex_search_video = segment_template_video_escaped.replace(r"\$RepresentationID\$", r"(.*?)")
            reg_ex_search_video = r"media=\"" + reg_ex_search_video

            reg_ex_search_audio = segment_template_audio_escaped.replace(r"\$RepresentationID\$", r"(.*?)")
            reg_ex_search_audio = r"media=\"" + reg_ex_search_audio

            lines = file.readlines()
            in_adaptation = False
            media_type = None
            for line in lines:
                if("<Adaptation" in line):
                    in_adaptation = True

                if(in_adaptation == True):
                    if("video" in line):
                        media_type = "video"

                    if("audio" in line):
                        media_type = "audio"

                    if(media_type == "audio" and "media=" in line):
                        media_value = re.search(reg_ex_search_audio, line)
                        dash_obj['audio_qualities'].append(str(media_value.group(1)))

                    if(media_type == "video" and "media=" in line):
                        media_value = re.search(reg_ex_search_video, line)
                        dash_obj['video_qualities'].append(str(media_value.group(1)))

                    if("</AdaptationSet>" in line):
                        media_type = None
                        in_adaptation = False
            return
        
        if(compact):
            skipped_header = False
            representation_start_string = "<Representation"
            lines = file.readlines()
            for line in lines:
                if(representation_start_string in line):
                        skipped_header = True
                if(not skipped_header):
                        continue
                idVideo = re.search(r'id="(.*?)".*\bwidth\b', str(line.strip()))
                idAudio = re.search(r'id="(?!.*\b(?:width|profiles|segmentAlignment)\b)(.*?)".*', str(line.strip()))                            
                if idVideo!=None:
                    dash_obj['video_qualities'].append(str(idVideo.group(1)))
                if idAudio!=None:
                    dash_obj['audio_qualities'].append(str(idAudio.group(1)))

# locate line -> locate a line inside of the manifest 
# Args:
# manifest_file, the manifest file
# target_text, initial target text we are looking for
# seg_temp, optional value to find a given desired line under the target text if the desired line is too ambiguous.
def locate_line(manifest_file, target_text, text_desired=None):
    with open(manifest_file, 'r') as file:
        lines = file.readlines()
        desired_line = None

        if(text_desired):
            target_line = text_desired
            target_found = False
        else:
            target_line = target_text
            target_found = True

        for line in lines:
            if target_text in line and not target_found:
                target_found = True
            if(target_line in line and target_found):
                desired_line = line.strip()
                return desired_line
