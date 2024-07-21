# Changelog

## [1.7.0](https://github.com/WGrape/sparrow/compare/v1.6.0...v1.7.0) (2024-07-21)


### Features

* Private cloud does not check whether the image exists ([4d273e1](https://github.com/WGrape/sparrow/commit/4d273e1aef0b160050df9138578c7078198b2c79))


### Docs

* update README.md (add /conf dir) ([233ab74](https://github.com/WGrape/sparrow/commit/233ab744c4751b2e90db9c7e3e2fbcaf6b6f28ca))

## [1.6.0](https://github.com/WGrape/sparrow/compare/v1.5.0...v1.6.0) (2024-05-17)


### Features

* add azkaban support ([0b6f5e5](https://github.com/WGrape/sparrow/commit/0b6f5e5f0cc01fc63686c3dc2aac39493ee98bb5))
* add difylocal service ([63bbb5c](https://github.com/WGrape/sparrow/commit/63bbb5c09d939de72707799b63d101c3ce8152c6))
* add django service and delete unnecessary {service}/Dockerfile ([3a03b69](https://github.com/WGrape/sparrow/commit/3a03b69ccaaccc4ae9746c4ed88dcabdbe7632c0))
* add start_local.sh of difylocal ([2d4f176](https://github.com/WGrape/sparrow/commit/2d4f1763f81cbf31f5ef36628e10038107db98af))
* change pip source of difylocal ([e447669](https://github.com/WGrape/sparrow/commit/e447669cc3350076ea36ffb217ead62f4893bbac))
* limit the memory of elasticsearch ([637460e](https://github.com/WGrape/sparrow/commit/637460e047d85365aa2520e0c53b4389fbecc1c1))
* nacos add token ([8ba82cf](https://github.com/WGrape/sparrow/commit/8ba82cf9837dcc4598d99c559eaebdf5fa3d1a1c))
* nacos support application.properties ([442abbf](https://github.com/WGrape/sparrow/commit/442abbfcb2be106f91e37b3b6e1e72500d9531bc))
* nacos support application.properties ([724cbfc](https://github.com/WGrape/sparrow/commit/724cbfc03c3f9c25068fbe46420afd2aaa97447d))


### Bug Fixes

* fix nacos mount ([e8101d2](https://github.com/WGrape/sparrow/commit/e8101d25b6f46405c831372c2930c047e13c8ae9))
* fix the .env_of_web of difylocal ([3e8c534](https://github.com/WGrape/sparrow/commit/3e8c5347ff10b1c0d2699680787c6e22c22c71ad))


### Docs

* CHANGELOG.md ([1bae571](https://github.com/WGrape/sparrow/commit/1bae5712b442c810b487085e91bbcd5109d6dee5))
* make .env_of_api better ([2f9a0d3](https://github.com/WGrape/sparrow/commit/2f9a0d331b85d67d711cd8c9b78ab53cdcb2bfe5))
* make difylocal doc better ([1aa0225](https://github.com/WGrape/sparrow/commit/1aa0225ca63c63d372fabd862047d26cd22a706f))

## [1.5.0](https://github.com/WGrape/sparrow/compare/v1.4.0...v1.5.0) (2024-03-27)


### Features

* add nacos ([392c7a0](https://github.com/WGrape/sparrow/commit/392c7a0305272ff768127e5ab509081275015de6))
* add prompthub ([db63b2c](https://github.com/WGrape/sparrow/commit/db63b2c73c2f8606bd405dcd6251f509afce1771))


### Docs

* make doc better ([4adfede](https://github.com/WGrape/sparrow/commit/4adfede74531d18923e63792baf744e9bda4e809))
* make doc better ([1043f62](https://github.com/WGrape/sparrow/commit/1043f6279b93e75df0803b8f0bcf7fd85a7d766a))
* make doc better ([349d68e](https://github.com/WGrape/sparrow/commit/349d68ecabeaede3edf74a5f857947071f3bce5e))

## [1.4.0](https://github.com/WGrape/sparrow/compare/v1.3.0...v1.4.0) (2024-03-20)


### Features

* add kibana service ([d5ec089](https://github.com/WGrape/sparrow/commit/d5ec08959b39d80d68e57bb79f6027376888e480))


### Docs

* add ssdb error ([a135f68](https://github.com/WGrape/sparrow/commit/a135f687859059de345c2ff5206abe1a28f28f53))
* add ssdb error ([d841390](https://github.com/WGrape/sparrow/commit/d8413901fecbea593b3782a1809e04330033292b))
* doc add video ([8796d89](https://github.com/WGrape/sparrow/commit/8796d89d73c0c2dd91d5c2f222daa480b94803d7))

## [1.3.0](https://github.com/WGrape/sparrow/compare/v1.2.0...v1.3.0) (2024-03-13)


### Features

* add elasticsearch support ([42363e8](https://github.com/WGrape/sparrow/commit/42363e8bebb2abe6c43d2885582464b744489a5b))


### Docs

* update CHANGELOG.md ([f5d2b6f](https://github.com/WGrape/sparrow/commit/f5d2b6fc3dd12194114a83bfc645be6f673291e3))
* update doc ([83478c8](https://github.com/WGrape/sparrow/commit/83478c898022833b59045dc24d9366c262efc574))


### Update

* add comments ([c036b37](https://github.com/WGrape/sparrow/commit/c036b3788e9670c8d8fd68139bd4a924fd13cca0))

## [1.2.0](https://github.com/WGrape/sparrow/compare/v1.1.0...v1.2.0) (2024-03-10)


### Features

* add .env.template ([3b1a0a0](https://github.com/WGrape/sparrow/commit/3b1a0a094f8bfd516c52eaa47186bb798f63d5a5))
* add DOCKERHUB_REPO configure when run _install.sh, add search test ([1f33cac](https://github.com/WGrape/sparrow/commit/1f33cac969641dc0d675474361a6b3333f4699ac))
* add prometheus and grafana support ([c9e3f08](https://github.com/WGrape/sparrow/commit/c9e3f0891b295d37ca74ca4b6e228ab8ddc70a6c))
* add ssdb support ([7eb25ab](https://github.com/WGrape/sparrow/commit/7eb25ab1e67a830ee7987546d752cff5346da6b1))
* move SSDB's codes to app ([ecd2d86](https://github.com/WGrape/sparrow/commit/ecd2d8609d18946bd0bc465184d134a69f75fe88))


### Docs

* make doc better - add DOCKERHUB_REPO concept ([d31d8d3](https://github.com/WGrape/sparrow/commit/d31d8d3fcf762cbda267d7a69db471916e529bc9))
* update daoc ([130db40](https://github.com/WGrape/sparrow/commit/130db40208da4f2c95a66a3777d4017e9e9bb55c))
* update doc ([022df2c](https://github.com/WGrape/sparrow/commit/022df2ca56e15ba2efafacd4a5dd8a568244b61d))
* update doc ([48ec95c](https://github.com/WGrape/sparrow/commit/48ec95c4845b72eafbac91770ac6241b812a3404))


### Tests

* add search test ([4783e8d](https://github.com/WGrape/sparrow/commit/4783e8d51998dc13b97de3ea367b1bf07751f650))
* add search test ([8622f0c](https://github.com/WGrape/sparrow/commit/8622f0c5518686d54fd5687c7743a7fe742a01a3))

## [1.1.0](https://github.com/WGrape/sparrow/compare/v1.0.5...v1.1.0) (2024-03-06)


### Features

* add CI and doc updates ([d1e5444](https://github.com/WGrape/sparrow/commit/d1e54443c761d4e2c13105dfca28a6957815ea64))
* add mongodb service ([b14adcb](https://github.com/WGrape/sparrow/commit/b14adcb1f25619d04ab768d998ca456b6d383a96))
* add the tip of before_sparrow_command if docker not exits ([e035ca9](https://github.com/WGrape/sparrow/commit/e035ca9ccb2a8b69c71aca1c62db7747d27a3090))
* update goproxy.conf.template and add some tips in multi_upload() ([2765d56](https://github.com/WGrape/sparrow/commit/2765d56994a0fe0836d68f10cd8ac97a49c735b1))


### Bug Fixes

* fix ci ([320eff5](https://github.com/WGrape/sparrow/commit/320eff51625e9ee7ffedca701f42594b0fc6f030))
* fix the for syntax is not available in sh ([c13f15a](https://github.com/WGrape/sparrow/commit/c13f15a3cd3e57944547c94fe8651f74375757fd))


### Docs

* make doc better ([3f6a6a1](https://github.com/WGrape/sparrow/commit/3f6a6a11cdc785b3b138234e552e0a7936e32d5f))
* make doc better ([d326241](https://github.com/WGrape/sparrow/commit/d3262411bdc0422315c1cc3b21c8ae960b465d52))
* make doc better ([1b1752a](https://github.com/WGrape/sparrow/commit/1b1752a6c3d00b2d519096ba9deccea878ed0346))
* make doc better ([df46b81](https://github.com/WGrape/sparrow/commit/df46b81a18f79282358ca48fbe29e78583c995f7))
* make doc better ([6372ac1](https://github.com/WGrape/sparrow/commit/6372ac13ab22707b943de7e67e0768312bc022db))
* update doc ([9dd67e8](https://github.com/WGrape/sparrow/commit/9dd67e8b48c318ee6939ec7122af9678d7158963))
* update doc ([7a57b3e](https://github.com/WGrape/sparrow/commit/7a57b3e0cc777cddd19d162369ac6e83897d34dc))


### Update

* update sparrowtool, clear one service or some services ([eedf7e0](https://github.com/WGrape/sparrow/commit/eedf7e05c61207d75ae860740d3effcc85bc62b0))
