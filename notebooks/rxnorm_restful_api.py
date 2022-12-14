class RXNORM_RESTFUL_API:
    def __init__(self):
        # base URL
        self.__ROOT = "https://rxnav.nlm.nih.gov/REST/"
        # approximate term
        self.APPROX_TERM = "approximateTerm?term={}&maxEntries=1&option=0"
        self.RXCUI_BY_SNOMED = "rxcui?idtype=snomedct&id={}&allsrc=0"
        self.PRIMARY_INGREDIENT = "rxcui/{}/allrelated?"
        self.RXCUI_ALLCODES = "rxcui/{}/allProperties?prop=codes"
        self.RXCUI_ALLNAMES = "rxcui/{}/allProperties?prop=names"
        

    def get_approx_term(self, term):
        return self.__ROOT + self.APPROX_TERM.format(term)
    
    def get_rxcui_by_snomed(self, snomed):
        return self.__ROOT + self.RXCUI_BY_SNOMED.format(snomed)
    
    def get_primary_ingredient(self, rxcui):
        return self.__ROOT + self.PRIMARY_INGREDIENT.format(rxcui)

    def get_rxcui_codes(self, rxcui):
        return self.__ROOT + self.RXCUI_ALLCODES.format(rxcui)
    
    def get_rxcui_names(self, rxcui):
        return self.__ROOT + self.RXCUI_ALLNAMES.format(rxcui)
