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

commodityUnitDict = {'sink_1_commodity': 'kW_el',
                     'source_1_commodity': 'kW_el',
                     'source_2_commodity': 'kW_el',
                     "storage_1_commodity": "kW_el"
                     }

commodities = {'sink_1_commodity',
               'source_1_commodity',
               'source_2_commodity',
               "storage_1_commodity"
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

#storage_1
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

#conversion_source_1
esM.add(fn.Conversion(esM=esM,
                      name='conversion_1',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_1:-1, sink_1:1},
                      hasCapacityVariable=False))


#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_2',
                      physicalUnit='kW_el',
                      commodityConversionFactors={source_2:-1, storage_1:1},
                      hasCapacityVariable=False))

#conversion_source_2
esM.add(fn.Conversion(esM=esM,
                      name='conversion_3',
                      physicalUnit='kW_el',
                      commodityConversionFactors={storage_1:-1, sink_1:1},
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