import common
import datetime


while True:
    current_time = datetime.datetime.now().replace(microsecond=0)
    time_offset = common.calculate_time_offset()
    new_time = current_time - time_offset

    print "[System] Time:"
    print current_time
    print "[Server] Time:"
    print time_offset
    print ""
    print "[NEW OFFSET]:"
    print new_time
