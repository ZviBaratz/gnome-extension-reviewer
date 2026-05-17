# Changelog

## [0.1.31](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.30...v0.1.31) (2026-05-17)


### Bug Fixes

* **ego-lint:** exclude desktop file ID strings from R-SEC-09 pattern ([#286](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/286)) ([84c7381](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/84c73818406f5b44de383e1e3236162a012d383f))
* **ego-lint:** suppress R-SLOP-24 when schema_id is a variable identifier ([#289](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/289)) ([b1b31f4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/b1b31f4156d74499e020767a56ed30b483fa0938))


### Documentation

* **ego-field-test:** add test mode field to template and lesson [#19](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/19) on EGO ZIP vs source divergence ([#285](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/285)) ([7a19eab](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/7a19eabe52952f6306a2754183bb2f1201829cca))

## [0.1.30](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.29...v0.1.30) (2026-05-14)


### Bug Fixes

* **ego-lint:** accept named default export syntax for R-FILE-07 and R-PREFS-02 ([#284](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/284)) ([fb4a453](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/fb4a4538f44f43ea952db72f934cc464e9a7ff9e))
* **ego-lint:** exclude dev-tooling dirs (gulp/, conf/) from pattern and script checks ([#275](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/275)) ([b6578b9](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/b6578b9da6801220b93fb8c9d5db648318ee5e96))
* **ego-lint:** exclude installed-tests/ when meson.build is present ([3eb0d04](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/3eb0d04353ab47cea4de944cbe6bff32be07c1fa))
* **ego-lint:** exclude root-level dev-tooling trigger files from pattern checks ([7d10d5c](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/7d10d5cf69823cbbcd3378ddbc26f9014bc81e35)), closes [#277](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/277)
* **ego-lint:** exempt self-UUID lookupByUUID from extension interference check ([#274](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/274)) ([38aa3a4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/38aa3a464d4ca910a7a53e81ca4900fec9968b43))
* **ego-lint:** suppress _install_version as SweetTooth artifact ([#272](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/272)) ([232b142](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/232b1420a78c3001afe15dabf7d8c46d04f566d2))

## [0.1.29](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.28...v0.1.29) (2026-05-07)


### Bug Fixes

* **ego-lint:** base verdict on FAIL count, not warning count ([#267](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/267)) ([2ad601c](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/2ad601c89ca6db9452977c8b2cdd724df8621969))
* **ego-lint:** deduplicate R-SLOP-44 GLib.source_remove advisory ([#262](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/262)) ([a62f39a](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/a62f39a7b93fa1efff152cf31438be0616d509cf))
* **ego-lint:** exclude GJS subprocess directories from pattern checks ([#259](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/259)) ([4146246](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/41462465ebe794719af95e71b6d1d557eb68812a))
* **ego-lint:** extend subprocess dir exclusion to lifecycle/quality checks ([#269](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/269)) ([ddad671](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ddad67156c2b62059968b4d4aed47d2850e57a52))
* **ego-lint:** resolve parent prefs class relative to prefs.js dir ([#264](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/264)) ([fe5fe88](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/fe5fe88044bdaeaf1e0fc6348079c87432821c81)), closes [#263](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/263)
* **ego-lint:** suppress R-VER48-05 when Shell.SnippetHook in Cogl ternary guard ([#270](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/270)) ([d5d77fd](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d5d77fdf99e0a82bde6ba7d088c33a2a938f8509))

## [0.1.28](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.27...v0.1.28) (2026-05-02)


### Bug Fixes

* **ego-lint:** add fix suggestion to no-console-log WARN for guarded calls ([#252](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/252)) ([cb15d1b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/cb15d1bd9c8ddd63bec81d9af1291e2d4457a2c0))
* **ego-lint:** suppress lifecycle/untracked-timeout FP for wrapper-tracked timeouts ([#256](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/256)) ([34a0538](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/34a053856ac7b21c2d849dbd54ac00556bb02868))
* **ego-lint:** suppress R-WEB-06 when local variable shadows document global ([#254](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/254)) ([0ffe0ea](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/0ffe0ea3fa2335bdf244ff6f89c6340153d4ed34))

## [0.1.27](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.26...v0.1.27) (2026-04-30)


### Bug Fixes

* **ego-lint:** clarify why debug guard is redundant in no-console-log warn ([#250](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/250)) ([88a5d88](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/88a5d885f640285b23cab5cc43f7f3797940735b))

## [0.1.26](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.25...v0.1.26) (2026-04-30)


### Bug Fixes

* **ego-lint:** extend metadata build-type guard to handle bracket notation ([#248](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/248)) ([3e53ef8](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/3e53ef871e71d89e70e26716ea317f33b982980b)), closes [#247](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/247)

## [0.1.25](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.24...v0.1.25) (2026-04-30)


### Bug Fixes

* **ego-lint:** add guard-pattern to R-VER46-03 for cairo_set_source_color existence check ([#245](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/245)) ([3fcb688](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/3fcb6886bac776c716f29dbfde3de3053ec5da6f))

## [0.1.24](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.23...v0.1.24) (2026-04-29)


### Bug Fixes

* **ego-lint:** recognize runtime settings.DEBUG guard in no-console-log check ([#244](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/244)) ([6ff3c5e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6ff3c5eb98bf59ced911ea6a26ffee502ae604c1))
* **ego-lint:** use word boundary in GLib.Uri network pattern to prevent GLib.UriFlags FP ([#241](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/241)) ([6135331](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/61353315f7c364604d39babd63ae91b4472529c0))

## [0.1.23](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.22...v0.1.23) (2026-04-28)


### Bug Fixes

* **ego-lint:** accept settings-schema as namespace prefix in schema/id-matches ([#238](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/238)) ([4548439](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4548439303cb752f66dd284c7a62be64320229d1))

## [0.1.22](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.21...v0.1.22) (2026-04-28)


### Tests

* add tsconfig-jsdoc suppression assertions for tsconfig-jsdoc@test fixture ([#236](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/236)) ([a46a46f](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/a46a46fd1ca2c930c3e3ec4e343b14affffbc357))

## [0.1.21](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.20...v0.1.21) (2026-04-27)


### Bug Fixes

* skip kwin/ subdirectory in JS file traversal (fixes [#232](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/232)) ([#233](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/233)) ([45cfb56](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/45cfb56c724d678f538f26665cd09907abe15e29))

## [0.1.20](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.19...v0.1.20) (2026-04-26)


### Bug Fixes

* **ego-lint:** suppress EGO download artifacts in metadata checks ([#230](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/230)) ([04e9d98](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/04e9d98a451805fc3f7d87ef43fa6d6c89197b1c))

## [0.1.19](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.18...v0.1.19) (2026-04-25)


### Bug Fixes

* **ego-lint:** suppress R-SLOP-01/02 for SPDX-licensed plain JS ([#228](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/228)) ([3fb2558](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/3fb2558cdb867985d4579a3a1beef2f9976d2b2a))
* **ego-lint:** suppress R-SLOP-01/02 JSDoc warnings for TypeScript projects ([#219](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/219)) ([5af940e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/5af940e8b0f4d37aeb218dbb2b0071fb90bf53fd))

## [0.1.18](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.17...v0.1.18) (2026-04-22)


### Features

* **ego-lint:** detect TypeScript source repos with helpful build hint ([#214](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/214)) ([83f757e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/83f757e685d5c93ee857e548de8d226c642bde88))


### Bug Fixes

* **ego-lint:** exclude build script dirs from R-SEC-04 sudo check ([#216](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/216)) ([15470b5](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/15470b52d0dc35611aaac35f19166377c1b9ce53)), closes [#215](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/215)

## [0.1.17](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.16...v0.1.17) (2026-04-22)


### Bug Fixes

* **ego-lint:** remove R-SLOP-03 duplicate of metadata/deprecated-version ([#212](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/212)) ([8d6ae7b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/8d6ae7b0abc6e7f5c8b3514d95093d59f2a89f84))
* **ego-lint:** suppress quality/module-state FP for conditional import pattern ([#211](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/211)) ([1626214](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/16262141e6c3d75ef03ba15cca583355e67df0c6))

## [0.1.16](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.15...v0.1.16) (2026-04-21)


### Bug Fixes

* **ego-lint:** add 'downloaded from' keyword to vendored-file detection ([d18c975](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d18c97574c1b021a06c63acb91e2a10f24d7f9c2))

## [0.1.15](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.14...v0.1.15) (2026-04-21)


### Bug Fixes

* **ego-lint:** exclude dev directories from non-gjs-scripts and script-permissions ([#206](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/206)) ([6192f48](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6192f4857d7812cc1de3185fd076843f36419658))

## [0.1.14](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.13...v0.1.14) (2026-04-20)


### Bug Fixes

* **ego-lint:** narrow schema-usage accessor regex to GSettings methods only ([#202](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/202)) ([ebe0267](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ebe0267fe0e763b54be1736eae0140143d0d2715)), closes [#203](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/203)

## [0.1.13](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.12...v0.1.13) (2026-04-20)


### Bug Fixes

* **ego-lint:** scan local parent class for enable/disable and prefs methods ([#200](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/200)) ([dd43cc9](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/dd43cc98a9137dbe741333356803d5cc712ff78e))

## [0.1.12](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.11...v0.1.12) (2026-04-20)


### Bug Fixes

* **ego-lint:** skip new X() in function default parameters ([#198](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/198)) ([4a98c15](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4a98c158f5ac3106d4965958c28e7f09e509b602))

## [0.1.11](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.10...v0.1.11) (2026-04-20)


### Bug Fixes

* **ego-lint:** detect anonymous extension class syntax in init check ([#196](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/196)) ([2cd6927](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/2cd692781d61e9f4ece81a07d64bd02e4ca902cc))

## [0.1.10](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.9...v0.1.10) (2026-04-19)


### Bug Fixes

* **ego-lint:** add fix suggestion to no-console-log FAIL ([#193](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/193)) ([1c77791](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/1c7779147cdcaab1422e377a4e66935e66a1faee))
* **ego-lint:** downgrade Shell global reads to WARN in check-init ([#191](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/191)) ([bea8d38](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/bea8d384766bb99f28a2d2a37dc0b6d05a55050d))
* **ego-lint:** exempt Gio.SubprocessLauncher from module-scope init check ([#195](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/195)) ([15380d3](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/15380d3f6a85d144571ec29eb67e806ad9b13d3f))


### Documentation

* **ego-lint:** add lifecycle accuracy warning to compiled-typescript output ([#192](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/192)) ([f127e89](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f127e899a92506b39ea8dc9191fbcb5f7bb93e85))

## [0.1.9](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.8...v0.1.9) (2026-04-17)


### Bug Fixes

* **ego-lint:** narrow resource-path-case FP on standard prefs.js ESM import ([#189](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/189)) ([1e4ddbc](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/1e4ddbc7d5fa9fe1d63e2e9f48fbf057a4008e9b))

## [0.1.8](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.7...v0.1.8) (2026-04-15)


### Bug Fixes

* **ego-lint:** expand JS file scan to all subdirectories ([#186](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/186)) ([6f10682](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6f106829ebf229d88a0fb8e58675e1f278f7ca84))

## [0.1.7](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.6...v0.1.7) (2026-04-15)


### Bug Fixes

* **ego-lint:** resolve 8 independent test failures unrelated to init/shell-modification ([#184](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/184)) ([39000d2](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/39000d2164194943207463b7487a7c23b678e51d))

## [0.1.6](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.5...v0.1.6) (2026-04-13)


### Bug Fixes

* **ego-lint:** downgrade no-console-log to WARN when guarded by build-type debug condition ([#182](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/182)) ([e0a141b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/e0a141b76b31e68a1232be684251cc47eba45e99)), closes [#180](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/180)
* **ego-lint:** gsettings-signal-leak FP on object-in-array cleanup pattern ([#181](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/181)) ([58e6b96](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/58e6b96d9e624e1e2adca53aa6113415ac563009)), closes [#179](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/179)

## [0.1.5](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.4...v0.1.5) (2026-04-10)


### Bug Fixes

* add skip-comments to R-DEPR-04, R-SEC-04, R-SEC-12 ([#177](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/177)) ([2f670e4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/2f670e4e79a01a17e84a9aef124cb18809a48029)), closes [#174](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/174)
* update CURRENT_STABLE to GNOME 50 ([#176](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/176)) ([6132eaf](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6132eaf17370a5781df2240f0c3c1fd63307757b))

## [0.1.4](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.3...v0.1.4) (2026-04-10)


### Bug Fixes

* **ego-lint:** skip R-I18N-02 when both gettext concat operands are string literals ([#172](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/172)) ([920ee19](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/920ee19f0fc29816435c4c479821b00f052cd93c))

## [0.1.3](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.2...v0.1.3) (2026-04-09)


### Bug Fixes

* **ego-field-test:** correct gsconnect annotations after service/ exclusion ([#166](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/166)) ([4669f64](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4669f64cf79a45d2e0488ff8f4f1ba253f495b8a))
* **ego-lint:** exclude tests/ dir from R-SEC-04 sudo check ([#171](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/171)) ([882a746](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/882a74619abb2f78e7eb7bbbae048c3525e19f28)), closes [#170](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/170)
* **ego-lint:** skip supplementary schemas in id-matches and filename checks ([#169](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/169)) ([db288a5](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/db288a51fd40e0600e351a86742ab65a64585acc)), closes [#168](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/168)

## [0.1.2](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.1...v0.1.2) (2026-04-06)


### Bug Fixes

* **ego-lint:** auto-exclude examples/ directory from pattern rules ([#158](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/158)) ([ee8575e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ee8575e0dc804145c2cf708d91ca36eae5746fa8))
* **ego-lint:** check ALL schema IDs for settings-schema match ([#154](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/154)) ([d77061f](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d77061f3785165a2f52c2f67ddd52e4b34dd74bd))
* **ego-lint:** don't flag gi:// strings passed to importInShellOnly/importInPrefsOnly ([#162](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/162)) ([c1f8858](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/c1f88581991bf39ae99a4992e5c5445b726fa66f))
* **ego-lint:** remove Meta.Cursor from R-SLOP-08 hallucinated API pattern ([#156](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/156)) ([d0687b4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d0687b4de079dd1321a7b9dd9909816c1882d8de)), closes [#155](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/155)
* **ego-lint:** skip R-DEPR-05 for export * as re-export declarations ([#164](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/164)) ([05dc2e7](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/05dc2e74f999105691e4b65e2074dc5bce2957b4))

## [0.1.1](https://github.com/ZviBaratz/gnome-extension-reviewer/compare/v0.1.0...v0.1.1) (2026-03-25)


### Features

* add automated field test pipeline ([#34](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/34)) ([6d906d6](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6d906d6b0da0cf09a71d33a4da25bba6382c1b2f))
* add parse-review-results.py for structured finding extraction ([#56](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/56)) ([2083bc7](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/2083bc75d8eaebe6f82fb8a0360cffb1b8bb26b0))
* **ego-lint:** add --show and --report flags for output filtering ([#111](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/111)) ([5fc5a6e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/5fc5a6e302306598d55ab9bebc32fc28991642e0))
* **ego-lint:** add .destroy without parentheses detection (R-LIFE-23) ([#50](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/50)) ([f9c035b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f9c035b0bea132e435ebc285e0e2dcad9957bf16))
* **ego-lint:** add compat-downgrade for version-aware deprecated API gating ([#104](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/104)) ([3e00e6e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/3e00e6e29bafd4e6cff659156fac3c1e355590e9))
* **ego-lint:** add D-Bus connectSignal leak detection (R-LIFE-25) ([#59](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/59)) ([c54d848](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/c54d848fff98fb43928788836465e625028e7571))
* **ego-lint:** add lifecycle leak detection (R-LIFE-21, R-LIFE-22, R-LIFE-24) ([#48](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/48)) ([10f6bbd](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/10f6bbd3ca78244e9833cb30a3933551a365e612))
* **ego-lint:** add module-scope mutable state detection (R-LIFE-26) ([#60](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/60)) ([9c5d2e3](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/9c5d2e304a42f1ddb796025504c8538966cf63a7))
* **ego-lint:** add module-scope prototype mutation detection (R-LIFE-27) ([#83](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/83)) ([0d2df8d](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/0d2df8db87f28ebb627310f715cc8ca4bf28ac76))
* **ego-lint:** add notification urgency abuse detection (R-QUAL-36) ([#49](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/49)) ([546bd10](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/546bd1031655bad5e3bb9d70ce984ac881d68f9e))
* **ego-lint:** detect indirect prototype mutation via function calls ([#114](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/114)) ([bce145b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/bce145bea97f87f04e3c3a7cb6d0e4c0b86514eb))
* **ego-review:** eliminate redundant work by referencing ego-lint findings ([787261a](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/787261aeb06a7db564d11b8e239ca87eb0e47678))


### Bug Fixes

* **ego-field-test:** fix IFS collapse and commit-hash fetch failures ([f4b480f](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f4b480fdeeb44658b7c7e90307416d27e7ad2108))
* **ego-field-test:** indent multi-line expressions in json_extract wrapper ([ae650be](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ae650bed5c9e573e11dc79930451b76fe28bcfcf))
* **ego-field-test:** resolve imports/no-gtk-in-extension false positives ([#128](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/128)) ([8e39d98](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/8e39d9875b532aee235ad40583f87d94c9935224))
* **ego-lint:** add missing CSS shell classes to KNOWN_SHELL_CLASSES ([#54](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/54)) ([c6c61be](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/c6c61be9515070547f1a88f6b162ae04cc83250b))
* **ego-lint:** add replacement-pattern to R-VER rules for version-compat suppression ([#84](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/84)) ([d7051cf](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d7051cff429a43cc7952c5dedef2776c56656a76))
* **ego-lint:** add skip-comments to R-LOG-03 to prevent block comment FPs ([#132](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/132)) ([f138a43](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f138a432ea2697566faf261a16abb62675656992))
* **ego-lint:** add src/ layout license fallback and UUID-dir skip ([#30](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/30)) ([9f616ec](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/9f616eccbb60b53e9a8aff97a8f14be501697957))
* **ego-lint:** add src/ metadata.json fallback for build-system extensions ([#24](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/24)) ([145b639](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/145b639da08eb1f808347b4b2d6883d47b21fe7d))
* **ego-lint:** add src/schemas/ fallback for non-standard layouts ([#80](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/80)) ([4d00563](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4d0056309452006cc047dd18e661d67bfcd993c8))
* **ego-lint:** add version-compat suppression and calibrate severities ([#69](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/69)) ([5442f13](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/5442f13186ebb2b554132ace2faf0f390f73491d))
* **ego-lint:** anchor Gdk import pattern to avoid matching GdkPixbuf ([#101](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/101)) ([0e07043](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/0e07043e1305441d6427cf50d751dd22a299a22c))
* **ego-lint:** auto-detect and exclude vendored files from all lint checks ([#152](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/152)) ([81d48cd](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/81d48cdf22e4611a879b3b7ce6158fd9d655e7da))
* **ego-lint:** avoid false FAIL when enum-id precedes schema-id in check-schema ([#148](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/148)) ([8399589](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/83995890882984965fe2533a48de424cbda56613))
* **ego-lint:** correct R-SLOP-01 provenance post-filter matching ([#85](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/85)) ([ff05efb](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ff05efb63a80a19667d165a1d956e3f6efa97a13))
* **ego-lint:** deduplicate prototype-override warnings ([#32](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/32)) ([431ad18](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/431ad1831a1f4c3b94452d5ed9111ff6ac9d0190))
* **ego-lint:** detect compiled TypeScript and suppress noisy rules ([#52](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/52)) ([1b1b5d4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/1b1b5d4d6f83f63e0a5ba7d9584b4332357a84f6))
* **ego-lint:** downgrade css/shell-class-override from FAIL to WARN ([#100](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/100)) ([4aa6f2f](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4aa6f2f25b933b6c7c81ed91235bf1495c2c1adb))
* **ego-lint:** downgrade css/shell-class-override from FAIL to WARN ([#112](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/112)) ([dc83726](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/dc83726501f76ba5dc3047a6eb8acf2fcdb6a60a))
* **ego-lint:** downgrade missing LICENSE from FAIL to WARN ([#110](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/110)) ([fe0eab7](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/fe0eab7e9d72174c0212c695fac3f43d0b1536de))
* **ego-lint:** enhance GSettings signal leak detection for helper classes ([#87](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/87)) ([21f7390](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/21f73904e110be1575cb56a390fa73af1738ee22))
* **ego-lint:** exclude preferences/ dirs from gsettings-signal-leak ([#102](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/102)) ([60b15d3](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/60b15d346c5024fe0dfa1fa11e6a836a789c4b4a))
* **ego-lint:** exclude service/ daemon code from extension-specific checks ([#147](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/147)) ([2962779](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/2962779cc0e695d4051027bcac769debaa519f7d))
* **ego-lint:** exclude service/ dir from R-DEPR-06 and R-DEPR-10 ([#99](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/99)) ([ed40e47](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/ed40e47251fa6d6982ac53fb3f3a0cca53df65fc))
* **ego-lint:** exempt isLocked guard from impossible-state and session-modes checks ([#31](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/31)) ([69c6254](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/69c6254faf476650d58c92bb30e53c9d7dc66865))
* **ego-lint:** expand CSS shell-class list from GNOME Shell SCSS source ([#57](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/57)) ([311da35](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/311da3586f131053dc0a8f739f465e3065362c69))
* **ego-lint:** expand init/shell-modification and constructor-resources exemptions ([#88](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/88)) ([14d0ca3](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/14d0ca3a06f74017e0a7eaba2382161c977dd8a8))
* **ego-lint:** expand R-SLOP-24 guard for system schema identifiers ([#139](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/139)) ([1a58b06](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/1a58b06cfe97e5d6f51441131ba3c897ba749f76))
* **ego-lint:** expand R-SLOP-24 guard for system schemas and multi-line constructors ([#135](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/135)) ([27787a6](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/27787a66ee34d36e5ad5f7e2aeded5ae1025fdd4))
* **ego-lint:** expand R-SLOP-38 guard for domain-specific identifiers ([#141](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/141)) ([4aaf615](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4aaf615db10e890d46ab1992288b8968175a36db))
* **ego-lint:** handle async arrow functions and GObject branch in check-init.py ([#55](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/55)) ([9d6654a](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/9d6654aa9421b9e46b3d6085527e33055544e117))
* **ego-lint:** make R-LIFE-25 bare connectSignal always FAIL regardless of disconnectSignal elsewhere ([#91](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/91)) ([05523f9](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/05523f932a40ce30df421bd6cf0535d7c222c590))
* **ego-lint:** narrow R-LIFE-25 auto-cleanup to D-Bus-specific disconnectSignal ([#65](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/65)) ([8263cbc](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/8263cbce2c98905a2b974f28f8e04beecac74b5e))
* **ego-lint:** propagate strip_comments newline preservation to all scripts ([#61](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/61)) ([4178a5a](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/4178a5acfa978c5c35c532887bc14b0e1ca77ca2))
* **ego-lint:** recognize alternative cleanup methods in resource tracking ([#130](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/130)) ([bbc0f51](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/bbc0f51d708aab372747288cf4c95eadb7a3d17a))
* **ego-lint:** recognize array-based signal ID storage in gsettings-signal-leak ([#64](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/64)) ([99c89c0](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/99c89c032237fcedb972d05177c59bb03b228cf1))
* **ego-lint:** recognize full GPL license text in license check ([#127](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/127)) ([38cbb59](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/38cbb5902335146e36a6601dcec98eeec3538af0))
* **ego-lint:** reduce false positives for R-SLOP-35, R-SEC-03, R-SLOP-13 ([#123](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/123)) ([860fc0b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/860fc0b0b4f9b3f41afff553c4d6692b5362bb93))
* **ego-lint:** reduce init-time safety false positives ([#21](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/21)) ([e46e2df](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/e46e2df6447bb2ca84e3a87ce5bb538c9fa63906))
* **ego-lint:** reduce Media Controls false positives ([#23](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/23)) ([7cea626](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/7cea626a84e66cd18311f3159d4f2abc434d775d))
* **ego-lint:** reduce resource-tracking FPs for blur-my-shell ([#143](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/143)) ([99c5903](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/99c5903c97ae3ca0eb835632f405ae225a42bc54))
* **ego-lint:** reduce resource-tracking/no-destroy-method false positives ([#86](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/86)) ([30bbeac](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/30bbeac6695add0fa00026e1a41695b5e3c5644f))
* **ego-lint:** reduce signal-balance false positives ([#13](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/13)) ([900b133](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/900b133f9e0aa487f517ffd0660c182fe47e0124))
* **ego-lint:** reduce Tiling Shell false positives ([#22](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/22)) ([62c5509](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/62c55092c3071d5e88b1f06231d249d3c4c4267b))
* **ego-lint:** remove Shell.ActionMode.ALL from hallucinated-API list ([#149](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/149)) ([715519f](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/715519fb29ebcc2225b97495b8d9203a981a411f))
* **ego-lint:** scope init/shell-modification to Extension class constructors ([#140](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/140)) ([5e86aa6](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/5e86aa6f41f1dfdf1967365ff9cf5014ccb82ccb))
* **ego-lint:** skip file-structure checks for compiled TypeScript extensions ([#103](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/103)) ([f15ddcb](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f15ddcb4cf312cc68371bb06fa231b6653a27161))
* **ego-lint:** skip JSDoc block comments in R-WEB-06 document.* check ([#150](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/150)) ([fc10806](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/fc108067c6e9ae8a945309008e9e108244707a5d))
* **ego-lint:** skip R-LOG-03 in resources/ and detect Promise-returning methods in catch-on-sync ([#145](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/145)) ([7d76ee5](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/7d76ee542ef7c3970e36796744593cbb3b4f155b))
* **ego-lint:** skip signal callback bodies in constructor init check ([#129](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/129)) ([d1fa661](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/d1fa661167970e3da6a72b9c97dc3e96f1ed60cd))
* **ego-lint:** split R-SLOP-11 to fix false positive on GLib.source_remove() ([#126](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/126)) ([a441201](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/a441201475558a2c7d7648c9f8179b0f8d77f0dc))
* **ego-lint:** suppress R-QUAL-28 for distinct getSettings() schema arguments ([#81](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/81)) ([f8e1da7](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f8e1da7e9217ff54b7809a0ba9cd37451cc8a040))
* **ego-lint:** suppress R-VER46-01/02 for ShellVersion-guarded else branches ([#151](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/151)) ([614883e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/614883e82ed24f45b9bdee0e7d9510421a3f1114))
* **ego-lint:** tighten R-SLOP-38 to reduce over-long identifier false positives ([#82](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/82)) ([fe88f1b](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/fe88f1b51c0f36f1ee57fd335f0a03bc0ac31815))
* **ego-lint:** verify R-VER48-02 guard matches Config.PACKAGE_VERSION ([#133](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/133)) ([6dfeca1](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/6dfeca1b38262c733a0130fcd974118e7ed7d8e3))
* **ego-lint:** widen R-VER48-02 guard-window for distant version checks ([#53](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/53)) ([5ae31e0](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/5ae31e0f2614896b827a343954bf96336b147e85))


### Documentation

* add ego-review pipeline efficiency design spec ([56bcdc3](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/56bcdc3986c7d9e3df7d10cbd655667a32829dfb))
* add field test reports for Tiling Shell and Media Controls ([#25](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/25)) ([f8b55f7](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/f8b55f7579d42361cc5dc22f54281ed3ff2fc3d3))
* add field-tests/README.md with extension catalog and results ([#67](https://github.com/ZviBaratz/gnome-extension-reviewer/issues/67)) ([22fc27c](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/22fc27c559f9af052bc6df79101fe73a3ec223da))
* add missing skill labels and fix issue template auto-labels ([782c7b4](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/782c7b408661decf08c711ad325043fbbd9f9f39))
* add resource-tracking FP reduction design spec ([a7e0a2c](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/a7e0a2c93be7bf8c3954098f7c37ddd99c484675))
* **ego-field-test:** add 03-08 regression report, update baselines and annotations ([c5b823e](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/c5b823e85784d7de93399ccfac58db5e3be19c5f))
* **ego-field-test:** add version info to README extension catalog and update to 03-08 ([bdb4919](https://github.com/ZviBaratz/gnome-extension-reviewer/commit/bdb491917f5e674110891165568a58e97e8d3381))

## v0.1.0 — 2026-03-03

### Features

- **ego-simulate**: Added ESLint errors as rejection reason #23 (weight 5) to the taxonomy — crash-at-runtime bugs from undefined references now score appropriately (#2, PR #5)
- **ego-simulate**: ego-lint FAIL results now integrate into taxonomy scoring — each unmapped FAIL adds weight 5, WARNs route to Advisory Notes (#3, PR #6)

### Bug Fixes

- **ego-review**: Added "NOT a signal" exception to ai-slop checklist item #4 — `_destroyed` + `_initializing` (re-entrancy guard) is not the over-engineered state machine anti-pattern (#1, PR #4)

### Changed

- **ego-lint**: Version-gated R-WEB-01/02/10/11 (setTimeout/setInterval/clearTimeout/clearInterval) to `max-version: 44` — GJS provides native polyfills since GNOME 45
- **ego-lint**: Extended license check to recognize LICENSE.rst/.md/.txt and COPYING variants
- **ego-lint**: Downgraded `uuid-matches-dir` from FAIL to WARN — cloned repos don't match UUID
- Moved "How This Was Built" section earlier in README for transparency
- Promoted `scripts/new-rule.sh` as primary contribution workflow in CONTRIBUTING.md
- Added fixture validation checklist and debugging tips to CONTRIBUTING.md
- Separated hara-hachi-bu regression into `tests/run-regression.sh`
- Named hara-hachi-bu as regression baseline in README
- Strengthened community ownership messaging in README
- Updated stale assertion/fixture counts in docs

### What's Included

- **124 pattern rules** in `rules/patterns.yaml` covering web APIs, deprecated APIs, security, import segregation, AI slop detection, GNOME 44–50 migration, and more
- **17 structural check scripts** (Python/bash) for metadata validation, lifecycle symmetry, resource graph construction, async safety, GObject patterns, preferences validation, schema checks, package validation, disclosure checks, polkit validation, schema usage analysis, and accessibility
- **Cross-file resource tracking** — builds a resource graph (signals, timeouts, widgets, D-Bus, file monitors, GSettings) and detects orphaned resources
- **Version-gated rules** — GNOME 44–50 migration rules that only fire when the extension's declared `shell-version` includes the relevant version
- **Contributor tooling** — `scripts/new-rule.sh` for scaffolding rules (with next-ID suggestion), `scripts/validate-fixture.sh` for fixture validation, `scripts/validate-rule.sh` for rule testing, `apply-patterns.py --validate` for rule file validation
- **153 test fixtures** with 416 assertions
- **CI integration** — GitHub Actions and GitLab CI examples in `docs/ci-integration.md`

### False Positive Reduction

- Removed R-SEC-07 (redundant clipboard check — `quality/clipboard-disclosure` is a strict superset)
- Consolidated `quality/private-api` output into a single warning per check instead of up to 6
- Changed verdict to count unique check IDs instead of raw warning lines
- Fixed `quality/gettext-pattern` fix message (was suggesting `this.gettext()`, now suggests ESM import)
- Added `deduplicate: true` to R-SEC-20 to reduce noise on multi-file pkexec references

### Documentation

- Added First Contribution Workflow, Where to Find Sources, severity upgrade criteria, and License sections to CONTRIBUTING.md
- Expanded Tier 2 contribution guide with script selection table covering all 13 check scripts
- Broadened PR template to cover non-rule contributions (bug fixes, docs, tooling)
- Added co-maintainer onboarding path to GOVERNANCE.md
- Added Help Wanted subsection to README surfacing self-contained gaps
- Added troubleshooting section to rules/README.md

### Research Basis

Rules are grounded in analysis of 9 real EGO reviews, 109 extracted requirements from gjs.guide, GNOME Shell GitLab guideline evolution across versions 44–50, and reverse-engineered patterns from 5 popular approved extensions. 8 unwritten reviewer rules were identified and encoded. Full research: [docs/research/](docs/research/).

### Known Limitations

- Polkit action ID validation not yet implemented (if `pkexec` used, `.policy` file not verified)
- Schema filename validation partial (warns but doesn't block on filename mismatch)
- Module-scope mutable state detection not yet implemented (`Map`/`Set` at module level)
- Full gap list: [docs/research/gap-analysis.md](docs/research/gap-analysis.md)
