"""The validation module."""

from json import dumps
from soso.strategies.eml.eml import EML
from soso.strategies.spase.spase import SPASE
from soso.utilities import delete_unused_vocabularies


def convert(file: str, strategy: str, **kwargs: dict) -> str:
    """Return SOSO markup for a metadata file and specified strategy.

    :param file:    The path to the metadata file. Refer to the strategy's
                    documentation for a list of supported file types.
    :param strategy:    The conversion strategy to use. Available
                        strategies include: EML and SPASE.
    :param kwargs:  Additional keyword arguments for passing information to
                    the chosen `strategy`. This can help in the case of
                    unmappable properties. See the Notes section in the
                    strategy's documentation for more information.

    :returns: The SOSO graph in JSON-LD format.
    """

    # Load the strategy based on user choice. Pass kwargs, so the strategy can
    # operate on them.
    if strategy.lower() == "eml":
        strategy = EML(file, **kwargs)
    elif strategy.lower() == "spase":
        strategy = SPASE(file, **kwargs)
    else:
        raise ValueError("Invalid choice!")

    # Build the graph
    graph = {
        "@context": {
            "@vocab": "https://schema.org/",
            "dbpedia": "http://dbpedia.org/resource/",
            "gsqtime": "https://vocabs.gsq.digital/object?uri=http://linked.data.gov.au/def/trs",
            "gstime": "http://schema.geoschemas.org/contexts/temporal#",
            "prov": "http://www.w3.org/ns/prov#",
            "provone": "http://purl.dataone.org/provone/2015/01/15/ontology#",
            "rdfs": "https://www.w3.org/2001/sw/RDFCore/Schema/200212/",
            "spdx": "http://spdx.org/rdf/terms#",
            "time": "http://www.w3.org/2006/time#",
            "ts": "http://resource.geosciml.org/vocabulary/timescale/",
            "xsd": "https://www.w3.org/TR/2004/REC-xmlschema-2-20041028/datatypes.html",
        },
        "@id": strategy.get_id(),
        "@type": "Dataset",
        "name": strategy.get_name(),
        "description": strategy.get_description(),
        "url": strategy.get_url(),
        "sameAs": strategy.get_same_as(),
        "version": strategy.get_version(),
        "isAccessibleForFree": strategy.get_is_accessible_for_free(),
        "keywords": strategy.get_keywords(),
        "identifier": strategy.get_identifier(),
        "citation": strategy.get_citation(),
        "variableMeasured": strategy.get_variable_measured(),
        "includedInDataCatalog": strategy.get_included_in_data_catalog(),
        "subjectOf": strategy.get_subject_of(),
        "distribution": strategy.get_distribution(),
        "potentialAction": strategy.get_potential_action(),
        "dateCreated": strategy.get_date_created(),
        "dateModified": strategy.get_date_modified(),
        "datePublished": strategy.get_date_published(),
        "expires": strategy.get_expires(),
        "temporalCoverage": strategy.get_temporal_coverage(),
        "spatialCoverage": strategy.get_spatial_coverage(),
        "creator": strategy.get_creator(),
        "contributor": strategy.get_contributor(),
        "provider": strategy.get_provider(),
        "publisher": strategy.get_publisher(),
        "funding": strategy.get_funding(),
        "license": strategy.get_license(),
        "prov:wasRevisionOf": strategy.get_was_revision_of(),
        "prov:wasDerivedFrom": strategy.get_was_derived_from(),
        "isBasedOn": strategy.get_is_based_on(),
        "prov:wasGeneratedBy": strategy.get_was_generated_by(),
    }

    # Override with user defined properties. Only override properties that
    # exist in the graph, because we don't want to add unrecognized properties.
    for key, value in kwargs.items():
        if key in graph:
            graph[key] = value

    # Remove properties where get methods returned None, so the user is
    # return a clean graph.
    for key, value in list(graph.items()):
        if value is None:
            del graph[key]

    # Remove unused vocabularies from the @context, so the user is returned a
    # clean graph.
    graph = delete_unused_vocabularies(graph)

    return dumps(graph)
