#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
        Services API * deltameterservices.com * """


import pandas as pd


def am_saves_results(comparisons):
    names = ['Electric Savings [kWh]', 'Gas Savings [Therms]',
                     'Elec. Base-load [kWh]', 'Elec. Cooling [kWh]',
                     'Elec. Heat [kWh]',
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
        
        uses.append([elecKwhSavings, gasThermSavings, elecBaseLdKwh,
                     elecClgKwh, elecHtgKwh, gasSpcHtgTherm, gasBaseLd])

        usesDf = pd.DataFrame(data=uses, columns=names)

    return usesDf
