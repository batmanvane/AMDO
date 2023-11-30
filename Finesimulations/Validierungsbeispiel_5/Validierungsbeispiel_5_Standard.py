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
                     "conversion_1" : "kW_el",
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
                     "storage_commodity",
                     "electricityWP_commodity",
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
                commodity=sink_1,
                hasCapacityVariable=False,
                operationRateFix=pd.read_excel("DataForExample/sink_1.xlsx"),
                ),
        )

#sink_2
esM.add(fn.Sink(esM=esM,
                name='sink_2',
                commodity=sink_2,
                hasCapacityVariable=False,
                operationRateFix=pd.read_excel("DataForExample/sink_2.xlsx"),
                ),
        )

#environment
esM.add(fn.Sink(esM=esM,
                name='environment',
                commodity=environment,
                hasCapacityVariable=False,
                opexPerOperation= 50
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
                      commodityConversionFactors={heatpump:-1, sink_2:1},
                      hasCapacityVariable= True,
                      investPerCapacity= 794.52,
                      opexPerCapacity= 794.52*0.02,
                      interestRate=0.07,
                      economicLifetime=20))

#conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_1:-1, sink_1:1, environment:0.3},
                      hasCapacityVariable=False))

#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_2',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_2:-1, storage_1:1, environment:0.01},
                      hasCapacityVariable=False))

#conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_3',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_1:-1, heatpump:1,environment:0.3},
                      hasCapacityVariable=False))

#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_4',
                      physicalUnit='kW_el',
                      commodityConversionFactors={storage_1:-1, heatpump:1},
                      hasCapacityVariable=False))

#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_5',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_3:-1, heatpump:1, environment:0.01},
                      hasCapacityVariable=False))

#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_6',
                      physicalUnit='kW_el',
                      commodityConversionFactors={storage_1:-1, sink_1:1,},
                      hasCapacityVariable=False))

##results

esM.cluster(numberOfTypicalPeriods=7)
esM.optimize(timeSeriesAggregation=True, solver='gurobi')



# 6. Results
srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
print(srcSnkSummary)
convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
print(convSummary)
storSummary = esM.getOptimizationSummary("StorageModel", outputLevel=1)
print(storSummary)