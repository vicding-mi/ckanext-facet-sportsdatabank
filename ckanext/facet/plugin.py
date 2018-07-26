import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IConfigurer)

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