from typing import List, Dict

import requests
from sgqlc.endpoint.http import HTTPEndpoint
from sgqlc.operation import Operation
# from tabulate import tabulate

import helpling_schema
import db

CandidateList = List[helpling_schema.DecoratedPotentialCandidateEdge]

BASE_URL = "https://www.helpling.de/api/"

DEFAULT_SEARCH_PARAMETERS = {
    "time": "14:00null",
    "date": "07/12/2019",
    "repeat": "true",
    "frequency": "week",
    "duration": 12600,
    "ironing": False,
    "pets": False,
    "materials_required": False,
    "workday_flexibility": False,
    "provider_type": "",
    "notes": ""
}

gql_endpoint = HTTPEndpoint(BASE_URL + "v2/rr", base_headers={
    # CloudFlare blocks the default user agent. Pretend to be IE 6.
    "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"
})


def create_bid(postcode: int, **kwargs) -> str:
    """
    Query the helpling API to create a new bid. Then, set the given parameters (or default values configured in
    ``DEFAULT_SEARCH_PARAMETERS``) to it. This is the first step to scraping offers for a region.
    :param postcode: The postcode for which to request a new bid
    :param kwargs: The parameters to set for the search.
    :return: The bidCode of the created bid
    """
    response = requests.post(BASE_URL + "v1/bids", {"bid[postcode]": postcode, "bid[checkout_version]": 1})
    bid_id = response.json().get("data").get("code")

    if bid_id is None:
        raise Exception("Bid for postcode " + str(postcode) + " could not be created: " + response.text)
    print("Create bid for " + str(postcode) + " (" + bid_id + "): OK")

    op = Operation(helpling_schema.Mutation)
    op.transition_bid_to_provider_selection(**{**DEFAULT_SEARCH_PARAMETERS, **kwargs, "bid_code": bid_id})

    result = gql_endpoint(op).get("data").get("transitionBidToProviderSelection")

    if result.get("success") is False:
        raise Exception("Bid " + bid_id + " could not be parametrized: " + result.get("errors"))
    print("Parametrize bid " + bid_id + ": OK")

    return bid_id


def get_candidates_for_bid(bid_id: str) -> List[helpling_schema.DecoratedPotentialCandidateEdge]:
    """
    Query the API for all (i.e. the first 1000) candidates for a given bid. The bid must have been parametrized already.
    Note that not all fields are actually requested from the backend.
    :param bid_id: Id of an already-parametrized bid
    :return: First 1000 candidates available for the bid
    """
    op = Operation(helpling_schema.Query)

    candidates = op.customer_bid(code=bid_id).potential_candidates(first=1000)

    candidates.edges.node.price_per_hour()

    provider = candidates.edges.node.provider
    provider.__fields__("id", "firstname", "shortname", "default_profile_image", "pets", "windows", "ironing",
                        "ratings_received_count", "verification_level", "documents", "performed_cleanings_count",
                        "language_skills", "instabook_enabled")
    provider.avg_rating.total()
    provider.experience.__fields__()
    provider.distance_to_bid(bid_code=bid_id)

    data = gql_endpoint(op)

    return (op + data).customer_bid.potential_candidates.edges


def get_bid(bid_id: str) -> helpling_schema.CustomerBid:
    """
    Get basic information on the given bid.
    :param bid_id: Id of a bid, parametrized or not.
    :return:
    """
    op = Operation(helpling_schema.Query)

    op.customer_bid(code=bid_id).__fields__("code", "duration", "start_time")

    data = gql_endpoint(op)
    return (op + data).customer_bid


def get_candidates(postcodes: List[int], parameters: Dict = None) -> List[CandidateList]:
    """
    Find potential candidates for a list of postcodes.
    :param postcodes:
    :param parameters: see DEFAULT_SEARCH_PARAMETERS
    """
    parameters = parameters or {}
    for postcode in postcodes:
        yield get_candidates_for_bid(create_bid(postcode, **parameters))


if __name__ == "__main__":
    postcodes = [10115, 14059]
    params = {"date": "07/12/2019"}
    for i, c in enumerate(get_candidates(postcodes, params)):
        as_dicts = [{**c.node.provider.__dict__,"postcode": postcodes[i],"date": params["date"],"price_per_hour": c.node.price_per_hour, "avg_rating": c.node.provider.avg_rating.total, "experience_description": c.node.provider.experience.experience_description, "experience_headline": c.node.provider.experience.experience_headline} for c in c]
        for d in as_dicts:
            d.pop("__selection_list__")
            d.pop("__fields_cache__")
            d.pop("__json_data__")
            d.pop("experience")

        # print(as_dicts)
        db.insert_entries(as_dicts)