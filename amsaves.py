#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
        Services API * deltameterservices.com * """


import pandas as pd
from collections import defaultdict


def amsaves_results(compDct, jModDct):
    """ Pass the results of get_model_comparisons function; produce requested 
        results for the 'America Saves!' program as a DataFrame """

    uses = []
    for key, value in compDct.items():
        json_comps = compDct[key].json()
        elecKwhSavings = round(-json_comps['ElectricDifference'], 0)
        gasThermSavings = round(-json_comps['GasDifference']/29.3072, 0)
        elecBaseLdKwh = round(json_comps['ModelAValues'][1] + \
                              json_comps['ModelAValues'][3] + \
                              json_comps['ModelAValues'][5] + \
                              json_comps['ModelAValues'][7], 0)
        elecClgKwh = round(json_comps['ModelAValues'][0], 0)
        elecHtgKwh = round(json_comps['ModelAValues'][8], 0)
        gasSpcHtgTherm = round(json_comps['ModelAValues'][9]/29.3072, 0)
        gasBaseLd = round((json_comps['ModelAValues'][2] + \
                           json_comps['ModelAValues'][4] + \
                           json_comps['ModelAValues'][6])/29.3072, 0)

        bldgArea = jModDct[key][0]['SquareFeet']

        uses.append([bldgArea, elecKwhSavings, gasThermSavings, elecBaseLdKwh,
                     elecClgKwh, elecHtgKwh, gasSpcHtgTherm, gasBaseLd])

    names = ['Bldg. Area [ft2]', 'Electric Savings [kWh]',
             'Gas Savings [Therms]', 'Elec. Base-load [kWh]',
             'Elec. Cooling [kWh]', 'Elec. Heat [kWh]',
             'Gas Space Heat [Therms]', 'Gas Base-load [Therms]']

    usesDf = pd.DataFrame(data=uses, columns=names)
    # TODO (eayoungs): Return a tuple, add primary building IDs from
    #                  deltameterservices.com; create a dictionary of
    #                  dataframes as in am_saves_audit, 
    return usesDf

def am_saves_audit(refModelIDs, audits):
    """ Pass the results of get_model_audits function; produce audit of 
        results for the 'America Saves!' program as a DataFrame """

    names = ['[kWh/Mo.]', 'Units', '[W/SF]', 'Per. Start', 'Per. End',
             'Hrs. in Per.', 'Air Temp']

    combinedUsageDct = {}
    i = 0
    for audit in audits:
        elecUsage = []
        gasUsage = []
        jsonAudits = audit.json()
        for jsonAudit in jsonAudits:
            values = jsonAudit['TotalUnitsUsed']
            unitOfMeasure = jsonAudit['UnitOfMeasure']
            periodStartDate = str(jsonAudit['PeriodStartDate'])
            periodEndDate = str(jsonAudit['PeriodEndDate'])
            hrsInPeriod = jsonAudit['DaysInPeriod']*24
            pwrDensity = jsonAudit['ElecWattsPerFt2']
            airTemp = jsonAudit['AirTemp']
                
            if jsonAudit['UnitOfMeasure'] == 'KWH':
                elecUsage.append([values, unitOfMeasure, pwrDensity,
                                 periodStartDate, periodEndDate, hrsInPeriod,
                                 airTemp])
            elif jsonAudit['UnitOfMeasure'] == 'THERM':
                gasUsage.append([values, unitOfMeasure, pwrDensity,
                                periodStartDate, periodEndDate, hrsInPeriod,
                                airTemp])
        # TODO (eayoungs): Move data frame construction to test function; stick
        #                  deltameterservices.com structure, filter & , per
        #                  amsaves_flags()
        gasUsageDf = pd.DataFrame(data=gasUsage, columns=names)
        elecUsageDf = pd.DataFrame(data=elecUsage, columns=names)
        combinedUsageDf = pd.concat([gasUsageDf, elecUsageDf], axis=1)
        combinedUsageDct[refModelIDs[i]] = combinedUsageDf
        i=i+1

    # TODO (eayoungs): Remove refModelIDs from return statement, revise
    #                  combinedUsageDct to a nested dictionary with primary
    #                  building IDs and reference model IDs from
    #                  deltameterservices.com, per amsaves_flags()
    return (refModelIDs, combinedUsageDct)

def amsaves_flags(fvCharts):
    """ Pass the results of get_fv_charts function; produce 'flags' formatted
        to specification of America Saves! project requirements """

    diagnMsgCodes = []
    dmsMsgNms = ['Occupant Load',
                 'Controls Heating',
                 'Shell Ventilation',
                 'Controls Cooling',
                 'Cooling Efficiency',
                 'Data Consistency']

    for fvChart in fvCharts:
        diagnstcs = fvChart['Diagnostics']
        msgCodeDfDct = defaultdict()
        for diagnstc in diagnstcs:
            if diagnstc['MessageName'] in dmsMsgNms:
                msgName = diagnstc['MessageName']
                msgCode = diagnstc['MessageCode']
                msgCodeDfDct[msgName] = msgCode

        diagnMsgCodes.append(msgCodeDfDct) 
    # TODO (eayoungs): Return tuple, add primary building IDs from
    # deltameterservices.com to return statment
    return diagnMsgCodes

# TODO (eayoungs): Create a function to return summary & meta data for each
#                  building. (Some metadata, such as date ranges of meter
#                  readings will come from audit data)
