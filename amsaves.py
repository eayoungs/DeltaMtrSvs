#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
        Services API * deltameterservices.com * """


import pandas as pd


def am_saves_results(comparisons):
    """ Pass the results of get_model_comparisons function; produce requested 
        results for the 'America Saves!' program as a DataFrame """

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
                              json_comps['ModelAValues'][7], 0)
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
        
        gasUsageDf = pd.DataFrame(data=gasUsage, columns=names)
        elecUsageDf = pd.DataFrame(data=elecUsage, columns=names)
        combinedUsageDf = pd.concat([gasUsageDf, elecUsageDf], axis=1)
        combinedUsageDct[refModelIDs[i]] = combinedUsageDf
        i=i+1

    return (refModelIDs, combinedUsageDct)

def amsaves_flags(fvCharts):
    """ Pass the results of get_fv_charts function; produce 'flags' formatted
        to specification of America Saves! project requirements """

    diagnMsgCodes = []
    amSavesMsgCodes = []
    dmsMsgNms = ['Occupant Load',
                 'Controls Heating',
                 'Shell Ventilation',
                 'Controls Cooling',
                 'Cooling Efficiency']

    for fvChart in fvCharts:
        diagnstcs = fvChart['Diagnostics']
        msgCode = [diagnstc['MessageCode'] for diagnstc in diagnstcs if
                   diagnstc['MessageName'] in dmsMsgNms]
        # if msgCode[0] == 'A' or msgCode[0] == 'B' or msgCode[0] == 'C':
        #     intElecConsFlg = msgCode[0]
        #     # TODO (eayoungs): Verify whether flags 'O' & 'P' are in this
        #     #                  field
        #     ultraHighElecIntExt = '?'
        # elif msgCode[0] == 'O' or msgCode[0] == 'P':
        #     intElecConsFlg = ''
        #     # TODO (eayoungs): ^
        #     ultraHighElecIntExt = msgCode[0]
        # else: intElecConsFlg = ''
        
        # amSavesMsgCodes = [intElecConsFlg, ultraHighElecIntExt]
        diagnMsgCodes.append(msgCode) 

    return diagnMsgCodes
