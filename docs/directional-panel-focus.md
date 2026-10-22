# Directional panel focus contract

[Provider design](../holonight-qt/docs/sdd/directional-panel-focus.md) adds
HnBreadcrumbBar.focusCurrentSegment(): bool; [Files design](../holonight-files/docs/sdd/directional-panel-focus.md)
consumes it for NORMAL-mode Ctrl+H/J/K/L routing. The provider owns delegate lookup
and keyboard focus indication; Files owns panel ancestry, routing and modal guards.
Focus changes must not activate locations or mutate browsing state.

Build/install the provider into an isolated development prefix before building Files
against that prefix. Run focused breadcrumb and window tests, QML checks and sibling
container acceptance. Native routing and outlines require manual verification.
Publish the provider before any future consumer publication. This task does not
publish repositories, install system packages or update umbrella pins.

[Panel-local keys](../holonight-files/docs/sdd/panel-key-navigation.md) add sidebar l
activation and opt-in provider breadcrumb h/l movement. The provider owns visible
button order, boundaries and modifier filtering; Files enables it under its existing
mode/modal guard. Tab/Backtab redesign is deferred. Verify provider behavior first,
then Files against the isolated prefix; publication order and pin policy are unchanged.
