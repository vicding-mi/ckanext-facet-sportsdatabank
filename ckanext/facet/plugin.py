import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class FacetPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IFacets)

    def dataset_facets(self, facets_dict, package_type):
        pprint(facets_dict)
        exit()
        return facets_dict