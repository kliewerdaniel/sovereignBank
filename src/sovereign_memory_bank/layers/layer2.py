"""Layer 2: Semantic Memory (taxonomy, clusters, communities)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from sovereign_memory_bank.layers.layer_manager import LayerIndex


class TaxonomyNode(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    children: list[str] = []
    concept_ids: list[str] = []


class Cluster(BaseModel):
    id: str
    name: str
    concept_ids: list[str]
    centroid: list[float] = []


class Community(BaseModel):
    id: str
    name: str
    member_ids: list[str]
    description: str = ""


class Layer2:
    """Manages semantic organization: taxonomy, clusters, communities."""

    def __init__(self, layer_manager) -> None:
        self.layers = layer_manager
        self.taxonomy_dir = layer_manager.get_subdir(LayerIndex.SEMANTIC, "taxonomy")
        self.clusters_dir = layer_manager.get_subdir(LayerIndex.SEMANTIC, "clusters")
        self.communities_dir = layer_manager.get_subdir(LayerIndex.SEMANTIC, "communities")

    def save_taxonomy(self, node: TaxonomyNode) -> Path:
        import json
        path = self.taxonomy_dir / f"{node.id}.json"
        path.write_text(node.model_dump_json(indent=2))
        return path

    def load_taxonomy(self, node_id: str) -> Optional[TaxonomyNode]:
        import json
        path = self.taxonomy_dir / f"{node_id}.json"
        if path.exists():
            return TaxonomyNode.model_validate_json(path.read_text())
        return None

    def list_taxonomy(self) -> list[TaxonomyNode]:
        nodes = []
        for f in sorted(self.taxonomy_dir.glob("*.json")):
            nodes.append(TaxonomyNode.model_validate_json(f.read_text()))
        return nodes

    def save_cluster(self, cluster: Cluster) -> Path:
        import json
        path = self.clusters_dir / f"{cluster.id}.json"
        path.write_text(cluster.model_dump_json(indent=2))
        return path

    def list_clusters(self) -> list[Cluster]:
        clusters = []
        for f in sorted(self.clusters_dir.glob("*.json")):
            clusters.append(Cluster.model_validate_json(f.read_text()))
        return clusters

    def save_community(self, community: Community) -> Path:
        import json
        path = self.communities_dir / f"{community.id}.json"
        path.write_text(community.model_dump_json(indent=2))
        return path

    def list_communities(self) -> list[Community]:
        communities = []
        for f in sorted(self.communities_dir.glob("*.json")):
            communities.append(Community.model_validate_json(f.read_text()))
        return communities
