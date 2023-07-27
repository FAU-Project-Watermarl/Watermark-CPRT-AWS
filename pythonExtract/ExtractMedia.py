import subprocess
import re
import MediaTransfer
import os
import isodate
import time
import shutil
import ErrorHandling

# parse mpd -> We parse the mpd and assign all the parsed data to the dash_obj, it's pass by reference so we don't need to return anything.
# Args:
# dash_obj, contains all the information about the parsed mpd
def parse_mpd(dash_obj):
    init_template=""
    segment_template=""
    start_number = 0
    media_types = ['video', 'audio']
    desired_line = None

    for type in media_types:
        target_text = f'mimeType="{type}/mp4"'
        desired_line_identifier = 'media='

        desired_line = locate_line(dash_obj['manifest_output_path'], target_text, desired_line_identifier)
        if(desired_line is None):
            ErrorHandling.error_handling_format("Unable to parse manifest, incorrect format")
    
        init_template = re.search(r'initialization="(.*?)"', desired_line)
        if(init_template is None):
             ErrorHandling.error_handling_format("Unable to parse, initialization not found")

        init_template = init_template.group(1)
    
        segment_template = re.search(r'media="(.*?)"', desired_line)

        if(segment_template == None):
            # look for mkv format
            ErrorHandling.error_handling_format("Unable to parse, media not found")

        segment_template = segment_template.group(1)

        if (type == 'video'):
            dash_obj['init_template_video'] = init_template
            dash_obj['segment_template_video'] = segment_template
        else:
            dash_obj['init_template_audio'] = init_template
            dash_obj['segment_template_audio'] = segment_template

    start_number = re.search(r'startNumber="(.*?)"', desired_line)
    if(start_number == None):
        ErrorHandling.error_handling_format("Unable to parse, start number not found")

    start_number = int(start_number.group(1))

    dash_obj['start_number'] = start_number

    mpd_file_path = f"{os.getcwd()}/{dash_obj['manifest_output_path']}"
    if("../" in init_template):
        split_template_array = init_template.split("/")
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

    if("RepresentationID" in init_template):
        get_media_representations(dash_obj, True)
        handle_compact(dash_obj)
    else:
        get_media_representations(dash_obj, False)
        handle_non_compact(dash_obj)

# handle_compact -> handles a compact manifest where the representation is started as a varaiable.
# Args:
# dash_obj, dictioanry containing all the parsed mpd information
def handle_compact(dash_obj):

    target_text = "MPD"
    desired_line = locate_line(dash_obj['manifest_output_nested_path'], target_text)
    presentation = re.search(r'mediaPresentationDuration="(.*?)"', desired_line)

    presentation = presentation.group(1)
    
    presentation_parse = isodate.parse_duration(presentation)
    presentation_seconds = presentation_parse.total_seconds()
    
    target_text = "mimeType="
    desired_line_identifier = 'duration='
    desired_line = locate_line(dash_obj['manifest_output_nested_path'], target_text, desired_line_identifier)
    duration = re.search(r'duration="(.*?)"', desired_line)

    target_text = "timescale="
    desired_line = locate_line(dash_obj['manifest_output_nested_path'], target_text)
    timescale = re.search(r'timescale="(.*?)"', desired_line)

    timescale = int(timescale.group(1))
    duration = int(duration.group(1))

    sec = duration / timescale
    if(sec < 1 or sec > 120):
       ErrorHandling.error_handling_format("Unable to parse fragment duration, estimated value:", sec)

    frag = presentation_seconds / sec

    if(frag > int(frag)):
        frag = frag + 1
    
    if(int(frag) <= 5 or int(frag) >= 100):
        dash_obj['total_segments'] = None
        return
    
    dash_obj['total_segments'] = int(frag)

# handle_non_compact -> handles a manifest that is not compact
# Args:
#dash_obj, dictioanry containing all the values
def handle_non_compact(dash_obj):
    replace_id = ['init_template_video', 'segment_template_video', 'init_template_audio', 'segment_template_audio']
    for id in range(0, len(replace_id)):
        dash_obj[replace_id[id]] = re.sub(r'o_(.*?)_', r'o_$RepresentationID$_', dash_obj[replace_id[id]])

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

# get media representations -> gets the ids of the audio and video representations
# Args:
# dash_obj, contains all the information about the parsed mpd
def get_media_representations(dash_obj, compact=False):
    with open(dash_obj['manifest_output_nested_path'], 'r') as file:
        skipped_header = False
        representation_start_string = "<Representation"
        for line in file:
            if(representation_start_string in line):
                skipped_header = True
            if(not skipped_header):
                continue
            idsVideos=""
            idAudio=""
            if(not compact):
                idsVideos = re.search(r'index_video_(.*?)_', str(line.strip()))
                idAudio = re.search(r'index_audio_(.*?)_', str(line.strip()))
            else:
                idsVideos = re.search(r'id="(.*?)".*\bwidth\b', str(line.strip()))
                idAudio = re.search(r'id="(?!.*\b(?:width|profiles|segmentAlignment)\b)(.*?)".*', str(line.strip()))
                
            if idsVideos!=None:
                dash_obj['video_qualities'].append(str(idsVideos.group(1)))
            if idAudio!=None:
                dash_obj['audio_qualities'].append(str(idAudio.group(1)))

        if(len(dash_obj['video_qualities']) == 0 or len(dash_obj['audio_qualities']) is 0):
            ErrorHandling.error_handling_format("Unable to parse, failed to extract quality id")

# apply_uuid -> apply the uuid to a given id.
# Args:
# dash_obj, contains all the information about the parsed mpd
# quality id, the quality id.
# media type, either audio or video 
def apply_uuid(dash_obj, quality_id, media_type):
    print('''--------------- Applying uuid ---------------------
    ''')

    if(media_type == "video"):
        init_template = dash_obj["init_template_video"].replace('$RepresentationID$', str(quality_id))
    else:
        init_template = dash_obj["init_template_audio"].replace('$RepresentationID$', str(quality_id))
    print("Applying uuid to path:",init_template)
    
    if not os.path.exists(init_template):
        print("Uuid not applied, path not found")
        return

    start_time = time.time()
    setCprt = f'mp4tag --set cprt:S:{dash_obj["uuid_value"]} {init_template} {init_template}'
    subprocess.run(setCprt, shell=True)

    end_time = time.time()
    total_time_ms = int((end_time - start_time) * 1000)
    dash_obj['cprt_time_complexity'] =  dash_obj['cprt_time_complexity'] + (total_time_ms)

    print("Applied UUID:",  dash_obj['uuid_value'], " Time duration to apply UUID:", total_time_ms,"milliseconds")

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

# extract media -> extracts the parsed media content be it the init or the segements or both.
# Args:
# dash_obj, contains all the information about the parsed mpd
# quality od, the id of what we are trying to extract
# media_type, audio or video
# init_only, optional value, true if we only want to extract the init false if we want the segments aswell.
def extract_media(dash_obj, quality_id, media_type, init_only=False):


    init_template=""
    segment_template=""
    if(media_type == "video"):
        init_template = dash_obj["init_template_video"].replace('$RepresentationID$', str(quality_id))
        segment_template = dash_obj["segment_template_video"].replace('$RepresentationID$', str(quality_id))
    else:
        init_template = dash_obj["init_template_audio"].replace('$RepresentationID$', str(quality_id))
        segment_template = dash_obj["segment_template_audio"].replace('$RepresentationID$', str(quality_id))

    MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], init_template, init_template)

    if(init_only):
        return
    
    num = 0 

    iterator = re.search(r'\$(.*?)\$', segment_template)
    if(not iterator.group(1)):
        ErrorHandling.error_handling_format("No iterator found")

    iterator = "$" + iterator.group(1) + "$"

    if (dash_obj['total_segments'] != None):
        for fragment_num in range(dash_obj['start_number'], dash_obj['start_number'] + dash_obj['total_segments']):
            num += 1

            init = segment_template.replace(iterator, str(fragment_num))

            print("Extracting File:", init)
            MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], init, init)
    else:
        fragment_status = True
        current_fragment = dash_obj['start_number']
        while fragment_status:
            num += 1
            init = segment_template.replace(iterator, str(current_fragment))

            print("Extracting File:", init)
            fragment_status = MediaTransfer.extract_media_into_folder(dash_obj['manifest_root'], init, init)
            current_fragment = current_fragment + 1
