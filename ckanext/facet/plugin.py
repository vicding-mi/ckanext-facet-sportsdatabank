from ckan.common import config
from ckan.lib import helpers as h
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
import json
import urllib2
import copy
from pprint import pprint

log = logging.getLogger(__name__)


def facet_get_extra_data_field(extras, field, lang=False):
    if not extras:
        return None

    extras_list = extras
    if extras_list and isinstance(extras_list, list):
        if lang:
            for item_dict in extras_list:
                k = item_dict.get('key').encode('utf-8')
                v = item_dict.get('value').encode('utf-8')
                if field in k:
                    return k, v
        else:
            for item_dict in extras_list:
                k = item_dict.get('key').encode('utf-8')
                v = item_dict.get('value').encode('utf-8')
                if k == field:
                    return k, v
    return None


def facet_get_similar_fields_from_extras(extras, field):
    result = list()
    if not extras:
        return None

    extras_list = extras
    if extras_list and isinstance(extras_list, list):
        for item_dict in extras_list:
            k = item_dict.get('key').encode('utf-8')
            v = item_dict.get('value').encode('utf-8')
            if field in k:
                result.append((k, v))
        return result
    return None


def facet_build_nav_main(*args):
    ''' build a set of menu items.

    args: tuples of (menu type, title) eg ('login', _('Login'))
    outputs <li><a href="...">title</a></li>
    '''
    output = ''
    for item in args:
        menu_item, title = item[:2]
        if len(item) == 3 and not h.check_access(item[2]):
            continue
        output += _make_menu_item(menu_item, title, class_='hcIsNav')
    return output


def _make_menu_item(menu_item, title, **kw):
    ''' build a navigation item used for example breadcrumbs

    outputs <li><a href="..."></i> title</a></li>

    :param menu_item: the name of the defined menu item defined in
    config/routing as the named route of the same name
    :type menu_item: string
    :param title: text used for the link
    :type title: string
    :param **kw: additional keywords needed for creating url eg id=...

    :rtype: HTML literal

    This function is called by wrapper functions.
    '''
    menu_item = h.map_pylons_to_flask_route_name(menu_item)
    _menu_items = config['routes.named_routes']
    if menu_item not in _menu_items:
        raise Exception('menu item `%s` cannot be found' % menu_item)
    item = copy.copy(_menu_items[menu_item])
    item.update(kw)
    needed = item.pop('needed')
    # log.debug('Items is: {}'.format(item))
    for need in needed:
        if need not in kw:
            raise Exception('menu item `%s` need parameter `%s`'
                            % (menu_item, need))
    link = h._link_to(title, menu_item, suppress_active_class=True, **item)
    return link


def facet_loadjson(orgstr, swap=True):
    '''return json obj'''
    json_data = json.loads(orgstr)
    if swap:
        if json_data['type'] == 'Point':
            json_data['coordinates'] = [[json_data['coordinates'][1], json_data['coordinates'][0]]]
        else:
            json_data['coordinates'] = map(lambda x: list(reversed(x)), reversed(json_data['coordinates']))
    return json_data


def facet_dumpjson(orgstr):
    return json.dumps(orgstr)

# def facet_nl2br(orgstr):


def facet_apisearch(q='', rows=99999):
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
        return len(obj) if obj else 0


def facet_vars(obj):
    return vars(obj)


def facet_capitalize(string):
    return string.capatalize


def facet_orgcount(org_id):
    request = urllib2.Request(
        'http://ckan:5000/api/3/action/organization_show?id=%s' % org_id )
    response = urllib2.urlopen(request)
    assert response.code == 200

    response_dict = json.loads(response.read())
    if response_dict['success'] is True:
        log.warning('%s has %s datasets' % (org_id, response_dict['result']['package_count']))
        if response_dict['result']['package_count'] > 40000:
            return 1
        else:
            return 2
        return response_dict['result']['package_count']
    else:
        return 0


def no_registering(context, data_dict):
    return {
        'success': False,
        'msg': toolkit._('Registration disabled. ')
    }


class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IRoutes, inherit=True)

    def get_auth_functions(self):
        return {
            'user_create': no_registering
        }

    def dataset_facets(self, facets_dict, package_type):
        return self._facets(facets_dict)

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        return self._facets(facets_dict)

    def _facets(self, facets_dict):
        # Deleted some default facets
        if 'license_id' in facets_dict:
            del facets_dict['license_id']
        if 'res_format' in facets_dict:
            del facets_dict['res_format']
        if 'tags' in facets_dict:
            del facets_dict['tags']
        if 'groups' in facets_dict:
            del facets_dict['groups']

        # Rename some default facets
        if 'notes' in facets_dict:
            facets_dict['notes'] = toolkit._('Notes')

        # Create custom facets
        ''' TODO: Add custom facet here
        It is adding ISEBEL facets now, should be adapted. 
        The command to add facets:
        facets_dict[facet_machine_name] = toolkit._(Facet Display Name)
        '''
        facets_dict['keyword'] = toolkit._('Keywords')

        return facets_dict

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_public_directory(config, 'public')
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'facet')

    def get_helpers(self):
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'facet_loadjson': facet_loadjson, 'facet_apisearch': facet_apisearch,
                'facet_pprint': facet_pprint, 'facet_len': facet_len, 'facet_vars': facet_vars,
                'facet_capitalize': facet_capitalize, 'facet_orgcount': facet_orgcount,
                'facet_build_nav_main': facet_build_nav_main, 'facet_dumpjson': facet_dumpjson,
                'facet_get_extra_data_field': facet_get_extra_data_field,
                'facet_get_similar_fields_from_extras': facet_get_similar_fields_from_extras
                }

    def before_map(self, map):
        """This IRoutes implementation overrides the standard
        ``/dataset`` behaviour with a custom controller.  You
        might instead use it to provide a completely new page, for
        example.
        Note that we have also provided a custom register form
        template at ``theme/templates/user/register.html``.
        """
        # Hook in our custom user controller at the points of creation
        # and edition.

        ######### map function ############
        # this code is to show the map with all datasets #
        # if we have geolocation or geotags, a map can be plotted using this controller #
        # It hooks into CKAN replace its default controller and replace with custom controller which is defined
        # in the controller.py

        # map.connect('/dataset',
        #             controller='ckanext.facet.controller:CustomPakcageController',
        #             action='search')

        return map
