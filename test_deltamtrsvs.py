#!/usr/bin/env python

__author__ = "Eric Allen Youngson"
__email__ = "eric@scneco.com"
__copyright__ = "Copyright 2015, Succession Ecological Services"
__license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the DeltaMeter
    Services API * deltameterservices.com * """

import deltamtrsvs as dms_api
import private as pvt
import types as tp
import re


headers = pvt.headers
properties_url = pvt.properties_url
model_url = pvt.model_url
comparison_url = pvt.comparison_url
sites = [pvt.FDL, pvt.HJSMS, pvt.Midlesboro]

def test_get_property_bldg_IDs():
    """ Pass a sites[0] id & header, confirm the fuction returns the expected bldg IDs """
    for site in sites:
        bldgIDs = dms_api.get_property_bldg_IDs(properties_url, site, headers)
    
        assert type(bldgIDs) == tp.ListType
        assert len(bldgIDs) > 0
        assert [type(bldgID)==tp.StringType for bldgID in bldgIDs]
        assert [re.match('\d{4}', bldgID) for bldgID in bldgIDs]

def test_get_bldg_models():
    """ Pass a list of bldg ids & header, confirm the fuction returns the
        expected valid bldg IDs """

    for site in sites:
        bldgIDs = dms_api.get_property_bldg_IDs(properties_url, site, headers)
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)

        assert type(valBldgIDs) == tp.ListType
        assert len(valBldgIDs) >= len(valBldgIDs)
        assert [type(valBldgID)==tp.StringType for valBldgID in valBldgIDs]
        assert [re.match('\d{4}', valBldgID) for valBldgID in valBldgIDs]

def test_get_model_comparisons():
    """ Pass a list of bldg ids & header, confirm the fuction returns the
        expected valid bldg IDs """

    for site in sites:
        bldgIDs = dms_api.get_property_bldg_IDs(properties_url, site, headers)
        (json_models, valBldgIDs) = dms_api.get_bldg_models(model_url, bldgIDs,
                                                            headers)
        (modelIDs, comparisons) = dms_api.get_model_comparisons(comparison_url,
                                                                json_models,
                                                                headers)

        assert type(modelIDs) == tp.ListType
        assert len(modelIDs) == 2*len(valBldgIDs)
        assert [type(modelID)==tp.StringType for modelID in modelIDs]
        assert [re.match('\d{4}', modelID) for modelID in modelIDs]

