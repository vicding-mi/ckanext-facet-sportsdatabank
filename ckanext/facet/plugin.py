import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)

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
        # Renamed facets
        if 'groups' in facets_dict:
            facets_dict['groups'] = 'Communities'
        # New facets
        facets_dict['identifier'] = toolkit._('Identifier')
        facets_dict['index'] = toolkit._('Index')
        facets_dict['keyword'] = toolkit._('Keyword')
        facets_dict['placeMentioned'] = toolkit._('Place Mentioned')
        facets_dict['placeOfNarration'] = toolkit._('Place Of Narration')
        return facets_dict