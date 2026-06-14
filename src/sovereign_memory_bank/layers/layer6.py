"""Layer 6: Executive Memory (research, specifications, projects, plans)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from sovereign_memory_bank.layers.layer_manager import LayerIndex


class ResearchTopic(BaseModel):
    id: str
    title: str
    description: str
    status: str = "open"
    related_question_ids: list[str] = []


class Specification(BaseModel):
    id: str
    title: str
    content: str
    version: str = "0.1.0"
    status: str = "draft"


class ProjectPlan(BaseModel):
    id: str
    title: str
    description: str
    tasks: list[dict] = []
    status: str = "planning"


class Layer6:
    """Manages executive memory for action-oriented knowledge."""

    def __init__(self, layer_manager) -> None:
        self.layers = layer_manager
        self.research_dir = layer_manager.get_subdir(LayerIndex.EXECUTIVE, "research")
        self.specs_dir = layer_manager.get_subdir(LayerIndex.EXECUTIVE, "specifications")
        self.projects_dir = layer_manager.get_subdir(LayerIndex.EXECUTIVE, "projects")
        self.plans_dir = layer_manager.get_subdir(LayerIndex.EXECUTIVE, "plans")

    def save_research(self, topic: ResearchTopic) -> Path:
        import json
        path = self.research_dir / f"{topic.id}.json"
        path.write_text(topic.model_dump_json(indent=2))
        return path

    def list_research(self) -> list[ResearchTopic]:
        topics = []
        for f in sorted(self.research_dir.glob("*.json")):
            topics.append(ResearchTopic.model_validate_json(f.read_text()))
        return topics

    def save_spec(self, spec: Specification) -> Path:
        path = self.specs_dir / f"{spec.id}.md"
        path.write_text(f"# {spec.title}\n\nVersion: {spec.version}\nStatus: {spec.status}\n\n{spec.content}")
        return path

    def list_specs(self) -> list[Specification]:
        specs = []
        for f in sorted(self.specs_dir.glob("*.md")):
            content = f.read_text()
            lines = content.split("\n")
            title = lines[0].lstrip("# ") if lines else f.stem
            specs.append(Specification(id=f.stem, title=title, content=content))
        return specs

    def save_plan(self, plan: ProjectPlan) -> Path:
        import json
        path = self.plans_dir / f"{plan.id}.json"
        path.write_text(plan.model_dump_json(indent=2))
        return path

    def list_plans(self) -> list[ProjectPlan]:
        plans = []
        for f in sorted(self.plans_dir.glob("*.json")):
            plans.append(ProjectPlan.model_validate_json(f.read_text()))
        return plans
