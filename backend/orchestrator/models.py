# Placeholder for config / status data models

from pydantic import BaseModel, Field


class IntentRequest(BaseModel):
    """
    Request body for /intent endpoint.
    """
    text: str = Field(..., description="Natural language description of the desired scenario")


class NodeConfig(BaseModel):
    sensors: int = Field(10, description="Number of sensor nodes")
    edges: int = Field(2, description="Number of edge gateways")
    sites: int = Field(1, description="Number of logical sites / clusters")
    cloud: int = Field(1, description="Number of cloud nodes (usually 1)")


class LinkProfile(BaseModel):
    inter_site_quality: str = Field(
        "normal",
        description="High-level description of inter-site link quality (weak/normal/strong)",
    )


class SimulationConfig(BaseModel):
    duration_s: int = Field(120, description="Simulation duration in seconds")


class ScenarioConfig(BaseModel):
    """
    Normalized internal representation of an intent, returned by /intent.
    """
    raw_intent: str = Field(..., description="Original user intent text")
    objective: str = Field(..., description="Primary optimization goal")
    protocol: str = Field(..., description="Chosen communication style (mqtt-like/tcp-like/udp-like/auto)")
    nodes: NodeConfig
    links: LinkProfile
    simulation: SimulationConfig
    notes: str | None = Field(
        None,
        description="Optional human-readable comment about how the intent was interpreted",
    )
