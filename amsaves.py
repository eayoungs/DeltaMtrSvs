#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@successionecological.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
        Services API * deltameterservices.com * """

from collections import defaultdict
import pandas as pd
import requests


def amsaves_results(comparisonsDct, bldgModelsDct, bldgIDct):
    """ Pass the results of get_model_comparisons function; produce requested 
        results for the 'America Saves!' program as a DataFrame """

    uses = []
    for key, value in comparisonsDct.iteritems():
        elecRatio = value['ElectricRatioA']
        gasRatio = value['GasRatioA']
        elecKwhSavings = round(-value['ElectricDifference']*elecRatio, 0)
        gasThermSavings = round(-value['GasDifference']/29.3072, 0)
        elecBaseLdKwh = round(value['ModelAValues'][1]*elecRatio + \
                              value['ModelAValues'][3]*elecRatio + \
                              value['ModelAValues'][5]*elecRatio + \
                              value['ModelAValues'][7]*elecRatio, 0)
        elecClgKwh = round(value['ModelAValues'][0]*elecRatio, 0)
        elecHtgKwh = round(value['ModelAValues'][8]*elecRatio, 0)
        gasSpcHtgTherm = round(value['ModelAValues'][9]/29.3072*gasRatio, 0)
        gasBaseLd = round((value['ModelAValues'][2]*gasRatio + \
                           value['ModelAValues'][4]*gasRatio + \
                           value['ModelAValues'][6])/29.3072*gasRatio, 0)
        bldgID = key
        bldg = bldgIDct[key]
        jsonModel = bldgModelsDct[key]['Reference Model']
        customID = bldg['ExternalID']
        bldgName = bldg['BuildingName']
        rSquare = jsonModel['R2Coefficient']
        iterQuant = jsonModel['IterationQty']
        bldgArea = jsonModel['SquareFeet']
        solnID = jsonModel['SolutionID']
        uses.append([key, customID, bldgName, rSquare, iterQuant, bldgArea,
                     solnID, elecKwhSavings, gasThermSavings, elecBaseLdKwh,
                     elecClgKwh, elecHtgKwh, gasSpcHtgTherm, gasBaseLd,
                     elecRatio, gasRatio])

    names = ['Blg. ID', 'BldgEnergy ID', 'Bldg Name', 'R2Coef.', 'Iterations',
             'Bldg. Area [ft2]', 'Solution ID', 'Electric Savings [kWh]',
             'Gas Savings [Therms]', 'Elec. Base-load [kWh]',
             'Elec. Cooling [kWh]', 'Elec. Heat [kWh]',
             'Gas Space Heat [Therms]', 'Gas Base-load [Therms]',
             'Elec. True-up Ratio', 'Gas True-up Ratio']

    usesDf = pd.DataFrame(data=uses, columns=names)
    # TODO (eayoungs): Return a tuple, add primary building IDs from
    #                  deltameterservices.com; create a dictionary of
    #                  dataframes as in am_saves_audit, 
    return usesDf


def amsaves_audit(audits):
    """ Pass the results of get_model_audits function; produce audit of 
        results for the 'America Saves!' program as a DataFrame """

    combinedUsageDct = {}
    for key, value in audits.iteritems():
        elecUsage = []
        gasUsage = []
        jsonAudits = value
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
        names = ['[kWh/Mo.]', 'Units', '[W/SF]', 'Per. Start', 'Per. End',
                 'Hrs. in Per.', 'Air Temp']
        elecUsageDf = pd.DataFrame(data=elecUsage, columns=names)
        if gasUsage:
            gasUsageDf = pd.DataFrame(data=gasUsage, columns=names)
            combinedUsageDf = pd.concat([elecUsageDf, gasUsageDf], axis=1)
            combinedUsageDct[key] = combinedUsageDf
        else: combinedUsageDct[key] = elecUsageDf

    return combinedUsageDct


def amsaves_flags(fvCharts):
    """ Pass the results of get_fv_charts function; produce 'flags' formatted
        to specification of America Saves! project requirements """

    diagnMsgCodes = {}
    dmsMsgNms = ['Occupant Load',
                 'Controls Heating',
                 'Shell Ventilation',
                 'Controls Cooling',
                 'Cooling Efficiency',
                 'Data Consistency',
                 'Summer Gas Use']
    for key, value in fvCharts.iteritems():
        diagnstcs = value['Diagnostics']
        msgCodeDfDct = defaultdict()
        for diagnstc in diagnstcs:
            if diagnstc['MessageName'] in dmsMsgNms:
                msgName = diagnstc['MessageName']
                msgCode = diagnstc['MessageCode']
                msgTxt = diagnstc['MessageText']
                msgCodeDfDct[msgName] = [msgCode, msgTxt]

        diagnMsgCodes[key] = msgCodeDfDct

    # TODO (eayoungs): Return tuple, add primary building IDs from
    # deltameterservices.com to return statment
    return diagnMsgCodes

# TODO (eayoungs): Create a function to return summary & meta data for each
#                  building. (Some metadata, such as date ranges of meter
#                  readings will come from audit data)


def amsaves_usage_range(audits):
    """ Pass the results of get_model_audits function; produce time span of
        utility billing used in ma given model results for the 'America
        Saves!' program """

    auditSpans = {}
    for key, value in audits.iteritems():
        elecStart = []
        elecEnd = []
        gasStart = []
        gasEnd = []
        spanData = {}
        jsonAudits = value
        for jsonAudit in jsonAudits:
            periodStartDate = str(jsonAudit['PeriodStartDate'])
            periodEndDate = str(jsonAudit['PeriodEndDate'])
            if jsonAudit['UnitOfMeasure'] == 'KWH':
                elecStart.append(periodStartDate)
                elecEnd.append(periodEndDate)
            elif jsonAudit['UnitOfMeasure'] == 'THERM':
                gasStart.append(periodStartDate)
                gasEnd.append(periodEndDate)

        elecSpanBegin = min(elecStart)
        elecSpanEnd = max(elecEnd)
        if len(gasStart) > 0:
            gasSpanBegin = min(gasStart)
            gasSpanEnd = max(gasEnd)
            spanData['E. Per. Begin'] = elecSpanBegin
            spanData['E. Per. End'] = elecSpanEnd
            spanData['G. Per. Begin'] = gasSpanBegin
            spanData['G. Per. End'] = gasSpanEnd
        else:
            spanData['E. Per. Begin'] = elecSpanBegin
            spanData['E. Per. End'] = elecSpanEnd
        auditSpans[key] = spanData

    return auditSpans


def amsaves_billing_rate(bldgMeterRecordsDct):
    """ Takes a dictionary of building meters with building IDs as keys, whose
        values are dictionaries with named keys describing the fuel type
        containing meter readings; returns a dictionary with building IDs as
        keys containing a dictionary of cost & consumption values with
        descriptive keys """

    bldgRatesDct = {}
    for key, value in bldgMeterRecordsDct.iteritems():
        utilityRateDct = {}
        elecMeterRecords = value['Elec. Meter Records']
        elecUse = sum([elecMeterRecord['TotalUnitsUsed'] for elecMeterRecord
                       in elecMeterRecords])
        elecCost = sum([elecMeterRecord['TotalUsageCost'] for elecMeterRecord
                        in elecMeterRecords])
        elecRate = elecCost / elecUse
        utilityRateDct['Electric Rate'] = elecRate

        if len(value) == 2:
            gasMeterRecords = value['Gas Meter Records']
            gasUse = sum([gasMeterRecord['TotalUnitsUsed'] for gasMeterRecord
                          in gasMeterRecords])
            gasCost = sum([gasMeterRecord['TotalUsageCost'] for gasMeterRecord
                           in gasMeterRecords])
            gasRate = gasCost / gasUse
            utilityRateDct['Gas Rate'] = gasRate
        bldgRatesDct[key] = utilityRateDct

    return bldgRatesDct 
