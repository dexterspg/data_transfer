

RELATIONSHIP_MAPPING = {

    ("LocationId", "PremiseId") : "location_premise",
    ("PremiseId", "LeaseId") : "premise_lease",
    ("LeaseId", "TermId") : "lease_term",

}


HIERARCHY = {
    "LocationId": ['PremiseId'],
    "PremiseId": ['LeaseId'],
    "LeaseId": ['TermId'],

}
