import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)

    def dataset_facets(self, facets_dict, package_type):
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
        facets_dict['author'] = toolkit._('Author')
        facets_dict['extras_Discipline'] = toolkit._('Discipline')
        facets_dict['extras_Language'] = toolkit._('Language')
        facets_dict['extras_Origin'] = toolkit._('Origin')
        facets_dict['extras_PublicationYear'] = toolkit._('Publication Year')
        facets_dict['narrator'] = toolkit._('Narrator')
        return facets_dict