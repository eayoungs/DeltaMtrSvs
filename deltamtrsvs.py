#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GPLv3"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """


import requests
import pandas as pd


def get_property_bldg_IDs(properties_url, site, headers):
  properties_endpt = properties_url + site
  bldgs = requests.get(properties_endpt, headers=headers).json()
  bldgIDs = [str(bldg['BuildingID']) for bldg in bldgs]

  return bldgIDs

def get_bldg_models(model_url, bldgIDs, headers):
  json_models = []
  valBldgIDs = []
  for bldgID in bldgIDs:
    model_endpt = model_url + bldgID
    models = requests.get(model_endpt, headers=headers)
    if requests.get(model_endpt, headers=headers):
        json_models.append(models.json())
        valBldgIDs.append(str(bldgID))

  return (json_models, valBldgIDs)

def get_model_comparisons(comparison_url, json_models, headers):
  modelIDs =[]
  for i in range(0, len(json_models)):
    for j in range(0, len(json_models[i])):
        modelID = str(json_models[i][j]['SolutionID'])
        modelIDs.append(modelID)

  comparisons =[]
  for i in range(0, len(modelIDs)-1, 2):
    comparison_endpt = comparison_url + modelIDs[i] + '/1/' + \
                             modelIDs[i+1] + '/1/'
    comparison = requests.get(comparison_endpt, headers=headers)
    comparisons.append(comparison)

  return (modelIDs, comparisons)

def am_saves_results(comparisons):
  names = ['Electric Savings [kWh]', 'Gas Savings [Therms]',
           'Elec. Base-load [kWh]', 'Elec. Cooling [kWh]', 'Elec. Heat [kWh]',
           'Gas Space Heat [Therms]', 'Gas Base-load [Therms]']

  uses = []
  for comparison in comparisons:
    json_comps = comparison.json()
    elecKwhSavings = round(-json_comps['ElectricDifference'], 0)
    gasThermSavings = round(-json_comps['GasDifference']/29.3072, 0)
    elecBaseLdKwh = round(json_comps['ModelAValues'][3] + \
                          json_comps['ModelAValues'][5] + \
                          json_comps['ModelAValues'][5], 0)
    elecClgKwh = round(json_comps['ModelAValues'][0], 0)
    elecHtgKwh = round(json_comps['ModelAValues'][8], 0)
    gasSpcHtgTherm = round(json_comps['ModelAValues'][9]/29.3072, 0)
    gasBaseLd = round((json_comps['ModelAValues'][2] + \
                       json_comps['ModelAValues'][4] + \
                       json_comps['ModelAValues'][6])/29.3072, 0)
    
    uses.append([elecKwhSavings, gasThermSavings, elecBaseLdKwh, elecClgKwh,
                 elecHtgKwh, gasSpcHtgTherm, gasBaseLd])

    usesDf = pd.DataFrame(data=uses, columns=names)

  return usesDf
