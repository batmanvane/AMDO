#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf

# Energiesystem:
# sink_1:      electricity
# source_1:     electricityImport
# source_2:     electricityPV
# conversion_source_1:  commodity_1     -->
# conversion_1:  electricityImport    -->     electricity
# conversion_2:  electricityPV        -->     electricity





import FINE as fn
import pandas as pd


## Aufbau EMS

locations = {'location01'}

commodityUnitDict = {'source_1_commodity': 'kW_el',
                    'source_1_splitted_conversion_1': 'kW_el',
                    'conversion_1':"kW_el",
                    'sink_1_conversion' :"kW_el",
                    'sink_1_commodity' : "kW_el"
                     }

commodities = {'source_1_commodity',
                'source_1_splitted_conversion_1',
               'conversion_1',
               'conversion_1_input',
                'conversion_1_output',
                'sink_1_conversion',
                'sink_1_commodity'
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


## sources

#source_1
esM.add(fn.Source(esM=esM,
                  name='source_1',
                  commodity='source_1_commodity',
                  hasCapacityVariable=False,
                  commodityCost=0.35
                  )
        )


## Conversions

#source_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_1_splitted_conversion_1': 1},
                      hasCapacityVariable=False))

#splitted_conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='source_1_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_splitted_conversion_1': -1, 'conversion_1': 1},
                      hasCapacityVariable=False))

#conversion_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_1': -1, "sink_1_conversion": 1},
                      hasCapacityVariable=False))



#sink_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='sink_1_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'sink_1_conversion': -1, 'sink_1_commodity': 1},
                      hasCapacityVariable=False))



##results

esM.cluster(numberOfTypicalPeriods=7)
esM.optimize(timeSeriesAggregation=True, solver='gurobi')



# 6. Results
srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
print(srcSnkSummary)
convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
print(convSummary)