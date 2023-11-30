#!/usr/bin/env python
# coding: utf-8
# autor: Klaus Markgraf

import FINE as fn
import pandas as pd


# Energiesystem:
sink_1 = "sink_1_commodity"
source_1 = "source_1_commodity"
source_2 = "source_2_commodity"
conversion_1 =["source_1_commodity","sink_1_commodity"]
conversion_2 =["source_2_commodity","sink_1_commodity"]


## Aufbau EMS

locations = {'location01'}

commodityUnitDict = {'sink_1_commodity': 'kW_el',
                     'source_1_commodity': 'kW_el',
                     'source_2_commodity': 'kW_el',
                     }

commodities = {'sink_1_commodity',
               'source_1_commodity',
               'source_2_commodity'
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

esM.add(fn.Sink(esM=esM,
                name='sink_2',
                commodity=source_2,
                hasCapacityVariable=False,
                commodityRevenue=0.082,
                ),
        )


## sources

#source_1
esM.add(fn.Source(esM=esM,
                  name='source_1',
                  commodity=source_1,
                  hasCapacityVariable=False,
                  commodityCost=0.40
                  )
        )

#source_2
investPerCapacity=1400
esM.add(fn.Source(esM=esM,
                  name='source_2',
                  commodity=source_2,
                 capacityFix=1,
                  # capacityMax=7,
                  hasCapacityVariable=True,
                  operationRateFix=pd.read_excel("DataForExample/PV_1.xlsx"),
                  investPerCapacity=investPerCapacity,
                  opexPerCapacity= investPerCapacity * 0.015,
                  interestRate=0.025,
                  economicLifetime=20,))



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
                      commodityConversionFactors={source_2:-1, sink_1:1},
                      hasCapacityVariable=False))



##results

esM.cluster(numberOfTypicalPeriods=7)
esM.optimize(timeSeriesAggregation=True, solver='gurobi')



# 6. Results
srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
print(srcSnkSummary)
convSummary = esM.getOptimizationSummary("ConversionModel", outputLevel=1)
print(convSummary)

TAC_gesamt = float(srcSnkSummary['location01'].loc[("source_1", 'TAC', '[1e Euro/a]')])
TAC_gesamt = TAC_gesamt+float(srcSnkSummary['location01'].loc[("source_2", 'TAC', '[1e Euro/a]')])
TAC_gesamt = TAC_gesamt+float(srcSnkSummary['location01'].loc[("sink_2", 'TAC', '[1e Euro/a]')])

operation = float(srcSnkSummary['location01'].loc[("source_1", 'operation', '[kW_el*h/a]')])
operation = operation+float(srcSnkSummary['location01'].loc[("source_2", 'operation', '[kW_el*h/a]')])
operation = operation+float(srcSnkSummary['location01'].loc[("sink_2", 'operation', '[kW_el*h/a]')])

print("TAC="+str(TAC_gesamt))
print("operation="+str(operation))