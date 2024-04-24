# Changelog

## [0.10.0](https://www.github.com/snakemake/snakedeploy/compare/v0.9.1...v0.10.0) (2024-04-24)


### Features

* add method to obtain schemas from workflow repo ([#60](https://www.github.com/snakemake/snakedeploy/issues/60)) ([2834e39](https://www.github.com/snakemake/snakedeploy/commit/2834e3911e970ddd56c88d1614fe525acb448191))


### Bug Fixes

* type annotations ([81948e0](https://www.github.com/snakemake/snakedeploy/commit/81948e015f9bbec22788c38b2bfa179624fa0ad8))

### [0.9.1](https://www.github.com/snakemake/snakedeploy/compare/v0.9.0...v0.9.1) (2023-10-30)


### Bug Fixes

* fix release process ([422b22d](https://www.github.com/snakemake/snakedeploy/commit/422b22d14af7ff7f22bb297277105e59f1f9ada6))

## [0.9.0](https://www.github.com/snakemake/snakedeploy/compare/v0.8.6...v0.9.0) (2023-10-30)


### Features

* add PR creation to pin-conda-envs ([58ce050](https://www.github.com/snakemake/snakedeploy/commit/58ce05026cc33941203d1449babf58f92df18738))


### Bug Fixes

* convert filepath to str ([4ba5cbc](https://www.github.com/snakemake/snakedeploy/commit/4ba5cbc52d4cf0a6d4273d95e223e7b78bbfd581))

### [0.8.6](https://www.github.com/snakemake/snakedeploy/compare/v0.8.5...v0.8.6) (2023-02-06)


### Bug Fixes

* remove accidental debugger invocation ([0e8df29](https://www.github.com/snakemake/snakedeploy/commit/0e8df298f0aa049fdee5d8d403086c57a72bb482))

### [0.8.5](https://www.github.com/snakemake/snakedeploy/compare/v0.8.4...v0.8.5) (2023-02-03)


### Bug Fixes

* use conda package version parsing by obtaining conda version spec from github ([#52](https://www.github.com/snakemake/snakedeploy/issues/52)) ([ed821c8](https://www.github.com/snakemake/snakedeploy/commit/ed821c8e61c5ab84191e94ea4ce403200d2aa1fb))

### [0.8.4](https://www.github.com/snakemake/snakedeploy/compare/v0.8.3...v0.8.4) (2023-02-01)


### Bug Fixes

* add debugging code for conda env update subcommand ([#50](https://www.github.com/snakemake/snakedeploy/issues/50)) ([0ba8e30](https://www.github.com/snakemake/snakedeploy/commit/0ba8e3024504601793931323599eebe4a95b7d55))

### [0.8.3](https://www.github.com/snakemake/snakedeploy/compare/v0.8.2...v0.8.3) (2023-01-30)


### Bug Fixes

* better error handling when parsing package versions ([#47](https://www.github.com/snakemake/snakedeploy/issues/47)) ([d20ff11](https://www.github.com/snakemake/snakedeploy/commit/d20ff112b7ce858056c5f5111d09f2705b25dced))

### [0.8.2](https://www.github.com/snakemake/snakedeploy/compare/v0.8.1...v0.8.2) (2022-10-27)


### Bug Fixes

* shuffle conda envs before updating (this ensures that running this in a fallible github action cron job still leads to updating all envs from time to time) ([#46](https://www.github.com/snakemake/snakedeploy/issues/46)) ([c6dad58](https://www.github.com/snakemake/snakedeploy/commit/c6dad5819742a7fa84687e2f532224980de7e2b1))
* various robustness improvements for conda env update mechanism ([#44](https://www.github.com/snakemake/snakedeploy/issues/44)) ([491c390](https://www.github.com/snakemake/snakedeploy/commit/491c390621ffdbf7f0844767d40584c73e65ce83))

### [0.8.1](https://www.github.com/snakemake/snakedeploy/compare/v0.8.0...v0.8.1) (2022-10-12)


### Bug Fixes

* if nothing to commit, do not create PR ([#42](https://www.github.com/snakemake/snakedeploy/issues/42)) ([84bb903](https://www.github.com/snakemake/snakedeploy/commit/84bb903a15a5443de515e73c25c559139cce1479))

## [0.8.0](https://www.github.com/snakemake/snakedeploy/compare/v0.7.2...v0.8.0) (2022-10-12)


### Features

* only update pinning if env was updated; ability to specify a regex for entity determination and adding labels when creating PRs from updated envs ([#40](https://www.github.com/snakemake/snakedeploy/issues/40)) ([f074e35](https://www.github.com/snakemake/snakedeploy/commit/f074e35f993b2b325f29e34e908dafb1bfcf150f))

### [0.7.2](https://www.github.com/snakemake/snakedeploy/compare/v0.7.1...v0.7.2) (2022-10-12)


### Bug Fixes

* various bug fixes in conda env update process ([#38](https://www.github.com/snakemake/snakedeploy/issues/38)) ([2fde118](https://www.github.com/snakemake/snakedeploy/commit/2fde11888fcac402612de3d4b4ec0775343a815f))

### [0.7.1](https://www.github.com/snakemake/snakedeploy/compare/v0.7.0...v0.7.1) (2022-10-12)


### Bug Fixes

* glob conda env files passed to related subcommands ([#36](https://www.github.com/snakemake/snakedeploy/issues/36)) ([c72d401](https://www.github.com/snakemake/snakedeploy/commit/c72d4011a8580eb6718395c9972a6446fcf711ab))

## [0.7.0](https://www.github.com/snakemake/snakedeploy/compare/v0.6.0...v0.7.0) (2022-10-11)


### Features

* if requested, automatically generate pull requests when updating conda envs ([#34](https://www.github.com/snakemake/snakedeploy/issues/34)) ([a0e978a](https://www.github.com/snakemake/snakedeploy/commit/a0e978af468f97c4218d3f0169c4e0e2c674f4b7))

## [0.6.0](https://www.github.com/snakemake/snakedeploy/compare/v0.5.0...v0.6.0) (2022-08-15)


### Features

* add subcommand for updating snakemake wrappers in given Snakefiles ([#32](https://www.github.com/snakemake/snakedeploy/issues/32)) ([d291113](https://www.github.com/snakemake/snakedeploy/commit/d291113b20682d1562b0fcf42007893542a39b24))

## [0.5.0](https://www.github.com/snakemake/snakedeploy/compare/v0.4.0...v0.5.0) (2022-06-22)


### Features

* support for deploying workflows from Gitlab ([#27](https://www.github.com/snakemake/snakedeploy/issues/27)) ([47fc31b](https://www.github.com/snakemake/snakedeploy/commit/47fc31bcbfd07d391a81498eecfa9fbae61c9613))

## [0.4.0](https://www.github.com/snakemake/snakedeploy/compare/v0.3.0...v0.4.0) (2022-05-18)


### Features

* add subcommands to update and pin given conda environment definition files ([#29](https://www.github.com/snakemake/snakedeploy/issues/29)) ([9058377](https://www.github.com/snakemake/snakedeploy/commit/90583779367b29c0eaced16b93b74802647c94de))

## [0.3.0](https://www.github.com/snakemake/snakedeploy/compare/v0.2.1...v0.3.0) (2021-12-01)


### Features

* ability to either define branch or tag when deploying ([8a079f0](https://www.github.com/snakemake/snakedeploy/commit/8a079f05d23bab6a91d385a439c903336153b1fa))
* require either --branch or --tag to be specified ([d0ae54b](https://www.github.com/snakemake/snakedeploy/commit/d0ae54b3b4ad2a64108ef47fd4ed298175d12eb8))


### Bug Fixes

* remove quotes around snakefile statement ([ad7feaf](https://www.github.com/snakemake/snakedeploy/commit/ad7feaf6fb602bb70209d9f8d8525d776d66b178))

### [0.2.1](https://www.github.com/snakemake/snakedeploy/compare/v0.2.0...v0.2.1) (2021-11-08)


### Bug Fixes

* minor rephrasing of CLI help. ([4939d9c](https://www.github.com/snakemake/snakedeploy/commit/4939d9ce656f27157de005353df9dc353ef10694))
