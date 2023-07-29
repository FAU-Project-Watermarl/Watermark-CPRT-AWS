import subprocess
import re
import os
import time

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


# apply_uuid -> apply the uuid to a given id.
# Args:
# dash_obj, contains all the information about the parsed mpd
# quality id, the quality id.
# media type, either audio or video 
def apply_uuid(dash_obj, quality_id, media_type):
    print('''--------------- Applying uuid ---------------------
    ''')

    start_time = time.time()
    if(dash_obj["edge_case_base_url"]):
        setCprt = f'mp4tag --set cprt:S:{dash_obj["uuid_value"]} {quality_id} {quality_id}'
        subprocess.run(setCprt, shell=True)
    else:
        if(media_type == "video"):
            init_template = dash_obj["init_template_video"].replace('$RepresentationID$', str(quality_id))
        else:
            init_template = dash_obj["init_template_audio"].replace('$RepresentationID$', str(quality_id))
        print("Applying uuid to path:",init_template)
        
        if not os.path.exists(init_template):
            print("Uuid not applied, path not found")
            return

        setCprt = f'mp4tag --set cprt:S:{dash_obj["uuid_value"]} {init_template} {init_template}'
        subprocess.run(setCprt, shell=True)

    end_time = time.time()
    total_time_ms = int((end_time - start_time) * 1000)
    dash_obj['cprt_time_complexity'] =  dash_obj['cprt_time_complexity'] + (total_time_ms)

    print("Applied UUID:",  dash_obj['uuid_value'], " Time duration to apply UUID:", total_time_ms,"milliseconds")
