#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf

import FINE as fn
import pandas as pd

# Energiesystem:
sink_1 = "sink_1_commodity"
environment = "environment_commodity"
source_1 = "source_1_commodity"
source_2 = "source_2_commodity"
conversion_1 =["source_1_commodity","sink_1_commodity"]
conversion_2 =["source_2_commodity","sink_1_commodity"]


## Aufbau EMS

locations = {'location01'}

commodityUnitDict = {'source_1_commodity': 'kW_el',
                    'source_1_splitted_conversion_commodity_1': 'kW_el',
                    'conversion_1':"kW_el",
                    'conversion_2':"kW_el",
                    'conversion_3' : "t_CO2e",
                    'sink_1_conversion' :"kW_el",
                    'sink_1_commodity' : "kW_el",
                    "environment_commodity" : "t_CO2e",
                    "environment_conversion" : "t_CO2e",
                    'source_1_splitted_conversion_commodity_2': "t_CO2e",

                     }

commodities = {'source_1_commodity',
                    'source_1_splitted_conversion_commodity_1',
                    'source_1_splitted_conversion_commodity_2',
                    'conversion_1',
                    'conversion_2',
                    'conversion_3',
                    'sink_1_conversion',
                    "sink_1_commodity",
                    "environment_commodity",
                    "environment_conversion"
               }


esM = fn.EnergySystemModel(locations={"location01"},
                            commodities=commodities,
                            numberOfTimeSteps=8760,
                            commodityUnitsDict=commodityUnitDict,
                            hoursPerTimeStep=1,
                            costUnit='1e Euro',
                            lengthUnit='km',
                            verboseLogLevel=0)


## Sinks

#sink_1
esM.add(fn.Sink(esM=esM,
                name='sink_1',
                commodity='sink_1_commodity',
                hasCapacityVariable=False,
                operationRateFix=pd.read_excel("DataForExample/sink_1.xlsx"),
                ),
        )

#environment
opexPerOperation = 50
esM.add(fn.Sink(esM=esM,
                name='environment',
                commodity=environment,
                hasCapacityVariable=False,
                opexPerOperation=opexPerOperation
                ),
        )


## sources

#source_1
esM.add(fn.Source(esM=esM,
                  name='source_1',
                  commodity=source_1,
                  hasCapacityVariable=False,
                  commodityCost=0.35
                  )
        )


## Conversions

#source_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_1_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_1_splitted_conversion_commodity_1': 1, 'source_1_splitted_conversion_commodity_2': 1 },
                      hasCapacityVariable=False))

#splitted_conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='source_1_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_splitted_conversion_commodity_1': -1, 'conversion_1': 1},
                      hasCapacityVariable=False))

#splitted_conversion_source_2
Wirkungsgrad = 0.3
esM.add(fn.Conversion(esM=esM,
                      name='source_1_splitted_conversion_2',
                      physicalUnit='t_CO2e',
                      commodityConversionFactors={'source_1_splitted_conversion_commodity_2': -1, 'conversion_2': Wirkungsgrad},
                      hasCapacityVariable=False))

#conversion_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_1': -1, 'sink_1_conversion': 1},
                      hasCapacityVariable=False))

#conversion_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_2',
                      physicalUnit='t_CO2e',
                      commodityConversionFactors={'conversion_2': -1, 'environment_conversion': 1},
                      hasCapacityVariable=False))



#sink_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='sink_1_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'sink_1_conversion': -1, 'sink_1_commodity': 1},
                      hasCapacityVariable=False))

#environment_conversion
esM.add(fn.Conversion(esM=esM,
                      name='environment_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'environment_conversion': -1, 'environment_commodity': 1},
                      hasCapacityVariable=False))



##results

esM.cluster(numberOfTypicalPeriods=7)
esM.optimize(timeSeriesAggregation=True, solver='gurobi')



# 6. Results
srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
print(srcSnkSummary)
convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
print(convSummary)