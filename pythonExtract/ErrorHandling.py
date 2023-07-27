
# will improve this later, for now it just formats in the future it should do proper error handling

def error_handling_format(error_handling, should_exit=True):
    line_length = len(error_handling) + 4

    print(" ")
    print("ERROR MESSAGE".center(line_length, " "))
    print("#" * line_length)
    print("#", error_handling.center(line_length - 4), "#")
    print("#" * line_length)
    print(" ")
    
    if(should_exit):
        exit(1)