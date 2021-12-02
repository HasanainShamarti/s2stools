import xarray as xr
import numpy as np
from tqdm import tqdm
from ._process_events import *

def composite_from_eventlist(event_list, data):
    event_comp = []
    missing_reftime_keys = []

    for event in tqdm(event_list, desc="Opening Events"):
        central_day = np.timedelta64(pd.Timedelta(event["leadtime"]))
        if np.datetime64(event["fc"]["reftime"]) in data.reftime.values:
            forecast = data.sel(
                reftime=event["fc"]["reftime"],
                hc_year=event["fc"]["hc_year"],
                number=event["fc"]["number"],
            )
            event_comp.append(
                forecast.assign_coords(
                    leadtime=data.leadtime - central_day
                ).rename(leadtime="lagtime")
            )
        elif event["fc"]["reftime"] in missing_reftime_keys:
            continue
        else:
            missing_reftime_keys.append(event["fc"]["reftime"])
            print(
                "KeyError Warning: reftime {} not in data".format(
                    event["fc"]["reftime"]
                )
            )

    event_comp = xr.concat(event_comp, dim="i")

    return event_comp.assign_coords(i=event_comp.i)


def composite_from_json(path, data):
    event_list = eventlist_from_json(path)
    composite = composite_from_eventlist(event_list, data)
    return composite


