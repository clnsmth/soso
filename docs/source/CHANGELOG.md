# CHANGELOG



## v0.6.1 (2025-10-23)


### Bug fixes

* fix: fix reference to soso PyPI listing ([`71c4781`](https://github.com/clnsmth/soso/commit/71c47816f8fe4d4fd9a7b53cc5aa31642b4733ff)) 

## v0.6.0 (2025-10-23)


### Continuous integration

* ci: check for release before uploading to PyPI ([`a2ecce9`](https://github.com/clnsmth/soso/commit/a2ecce9c645467179e246117b18a408b37dcab1d)) 

### Features

* feat: support bundled and local SHACL shape files (#302) ([`1e06fc4`](https://github.com/clnsmth/soso/commit/1e06fc45c4990985ce8f9d9e31a1853ba7747da9)) 
* feat: implement daiquiri for structured logging (#302) ([`cedf21f`](https://github.com/clnsmth/soso/commit/cedf21fb0638d147f8a97aa33f8babaf11b4556d)) 
* feat: reorganize validation code into dedicated module (#302) ([`52e285c`](https://github.com/clnsmth/soso/commit/52e285c428755679dedc76781cfa9ac3b7d6b2fe)) 

### Refactoring

* refactor: group validation code into a single file module (#302) ([`bc9ba6f`](https://github.com/clnsmth/soso/commit/bc9ba6f2c79fe3d7caa81ad9fd65ebdb2a9718b1)) 
* refactor: return dictionary with provenance and report (#302) ([`c2bedd9`](https://github.com/clnsmth/soso/commit/c2bedd9fbaa8558706dfad2701f63e71edeee718)) 

## v0.5.4 (2025-10-07)


### Bug fixes

* fix: address suffixes and first name initials ([`5041016`](https://github.com/clnsmth/soso/commit/5041016883d10bb16f54e54c2a8d1e70af78ae18)) 

## v0.5.3 (2025-09-02)


### Bug fixes

* fix: update sidebar HTML _template/ reference ([`8217482`](https://github.com/clnsmth/soso/commit/8217482fdb4cd59121de0a86e835d473cb0fbcad)) 

## v0.5.2 (2025-09-02)


### Bug fixes

* fix: bump Zenodo release workflow ([`828fa5f`](https://github.com/clnsmth/soso/commit/828fa5f3b693c2c20c8366f457a3e43531fd35bb)) 

### Continuous integration

* ci: fix .zenodo.json contributor types ([`ef66b31`](https://github.com/clnsmth/soso/commit/ef66b31788ed2cff9b5ae667a103b04827a3ea62)) 

## v0.5.1 (2025-09-02)


### Bug fixes

* fix: conditionally run release steps in workflow ([`3c83694`](https://github.com/clnsmth/soso/commit/3c83694a649fdf5e14a44b2f602f42591386dddd)) 

### Continuous integration

* ci: revert to previous PyPI release method ([`d470cbc`](https://github.com/clnsmth/soso/commit/d470cbc5e37c4f5c6249fbede2a5f52713699cfd)) 
* ci: add role and type to .zenodo.json contributors ([`ef32646`](https://github.com/clnsmth/soso/commit/ef326468d601b2f1dda3db6312d093d1168c9ac5)) 
* ci: use Trusted Publishing in CD ([`1508e28`](https://github.com/clnsmth/soso/commit/1508e282191ff5154e9e78026e1ab07bd5e4fb02)) 

## v0.5.0 (2025-09-02)


### Bug fixes

* fix: ensure temporary SPASE file is properly closed ([`8532d89`](https://github.com/clnsmth/soso/commit/8532d890f18a5b7737f0eea467d4e2a7f75a1107)) 
* fix: standardize MIME type guessing with fallback (#263) ([`bb2906f`](https://github.com/clnsmth/soso/commit/bb2906f93cf5775583b09e853229122e6aa3af53)) 
* fix: use platform-agnostic pathlib.Path type (#261) ([`7db7198`](https://github.com/clnsmth/soso/commit/7db719843a374338f8a3c6f21e6c0c4c87284737)) 
* fix: subject/object order in EML SSSOM is reversed (#240) ([`990ab8a`](https://github.com/clnsmth/soso/commit/990ab8aa22e4e05960767558748150eabb150d12)) 

### Build system

* build: remove deprecated Poetry dev dependencies (#255) ([`d4615ab`](https://github.com/clnsmth/soso/commit/d4615abe65f770cf901e34597d78bb4db7818c1f)) 

### Continuous integration

* ci: add to PyPI on release ([`f1e5c24`](https://github.com/clnsmth/soso/commit/f1e5c2481f7d244ae70cda2ee4d68e54b6cd51fc)) 
* ci: add CODEOWNERS to streamline maintenance (#235) ([`bd90e6a`](https://github.com/clnsmth/soso/commit/bd90e6ac94b0d25ef7bf4e325d5c4ab3da47bcb7)) 
* ci: run CI on pull requests to any branch ([`aa2454e`](https://github.com/clnsmth/soso/commit/aa2454e40a3b0d7a7212648adaf3d67a6da3a8c8)) 
* ci: remove redundant Poetry and package installation (#257) ([`25acabd`](https://github.com/clnsmth/soso/commit/25acabdf007f58d4be9c2844b2f5a7f0b4135c9c)) 
* ci: harmonize black formatting versions (#252) ([`e57d7b4`](https://github.com/clnsmth/soso/commit/e57d7b4272e475534d72b732cafbbdff619cd350)) 

### Documentation

* docs: add missing docstring ([`d7eaea0`](https://github.com/clnsmth/soso/commit/d7eaea0dd16f44e3f000abd4e09dbcd99be23da1)) 
* docs: remove text from logo to be DRY ([`9b98e21`](https://github.com/clnsmth/soso/commit/9b98e21d288def757b94ddc822c8f28c7027948b)) 
* docs: add example vignette for more complex cases (#237) ([`f76cbda`](https://github.com/clnsmth/soso/commit/f76cbda58e22ab266cfb980d6c3dabef6008788c)) 
* docs: support unrecognized properties in SOSO records (#243) ([`adcf6af`](https://github.com/clnsmth/soso/commit/adcf6af615b73b9b7fb54fe5ae26bbbecc582456)) 
* docs: accommodating shared infrastructure code (#237) ([`913deb5`](https://github.com/clnsmth/soso/commit/913deb5f780e98db29d9a099209043e47a16dffd)) 
* docs: add Zenodo DOI badge (#241) ([`e2b730b`](https://github.com/clnsmth/soso/commit/e2b730be0f575120125868b349e8b35f9b2c1987)) 
* docs: update the documentation on skipping tests ([`ca734f4`](https://github.com/clnsmth/soso/commit/ca734f41d74e0880d5a321ccb3c59ef993042c0f)) 
* docs: fix sidebar, changelog, and logo references ([`eac4ff1`](https://github.com/clnsmth/soso/commit/eac4ff1bb93d77385c1dff7083f7273c2951fbdc)) 
* docs: make minor editing for consistency ([`4133086`](https://github.com/clnsmth/soso/commit/4133086df3a5bd3e3a06278a27ba57b08f367f20)) 
* docs: add a logo for branding ([`40b12b8`](https://github.com/clnsmth/soso/commit/40b12b845c16956cebc6983cd467229af91ee8f0)) 
* docs: improve the visibility of the Code of Conduct (#239) ([`fead0ee`](https://github.com/clnsmth/soso/commit/fead0eeec0ce629dce0755850b6245e026e23095)) 
* docs: enhance contributing guidelines for clarity (#238) ([`1565297`](https://github.com/clnsmth/soso/commit/156529762c5a6075b6e38077b40b030b7be2a1e8)) 
* docs: refine project scope for clarity and focus (#236) ([`4cf2b23`](https://github.com/clnsmth/soso/commit/4cf2b23b1a0efc9339e6a7d7df1026ffa1b68bbc)) 
* docs: update pyproject.toml with SPASE authors (#234) ([`abf7963`](https://github.com/clnsmth/soso/commit/abf796318da0dbb9126d795fc56305be0e2c20d7)) 

### Features

* feat: complete SPASE strategy implementation ([`df49632`](https://github.com/clnsmth/soso/commit/df49632279933b477e6b9e49f961b1874b93469d)) 

### Refactoring

* refactor: add strategy specific directories (#242) ([`d331dac`](https://github.com/clnsmth/soso/commit/d331dac435759e0d914c73dc7c9094697a79cae7)) 
* refactor: ensure SPASE strategy passes linting ([`5eca6bd`](https://github.com/clnsmth/soso/commit/5eca6bde642c8ea4b3e8c8cb069ed198a8691b7a)) 

### Testing

* test: remove unused argument to fix pylint issue ([`38ad988`](https://github.com/clnsmth/soso/commit/38ad9886dd71acc895da3561478c15ae78362705)) 
* test: fix pytest.skipif declarations ([`595b2a5`](https://github.com/clnsmth/soso/commit/595b2a5f0e362c206aa79e7e683f316ef95b441e)) 

## v0.4.0 (2025-01-17)


### Bug fixes

* fix: translate docstrings into comments (#213, #222) ([`ba74a46`](https://github.com/clnsmth/soso/commit/ba74a463cb3bd86869114c7eb2c19b2a24520e12)) 

### Build system

* build: configure Read the Docs for explicit path to config.py ([`a1a54c0`](https://github.com/clnsmth/soso/commit/a1a54c010ac626033c75369e59fb6cf8b90bf2dc)) 

### Features

* feat: add spatial coverage support for SPASE (#213) ([`4c3154b`](https://github.com/clnsmth/soso/commit/4c3154b8b4dbbf75f109a959ca145dc6a1b64f57)) 

### Refactoring

* refactor: address Pylint issues in SPASE strategy integrations ([`e793798`](https://github.com/clnsmth/soso/commit/e793798a252a28f4c285c8a4f8c1817d84ae8df5)) 

## v0.3.0 (2024-12-12)


### Bug fixes

* fix: prevent invalid property assignments in SOSO records (#218) ([`de3b430`](https://github.com/clnsmth/soso/commit/de3b4307146207d96085408d3e322a92efd6b2dd)) 
* fix: correct XML declaration in example SPASE file (#213) ([`599807e`](https://github.com/clnsmth/soso/commit/599807e18b8b05200c37413e1be8674c45fe2ffb)) 
* fix: enhance `generate_citation_from_doi` for invalid input handling ([`ceb6706`](https://github.com/clnsmth/soso/commit/ceb6706b225ec75e3146586ca60c1dd6a7dc8236)) 

### Features

* feat: first set of mapping implementation #213 ([`6b07636`](https://github.com/clnsmth/soso/commit/6b0763649922fbe884bf4db8756622a493e98e14)) 
* feat: establish SPASE conversion strategy (#213) ([`3ce2b25`](https://github.com/clnsmth/soso/commit/3ce2b2526dffac806d4d63eef6981e1fe5253dc3)) 
* feat: add SPASE empty file #213 ([`b4f5ad1`](https://github.com/clnsmth/soso/commit/b4f5ad19d432c0ccf9e1925e4771aa568c3e445e)) 
* feat: create example spase.xml for testing (#213) ([`cbef3a1`](https://github.com/clnsmth/soso/commit/cbef3a16849ddbda784028d5efb37cb3c3ab97ac)) 

### Testing

* test: add missing `@id` property to test fixture (#213) ([`5d980c8`](https://github.com/clnsmth/soso/commit/5d980c83df8e2738f86af23de55f941d49be3562)) 

## v0.2.0 (2024-09-27)


### Bug fixes

* fix: add @id for Organization type in EML strategy ([`0765e08`](https://github.com/clnsmth/soso/commit/0765e08703580c547881a47bfdbe8720bc27a499)) 
* fix: add @id for MonetaryGrant type in EML strategy ([`cdbdafd`](https://github.com/clnsmth/soso/commit/cdbdafd3107a965b4ae7b21b346d8287a04a5477)) 
* fix: incorrect comparison of bytes and string objects ([`f883bfd`](https://github.com/clnsmth/soso/commit/f883bfda01f8b753abc8f8e93dcb00a3a4af3f8d)) 
* fix: add @id for identifier of Person and Org type in EML strategy ([`98887ee`](https://github.com/clnsmth/soso/commit/98887eeaf1bddd238fc519a81f42f8d78921e637)) 

### Continuous integration

* ci: fix code coverage report generation ([`3bed01d`](https://github.com/clnsmth/soso/commit/3bed01dd29fe28db41bdaf0b18aac7046d329485)) 

### Documentation

* docs: enforce `schema:URL` type for `@id` in EML strategy SSSOM ([`9a5149d`](https://github.com/clnsmth/soso/commit/9a5149dfc9ca372212c64ee4e1ec8bd17b07a5d2)) 
* docs: update SSSOM file for EML strategy ([`97ad0b7`](https://github.com/clnsmth/soso/commit/97ad0b770b409da0e2260fba1d3ec15d7a8fa3a4)) 
* docs: update codecov badge to reflect current coverage ([`8f70c10`](https://github.com/clnsmth/soso/commit/8f70c10241653107c55460e724831e235e6d2f2c)) 
* docs: correct branch reference for codecov and documentation ([`490d382`](https://github.com/clnsmth/soso/commit/490d382b0fe7635a5f825acf65dce53b82635a22)) 
* docs: enhance README with installation and quickstart ([`851ed49`](https://github.com/clnsmth/soso/commit/851ed4986c63bd850bd9bf288981ec776ab30eb1)) 
* docs: correct _templates/ structure for proper rendering ([`5a3e878`](https://github.com/clnsmth/soso/commit/5a3e87869fada55248a260d17f8545c03e304d25)) 

### Features

* feat: add @id for Dataset type in EML strategy ([`b41a572`](https://github.com/clnsmth/soso/commit/b41a572009688f19e929e5516fbf9efd3a999a16)) 
* feat: add @id for Dataset type in strategy interface ([`bf86774`](https://github.com/clnsmth/soso/commit/bf86774449bf723f62ce547bb639fab52f62350a)) 
* feat: implement heuristic URL validation utility ([`0c7729f`](https://github.com/clnsmth/soso/commit/0c7729fbd20219cfc4f122336b862e61e6d14291)) 

## v0.1.0 (2024-07-30)


### Bug fixes

* fix: adjust mapping implementations ([`df72499`](https://github.com/clnsmth/soso/commit/df72499c58a6219968481fd9f9f2a5a4ab856e92)) 
* fix: future deprecation warning ([`5a74275`](https://github.com/clnsmth/soso/commit/5a742759b91e99b2baa0f5fd990ebbbca7c21022)) 
* fix: geo time `xsd:decimal` could be string ([`635d0ed`](https://github.com/clnsmth/soso/commit/635d0ed62252025ce212dad2c80f5ff71ea4e8e3)) 
* fix: add missing contributors ([`daaf1e3`](https://github.com/clnsmth/soso/commit/daaf1e3e085f898a9a2b5e32a5ba203288212eb3)) 
* fix: limit textual properties to 5000 characters ([`c53bce9`](https://github.com/clnsmth/soso/commit/c53bce99977b1871f6eb1fad5699893e3d5ddb9f)) 
* fix: get_description returns incomplete value ([`ea993a3`](https://github.com/clnsmth/soso/commit/ea993a37cca23b4394a9514fddb3d20aee0a409c)) 
* fix: get_checksum errors on no checksum value ([`f64de9c`](https://github.com/clnsmth/soso/commit/f64de9c7f8ef0b21cdcbd256bc7fd2108ebb5942)) 
* fix: get_content_size errors when unit not present ([`f85f972`](https://github.com/clnsmth/soso/commit/f85f9728a59bfee3e8d806f8b85f247c01d26153)) 
* fix: strategy_instance returns class, not PosixPath ([`16c205d`](https://github.com/clnsmth/soso/commit/16c205dc399f386593972094d390fd5f8a96f4b5)) 
* fix: don't list nested properties as "unmappable" ([`316c525`](https://github.com/clnsmth/soso/commit/316c525bbb3f4cf2ee60dfa05d3692dc41098b59)) 
* fix: consistent representation of metadata acronyms ([`fad2836`](https://github.com/clnsmth/soso/commit/fad2836ae82f14347e9ad344eda4e08db78b55fe)) 
* fix: convert SPDX license URL to URI for EML ([`dea8bfe`](https://github.com/clnsmth/soso/commit/dea8bfef18051c8369bb284d43b4e1bacfe86d34)) 
* fix: add missing prefixes to top-level properties ([`88e956f`](https://github.com/clnsmth/soso/commit/88e956febf0f8d55bdd019af50df9cac14219b02)) 
* fix: use contentUrl not contentURL ([`158330e`](https://github.com/clnsmth/soso/commit/158330e783618c22b9478a053a1616fbf2e4dbda)) 
* fix: correct typo in EML SSSOM ([`114080b`](https://github.com/clnsmth/soso/commit/114080b782b7a74647b2a7257309de916e4c0679)) 
* fix: differentiate persons from organizations (#5) ([`4d3218e`](https://github.com/clnsmth/soso/commit/4d3218ea27ee14de8a22e80dc26755f3b4ee9df7)) 
* fix: resolve pylint warning regarding long line ([`f3bd1ea`](https://github.com/clnsmth/soso/commit/f3bd1ea14729abfda043d32c464f8b0ef152b145)) 
* fix: note publisher is unmappable (#5) ([`215d24c`](https://github.com/clnsmth/soso/commit/215d24c86dabee8ffed4e93a79934cae0e61c243)) 
* fix: note provider is unmappable (#5) ([`e664f01`](https://github.com/clnsmth/soso/commit/e664f016e08d6a94247810cdc9f0054191f962a0)) 
* fix: return None creator/contributor for readability ([`0d62bdf`](https://github.com/clnsmth/soso/commit/0d62bdf5eb9a099fbf87bcfde3ee7fa9a43c2d64)) 
* fix: add missing return type to method docstring (#5) ([`3654bd1`](https://github.com/clnsmth/soso/commit/3654bd12b170706a9fd87b7d738fa3f3100502b7)) 
* fix: update spatialCoverage mapping dates (#5) ([`bcb2a4f`](https://github.com/clnsmth/soso/commit/bcb2a4f887e43db00807a664bc246f05c044e45d)) 
* fix: fix distribution in EML SSSOM (#5) ([`5c29cc2`](https://github.com/clnsmth/soso/commit/5c29cc23a122bb2804edd677e53abcf776f983ee)) 
* fix: revert to previous SSSOM practices (#5) ([`05816b3`](https://github.com/clnsmth/soso/commit/05816b311af595f61c8570cdacb961b86c342de1)) 
* fix: fully represent properties with 'schema' prefix (#5) ([`17e5953`](https://github.com/clnsmth/soso/commit/17e59539f8a09375b0372027f05097e5267d3a05)) 
* fix: add missing note to EML strategy (#5) ([`5978c78`](https://github.com/clnsmth/soso/commit/5978c785440ea0f95f561ba8871d645a55e32d69)) 
* fix: specify expected string format ([`a3f9b30`](https://github.com/clnsmth/soso/commit/a3f9b30b44347d4efb76aed412c60e1efe31ce37)) 
* fix: deprecation warnings issued by pytest ([`fcee9df`](https://github.com/clnsmth/soso/commit/fcee9df16b35dc76b828e783a72eaa978e6d7ff1)) 
* fix: return JSON-LD str not JSON dict ([`6fa9ff8`](https://github.com/clnsmth/soso/commit/6fa9ff8ce4965af6cb285fedcc957ac2b2f6e625)) 

### Build system

* build: clean up env build files ([`07277f5`](https://github.com/clnsmth/soso/commit/07277f5cb62b5ed79150b350bab51cee66a76c06)) 
* build: update dependencies ([`7d87a08`](https://github.com/clnsmth/soso/commit/7d87a08256961daa51fe611047c054af84d66f4d)) 
* build: remove unused Pandas ([`b08101a`](https://github.com/clnsmth/soso/commit/b08101a3f635f1c2406ab8cc7be2c177db8c313b)) 
* build: synchronize environment files ([`f163ffd`](https://github.com/clnsmth/soso/commit/f163ffd9ef8f5a976471812ca53f33c33f424aff)) 
* build: remove invalid package metadata ([`3e1a8e3`](https://github.com/clnsmth/soso/commit/3e1a8e31a96c8240cf32699b163664745e629c98)) 

### Continuous integration

* ci: fix failing release workflow ([`ee76c39`](https://github.com/clnsmth/soso/commit/ee76c398dd1b59104f4d1925c5f3f4ff775a0199)) 
* ci: ignore Pylint too-many-instance-attributes ([`25d33e2`](https://github.com/clnsmth/soso/commit/25d33e2917d816e1a6bc1b0e1037b8ba7466844c)) 
* ci: ignore Pylint 'too many arguments' ([`83ca931`](https://github.com/clnsmth/soso/commit/83ca93143153ecc0d5d1b4a57f0fad35153c3da8)) 
* ci: ignore pylint R0912 for is_property_type ([`e64906b`](https://github.com/clnsmth/soso/commit/e64906b66148b9d06cb5c49e93e987020d983968)) 
* ci: use 'black' version 23.7.0 ([`c84d8b3`](https://github.com/clnsmth/soso/commit/c84d8b339573754d0af5ddd42f4f8053dc805251)) 
* ci: ignore pylint c-extension-no-member messages ([`7d6e9cc`](https://github.com/clnsmth/soso/commit/7d6e9cc75529f771bdb1028df884dae98af721d3)) 
* ci: simplify pylint calls with pyproject.toml ([`7578728`](https://github.com/clnsmth/soso/commit/7578728f760b5581cbaf87c70630004ee7980716)) 

### Documentation

* docs: reformat changelog for better readability ([`11a952e`](https://github.com/clnsmth/soso/commit/11a952e8b1ebe179ead5a3a8659213326b28e932)) 
* docs: encourage contribution ([`60b6e5d`](https://github.com/clnsmth/soso/commit/60b6e5d7237ef4874dac8a7280be34488763dd6d)) 
* docs: review and edit documentation ([`04df73f`](https://github.com/clnsmth/soso/commit/04df73ff33bd94fb8be92a2f9b9a0f11fa785bd6)) 
* docs: update mapping guidelines ([`042db8e`](https://github.com/clnsmth/soso/commit/042db8ef91b85278f1a9fa74f28558c2132de640)) 
* docs: update SSSOM mapping for EML ([`b0f0baa`](https://github.com/clnsmth/soso/commit/b0f0baa87423a2d4033ce95b1a6b0f63fa986d0f)) 
* docs: improve design requirement clarity ([`f44c8d7`](https://github.com/clnsmth/soso/commit/f44c8d7da6080f454211804725f3ce7887737063)) 
* docs: define "acceptable mapping implementation" ([`93b5526`](https://github.com/clnsmth/soso/commit/93b5526a03939b84ec9d825536f5aa7cd689c433)) 
* docs: don't coerce SSSOM mapping predicates ([`318c6a6`](https://github.com/clnsmth/soso/commit/318c6a6f792a047dbb39e8c673fa5edfc071d0ce)) 
* docs: install from GitHub ([`3c9e17b`](https://github.com/clnsmth/soso/commit/3c9e17b71d6f2921c625f395f342fc792efe0d2a)) 
* docs: clean up code in "Wrapping it All Up" demo ([`4a882e6`](https://github.com/clnsmth/soso/commit/4a882e6c68d70c51eff782af81d31412e6fe8b18)) 
* docs: establish consistent mapping terminology ([`622b25c`](https://github.com/clnsmth/soso/commit/622b25cc28409f4893bcef9c3c7bcb304e7e0542)) 
* docs: new strategy methods should use delete_null_values ([`1b58b0b`](https://github.com/clnsmth/soso/commit/1b58b0b6fd71f177229e5e6d5a13bd8a952b696c)) 
* docs: remove "precision-based property control" ([`955b895`](https://github.com/clnsmth/soso/commit/955b8957b71033e75f9c659ed35d1144c3b0d32c)) 
* docs: de-emphasize section headings of quickstart notes ([`504521d`](https://github.com/clnsmth/soso/commit/504521dfbb83a6251c8763d1316c968fe0fbf5d9)) 
* docs: consistently emphasize package name ([`fc6e357`](https://github.com/clnsmth/soso/commit/fc6e3574ec67e9397b911f16173c40e2a2a535d2)) 
* docs: remove mention of Numpy docstrings ([`ac7b2f2`](https://github.com/clnsmth/soso/commit/ac7b2f26b59523f03e80002e41d94fc346bc783a)) 
* docs: relocate code of conduct ([`2024f40`](https://github.com/clnsmth/soso/commit/2024f404036216e0042d89a05e27700c8c45a1c9)) 
* docs: sync sidebar html docs ([`9d203c7`](https://github.com/clnsmth/soso/commit/9d203c74a6f8a9e07abd9049743842c2955989f0)) 
* docs: use Poetry in dev workflow ([`119fdb7`](https://github.com/clnsmth/soso/commit/119fdb7ceb3449c5a6262b714ebb5c9d357a2aaf)) 
* docs: link to quickstart guide for customization ([`63428c3`](https://github.com/clnsmth/soso/commit/63428c319e3e7421b1fad0962a76834210bed478)) 
* docs: add support for a new metadata standard ([`43b45ed`](https://github.com/clnsmth/soso/commit/43b45ed98e733dfbf79a354acc317e5c5db5294b)) 
* docs: remove architecture heading from design docs ([`0cb7200`](https://github.com/clnsmth/soso/commit/0cb720001bf17993ef9a67cb99457b9afa411026)) 
* docs: design docs don't belong in contributor guide ([`6334512`](https://github.com/clnsmth/soso/commit/6334512b95b34135b25da45cd4080cfe029e81c3)) 
* docs: refactor remaining system details of design docs ([`ccf46be`](https://github.com/clnsmth/soso/commit/ccf46be56b60d7929a7f1c9c373fdc0b8bef8366)) 
* docs: simplify detailed testing section of design docs ([`3290bcc`](https://github.com/clnsmth/soso/commit/3290bcc527ba2254bded11d3bfd285a8c6fc4833)) 
* docs: remove unused advanced section ([`249e4da`](https://github.com/clnsmth/soso/commit/249e4da8886b428528483e252359bdca8dc52c7b)) 
* docs: add quickstart notes ([`2cbfe2d`](https://github.com/clnsmth/soso/commit/2cbfe2d91c8ce39085f82c61ed832609c420ff3b)) 
* docs: remove lingering docstring type descriptions ([`05711b8`](https://github.com/clnsmth/soso/commit/05711b827733141d508c21465d4aa2472d12abc9)) 
* docs: demo wrapper function construction ([`3fb2796`](https://github.com/clnsmth/soso/commit/3fb2796051bc7aa70a6461c0fd74d73c5e453956)) 
* docs: demo property method override ([`75fcf95`](https://github.com/clnsmth/soso/commit/75fcf95f031e1c162bf2a9459291c6768d27480c)) 
* docs: demo property overwrite ([`11fa452`](https://github.com/clnsmth/soso/commit/11fa4520c28a2000bd33ecb7d6d55994e35137d6)) 
* docs: update title of property addition demo ([`e6d091d`](https://github.com/clnsmth/soso/commit/e6d091de25690af65e3ddbfe0c245118bf35b057)) 
* docs: note how to test positive and negative cases ([`db90863`](https://github.com/clnsmth/soso/commit/db9086396919e4701946115eaba6cd67744bccf7)) 
* docs: use reST rather than Numpy formatting for consistency ([`f971227`](https://github.com/clnsmth/soso/commit/f97122705c411ed43068aab517706dff7cdf2cbc)) 
* docs: describe new approach to property override with kwargs ([`6e7a9e4`](https://github.com/clnsmth/soso/commit/6e7a9e4ae6acca3740641f5605177333a597da1e)) 
* docs: disambiguate property definitions ([`918ff1a`](https://github.com/clnsmth/soso/commit/918ff1a014a5cdb5a94111c5f6395846903bef74)) 
* docs: override methods for advanced customization ([`50769f8`](https://github.com/clnsmth/soso/commit/50769f8bba71d606c643bcb93b90f1d0c1fd0503)) 
* docs: note mapping via params (#111) ([`21056b9`](https://github.com/clnsmth/soso/commit/21056b9e6b4eb254575d50ba211247316ef0e8f1)) 
* docs: eliminate redundant statement ([`f6aaa9b`](https://github.com/clnsmth/soso/commit/f6aaa9b1bb2e425c7d7dea6b9d00d56c379b26e2)) 
* docs: add unmappable EML properties via parameters ([`9f25733`](https://github.com/clnsmth/soso/commit/9f25733a0b0b7c1a22a189698ef5a4a9b6aa5020)) 
* docs: streamline customization via parameters ([`72d6885`](https://github.com/clnsmth/soso/commit/72d6885327670f4753372c3b5c2efcec69a7cab3)) 
* docs: create unmappable properties with params ([`634bca8`](https://github.com/clnsmth/soso/commit/634bca84020ca74d264a73e3b723f8cf815ed67a)) 
* docs: stay up-to-date with Science-On-Schema.Org ([`13eec9e`](https://github.com/clnsmth/soso/commit/13eec9e3b931ab4819ed9933af6483d94847c20e)) 
* docs: explain logic of is_property_type function ([`531d7f0`](https://github.com/clnsmth/soso/commit/531d7f056c1ed44ab027dd06502df70b9c55f420)) 
* docs: add basic usage to the quickstart guide ([`4f54279`](https://github.com/clnsmth/soso/commit/4f5427978e56b3c7370ccba625c6ac9a52b15676)) 
* docs: fix reference to old GitHub ([`823fcd1`](https://github.com/clnsmth/soso/commit/823fcd171265fd2a1138402f578488eebaa6c004)) 
* docs: improve narrative in opening examples ([`d03f96b`](https://github.com/clnsmth/soso/commit/d03f96b9e3f98f0e5b6ac5c6e17304011894f561)) 
* docs: remove short list of features ([`e344d86`](https://github.com/clnsmth/soso/commit/e344d8641ae6ed9979f11457402de659da4b9fb1)) 
* docs: fix typo in opening example ([`072d4df`](https://github.com/clnsmth/soso/commit/072d4df71d6743bf356f72f05b9fb3cd896df9e7)) 
* docs: align project description with SOSO ([`bfe3914`](https://github.com/clnsmth/soso/commit/bfe3914f2ddfeeb8e51d6c1a6e02a8452dcbf58c)) 
* docs: update project description in README ([`644c48a`](https://github.com/clnsmth/soso/commit/644c48a7bb1606d0b22099dae7afe2e5518a7326)) 
* docs: list features of this application ([`997e93f`](https://github.com/clnsmth/soso/commit/997e93ff4145375f0dc2cac9a41355e59b62a2dc)) 
* docs: demonstrate basic usage ([`5aa0cd4`](https://github.com/clnsmth/soso/commit/5aa0cd4d6e3e9159b38d7434737f990af27bc6d7)) 
* docs: add design docs for effective contributions ([`f93f568`](https://github.com/clnsmth/soso/commit/f93f5687772aa41898a9b9bc48ef59f21b4beaa0)) 
* docs: note unmappable property for CRS ([`1a1863f`](https://github.com/clnsmth/soso/commit/1a1863f0fbdd225fd015d3fd2fb36a3b8d2a055c)) 
* docs: improve delete_unused_vocabularies description ([`01ad124`](https://github.com/clnsmth/soso/commit/01ad12464c47131d520b38a01cce73bdab37e242)) 
* docs: define "null" in rm_null_values function ([`69ad083`](https://github.com/clnsmth/soso/commit/69ad083f754020dbaaaee824151812cab256e103)) 
* docs: improve strategy return type descriptions ([`fc8c0e5`](https://github.com/clnsmth/soso/commit/fc8c0e53d7aefdda68ab92d68b60239b173063e5)) 
* docs: fix broken reference URLs in Maintainer Guide ([`d2f17d6`](https://github.com/clnsmth/soso/commit/d2f17d6686068936b69a913ecdc499dd4a50fab1)) 
* docs: fix local test instructions ([`9da4dce`](https://github.com/clnsmth/soso/commit/9da4dce055076a440025abee8d67882cf8f00765)) 
* docs: note nuances of EML object identifiers (#5) ([`a281c93`](https://github.com/clnsmth/soso/commit/a281c935db334096862a7b74d07332f138b65873)) 
* docs: refine project descriptions ([`9933d45`](https://github.com/clnsmth/soso/commit/9933d45bf152dbf4613b6e727a1b809cbd3d4e21)) 

### Features

* feat: convert multiple versions of source metadata ([`0a200f5`](https://github.com/clnsmth/soso/commit/0a200f586af6dbea17714bfdc3c5cd3b16651a99)) 
* feat: cast value to numeric type ([`503fc52`](https://github.com/clnsmth/soso/commit/503fc525c1ba439a0b7726ffa56728c8cea833ca)) 
* feat: make 'file' argument accessible to strategy methods ([`a132797`](https://github.com/clnsmth/soso/commit/a132797dae9005b8f945b388b75d5bf2acc73d26)) 
* feat: override any top-level SOSO property via kwargs ([`158a924`](https://github.com/clnsmth/soso/commit/158a92423eaa9d48c7c0a99ec8626463f4d3bc15)) 
* feat: create expires via parameter for EML ([`b1bde5b`](https://github.com/clnsmth/soso/commit/b1bde5bb623ca9244d79631b38ebeab83082d191)) 
* feat: create dateCreated via parameter for EML ([`e55a3ef`](https://github.com/clnsmth/soso/commit/e55a3efa87760958cd5c3497b889c0b5629d86fa)) 
* feat: create includedInDataCatalog via parameter for EML ([`0388a78`](https://github.com/clnsmth/soso/commit/0388a78f6e229a36cf9a49496257cb0d0646ff46)) 
* feat: create citation via parameter for EML ([`475cc62`](https://github.com/clnsmth/soso/commit/475cc62edf4a288968a17e0103a2a766531211c1)) 
* feat: create isAccessibleForFree via parameter for EML ([`1198b09`](https://github.com/clnsmth/soso/commit/1198b096797284b9ef26474ef697243f154034c3)) 
* feat: create version via parameter for EML ([`7bff72b`](https://github.com/clnsmth/soso/commit/7bff72b0f6f2ca305ac660230b182eb848c42fd2)) 
* feat: create sameAs via parameter for EML ([`da8b3d8`](https://github.com/clnsmth/soso/commit/da8b3d82aba83aefb8df9f86e1f0a8943b480bef)) 
* feat: create url via parameter for EML ([`e912c7e`](https://github.com/clnsmth/soso/commit/e912c7e434042459329d04b747d25ee4dd920d29)) 
* feat: get checksum from EML ([`14026f8`](https://github.com/clnsmth/soso/commit/14026f8cee47edd252b6e1e8dc638d46a2355114)) 
* feat: generate citation from DOI ([`f7a3faf`](https://github.com/clnsmth/soso/commit/f7a3fafb421cea4b7bda7c51e40f2815389545f9)) 
* feat: add measurementTechnique to EML strategy ([`df81edb`](https://github.com/clnsmth/soso/commit/df81edbd59892f6b03b233129693544ce6ca58de)) 
* feat: add get_subject_of method for EML strategy ([`3791795`](https://github.com/clnsmth/soso/commit/3791795219c5f27bdc431d9631ef9a0ea2b5ca68)) 
* feat: get encoding format of EML record ([`2966cf0`](https://github.com/clnsmth/soso/commit/2966cf055095ed62e373c511a5a44e0652d3d4a1)) 
* feat: apply rm_null_values to strategy methods ([`76c7cd0`](https://github.com/clnsmth/soso/commit/76c7cd008e8967eab05f681e8e67f3b1af91727e)) 
* feat: remove null values from properties ([`d229402`](https://github.com/clnsmth/soso/commit/d2294021726af3db182533efbc65868fbbd1588e)) 
* feat: get encodingFormat from file extension (#5) ([`d663bc4`](https://github.com/clnsmth/soso/commit/d663bc429df81711821c5958ffbc9f886483a241)) 
* feat: get wasGeneratedBy from argument (#5) ([`7fddca7`](https://github.com/clnsmth/soso/commit/7fddca7d06c44c3f990c5bf8b35dad4abb544a04)) 
* feat: get isBasedOn from EML (#5) ([`150e044`](https://github.com/clnsmth/soso/commit/150e044d2e17ad54b24965cf70f83df44ddf9037)) 
* feat: get wasDerivedFrom from EML (#5) ([`ab43abc`](https://github.com/clnsmth/soso/commit/ab43abc64ec24671a4e0d7a4df03b20e5755d9e1)) 
* feat: get wasRevisionOf from argument (#5) ([`c90caaa`](https://github.com/clnsmth/soso/commit/c90caaa5cbb3262f26429e60f52036a8bf0cc42d)) 
* feat: get license from EML (#5) ([`ba18e06`](https://github.com/clnsmth/soso/commit/ba18e06fd1624ae35065a59da2d0ac6ab49723e5)) 
* feat: get funding from EML (#5) ([`667d043`](https://github.com/clnsmth/soso/commit/667d043e7864c9fb3b8741454c6fe45b5e02be3c)) 
* feat: get provider from argument (#5) ([`ed2911f`](https://github.com/clnsmth/soso/commit/ed2911ff1459c50451977ccaf7919ffd33531a33)) 
* feat: get publisher from EML (#5) ([`f5f8f82`](https://github.com/clnsmth/soso/commit/f5f8f826817f98174813a53c1b9fa67a97275abb)) 
* feat: get contributor from EML (#5) ([`a42bd11`](https://github.com/clnsmth/soso/commit/a42bd1121c92899d279adcfd630e0af00ba66e15)) 
* feat: get creator from EML (#5) ([`eb89309`](https://github.com/clnsmth/soso/commit/eb89309b52af1be11ca82006fb3584110f8688f3)) 
* feat: get spatialCoverage from EML (#5) ([`e888fb7`](https://github.com/clnsmth/soso/commit/e888fb71410426cbcc295f69d28dac45d00c5ba2)) 
* feat: get temporalCoverage from EML (#5) ([`ff55894`](https://github.com/clnsmth/soso/commit/ff558949bf9b2b662a2bfd93c06b98743dd67c1e)) 
* feat: get expires from argument (#5) ([`c684ab2`](https://github.com/clnsmth/soso/commit/c684ab21113650680604794e35fd8424472e61ec)) 
* feat: get datePublished from EML (#5) ([`85050cf`](https://github.com/clnsmth/soso/commit/85050cfe5233279390028fed3619119cef5b6171)) 
* feat: get dateModified from EML (#5) ([`d94c583`](https://github.com/clnsmth/soso/commit/d94c5834e50c2b72d5bef7e3f40115feb1b5aad3)) 
* feat: get dateCreated from argument (#5) ([`f7720c0`](https://github.com/clnsmth/soso/commit/f7720c019c7d3301ba257f7e0e2a6ada32bc77c1)) 
* feat: get potentialAction from argument (#5) ([`5a4e9d8`](https://github.com/clnsmth/soso/commit/5a4e9d81d10007ccf555f3f6e003333e2b8f9782)) 
* feat: get distribution property from EML (#5) ([`dc5cb9d`](https://github.com/clnsmth/soso/commit/dc5cb9dab6a26ed7cf9c601d73bbb109c5212464)) 
* feat: get subjectOf from argument (#5) ([`b0f89ce`](https://github.com/clnsmth/soso/commit/b0f89ce0ab29886b54b6c3ae009e041318580523)) 
* feat: get includedInDataCatalog from argument (#5) (#29) ([`48e06fe`](https://github.com/clnsmth/soso/commit/48e06feffa9988c91e0850f944c165554f3bec57)) 
* feat: get variableMeasured property from EML (#5) ([`42f6a86`](https://github.com/clnsmth/soso/commit/42f6a863fe8b7b7ec774c0044379849254b0022e)) 
* feat: get citation property from argument (#5) ([`9cc297e`](https://github.com/clnsmth/soso/commit/9cc297e02ac1d7c87f4107274fa9019e6e68cf4a)) 
* feat: get identifier property from EML (#5) ([`60c7373`](https://github.com/clnsmth/soso/commit/60c7373cc465f6b82d5564111e99f7328c065fce)) 
* feat: get keywords property from EML (#5) ([`e78012d`](https://github.com/clnsmth/soso/commit/e78012d0558555b660fc975824b92d336acd2899)) 
* feat: get isAccessibleForFree property from argument (#5) ([`707bf1a`](https://github.com/clnsmth/soso/commit/707bf1a22113f2d2842ee32bde0bba97abe378b5)) 
* feat: get version property from argument (#5) ([`2a336ed`](https://github.com/clnsmth/soso/commit/2a336ede15b5dd1979879f38c48b40cfa81abd45)) 
* feat: get sameAs property from argument (#5) ([`6460d08`](https://github.com/clnsmth/soso/commit/6460d08785e8c79d43bf439bed216ccb1592d483)) 
* feat: remove empty properties from graph ([`1228b05`](https://github.com/clnsmth/soso/commit/1228b05239ad8b09a608fc04f9a87b0cfc0fe0b7)) 
* feat: get url property from argument (#5) ([`d81d719`](https://github.com/clnsmth/soso/commit/d81d71946df1166dd7b5c807e3a0aba755db9ebe)) 
* feat: get description property from EML (#5) ([`ff96f2b`](https://github.com/clnsmth/soso/commit/ff96f2b5a2630276805bb6892e41d646b7e8fd3d)) 
* feat: get name from EML (#5) ([`ee9f2f7`](https://github.com/clnsmth/soso/commit/ee9f2f7f5f66510792768477b8b01714d85dc1f6)) 
* feat: read metadata for strategy method access ([`3598d06`](https://github.com/clnsmth/soso/commit/3598d0603e8750c86980ec9ec8a967d9a27ad6b0)) 
* feat: read SSSOM for flow control logic ([`4301349`](https://github.com/clnsmth/soso/commit/43013499131e091f02d8e12240b30bc5f9d41339)) 
* feat: map SOSO to EML with SSSOM (#5) ([`2a7dfe6`](https://github.com/clnsmth/soso/commit/2a7dfe649749987ac098f33c421a371e3cdcd0dd)) 
* feat: validate graph against the dataset SHACL shape ([`a1abc3f`](https://github.com/clnsmth/soso/commit/a1abc3f27b1d186fc7d740eaf0ebc5311fd8958d)) 

### Refactoring

* refactor: remove unused SSSOM functions ([`0157622`](https://github.com/clnsmth/soso/commit/01576226d0a6bdfbe9d0cbbfbd23fa140d28f7af)) 
* refactor: list subjectOf as unmappable, not contentUrl ([`d76eade`](https://github.com/clnsmth/soso/commit/d76eadeb4329c15e5b87227351d4c3b03e2f6c76)) 
* refactor: improve parsing of empty metadata ([`e467c86`](https://github.com/clnsmth/soso/commit/e467c86f1dd9cacd2e23fcbd71bb104732a5ce80)) 
* refactor: exception handling for EML file types ([`4ea27cb`](https://github.com/clnsmth/soso/commit/4ea27cb879dbb400ed5b8d59c184b5c7ba1700aa)) 
* refactor: add missing type hints to strategies ([`860f826`](https://github.com/clnsmth/soso/commit/860f82617dee00a9233d7e8ad4e1ec94a57b51b0)) 
* refactor: use type hints for static code analysis ([`ec9eab8`](https://github.com/clnsmth/soso/commit/ec9eab8b54561d3f16b0ec69d0cba9b552e32e97)) 
* refactor: use method override for unmapped properties ([`dd276b8`](https://github.com/clnsmth/soso/commit/dd276b86c5c2d37966492c6b9a1f0096c7b450d0)) 
* refactor: apply consistent name prefixes for clarity ([`65491ee`](https://github.com/clnsmth/soso/commit/65491ee10bc0edd3d1fd9173c7a2c426683c0ff2)) 
* refactor: remove unused vocabularies from @context ([`74622ce`](https://github.com/clnsmth/soso/commit/74622cea9c0e9000ee7dfa41018ae8ea65975229)) 
* refactor: add common vocabularies to @context ([`00a1e9e`](https://github.com/clnsmth/soso/commit/00a1e9eb05de425114552160342cf88e7fbe014b)) 
* refactor: fix typo ([`e667878`](https://github.com/clnsmth/soso/commit/e667878e6bbbcc6c03cdd6b20954eb246532316a)) 
* refactor: use consistent variable names for readability ([`eb6b491`](https://github.com/clnsmth/soso/commit/eb6b491a0b2bd54af177d11e25e16328cf50e307)) 
* refactor: rename method for readability ([`dcf34e8`](https://github.com/clnsmth/soso/commit/dcf34e840790361633468ba8a9d34e93a237644b)) 
* refactor: enhance clarity of the public-facing API ([`de7260d`](https://github.com/clnsmth/soso/commit/de7260da9dc4ef66a9bf476da8e1b37f295fbae8)) 
* refactor: re-enable pylint checks to improve code ([`dee39e9`](https://github.com/clnsmth/soso/commit/dee39e99dee5fdfc9475cc72191749a2b907cb20)) 
* refactor: use "strategy" instead of "standard" ([`941c37f`](https://github.com/clnsmth/soso/commit/941c37f28496d537879452ae0feab1f8937646ae)) 
* refactor: comment out stubs for implementation ([`f5f5829`](https://github.com/clnsmth/soso/commit/f5f582962f94c155badcc31394995d4a7bb9bc41)) 
* refactor: remove TODO and FIXME to silence pylint ([`7def44d`](https://github.com/clnsmth/soso/commit/7def44d9512a093e0d13c00300f04191f99c2605)) 
* refactor: match test and code module names ([`baeb00e`](https://github.com/clnsmth/soso/commit/baeb00e6f252fede24177570d475efdb50aa02b3)) 

### Testing

* test: nest abstract of test EML ([`c4c0f59`](https://github.com/clnsmth/soso/commit/c4c0f59e6f8e73a01413ca2bd7c517831b6cdf3f)) 
* test: use empty metadata for testing negative cases ([`336dd7b`](https://github.com/clnsmth/soso/commit/336dd7b9ee8364250e2c000a5dc6b0e0d371ddaa)) 
* test: instantiate strategy with parameters ([`c881dcd`](https://github.com/clnsmth/soso/commit/c881dcd12b7758e94fe10d8a2bd5581d6058fa1d)) 
* test: fix typo in test code ([`68bf7c9`](https://github.com/clnsmth/soso/commit/68bf7c952ec45adebbca4baa6fbc52ab3e65d91c)) 
* test: add missing info to test EML file ([`11346c1`](https://github.com/clnsmth/soso/commit/11346c1ba6963e3790f4580ca3895b39ed3dd397)) 
* test: update rationale for skipped test ([`15e9fb7`](https://github.com/clnsmth/soso/commit/15e9fb706040562937c7bc530b9a764da7d20cb6)) 
* test: reduce false positive test results ([`fbc8ce5`](https://github.com/clnsmth/soso/commit/fbc8ce557b0b07459907ad72ce1d1fb4771c9d22)) 
* test: add verification test for conversion strategies ([`292ce9a`](https://github.com/clnsmth/soso/commit/292ce9ae8081f0b33250595467d0935d15d99eb2)) 
* test: add missing negative cases for is_not_null ([`e0be5cf`](https://github.com/clnsmth/soso/commit/e0be5cf7799230f880b5aaa215db7ad8e57e6e73)) 
* test: strategy methods return None, not null values ([`7313f1b`](https://github.com/clnsmth/soso/commit/7313f1bff41b78f998380270eeb7a47b323ca967)) 
* test: implement function for property type testing ([`542aea2`](https://github.com/clnsmth/soso/commit/542aea2ed3200a584045ccca20f2bda888e92ecc)) 
* test: add full EML record for tests and examples ([`4cf04ea`](https://github.com/clnsmth/soso/commit/4cf04eab30ae3807588712822d1bec827d5863bc)) 

### Unknown

* Stub out codebase following a Strategy Design Pattern ([`faa473a`](https://github.com/clnsmth/soso/commit/faa473abf6dd8397bb193c6e000a3f555e12b8a9))

* Initialize git repository ([`ecbb794`](https://github.com/clnsmth/soso/commit/ecbb794a45ea989042a61f4e785ae777b0b4d048))
