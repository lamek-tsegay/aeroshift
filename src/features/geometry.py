# duration
# Accepts a single-flight dataframe, Sorts by time_s
# Computes: start_time, end_time, duration
# Returns the duration
def compute_duration(flight_df):
    # we want to return duration in seconds - To find duration we will subtract the max and min time
    # we will subtract time_s of (0) syn_00000 - (895) syn_00000 

    # make sure time is in order, earliest time first
    # loop through flight_df and if time is in wrong order thenn move it around until we reach the end.
    for t in flight_df["time_s"]:
        


# total_distance
# net_displacement
# efficiency