#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@successionecological.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import datetime
import types as tp
import pandas as pd
import re
import deltamtrsvs 
import amsaves as ams
import private as pvt

headers = pvt.headers
properties_url = pvt.properties_url
model_url = pvt.model_url
comparison_url = pvt.comparison_url
audit_url = pvt.audit_url
sites = [pvt.Middlesboro]#, pvt.FDL, pvt.HJSMS]


def test_amsaves_results():
    """ Pass the results of get_model_comparisons to the amsaves_results 
        function, confirm DataFrame returned in requested results format for
        the 'America Saves!' program (write contents to .CSV file for review)
        """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                    headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))
        bldgModelsDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                headers)
        modelIDs = []
        for key, value in bldgModelsDct.iteritems():
            jsonModelsDct = value
            for key, value in jsonModelsDct.iteritems():
                modelIDs.append(str(value['SolutionID']))
                
        comparisonsDct = deltamtrsvs.get_model_comparisons(comparison_url,
                                                           bldgModelsDct,
                                                           headers)
        bldgModelsDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                    headers)
        usesDf = ams.amsaves_results(comparisonsDct, bldgModelsDct, bldgIDct)

        fname = site+'-results.csv'
        with open(fname, 'wb') as outf:
            outcsv = usesDf.to_csv(fname)

    assert isinstance(usesDf, pd.DataFrame)
    assert usesDf.shape[1] == 16


def test_amsaves_audit():
    """ Pass the results of get_model_audits function, confirm DataFrame
        returned in requested results format for the 'America Saves!' program
        (write contents to .CSV file for review) """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        bldgModelsDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                headers)
        refModelsDct = {}
        for key, value in bldgModelsDct.iteritems():
            refModelsDct[key] = value['Reference Model']
                
        comparisonsDct = deltamtrsvs.get_model_comparisons(comparison_url,
                                                           bldgModelsDct,
                                                           headers)
        audits = deltamtrsvs.get_model_audits(audit_url, refModelsDct, headers)
        combinedUsageDct = ams.amsaves_audit(audits)

        assert isinstance(combinedUsageDct, dict)
        assert len(combinedUsageDct) == len(audits)

        for key, value in combinedUsageDct.iteritems():
            df = value
            assert isinstance(value, pd.DataFrame)
            fname = key + '-audit.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)


def test_amsaves_flags():
    """ """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        valBldgIDs = []
        for key in modelsJsonDct:
            valBldgIDs.append(str(key))

        fvCharts = deltamtrsvs.get_fv_charts(pvt.fv_charts_url, valBldgIDs,
                                         headers)
        diagnMsgCodes = ams.amsaves_flags(fvCharts)
        # TODO (eayoungs): Needs more robust assertions
        assert type(diagnMsgCodes) == tp.DictType
        siteFlags = []
        for key, value in diagnMsgCodes.iteritems():
            bldgvalues = []
            if value['Occupant Load'][0] == 'A' or \
                value['Occupant Load'][0] == 'B' or \
                value['Occupant Load'][0] == 'C':
                intrnElec = value['Occupant Load'][0]
                ultrHighIntExt = ''
            elif value['Occupant Load'][0] == 'O' or \
                value['Occupant Load'] == 'P':
                ultrHighIntExt = value['Occupant Load'][0]
                intrnElec = ''
            # TODO (eayoungs): Add exception handling for final *else*
            #                  statement
            if value['Summer Gas Use'][1] == "High":
                highGasBaseLd = "M"
            else: highGasBaseLd = ""

            bldgFlags = [key, intrnElec, ultrHighIntExt,
                         value['Controls Heating'][0],
                         value['Shell Ventilation'][0],
                         value['Controls Cooling'][0],
                         value['Cooling Efficiency'][0],
                         value['Data Consistency'][0],
                         highGasBaseLd]

            siteFlags.append(bldgFlags)
            assert len(bldgFlags) == 9
            assert [type(bldgFlag) == tp.StringType for bldgFlag in bldgFlags]
            assert [len(bldgFlag) == 1 for bldgFlag in bldgFlags]
    
            colNms = ['Bldg ID','Int. Elec.', 'Ultra-High Elec.',
                      'Excessive Htg.', 'Shell & Vent.', 'Excessive Clg',
                      'Inefficient Clg', 'Erratic Operation', 'High Gas Eqp.']
            df = pd.DataFrame(data=siteFlags, columns=colNms)

            fname = site+'-flags.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

    assert len(siteFlags) == len(diagnMsgCodes)
    assert len(fvCharts) <= len(bldgIDs)


#def test_amsaves_usage_range():
#    """ Pass the results of get_model_audits function, confirm returned
#        dictionary in requested results format for the 'America Saves!' program
#        """
#
#    for site in sites:
#        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
#                                                  headers)
#        bldgIDs = []
#        for key in bldgIDct:
#            bldgIDs.append(str(key))
#
#        bldgModelsDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
#                                                headers)
#        refModelIDs = []
#        for key, value in bldgModelsDct.iteritems():
#            refModel = value['Reference Model']
#            refModelIDs.append(str(refModel['SolutionID']))
#                
#        comparisonsDct = deltamtrsvs.get_model_comparisons(comparison_url,
#                                                           bldgModelsDct,
#                                                           headers)
#        audits = deltamtrsvs.get_model_audits(audit_url, refModelIDs, headers)
#        auditSpans = ams.amsaves_usage_range(audits)
#        assert type(auditSpans) == tp.DictType
#        # assert len(auditSpans) == len(refModelIDs)
#
#        spans = []
#        for key, value in auditSpans.iteritems():
#            assert type(key) == tp.StringType
#            assert type(value) == tp.DictType
#            vals = []
#            colNms = []
#            if len(auditSpans[key]) == 2:
#                vals = [key, auditSpans[key]['E. Per. Begin'],
#                        auditSpans[key]['E. Per. End']]
#                colNms = ['Ref. Model ID', 'E. Per. Begin', 'E. Per. End']
#            elif len(auditSpans[key]) == 4:
#                vals = [key, auditSpans[key]['E. Per. Begin'],
#                        auditSpans[key]['E. Per. End'],
#                        auditSpans[key]['G. Per. Begin'],
#                        auditSpans[key]['G. Per. End']]
#                colNms = ['Ref. Model ID', 'E. Per. Begin', 'E. Per. End',
#                          'G. Per. Begin', 'G. Per. End']
#            # TODO (eayoungs): Add exception handling and include in final
#            #                  *else* statement
#            spans.append(vals)
#            df = pd.DataFrame(data=spans, columns=colNms)
#            
#        fname = site +'-use_ranges.csv'
#        with open(fname, 'wb') as outf:
#            outcsv = df.to_csv(fname)


#def test_amsaves_billing_rate():
#    """ Pass the results of get_meter_records, confirm results of
#        amsaves_billing_rate function returns expected data types & structures
#        """
#
#    #for site in sites:
#    site = '46'
#    bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
#                                              headers)
#    bldgIDs = []
#    for key in bldgIDct:
#        bldgIDs.append(str(key))
#
#    bldgModelsDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
#                                            headers)
#    refModelIDs = []
#    for key, value in bldgModelsDct.iteritems():
#        refModel = value['Reference Model']
#        refModelIDs.append(str(refModel['SolutionID']))
#                
#    comparisonsDct = deltamtrsvs.get_model_comparisons(comparison_url,
#                                                       bldgModelsDct,
#                                                       headers)
#    audits = deltamtrsvs.get_model_audits(audit_url, refModelIDs, headers)
#    auditSpans = ams.amsaves_usage_range(refModelIDs, audits)
#    bldgMeterDct = deltamtrsvs.get_bldg_meters(pvt.bldg_meters_url, bldgIDs,
#                                               headers)
#    bldgMeterRecordsDct = deltamtrsvs.get_meter_records(auditSpans,
#                                                        bldgMeterDct,
#                                                        pvt.meter_records_url,
#                                                        headers)
#    bldgRatesDct = ams.amsaves_billing_rate(bldgMeterRecordsDct)
#    assert type(bldgRatesDct) == tp.DictType
#    assert len(bldgRatesDct) == len(bldgMeterRecordsDct)
#    rates = []
#    for key, value in bldgRatesDct.iteritems():
#        assert type(key) == tp.StringType
#        assert type(value) == tp.DictType
#        if len(value) > 1:
#            # TODO (eayoungs): Add 'UnitOfMeasure' to amsaves_billing_rate
#            #                  function
#            colNms = ['Bldg ID', '$/kWh','$/Therm']
#            rates.append([key, value['Electric Rate'], value['Gas Rate']])
#        else:
#            colNms = ['Bldg ID', '$/kWh']
#            rates.append([key, value['Electric Rate']])
#
#    df = pd.DataFrame(data=rates, columns=colNms)
#    fname = site +'-billing_rates.csv'
#    with open(fname, 'wb') as outf:
#        outcsv = df.to_csv(fname)
#    assert len(fvCharts) == len(bldgIDs)
