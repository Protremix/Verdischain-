from plugin_architecture import PluginRegistry, PluginType, Capability
from llm_providers import register_all_providers
from specialized_providers import register_all_specialized

r = PluginRegistry()
register_all_providers(r)
register_all_specialized(r)

stats = r.stats()
print(f"Total providers: {stats['total_plugins']}")
print(f"By type: {stats['by_type']}")
print()

for cap in Capability:
    providers = r.list_by_capability(cap)
    if providers:
        ids = [p.id for p in providers]
        print(f"{cap.value}: {ids}")
