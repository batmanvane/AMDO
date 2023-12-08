#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf // Robert Flassig

import FINE as fn
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate
from getPVPowerprofile import getPVPowerProfile, calculate_moduleRowSpacing, plotSolarElevation


def energySystemsStats(tilt=20, azimuth=180, longitude=13.5, latitude=52.5, maxCapacityPV=100, fixCapacityPV=None,
                         maxCapacityST=100, fixCapacityST=5,
                         start=2014, end=2014, investPerCapacityPV=800, investPerCapacityST=700, relEmissionCosts=50,
                         scale_sink=1, module_width=1.5, moduleRowSpacing=3):
    """
   Calculates the statistics of an energy system model based on the given parameters.

   Args:
       tilt (int, optional): Tilt angle of the PV panels in degrees. Defaults to 20.
       azimuth (int, optional): Azimuth angle of the PV panels in degrees. Defaults to 180.
       longitude (float, optional): Longitude of the location. Defaults to 13.5.
       latitude (float, optional): Latitude of the location. Defaults to 52.5.
       maxCapacityPV (int, optional): Maximum capacity of PV panels in kW. Defaults to 100.
       fixCapacityPV (int, optional): Fixed capacity of PV panels in kW. Defaults to None.
       maxCapacityST (int, optional): Maximum capacity of storage in kW. Defaults to 100.
       fixCapacityST (int, optional): Fixed capacity of storage in kW. Defaults to 5.
       start (int, optional): Start year of the simulation. Defaults to 2014.
       end (int, optional): End year of the simulation. Defaults to 2014.
       investPerCapacityPV (int, optional): Investment cost per capacity of PV panels in Euro. Defaults to 800.
       investPerCapacityST (int, optional): Investment cost per capacity of storage in Euro. Defaults to 700.
       relEmissionCosts (int, optional): Relative emission costs in Euro per ton of CO2 equivalent. Defaults to 50.
       scale_sink (int, optional): Scaling factor for the electricity load demand profile. Defaults to 1.
       module_width (float, optional): Width of the PV module in m. Defaults to 1.5m for 1 module row.
       moduleRowSpacing (int, optional): Spacing between the PV module rows in m. Defaults to 3
   Returns:
   - Dictionary containing the following variables:
       - 'df_transposed': Transposed DataFrame for tabular view.
       - 'srcSnkSummary': Summary for source and sink.
       - 'convSummary': Conversion summary.
       - 'storSummary': Storage summary.
       - 'esM': Energy system model.
       - 'data': Original data.
       - 'alignmentPV': PV alignment result.
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
    esM = fn.EnergySystemModel(locations=locations,
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
    dataPVgis, data = getPVPowerProfile(latitude, longitude, start, end, surface_tilt=tilt,
                                           surface_azimuth=azimuth)
    dataPVgis.rename("location01", inplace=True)

    # Filter for December 21st
    december_21_data = data[(data.index.month == 12) & (data.index.day == 21)]

    # Filter for June 21st
    june_21_data = data[(data.index.month == 6) & (data.index.day == 21)]

    alignmentPVlow = calculate_moduleRowSpacing(december_21_data, module_width=module_width,
                                                  moduleRowSpacing=moduleRowSpacing)
    alignmentPVHigh = calculate_moduleRowSpacing(june_21_data, module_width=module_width,
                                                   moduleRowSpacing=moduleRowSpacing)
    dampingLow = alignmentPVlow["damping"]
    dampingHigh = alignmentPVHigh["damping"]

    print(dampingLow, dampingHigh)
    dataPVgis = dataPVgis * (1 - (dampingLow + dampingHigh) / 2)

    # Multiply entries by damping if solar_elevation is smaller than elevarionearly
    # dataPVgis['solar_elevation'] = dataPVgis.apply(
    #    lambda x: x['solar_elevation'] * damping if x['solar_elevation'] < alignmentPV["elevationAngleTimeEarly"] else x['solar_elevation'])
    # Multiply entries by Damping if solar_elevation is smaller than elevarionearly
    # models shadowing effects of PV panels
    # dataPVgisDamp = dataPVgis * np.where(data['solar_elevation'] < alignmentPV["elevationAngleTimeEarly"], 1 - 0.5, 1)
    # plt.plot(dataPVgis, label='Original dataPVgis')
    # plt.plot(dataPVgisDamp, label='Modified dataPVgisdamp')
    #                                 1)

    # # Adding labels and title
    # plt.xlabel('X-axis Label')
    # plt.ylabel('Y-axis Label')
    # plt.title('Comparison of Original and Modified DataPVgis')

    ## Display legend
    # plt.legend()
    # plt.savefig('resultDamping.pdf')
    # # Show the plot
    # plt.show()

    # plotSolarElevation(data)
    # dataplot= data
    # dataplot['solar_elevation']=dataplot['solar_elevation'] * np.where(data['solar_elevation'] < alignmentPV["elevationAngleTimeEarly"], damping, 1)
    # plotSolarElevation(dataplot)

    esM.add(fn.Source(esM=esM,
                      name='PV',
                      commodity=source_2,
                      hasCapacityVariable=True,
                      capacityFix=fixCapacityPV * module_width / 1.5,  # minimal capacity to be installed
                      capacityMax=maxCapacityPV * module_width / 1.5,  # maximal possible capacity
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
    esM.optimize(timeSeriesAggregation=True, solver='GLPK')

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
    tableview = pd.DataFrame(dataprint)
    # Transpose the DataFrame
    tableviewTransposed = tableview.T
    # Format the DataFrame as a table
    # table: str = tabulate(tableviewTransposed, headers='keys', tablefmt='psql', showindex=True)

    # Display the table
    # print(table)

    ## Export results to Excel
    [esM.getOptimizationSummary("SourceSinkModel", outputLevel=1).to_excel("Results/SourceSinkModel.xlsx"), ]
    [esM.getOptimizationSummary("StorageModel", outputLevel=1).to_excel("Results/StorageModel.xlsx"), ]
    [esM.getOptimizationSummary("ConversionModel", outputLevel=1).to_excel("Results/ConversionModel.xlsx"), ]
    tableviewTransposed.to_excel("Results/Summary.xlsx")

    ## Export results to CSV
    esM.getOptimizationSummary("SourceSinkModel", outputLevel=1).to_csv("Results/SourceSinkModel.csv", )
    esM.getOptimizationSummary("StorageModel", outputLevel=1).to_csv("Results/StorageModel.csv", )
    esM.getOptimizationSummary("ConversionModel", outputLevel=1).to_csv("Results/ConversionModel.csv", )
    tableviewTransposed.to_csv("Results/Summary.csv", )

    # Create a dictionary to store the results
    results = {
        'tableview': tableviewTransposed,
        'srcSnkSummary': srcSnkSummary,  # Replace None with the actual srcSnkSummary calculation
        'convSummary': convSummary,  # Replace None with the actual convSummary calculation
        'storSummary': storSummary,  # Replace None with the actual storSummary calculation
        'esM': esM,  # Replace None with the actual esM calculation
        'data': data,
        'alignmentPVlow': alignmentPVlow,  # Store areaUsage as alignmentPV for demonstration purposes
        'alignmentPVHigh': alignmentPVHigh  # Store areaUsage as alignmentPV for demonstration purposes
    }

    return results

if __name__ == "__main__":
    # tilt = 20
    # azimuth = 110
    # modulRowSpacing = 3
    # storage = 5
    #
    # energySystemsStats(tilt=tilt, azimuth=azimuth, fixCapacityST=storage, maxCapacityST=storage, fixCapacityPV=100,
    #                      maxCapacityPV=100, scale_sink=10,
    #                      module_width=1.5, moduleRowSpacing=modulRowSpacing)
    #
    from deap import base, creator, tools, algorithms
    from concurrent.futures import ThreadPoolExecutor
    import concurrent.futures
    import matplotlib.pyplot as plt

    def multi_objective_function(params):
        try:
            tilt, azimuth, modulRowSpacing, storage, moduleWidth = params
            result = energySystemsStats(tilt=tilt, azimuth=azimuth, fixCapacityST=storage,maxCapacityST=storage,fixCapacityPV=100, maxCapacityPV=100,
                                          scale_sink=10, module_width=moduleWidth, moduleRowSpacing=modulRowSpacing)

            # Minimize both TAC and CO2
            objectiveTAC = result['tableview'].loc['TAC'].values[0]
            objective_CO2 = result['tableview'].loc['operationTotCO2'].values[0]
            objectiveSelfSufficiency = result['tableview'].loc['selfsufficiency'].values[0]
            objectiveSelfConsumption = result['tableview'].loc['selfconsumption'].values[0]
            return [objectiveTAC, -objectiveSelfSufficiency]
        except Exception as e:
            print(e)
            return [np.inf, np.inf]

    def feasible(individual):
        """Feasibility function for the individual. Returns True if feasible, False otherwise."""
        if 1 < individual[0] < 85:
            if 30 < individual[1] < 330:
                if 0.5 < individual[2] < 10:
                    if 1 < individual[3] < 100:
                        if 1.5 < individual[4] < 4:
                            return True
        return False

        # Define the NSGA-II algorithm parameters
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))  # Minimize both objectives
    creator.create("Individual", list, fitness=creator.FitnessMulti)

    toolbox = base.Toolbox()
    toolbox.register("attr_float", np.random.uniform, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=5)
    # Define the box constraints for each variable
    low_bounds = [1, 30, 0.5, 1, 1.5]  # tilt, azimuth, modulRowSpacing, minStorage, moduleWidth
    up_bounds = [85, 330, 10, 100, 4]  # tilt, azimuth, modulRowSpacing, minStorage, moduleWidth
    toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=low_bounds, up=up_bounds, eta=15)
    toolbox.register("mutate", tools.mutPolynomialBounded,indpb=0.2, low=low_bounds, up=up_bounds, eta=20)

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("select", tools.selNSGA2)
    toolbox.register("evaluate", multi_objective_function)
    toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 1e9))


    def evaluate_parallel(individual):
        return multi_objective_function(individual),

        # Number of generations and population size (adjust as needed)
    ngen = 50
    pop_size = 20

    # Create an initial population
    population = toolbox.population(n=pop_size)

    # Use ThreadPoolExecutor for parallel evaluation of individuals
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(toolbox.evaluate, ind): ind for ind in population}
        for future in concurrent.futures.as_completed(futures):
            ind = futures[future]
            try:
                fitness_values = future.result()
                ind.fitness.values = fitness_values
            except Exception as e:
                print(f"Error in evaluating individual {ind}: {e}")

    # Use eaMuPlusLambda without the evaluate keyword
    algorithms.eaMuPlusLambda(population, toolbox, mu=pop_size, lambda_=2 * pop_size, cxpb=0.7, mutpb=0.2, ngen=ngen,
                              stats=None, halloffame=None, verbose=True)

    # Extracting Pareto front (non-dominated solutions)
    pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]

    # Displaying the Pareto front solutions
    print("Pareto Front Solutions:")
    for ind in pareto_front:
        print("Tilt:", ind[0], "Azimuth:", ind[1], "ModulRowSpacing:", ind[2], "Storage:", ind[3], "ModuleWidth:", ind[4])
        print("Objectives (TAC, Selfsufficiency):", multi_objective_function(ind))
        print("---")

    # Extracting all solutions
    all_solutions = np.array([ind.fitness.values for ind in population])

    # Scatter plot of all solutions
    plt.scatter(all_solutions[:, 0], -all_solutions[:, 1], label='All Solutions', alpha=0.5)

    # Highlight Pareto front solutions
    pareto_solutions = np.array([ind.fitness.values for ind in pareto_front])
    plt.scatter(pareto_solutions[:, 0], -pareto_solutions[:, 1], label='Pareto Front', color='red')

    # Set x-axis to logarithmic scale
    plt.xscale('log')

    plt.xlabel('TAC')
    plt.ylabel('Selfsufficiency')
    plt.title('Scatter Plot of All Solutions')
    plt.legend()

    # Save the plot as a PDF file
    plt.savefig('resultLastGeneration.pdf')

    plt.show()
