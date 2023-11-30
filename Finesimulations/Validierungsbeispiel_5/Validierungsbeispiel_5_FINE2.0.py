#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf

import FINE as fn
import pandas as pd

# Energiesystem:
sink_1 = "sink_1_commodity"
sink_2 = "sink_2_commodity"
environment = "environment_commodity"
source_1 = "source_1_commodity"
source_2 = "source_2_commodity"
source_3 = "source_3_commodity"
heatpump = "electricityWP_commodity"
storage_1 = "storage_commodity"


## Aufbau EMS

locations = {'location01'}

commodityUnitDict = {'sink_1_commodity': 'kW_el',
                     'sink_2_commodity': 'kW_th',
                     "environment_commodity" : "t_CO2e",
                     'source_1_commodity': 'kW_el',
                     'source_2_commodity': 'kW_el',
                     'source_3_commodity': 'kW_el',
                     "storage_commodity" : "kW_el",
                     "electricityWP_commodity" : "kW_th",
                     'sink_1_conversion': "kW_el",
                     'sink_2_conversion': "kW_el",
                     "environment_conversion": "t_CO2e",
                     "storage_1_input_conversion_commodity": "kW_el",
                     'storage_1_splitted_conversion_commodity_1': 'kW_el',
                     "electricityWP_input": "kW_el",
                     'electricityWP_splitted_conversion_commodity_1': 'kW_th',
                     'source_1_splitted_conversion_commodity_1': 'kW_el',
                     'source_1_splitted_conversion_commodity_2': 'kW_el',
                     'source_1_splitted_conversion_commodity_3': 'kW_el',
                     'source_2_splitted_conversion_commodity_1': 'kW_el',
                     'source_2_splitted_conversion_commodity_2': 'kW_el',
                     'source_3_splitted_conversion_commodity_1': 'kW_el',
                     'source_3_splitted_conversion_commodity_2': 'kW_el',
                     "conversion_1": "kW_el",
                     "conversion_2": "kW_el",
                     "conversion_3": "kW_el",
                     "conversion_4": "kW_el",
                     "conversion_5": "kW_el",
                     "conversion_6": "kW_el",
                     }

commodities = {'sink_1_commodity',
                     'sink_2_commodity',
                     "environment_commodity",
                     'source_1_commodity',
                     'source_2_commodity',
                     'source_3_commodity',
                     "storage_commodity" ,
                     "electricityWP_commodity",
                     'sink_1_conversion',
                     'sink_2_conversion',
                     "environment_conversion",
                     "storage_1_input_conversion_commodity",
                     'storage_1_splitted_conversion_commodity_1',
                     "electricityWP_input",
                     'electricityWP_splitted_conversion_commodity_1',
                     'source_1_splitted_conversion_commodity_1',
                     'source_1_splitted_conversion_commodity_2',
                     'source_1_splitted_conversion_commodity_3',
                     'source_2_splitted_conversion_commodity_1',
                     'source_2_splitted_conversion_commodity_2',
                     'source_3_splitted_conversion_commodity_1',
                     'source_3_splitted_conversion_commodity_2',
               "conversion_1",
               "conversion_2",
               "conversion_3",
               "conversion_4",
               "conversion_5",
               "conversion_6",
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

#sink_2
esM.add(fn.Sink(esM=esM,
                name='sink_2',
                commodity='sink_2_commodity',
                hasCapacityVariable=False,
                operationRateFix=pd.read_excel("DataForExample/sink_2.xlsx"),
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

#source_3
esM.add(fn.Source(esM=esM,
                  name='source_3',
                  commodity=source_3,
                  hasCapacityVariable=True,
                  commodityCost=0.12,
                  operationRateMax=pd.read_excel("DataForExample/WP.xlsx"),
                  ))

#storage
maxCapacity = 10
investPerCapacity = 1000
fixCapacity = 5
esM.add(fn.Storage(esM=esM,
                   name='storage_1',
                   commodity=storage_1,
                   hasCapacityVariable=True,
                   capacityFix= fixCapacity,                    # gezwungene zu installierende Kapazität
                   capacityMax= maxCapacity,                    # maximal installierbare Kapazität
                   chargeEfficiency=0.95,                       # Verhältnis von eingehender commodity zu gespeicherter commodity
                   dischargeEfficiency=0.95,                    # Verhältnis von gespeicherter commodity zu ausgehender commodity
                   chargeRate=750 / maxCapacity,                # 750 kW Ladeleistung bezogen auf max. Kapazität
                   dischargeRate=750 / maxCapacity,             # 750 kW Entladeleistung bezogen auf max. Kapazität
                   selfDischarge=0.00003,                       # Selbstentladung pro h (entspricht 0,5 %/Woche)
                   cyclicLifetime=7000,                         # maximale Ladezyklen
                   stateOfChargeMin=0.1,                        # min. Entladetiefe = 10%
                   investPerCapacity=investPerCapacity,         # Investitionskosten pro Kapazität
                   opexPerCapacity=investPerCapacity * 0.005,   # sehr geringe bis keine Betriebskosten por Kapazität
                   economicLifetime=20,                         # Lebenszeit
                   interestRate=0.08))

## Conversions

#heatpump

esM.add(fn.Conversion(esM=esM,
                      name=heatpump,
                      physicalUnit='kW_th',
                      commodityConversionFactors={heatpump:-1, 'electricityWP_splitted_conversion_commodity_1':1},
                      hasCapacityVariable= True,
                      investPerCapacity= 794.52,
                      opexPerCapacity= 794.52*0.02,
                      interestRate=0.07,
                      economicLifetime=20))

#source_1_conversion

esM.add(fn.Conversion(esM=esM,
                      name='source_1_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_1_splitted_conversion_commodity_1': 1, 'source_1_splitted_conversion_commodity_2': 1 },
                      hasCapacityVariable=False))

esM.add(fn.Conversion(esM=esM,
                      name='source_1_conversion_2',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_1_splitted_conversion_commodity_3':1},
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



#source_2_conversion
esM.add(fn.Conversion(esM=esM,
                      name='source_2_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_1_commodity': -1, 'source_2_splitted_conversion_commodity_1': 1, 'source_2_splitted_conversion_commodity_2': 1 },
                      hasCapacityVariable=False))

#source_2_splitted_conversion_1
esM.add(fn.Conversion(esM=esM,
                      name='source_2_splitted_conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'source_2_splitted_conversion_commodity_1': -1, 'conversion_3': 1},
                      hasCapacityVariable=False))

#source_2_splitted_conversion_2
Wirkungsgrad = 0.1
esM.add(fn.Conversion(esM=esM,
                      name='source_1_splitted_conversion_2',
                      physicalUnit='t_CO2e',
                      commodityConversionFactors={'source_1_splitted_conversion_commodity_2': -1, 'conversion_4': Wirkungsgrad},
                      hasCapacityVariable=False))

#conversion_3
esM.add(fn.Conversion(esM=esM,
                      name='conversion_3',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'conversion_3': -1, "storage_1_input_conversion_commodity": 1},
                      hasCapacityVariable=False))

#conversion_4
esM.add(fn.Conversion(esM=esM,
                      name='conversion_4',
                      physicalUnit='t_CO2e',
                      commodityConversionFactors={'conversion_4': -1, 'environment_conversion': 1},
                      hasCapacityVariable=False))

#storage_conversions

#storage_1_input_conversion
esM.add(fn.Conversion(esM=esM,
                      name="storage_1_input_conversion",
                      physicalUnit='kW_el',
                      commodityConversionFactors={"storage_1_input_conversion_commodity": -1, storage_1: 1},
                      hasCapacityVariable=False))

#storage_1_splitted
esM.add(fn.Conversion(esM=esM,
                      name='storage_1_splitted_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={storage_1: -1, 'storage_1_splitted_conversion_commodity_1': 1},
                      hasCapacityVariable=False))

#conversion_5
esM.add(fn.Conversion(esM=esM,
                      name='conversion_5',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'storage_1_splitted_conversion_commodity_1': 1,"electricityWP_input":1},
                      hasCapacityVariable=False))

#heatpump_input
esM.add(fn.Conversion(esM=esM,
                      name='heatpump_input',
                      physicalUnit='kW_el',
                      commodityConversionFactors={"electricityWP_input": 1,heatpump:1},
                      hasCapacityVariable=False))

#conversion_6
esM.add(fn.Conversion(esM=esM,
                      name='conversion_6',
                      physicalUnit='kW_th',
                      commodityConversionFactors={'electricityWP_splitted_conversion_commodity_1':1, 'sink_2_commodity':1},
                      hasCapacityVariable=False))



#sink_1_conversion
esM.add(fn.Conversion(esM=esM,
                      name='sink_1_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'sink_1_conversion': -1, 'sink_1_commodity': 1},
                      hasCapacityVariable=False))

#sink_2_conversion
esM.add(fn.Conversion(esM=esM,
                      name='sink_2_conversion',
                      physicalUnit='kW_el',
                      commodityConversionFactors={'sink_2_conversion': -1, 'sink_2_commodity': 1},
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