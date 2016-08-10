# MarsExpressChallenge
https://kelvins.esa.int/mars-express-power-challenge/

A big thank you to the European Space Agency and specifically the Advanced Concepts Team and the Data Analytics Team of the Advanced Mission Concepts Section for a very interesting and well organized competition.

## Dependencies
- python 2.7
- scikit-learn 0.17.1
- xgboost 0.4
- pandas 0.18.1

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




