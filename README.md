# MarsExpressChallenge
This repo summarizes the 2nd place solution in the Mars Express Power Challenge conducted by the European Space Agency (ESA). https://kelvins.esa.int/mars-express-power-challenge/

This repository is still a work in progress.

## Background
The Mars Express spacecraft orbiting around Mars is operated by ESA and is the second longest surviving, continually active spacecraft in orbit around a planet other than Earth, behind only NASA's still active 2001 Mars Odyssey.

The spacecraft has an internal thermal subsystem. It works autonomously to keep each part of the spacecraft within pre-defined working temperatures. This thermal subsystem is composed of nodes (including heaters and coolers) that consume electric power as needed.  Remaining power can be used to conduct science observations. 

`Science Power = Produced Power - Platform Power - Thermal Power`

Overestimating thermal power means conducting less science. Underestimating thermal power, and doing too much science, could send the orbiter in "safe mode", halting science observations and using a lot of reserve fuel in the meantime as it maneuvers in the ‘Sun acquisition’ process. 

As a result, accurately predicting the behavior of this thermal subsystem by modeling the electric power consumption in each of these nodes is very important to mission operators. 

In the Mars Express Power Challenge competitors were asked to analyse the three given Martian years of Mars Express data, including context data (explanatory/predictor variables) and measurements of the electric current (target variables) in each thermal subsystem node, to predict the average electric current of 33 thermal power lines per hour of the fourth Martian year (2014-04-14 to 2016-03-01). For this fourth Martian year only the context data is provided. 

## Dependencies
- python 2.7
- scikit-learn 0.17.1
- xgboost 0.4
- pandas 0.18.1

## Workflow of best submission
![alt tag](https://raw.githubusercontent.com/stephanos-stephani/MarsExpressChallenge/master/pngs/best_submission_flow.png)

## Feature Engineering
Note that not all features necessarily made it to the final model but all are available for `MarsExpressPowerChallenge.ipynb` when it  scans for important features.

`DataReader.py` is responsible for all feature creation and data massaging. `dmopPairsExample.ipynb` plays with adding delays to all features.

Context files were used as follows, custom features are marked with an asterisk
#### EVTF 
- Time to pericenter (\*)
- Time in umbra/penumbra (\*)
- Height change (\*)
- Ascend / descend indicators (\*)

#### LTDATA
- solarconstantmars
- sunmarsearthangle_deg
- eclipseduration_min
- occultationduration_min
- sunmarsearthangle_deg2 (allows the angle to go negative) (\*)
- conjuction indicator (\*)

#### DMOP
- Command shorthands (first 4 chars) (\*)
- Pairs of subsystem commands (\*) suspected to be on-off toggles (see `dmopPairsExample.ipynb`)

#### FTL
'ACROSS_TRACK','D1PVMC','D2PLND','D3POCM','D4PNPO','D7PLTS','D8PLTP','D9PSPO',
'EARTH','INERTIAL','MAINTENANCE','NADIR','NADIR_LANDER','SLEW','SPECULAR','WARMUP','flagcomms'

#### SAAF
'sa','sx',sy','sz'


## Acknowledgements
A big thank you to the European Space Agency and specifically the Advanced Concepts Team and the Data Analytics Team of the Advanced Mission Concepts Section for a very interesting and well organized competition.

