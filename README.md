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


## Feature Engineering
Note that not all features necessarily made it to the final model but all are available for `MarsExpressPowerChallenge.ipynb` when it  scans for important features.

`DataReader.py` is responsible for all feature creation and data massaging. `dmopPairsExample.ipynb` plays with adding delays to all features.

Context files were used as follows, custom features are marked with an asterisk
#### Events Files (EVTF)
- Time to pericenter (\*)
- Time in umbra/penumbra (\*)
- Height change (\*)
- Ascend / descend indicators (\*)

#### Long-term data (LTDATA)
- solarconstantmars
- sunmarsearthangle_deg
- eclipseduration_min
- occultationduration_min
- sunmarsearthangle_deg2 (allows the angle to go negative) (\*)
- conjuction indicator (\*)

#### Detailed Mission Operations Plan (DMOP)
- Command shorthands (first 4 chars) (\*)
- Pairs of subsystem commands (\*) suspected to be on-off toggles (see `dmopPairsExample.ipynb`)

#### Flight Dynamics Timeline (FTL)
'ACROSS_TRACK','D1PVMC','D2PLND','D3POCM','D4PNPO','D7PLTS','D8PLTP','D9PSPO',
'EARTH','INERTIAL','MAINTENANCE','NADIR','NADIR_LANDER','SLEW','SPECULAR','WARMUP','flagcomms'

#### Solar aspect angles (SAAF)
'sa','sx',sy','sz'

## Workflow
### Best submission (Public RMSE:0.08025 (1st place) Overall RMSE: 0.08030 (2nd place))
Uses a constant set of features for all power lines, but trains power lines independently.
Combines xgboost and Extra tree models.
![alt tag](https://raw.githubusercontent.com/stephanos-stephani/MarsExpressChallenge/master/pngs/best_submission_flow.png)

### Maybe most practical submission submission (Public RMSE:0.0825 (4th))
Whereas the best submission had some manual feature selection, and an arguably complicated ensemble procedure, an attractive alternative is the following, which might be more robust for future operations: 
1. Automatically selecting the best features per power line by first training an extra trees regressor for each power line.
2. Training a simple ensemble of xgboost and Extra Trees on each power line
![alt tag](https://raw.githubusercontent.com/stephanos-stephani/MarsExpressChallenge/master/pngs/flexible_model.png)


## Acknowledgements
A big thank you to the European Space Agency and specifically the Advanced Concepts Team and the Data Analytics Team of the Advanced Mission Concepts Section for a very interesting and well organized competition.

