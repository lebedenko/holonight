# Superseded: external dependency management

The framework-convergence initiative is superseded by ordinary CMake package discovery,
one digest-pinned Arch development/CI image, and proportional SDD. Historical design
and verification records remain for context; their unfinished framework work is retired.

See [the current workflow contract](../cmake-workflow/README.md) and [contribution rules](../../../CONTRIBUTING.md). CMake owns dependency requirements;
native builds use installed packages and `CMAKE_PREFIX_PATH`. Standalone container
acceptance builds pinned provider sources into a fresh prefix. The umbrella installer
continues to build against host packages and retain ownership/collision protections.
