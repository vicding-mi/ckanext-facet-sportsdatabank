import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import json
import urllib2
from pprint import pprint

log = logging.getLogger(__name__)

def facet_loadjson(orgstr, swap=True):
    '''return json obj'''
    json_data = json.loads(orgstr)
    if swap:
        if json_data['type'] == 'Point':
            json_data['coordinates'] = [[json_data['coordinates'][1], json_data['coordinates'][0]]]
        else:
            json_data['coordinates'] = map(lambda x: list(reversed(x)), reversed(json_data['coordinates']))
    return json_data

def facet_apisearch(q='', rows=999999):
    request = urllib2.Request(
        'http://ckan:5000/api/3/action/package_search?q=%s&rows=%s' % (q, rows))

    # Creating a dataset requires an authorization header.
    # request.add_header('Authorization', apikey)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # Use the json module to load CKAN's response into a dictionary.
    response_dict = json.loads(response.read())
    assert response_dict['success'] is True
    return response_dict['result']

def facet_pprint(obj):
    pprint(obj)

def facet_len(obj):
    return len(obj)

def facet_vars(obj):
    return vars(obj)

class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def dataset_facets(self, facets_dict, package_type):
        return self._facets(facets_dict)

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        return self._facets(facets_dict)

    def _facets(self, facets_dict):
        # Deleted facets
        if 'license_id' in facets_dict:
            del facets_dict['license_id']
        if 'res_format' in facets_dict:
            del facets_dict['res_format']
        if 'tags' in facets_dict:
            del facets_dict['tags']
        # Renamed facets
        if 'groups' in facets_dict:
            del facets_dict['groups']
            # facets_dict['groups'] = 'Communities'
            # del facets_dict['Communities']
        # New facets
        # facets_dict['identifier'] = toolkit._('Identifier')
        # facets_dict['index'] = toolkit._('Index')

        facets_dict['keyword'] = toolkit._('Keywords')
        facets_dict['da_keyword'] = toolkit._('Danish Keywords')
        facets_dict['nl_keyword'] = toolkit._('Dutch Keywords')
        facets_dict['de_keyword'] = toolkit._('German Keywords')

        facets_dict['placeMentioned'] = toolkit._('Place Mentioned')
        facets_dict['placeOfNarration'] = toolkit._('Place of Narration')
        return facets_dict

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'general.css')

    def get_helpers(self):
        '''Register the most_popular_groups() function above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'facet_loadjson': facet_loadjson, 'facet_apisearch': facet_apisearch,
                'facet_pprint': facet_pprint, 'facet_len': facet_len, 'facet_vars': facet_vars,
                }