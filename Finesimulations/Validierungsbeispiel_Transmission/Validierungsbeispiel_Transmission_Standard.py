# Autor: Georg Sandkamp


"""
Aufbau:
  location Nord mit Windkraft als Quelle
  location Süd nur Strombedarf (aber doppelt so groß wie im Norden)ohne Quelle

  Nord und Süd sind mit einer Transmisssion verbunden

  Quellen so wie Bedarf als konstanter Verlauf eine Einheit pro Stunde d.h. 8760 pro Jahr

"""

import FINE as fn
import pandas as pd
import numpy as np

loc=2
columns=['Nord','Süd'] #column-Liste für die dataframes
index=['Nord','Süd'] #index-Liste für die dataframes
locations={'Nord','Süd'}

commodityUnitDict = {"electricity": "kW_el","electricityImport": "kW_el","electricityPV": "kW_el", "electricityCable": "kW_el"}

commodities = {"electricity","electricityImport","electricityPV", "electricityCable"}

esM = fn.EnergySystemModel(locations=locations,
                       commodities=commodities,
                       numberOfTimeSteps=8760,
                       commodityUnitsDict=commodityUnitDict,
                       hoursPerTimeStep=1,
                       costUnit="1e Euro",
                       lengthUnit="km",
                       verboseLogLevel=0)

# 3. Quellen
# 3.1 Netzbezug

kosten_strombezug=0.326

esM.add(fn.Source(esM=esM,
                  name="Electricity purchase",
                  commodity="electricityImport",
                  hasCapacityVariable=False,
                  commodityCost=float(kosten_strombezug)))

#3.2 Wind


investPerCapacityWind = 3000
cMaxWind=[2,0.0]
esM.add(fn.Source(esM=esM,
                  name='PV',
                  commodity='electricityPV',
                  hasCapacityVariable=True,
                  operationRateMax=pd.read_excel("DataForExample/PV_1.xlsx"),
                  capacityFix=pd.Series(cMaxWind,index=index),
                  investPerCapacity=investPerCapacityWind,
                  opexPerCapacity=investPerCapacityWind * 0.025,
                  interestRate=0.08,
                  economicLifetime=15))

#4. Senken
#4.1 Strombedarf


opRateStrom = pd.read_excel("DataForExample/sink_1.xlsx"),

esM.add(fn.Sink(esM=esM,
                name="Electricity demand",
                commodity="electricity",
                hasCapacityVariable=False,
                operationRateFix=pd.read_excel("DataForExample/sink_1.xlsx")))


#5. Transmission
#5.1 Verbindung der Quellen mit der Senke

"""
- Sowohl bei der Kapazität als auch bei dem Abstand ist auf eine symetrische Matrix zu Achten
- Beispiel: [0,4] -> Hauptdiagonale mit Null versehen
            [4,0]
- Verluste entsprechend als eine FließkommaZahl (gültig für alle Verbindungen)
"""


cF=np.array([[0,1],[1,0]])
distances=np.array([[0.0,10],[10,0.0]])
losses=0.001

capacityFix=pd.DataFrame(cF,
                         columns=columns,
                         index=index)
distances=pd.DataFrame(distances,
                        columns=columns,
                        index=index)
esM.add(fn.Transmission(esM=esM,
                        name="AC cables",
                        commodity="electricityCable",
                        hasCapacityVariable=True,
                        capacityMax=capacityFix,
                        distances=distances,
                        losses=losses))

# 6. Optimization
esM.cluster(numberOfTypicalPeriods=7)
esM.optimize(timeSeriesAggregation= True, solver='gurobi')

srcSnkSummary = esM.getOptimizationSummary("SourceSinkModel", outputLevel=1)
print(srcSnkSummary)
transSummary = esM.getOptimizationSummary("TransmissionModel", outputLevel=1)
print(transSummary)

"""
Rechenbeipiel:

        Verbrauch        Wind     Strombezug
  Nord    8760           17520
  Süd     17520          0        8847,6

-> Verbrauch im Norden von Wind gedeckt
-> Verbrauch im Süden größer als die Produktion
d.h. Stromeinkauf und Überproduktion im Norden kann über Transmission den Süden mit Strom versorgen

Überproduktion im Norden 8760, welche im Süden benötigt werden

Transmission 8760 von Nord nach Süd

losses * distances = 0,001*10=0,01

8760*0,01=87,6 ,Welche durch den Verlust der Transmission verloren geht

Im Süden kommt somit 8760-87,6=8672,4 an.

17520-8672,4=8847,6 müssen aus dem Netz bezogen werden.

"""