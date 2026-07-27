# pymakeutils

A collection of CLI utilities to extract information from Makefiles:
- `list-make-prerequisites`: List all prerequisites of a target (optionally recursively)
- `list-dependent-make-targets`: List all targets that depend on a certain prerequisite (optionally recursively)

## Related GitHub Actions
- [colluca/list-make-prerequisites](https://github.com/colluca/list-make-prerequisites): List a target's prerequisites and their combined hash
- [colluca/make-prerequisites-changed](https://github.com/colluca/make-prerequisites-changed): Check whether any of a target's prerequisites changed since a base commit
