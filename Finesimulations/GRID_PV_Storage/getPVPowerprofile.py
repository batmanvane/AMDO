import numpy as np
import pvlib
import pandas as pd


def get_pv_power_profile(latitude: object = 52, longitude: object = 13.5, start: object = 2014, end: object = 2014,
                         surface_tilt: object = 20,
                         surface_azimuth: object = 180,f=0.3) -> object:
    """
    Fetches PV power profile data using the pvlib library.

    Parameters:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start (int or str): Start year or timestamp for the data range.
        end (int or str): End year or timestamp for the data range.
        surface_tilt (float): Tilt angle of the PV panels.
        surface_azimuth (float): Azimuth angle of the PV panels.
        f: area fraction (float, default: 0.3)

    Returns:
        pd.Series: PV power profile data.

    Note: API calls have a rate limit of 30 calls/second per IP address. Check: https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en

    """
    # Convert start and end years to timestamps
    start = pd.Timestamp(f'{start}-01-01')
    end = pd.Timestamp(f'{end}-12-31')

    # Call the get_pvgis_hourly function

    horizon=calculateHorizon(f=f,surface_tilt=surface_tilt)

    data: object

    data, _, _ = pvlib.iotools.get_pvgis_hourly(latitude=latitude,
                                                longitude=longitude,
                                                start=start,
                                                end=end,
                                                surface_tilt=surface_tilt,
                                                surface_azimuth=surface_azimuth,
                                                usehorizon=True,
                                                userhorizon=horizon,
                                                peakpower=1,  # peakpower (float, default: None) – Nominal power of PV
                                                # system in kW. Required if pvcalculation=True.
                                                pvtechchoice='crystSi',  # ({'crystSi', 'CIS', 'CdTe', 'Unknown'},
                                                # default: 'crystSi') – PV technology.
                                                mountingplace='free', # ({'free', 'building'}, default: free) – Type
                                                # of mounting for PV system. Options of ‘free’ for free-standing and
                                                # ‘building’ for building-integrated.
                                                loss=10,# Sum of PV system losses in percent. Required if pvcalculation=True
                                                trackingtype=0,
                                                pvcalculation=1,
                                                timeout=30)# Time in seconds to wait for server response before timeout
    dataP = data['P']
    dataP.reset_index(drop=True, inplace=True)
    return dataP / 1000, horizon  # return in kWh

def calculateHorizon(f=0.3,surface_tilt=30,azimuthSegments=20,surface_azimuth=180):
    """
    Calculates the horizon angle based on the given f and surface_tilt.

    Parameters:
        f (float): The f parameter.
        surface_tilt (float): Tilt angle of the PV panels.

    Returns:
        float: The horizon angle.

    """
    alpha = np.zeros(azimuthSegments)
    azimuthspan=np.arange(0,360,azimuthSegments)
    i=0
    for azimuth in azimuthspan:
        alpha[i]=np.arctan(f*np.sin(surface_tilt*np.pi/180)/(1-f*np.cos(surface_tilt*np.pi/180)))
        i=i+1
    alpha=alpha*180/np.pi
    return alpha

if __name__ == "__main__":
    power_profile = get_pv_power_profile()
    print(power_profile.head())
