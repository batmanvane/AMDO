import numpy as np
import pvlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def get_pv_power_profile(latitude: object = 52, longitude: object = 13.5, start: object = 2014, end: object = 2014,
                         surface_tilt: object = 20,
                         surface_azimuth: object = 180) -> object:
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

    data: object

    data, _, _ = pvlib.iotools.get_pvgis_hourly(latitude=latitude,
                                                longitude=longitude,
                                                start=start,
                                                end=end,
                                                surface_tilt=surface_tilt,
                                                surface_azimuth=surface_azimuth,
                                                usehorizon=True,
                                                userhorizon=None,
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
    return dataP / 1000, data  # return in kWh


def plot_solar_elevation(data):

    """
    Plot solar elevation for December 21st and June 21st.

    Parameters:
    - data: DataFrame with a datetime-like index and solar elevation data.

    Returns:
    - None (displays the plot).
    """
    # Filter for December 21st
    december_21_data = data[(data.index.month == 12) & (data.index.day == 21)]

    # Filter for June 21st
    june_21_data = data[(data.index.month == 6) & (data.index.day == 21)]

    # Plot the data
    plt.plot(december_21_data.index.hour + december_21_data.index.minute / 60, december_21_data["solar_elevation"],
             label="Dec 21")
    plt.plot(june_21_data.index.hour + june_21_data.index.minute / 60, june_21_data["solar_elevation"], label="Jun 21")

    plt.xlabel("Time (hours)")
    plt.ylabel("Solar Elevation")
    plt.title("Solar Elevation on Dec 21 and Jun 21 (24-hour timescale)")
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_module_row_spacing(data, time1='09:00:00', time2='15:00:00', surface_tilt=30, module_width_D=2):
    """
    Calculate solar elevation angles at specified times and module row spacing.

    Parameters:
    - data: DataFrame with a datetime-like index and solar elevation data.
    - time1: First specified time (default: '09:00:00').
    - time2: Second specified time (default: '15:00:00').
    - surface_tilt: Surface tilt angle in degrees (default: 30).
    - module_width_D: Module width in the same unit as the surface_tilt (default: 1.5).

    Returns:
    - Dictionary containing elevation angles, module row spacing, and area usage.
    """
    # Ensure that the index is in datetime format
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("The DataFrame index should be in datetime format.")

    # Extract the time and solar elevation values
    time_values = data.index
    elevation_values = data["solar_elevation"].values

    # Convert specified times to datetime objects
    time1_dt = pd.to_datetime(time1).time()
    time2_dt = pd.to_datetime(time2).time()

    # Find the indices corresponding to the specified hours
    index_time1 = np.argmax(time_values.hour == time1_dt.hour)
    index_time2 = np.argmax(time_values.hour == time2_dt.hour)

    # Get elevation angles at specified times
    elevation_angle_time1 = elevation_values[index_time1]
    elevation_angle_time2 = elevation_values[index_time2]

    # Calculate Height_Difference
    height_difference = np.sin(np.radians(surface_tilt)) * module_width_D

    # Calculate Module_Row_Spacing_L using the maximum of the two elevation angles
    min_elevation_angle = max(elevation_angle_time1, elevation_angle_time2)
    module_row_spacing_L = height_difference / np.tan(np.radians(min_elevation_angle))

    # Calculate Area_Usage
    area_usage = module_width_D / module_row_spacing_L

    result = {
        'elevationAngleTimeEarly': elevation_angle_time1,
        'elevationAngleTimeLate': elevation_angle_time2,
        'moduleRowSpacingL': module_row_spacing_L,
        'areaUsage': area_usage
    }

    return result


if __name__ == "__main__":
    power_profile, data = get_pv_power_profile()
    plot_solar_elevation(data)
    result = calculate_module_row_spacing(data)
