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
sites = [pvt.Middlesboro, pvt.FDL, pvt.HJSMS]


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
        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                    headers)
        modelIDs = []
        for key in modelsJsonDct:
            modelIDs.append(str(key))
        (modelIDs, compDct, jModDct) = deltamtrsvs.get_model_comparisons(
                                                                comparison_url,
                                                                modelsJsonDct,
                                                                headers)
        usesDf = ams.amsaves_results(compDct, jModDct, bldgIDct)

        fname = site+'-results.csv'
        with open(fname, 'wb') as outf:
            outcsv = usesDf.to_csv(fname)

    assert isinstance(usesDf, pd.DataFrame)
    assert usesDf.shape[1] == 13
    # assert usesDf.shape[0] == compLen


def test_am_saves_audit():
    """ Pass the results of get_model_audits function, confirm DataFrame
        returned in requested results format for the 'America Saves!' program
        (write contents to .CSV file for review) """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons, jModDct) = deltamtrsvs.get_model_comparisons(
                                                                comparison_url,
                                                                modelsJsonDct,
                                                                headers)
        (refModelIDs, audits) = deltamtrsvs.get_model_audits(audit_url,
                                                             modelIDs, headers)
        combinedUsageDct = ams.am_saves_audit(refModelIDs, audits)

        assert isinstance(combinedUsageDct, dict)
        assert len(combinedUsageDct) == len(refModelIDs)

        for refModelAdtID in refModelIDs:
            df = combinedUsageDct[refModelAdtID]
            # span = datetime.date.datefromtimestamp(df['Per. Start'])
            # print(span.max)

            fname = refModelAdtID + '-audit.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

            assert isinstance(combinedUsageDct[refModelAdtID], pd.DataFrame)


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
        flags = ams.amsaves_flags(fvCharts)
        # TODO (eayoungs): Needs more robust assertions
        assert [type(flag)==tp.StringType for flag in flags]

        siteFlags = []
        for flag in flags:
            bldgFlags = []
            if flag['Occupant Load'][0] == 'A' or \
                flag['Occupant Load'][0] == 'B' or \
                flag['Occupant Load'][0] == 'C':
                intrnElec = flag['Occupant Load'][0]
                ultrHighIntExt = ''
            elif flag['Occupant Load'][0] == 'O' or \
                flag['Occupant Load'] == 'P':
                ultrHighIntExt = flag['Occupant Load'][0]
                intrnElec = ''
            # TODO (eayoungs): Add exception handling for final *else*
            #                  statement
            if flag['Summer Gas Use'][1] == "High":
                highGasBaseLd = "M"
            else: highGasBaseLd = ""

            bldgFlags = [intrnElec, ultrHighIntExt,
                         flag['Controls Heating'][0],
                         flag['Shell Ventilation'][0],
                         flag['Controls Cooling'][0],
                         flag['Cooling Efficiency'][0],
                         flag['Data Consistency'][0],
                         highGasBaseLd]

            siteFlags.append(bldgFlags)
            assert len(bldgFlags) == 8
            assert [type(bldgFlag) == tp.StringType for bldgFlag in bldgFlags]
            assert [len(bldgFlag) == 1 for bldgFlag in bldgFlags]
    
            colNms = ['Int. Elec.', 'Ultra-High Elec.', 'Excessive Htg.',
                      'Shell & Vent.', 'Excessive Clg', 'Inefficient Clg',
                      'Erratic Operation', 'High Gas Eqp.']
            df = pd.DataFrame(data=siteFlags, columns=colNms)

            fname = site+'-flags.csv'
            with open(fname, 'wb') as outf:
                outcsv = df.to_csv(fname)

    assert len(siteFlags) == len(flags)
    assert len(fvCharts) == len(bldgIDs)


def test_amsaves_usage_range():
    """ Pass the results of get_model_audits function, confirm returned
        dictionary in requested results format for the 'America Saves!' program
        """

    for site in sites:
        bldgIDct = deltamtrsvs.get_property_bldgs(properties_url, site,
                                                  headers)
        bldgIDs = []
        for key in bldgIDct:
            bldgIDs.append(str(key))

        modelsJsonDct = deltamtrsvs.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons, jModDct) = deltamtrsvs.get_model_comparisons(
                                                                comparison_url,
                                                                modelsJsonDct,
                                                                headers)
        (refModelIDs, audits) = deltamtrsvs.get_model_audits(audit_url,
                                                             modelIDs, headers)
        auditSpans = ams.amsaves_usage_range(refModelIDs, audits)
        assert type(auditSpans) == tp.DictType
        # assert len(auditSpans) == len(refModelIDs)

        spans = []
        for key, value in auditSpans.iteritems():
            assert type(key) == tp.StringType
            assert type(value) == tp.DictType
            vals = []
            colNms = []
            if len(auditSpans[key]) == 2:
                vals = [key, auditSpans[key]['E. Per. Begin'],
                        auditSpans[key]['E. Per. End']]
                colNms = ['Ref. Model ID', 'E. Per. Begin', 'E. Per. End']
            elif len(auditSpans[key]) == 4:
                vals = [key, auditSpans[key]['E. Per. Begin'],
                        auditSpans[key]['E. Per. End'],
                        auditSpans[key]['G. Per. Begin'],
                        auditSpans[key]['G. Per. End']]
                colNms = ['Ref. Model ID', 'E. Per. Begin', 'E. Per. End',
                          'G. Per. Begin', 'G. Per. End']
            # TODO (eayoungs): Add exception handling and include in final
            #                  *else* statement
            spans.append(vals)
            df = pd.DataFrame(data=spans, columns=colNms)
            
        fname = site +'-use_ranges.csv'
        with open(fname, 'wb') as outf:
            outcsv = df.to_csv(fname)


def test_amsaves_billing_rate():
    """ Pass the results of get_meter_records, confirm results of
        amsaves_billing_rate function returns expected data types & structures
        """
