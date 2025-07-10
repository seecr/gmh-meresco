# GMH Meresco

De Gemeenschappelijke Metadata Harvester (GMH) van de [Koninklijke Bibliotheek](https://www.kb.nl) is gebaseerd op de open source library [Meresco](https://github.com/orgs/seecr/repositories?q=meresco). De GMH en de libraries worden onderhouden door [Seecr](https://seecr.nl)

# Services van GMH Meresco

GMH Meresco heeft de volgende services:
- Gateway, ontvangt records aangeleverd door de harvester. De records worden genormaliseerd naar NL\_DIDL en gevalideerd.
- API, haalt de genormaliseerde records op bij de Gateway op en biedt deze als OAI service aan.
- Resolver, haalt de genormaliseerde records op bij de Gateway en registreert de NBN identifier en object locatie bij de GMH Registration Service

# Services onderdeel van GMH

Deze services zijn onderdeel van de GMH dienst maar niet van dit project.

- [Metastreams Harvester](https://github.com/seecr/metastreams-harvester) een OAI-PMH harvester die records harvest bij repositories.
- GMH Resolver UI, de persistent resolver voor het opzoeken van NBN identifiers. [Resolver UI](https://persistent-identifier.nl)
- GMH Registration Service, een dienst om via een API call data toe te voegen aan de resolver service. [OPENAPI Beschrijving](https://persistent-identifier.nl/gmh-registration-service/api/v1/openapi.yaml)


