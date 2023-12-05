#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf // Robert Flassig

import FINE as fn
import pandas as pd
from pandas import Series
from tabulate import tabulate
from getPVPowerprofile import get_pv_power_profile


def energy_systems_stats(tilt=20, azimuth=180, longitude=13.5, latitude=52.5, maxCapacityPV=100, fixCapacityPV=None,
                         maxCapacityST=100, fixCapacityST=5,
                         start=2014, end=2014, investPerCapacityPV=800, investPerCapacityST=700, relEmissionCosts=50,
                         scale_sink=1,f=0.3):
    """
    input: tilt, azimuth, long, lat, maxCapacityPV, fixCapacityPV, maxCapacityST, fixCapacityST, investPerCapacityPV,
    investPerCapacityST, relEmissionCosts) returns stats at table
    """
    # Define Components of EnergySystemModel

    # 1. Define locations of the energy system model
    locations = {'location01'}
    # 2. Define commodities and units of commodities
    commodities = {'sink_1_commodity',
                   'source_1_commodity',
                   'source_2_commodity',
                   'storage_1_commodity',
                   'environment_commodity'
                   }
    commodityUnitDict = {'sink_1_commodity': 'kW_el',
                         'source_1_commodity': 'kW_el',
                         'source_2_commodity': 'kW_el',
                         'storage_1_commodity': 'kW_el',
                         'environment_commodity': 't_CO2e'
                         }
    # 3. Abbrevieate commodities
    sink_1 = "sink_1_commodity"  # electricity load demand profile
    source_1 = "source_1_commodity"  # Grid
    source_2 = "source_2_commodity"  # PV
    environment = "environment_commodity"  # CO2 in kg CO2 equivalent
    storage_1 = "storage_1_commodity"  # Storage, track Storage to sink_1

    # 4. Define the energy system model instance
    esM = fn.EnergySystemModel(locations={"location01"},
                               commodities=commodities,
                               numberOfTimeSteps=8760,
                               commodityUnitsDict=commodityUnitDict,
                               hoursPerTimeStep=1,
                               costUnit='1e Euro',
                               lengthUnit='km',
                               verboseLogLevel=0)

    ## Add Sinks
    # sink_1 Electricity load demand profile
    esM.add(fn.Sink(esM=esM,
                    name='sink_1',
                    commodity=sink_1,
                    hasCapacityVariable=False,
                    operationRateFix=pd.read_excel("DataForExample/sink_1.xlsx") * scale_sink,
                    ),
            )

    # environment
    relEmissionCosts = relEmissionCosts  # 50 Euro pro t CO2
    esM.add(fn.Sink(esM=esM,
                    name='environment',
                    commodity=environment,
                    hasCapacityVariable=False,
                    opexPerOperation=relEmissionCosts
                    ),
            )
    # spot market

    esM.add(fn.Sink(esM=esM,
                    name='spot',
                    commodity=source_2,
                    hasCapacityVariable=False,
                    commodityRevenue=0.05
                    ),
            )
    ## Add sources
    # source_1 as Grid
    esM.add(fn.Source(esM=esM,
                      name='GRID',
                      commodity=source_1,
                      hasCapacityVariable=False,
                      commodityCost=0.35
                      )
            )
    # source_2 as PV
    # load PV data
    # dataPV = pd.read_excel("DataForExample/PV_1.xlsx")
    dataPVgis, horizon = get_pv_power_profile(latitude, longitude, start, end, surface_tilt=tilt,
                                             surface_azimuth=azimuth,f=f)
    dataPVgis.rename("location01", inplace=True)
    maxCapacityPV=maxCapacityPV*f
    esM.add(fn.Source(esM=esM,
                      name='PV',
                      commodity=source_2,
                      hasCapacityVariable=True,
                      capacityFix=fixCapacityPV,  # minimal capacity to be installed
                      capacityMax=maxCapacityPV,  # maximal possible capacity
                      operationRateMax=dataPVgis,
                      investPerCapacity=investPerCapacityPV,
                      opexPerCapacity=investPerCapacityPV * 0.015,
                      interestRate=0.05,
                      economicLifetime=25))

    ## Add storages
    # storage_1
    esM.add(fn.Storage(esM=esM,
                       name='STORAGE',
                       commodity=storage_1,
                       hasCapacityVariable=True,
                       capacityFix=fixCapacityST,  # minimal capacity to be installed
                       capacityMax=maxCapacityST,  # maximal possible capacity
                       chargeEfficiency=0.95,  # Verhältnis von eingehender commodity zu gespeicherter commodity
                       dischargeEfficiency=0.95,  # Verhältnis von gespeicherter commodity zu ausgehender commodity
                       chargeRate=750 / maxCapacityST,  # 750 kW Ladeleistung bezogen auf max. Kapazität
                       dischargeRate=750 / maxCapacityST,  # 750 kW Entladeleistung bezogen auf max. Kapazität
                       selfDischarge=0.00003,  # Selbstentladung pro h (entspricht 0,5 %/Woche)
                       cyclicLifetime=7000,  # maximale Ladezyklen
                       stateOfChargeMin=0.1,  # min. Entladetiefe = 10%
                       investPerCapacity=investPerCapacityST,  # Investitionskosten pro Kapazität
                       opexPerCapacity=investPerCapacityST * 0.005,
                       # sehr geringe bis keine Betriebskosten por Kapazität
                       economicLifetime=20,  # Lebenszeit
                       interestRate=0.08))

    ##Add Conversions
    # conversion_source_1
    esM.add(fn.Conversion(esM=esM,
                          name='conversion_1',
                          physicalUnit='kW_el',
                          commodityConversionFactors={source_1: -1, sink_1: 1, environment: 0.3},
                          hasCapacityVariable=False))

    # conversion source_2 to storage
    esM.add(fn.Conversion(esM=esM,
                          name='conversion_2',
                          physicalUnit='kW_el',
                          commodityConversionFactors={source_2: -1, storage_1: 1, environment: 0.01},
                          hasCapacityVariable=False))

    # conversion storage to sink_1
    esM.add(fn.Conversion(esM=esM,
                          name='conversion_3',
                          physicalUnit='kW_el',
                          commodityConversionFactors={storage_1: -1, sink_1: 1, environment: 0.02},
                          hasCapacityVariable=False))

    ##Generate Results
    # 5. Optimize the energy system model
    # prepare optimization by aggregating time series data
    # Temporally cluster the time series data of all components
    # considered in the EnergySystemModel instance and then stores
    # the clustered data in the respective components. For this, the time series data
    # is broken down into an ordered sequence of periods (e.g. 365 days) and
    # to each period a typical period (e.g. 7 typical days with 24 hours) is assigned.
    esM.aggregateTemporally(numberOfTypicalPeriods=7)
    # set optimizer and solver (GLPK, CPLEX, GUROBI)
    esM.optimize(timeSeriesAggregation=True, solver='glpk')

    ## Get the optimization summary
    # 6. Results
    ## Prepare results for export
    # source sink summary
    srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
    # conversion summary
    convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
    # storage summary
    storSummary = esM.getOptimizationSummary("StorageModel", outputLevel=1)
    # extract optimal capacity of PV source
    capacityPVOptimum = srcSnkSummary['location01'].loc[('PV', 'capacity', '[kW_el]')]
    # extract optimal capacity of storage
    capacityStorageOptimum = storSummary['location01'].loc[('STORAGE', 'capacity', '[kW_el*h]')]

    # calculate maximal output of optimal PV source
    operationRateMaxPV = dataPVgis * capacityPVOptimum

    # actual total operation, charge and discharge
    operationTotOptimumGrid = srcSnkSummary['location01'].loc[('GRID', 'operation', '[kW_el*h/a]')]
    operationTotOptimumPV = srcSnkSummary['location01'].loc[('PV', 'operation', '[kW_el*h/a]')]
    operationTotOptimumStorageCharge = storSummary['location01'].loc[('STORAGE', 'operationCharge', '[kW_el*h/a]')]
    operationTotOptimumStorageDischarge = storSummary['location01'].loc[
        ('STORAGE', 'operationDischarge', '[kW_el*h/a]')]
    operationTotCO2 = srcSnkSummary['location01'].loc[('environment', 'operation', '[t_CO2e*h/a]')]
    operationTotSink = srcSnkSummary['location01'].loc[('sink_1', 'operation', '[kW_el*h/a]')]
    # calculate selfconsumption and selfsufficiency
    selfconsumption = (
                              operationTotOptimumPV - operationTotOptimumStorageCharge + operationTotOptimumStorageDischarge) / (
                          operationRateMaxPV.cumsum().iloc[-1])

    selfsufficiency = (
                              operationTotOptimumPV - operationTotOptimumStorageCharge + operationTotOptimumStorageDischarge) / (
                              operationTotOptimumGrid + operationTotOptimumPV + operationTotOptimumStorageDischarge)

    # calculate costs
    TACPV = srcSnkSummary['location01'].loc[('PV', 'TAC', '[1e Euro/a]')]
    TACSTORAGE = storSummary['location01'].loc[('STORAGE', 'TAC', '[1e Euro/a]')]
    TACGRID = srcSnkSummary['location01'].loc[('GRID', 'TAC', '[1e Euro/a]')]
    TACENV = srcSnkSummary['location01'].loc[('environment', 'TAC', '[1e Euro/a]')]
    TAC = TACPV + TACSTORAGE + TACGRID + TACENV
    try:
        LCOEPV = TACPV / (operationTotOptimumPV)
    except ZeroDivisionError:
        print("Error: Division by zero in operationTotOptimumPV!")
        LCOEPV = 0

    try:
        LCOESTORAGE = TACSTORAGE / (operationTotOptimumStorageDischarge)
    except ZeroDivisionError:
        print("Error: Division by zero in operationTotOptimumStorageDischarge!")
        LCOESTORAGE = 0

    try:
        LCOEGRID = TACGRID / (operationTotOptimumGrid)
    except ZeroDivisionError:
        print("Error: Division by zero in operationTotOptimumGrid!")
        LCOEGRID = 0

    # print((TAC,operationTotCO2))

    # Create a dictionary with variable names and their corresponding values
    dataprint = {
        'capacityPVOptimum': [capacityPVOptimum],
        'capacityStorageOptimum': [capacityStorageOptimum],
        'operationTotOptimumGrid': [operationTotOptimumGrid],
        'operationTotOptimumPV': [operationTotOptimumPV],
        'operationTotOptimumStorageCharge': [operationTotOptimumStorageCharge],
        'operationTotOptimumStorageDischarge': [operationTotOptimumStorageDischarge],
        'operationTotSink': [operationTotSink],
        'operationTotCO2': [operationTotCO2],
        'TAC': [TAC],
        'LCOEPV': [LCOEPV],
        'LCOESTORAGE': [LCOESTORAGE],
        'LCOEGRID': [LCOEGRID],
        'selfconsumption': [selfconsumption],
        'selfsufficiency': [selfsufficiency]
    }

    # Create a pandas DataFrame from the dictionary
    df = pd.DataFrame(dataprint)
    # Transpose the DataFrame
    df_transposed = df.T
    # Format the DataFrame as a table
    table: str = tabulate(df_transposed, headers='keys', tablefmt='psql', showindex=True)

    # Display the table
    # print(table)

    ## Export results
    [esM.getOptimizationSummary("SourceSinkModel", outputLevel=1).to_excel("Results/SourceSinkModel.xlsx"), ]
    [esM.getOptimizationSummary("StorageModel", outputLevel=1).to_excel("Results/StorageModel.xlsx"), ]
    [esM.getOptimizationSummary("ConversionModel", outputLevel=1).to_excel("Results/ConversionModel.xlsx"), ]
    df_transposed.to_excel("Results/Summary.xlsx")

    return df_transposed, srcSnkSummary, convSummary, storSummary, esM, horizon


if __name__ == "__main__":

    result, _, _, _, _, horizon = energy_systems_stats(tilt=7, azimuth=180, maxCapacityPV=30, scale_sink=10,f=.9)
    print(tabulate(result, headers='keys', tablefmt='psql', showindex=True))
    print(horizon)