# Build and update checks

This repository follows the same addon layout as [BigDebuffs](https://github.com/oliome/bigdebuffs): Lua/TOC files at the root, Luacheck, `.pkgmeta`, and the BigWigs packager. GitHub Releases contain the install ZIP; no binaries or Python tooling are committed. Development files under `.github` are excluded from the package.

Push a `v*` tag to run the checks and package a release. Tags containing `beta` create preview releases. The TOC's `@project-version@` is replaced by the packager. Native Lua 5.1 tests run the real addon using mocked WoW APIs; shell tests cover update detection and issue reporting.

`Forever update` polls [Blizzard's live wowf endpoint](https://us.version.battle.net/v2/products/wowf/versions) hourly. It can also run manually or receive a `wow-updated` repository dispatch. New builds of the known game patch stage an addon patch-version bump in `wow-version.json`, then run the checks. Passing updates are committed/tagged and packaged; failures open one deduplicated issue with logs. Unchanged builds stay quiet.

An unfamiliar game patch blocks publication until its actual Interface is verified. Blizzard's table does not provide Interface; it is never guessed from the build. An optional `FOREVER_BUILD_FEED_URL` repository variable may point to an HTTPS JSON feed with `product: wowf`, `channel: live`, and the exact official live `build`/`interface`. Otherwise verify that value in-game and update the checkpoint in a reviewed commit. The known patch retains its previously verified Interface; mocks do not prove live rendering/API compatibility. `runtime_ready: false` keeps automated tags in beta form.

Both workflows reuse the same checks. Update jobs package directly after tagging because a `GITHUB_TOKEN` push does not trigger the tag-build workflow. Push races and upload failures raise issues rather than overwriting history; if upload fails after a tag was pushed, rerun the build for that tag. GitHub schedules may be delayed or disabled after inactivity. The addon itself never downloads updates.
