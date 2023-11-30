#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf

import FINE as fn
import pandas as pd

# Energiesystem:
sink_1 = "sink_1_commodity"
source_1 = "source_1_commodity"
source_2 = "source_2_commodity"
storage_1 = "storage_1_commodity"
conversion_1 =["source_1_commodity","sink_1_commodity"]
conversion_2 =["source_2_commodity","sink_1_commodity"]

## Aufbau EMS

locations = {'location01'}

commodityUnitDict = {'source_1_commodity': 'kW_el',
                    'source_1_splitted_conversion_commodity_1': 'kW_el',
                    'conversion_1':"kW_el",
                     'conversion_2': "kW_el",
                    'source_2_commodity': 'kW_el',
                    'source_2_splitted_conversion_commodity_1': 'kW_el',
                    'sink_1_conversion' :"kW_el",
                    'sink_1_commodity' : "kW_el",
                    "storage_1_commodity" : "kW_el",
                    "storage_1_input_conversion_commodity" : "kW_el",
                    'storage_1_splitted_conversion_commodity_1': 'kW_el',

                     "conversion_3": "kW_el",
                     "conversion_4": "kW_el",
                     "conversion_5": "kW_el",
                     "conversion_6": "kW_el",
                     }

commodities = {'source_1_commodity',
                'source_1_splitted_conversion_commodity_1',
                'conversion_1',
               'conversion_2',
                'sink_1_conversion',
                'sink_1_commodity',
                'source_2_commodity',
                'source_2_splitted_conversion_commodity_1',
               "storage_1_commodity",
               "storage_1_input_conversion_commodity",
               'storage_1_splitted_conversion_commodity_1',
               'conversion_3',
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


#source_2
investPerCapacity=1400
esM.add(fn.Source(esM=esM,
                  name='source_2',
                  commodity=source_2,
                  hasCapacityVariable=True,
                  #capacityMax= 5,
                  operationRateMax=pd.read_excel("DataForExample/PV_1.xlsx"),
                  investPerCapacity=investPerCapacity,
                  opexPerCapacity= investPerCapacity * 0.015,
                  interestRate=0.05,
                  economicLifetime=25))

## storage

#storage_1
maxCapacity = 10
investPerCapacity = 1000
fixCapacity = 5
esM.add(fn.Storage(esM=esM,
                   name='storage_1',
                   commodity=storage_1,
                   hasCapacityVariable=True,
                   capacityMax= maxCapacity,
                   capacityFix= fixCapacity,
                   chargeEfficiency=0.95,  # Verhältnis von eingehender commodity zu gespeicherter commodity
                   dischargeEfficiency=0.95,
                   chargeRate=750 / maxCapacity,  # 750 kW Ladeleistung bezogen auf max. Kapazität
                   dischargeRate=750 / maxCapacity,  # 750 kW Entladeleistung bezogen auf max. Kapazität
                   selfDischarge=0.00003,  # Selbstentladung pro h (entspricht 0,5 %/Woche)
                   cyclicLifetime=7000,
                   stateOfChargeMin=0.1,  # min. Entladetiefe = 10%
                   investPerCapacity=investPerCapacity,
                   opexPerCapacity=investPerCapacity * 0.005,  # sehr geringe bis keine Betriebskosten
                   economicLifetime=20,
                   interestRate=0.08))


## Conversions

#source_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_1_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_1_splitted_conversion_commodity_1': 1},
                      hasCapacityVariable=False))

#splitted_conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='source_1_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_splitted_conversion_commodity_1': -1, 'conversion_1': 1},
                      hasCapacityVariable=False))

#conversion_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_1': -1, 'sink_1_conversion': 1},
                      hasCapacityVariable=False))

#source_2_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_2_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_2_commodity': -1, 'source_2_splitted_conversion_commodity_1': 1},
                      hasCapacityVariable=False))

#source_2_splitted_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_2_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_2_splitted_conversion_commodity_1': -1, 'conversion_2': 1},
                      hasCapacityVariable=False))

#conversion_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_2',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_2': -1, "storage_1_input_conversion_commodity": 1},
                      hasCapacityVariable=False))

#storage_1_input_conversion
esM.add(fn.Conversion(esM=esM,
                      name='storage_1_input_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={"storage_1_input_conversion_commodity": -1, 'storage_1_commodity': 1},
                      hasCapacityVariable=False))

#storage_1_output_conversion
esM.add(fn.Conversion(esM=esM,
                      name='storage_1_output_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'storage_1_commodity': -1, 'storage_1_splitted_conversion_commodity_1': 1},
                      hasCapacityVariable=False))

#storage_1_splitted_conversion
esM.add(fn.Conversion(esM=esM,
                      name='storage_1_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'storage_1_splitted_conversion_commodity_1': -1, 'conversion_3': 1},
                      hasCapacityVariable=False))

#conversion_3
esM.add(fn.Conversion(esM=esM,
                      name='conversion_3',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_3': -1, 'sink_1_conversion': 1},
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
storSummary = esM.getOptimizationSummary("StorageModel", outputLevel=1)
print(storSummary)
convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
print(convSummary)
