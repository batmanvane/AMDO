import pvlib
import pandas as pd

def get_pv_power_profile(latitude=52, longitude=13.5, start=2014, end=2014, surface_tilt=20, surface_azimuth=180):
    """
    Fetches PV power profile data using the pvlib library.

    Parameters:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start (int or str): Start year or timestamp for the data range.
        end (int or str): End year or timestamp for the data range.
        surface_tilt (float): Tilt angle of the PV panels.
        surface_azimuth (float): Azimuth angle of the PV panels.

    Returns:
        pd.Series: PV power profile data.
    """
    # Convert start and end years to timestamps
    start = pd.Timestamp(f'{start}-01-01')
    end = pd.Timestamp(f'{end}-12-31')

    # Call the get_pvgis_hourly function
    data, _, _ = pvlib.iotools.get_pvgis_hourly(latitude=latitude,
                                                 longitude=longitude,
                                                 start=start,
                                                 end=end,
                                                 surface_tilt=surface_tilt,
                                                 surface_azimuth=surface_azimuth,
                                                 peakpower=1,
                                                 pvcalculation=1)


    dataPowerHour=data['P'].reset_index(drop=True)
    return dataPowerHour


if __name__ == "__main__":
    power_profile = get_pv_power_profile()
    print(power_profile.head())
