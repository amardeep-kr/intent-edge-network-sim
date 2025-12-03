# # Placeholder for intent → config parser

# import re
# from typing import Tuple

# from .models import ScenarioConfig, NodeConfig, LinkProfile, SimulationConfig


# def _extract_first_int_near_keyword(text: str, keyword: str, default: int) -> int:
#     """
#     Look for a number that appears near a given keyword.
#     Very simple heuristic: find '<number> <keyword>' or '<keyword> <number>'.
#     If nothing is found, return default.
#     """
#     pattern_before = rf"(\d+)\s+\w*{re.escape(keyword)}\w*"
#     pattern_after = rf"\w*{re.escape(keyword)}\w*\s+(\d+)"

#     match = re.search(pattern_before, text)
#     if match:
#         return int(match.group(1))

#     match = re.search(pattern_after, text)
#     if match:
#         return int(match.group(1))

#     return default


# def _parse_objective(text: str) -> str:
#     text_l = text.lower()
#     if "reliab" in text_l or "robust" in text_l or "resilien" in text_l:
#         return "reliability"
#     if "latenc" in text_l or "fast" in text_l or "responsive" in text_l:
#         return "latency"
#     if "bandwidth" in text_l or "efficient" in text_l or "cost" in text_l:
#         return "bandwidth_saving"
#     return "balanced"


# def _parse_protocol(text: str) -> str:
#     text_l = text.lower()
#     if "mqtt" in text_l:
#         return "mqtt-like"
#     if "coap" in text_l:
#         return "coap-like"
#     if "tcp" in text_l:
#         return "tcp-like"
#     if "udp" in text_l:
#         return "udp-like"
#     if "pub-sub" in text_l or "publish-subscribe" in text_l:
#         return "mqtt-like"
#     return "auto"


# def _parse_duration(text: str, default: int = 120) -> int:
#     """
#     Parse phrases like 'for 5 minutes', 'run 60s', etc.
#     Returns duration in seconds.
#     """
#     text_l = text.lower()
#     m = re.search(r"(\d+)\s*(seconds?|secs?|s)\b", text_l)
#     if m:
#         return int(m.group(1))

#     m = re.search(r"(\d+)\s*(minutes?|mins?|m)\b", text_l)
#     if m:
#         return int(m.group(1)) * 60

#     return default


# def _parse_sites(text: str, default: int = 1) -> int:
#     text_l = text.lower()
#     m = re.search(r"(\d+)\s+sites?", text_l)
#     if m:
#         return int(m.group(1))
#     m = re.search(r"(\d+)\s+factories?", text_l)
#     if m:
#         return int(m.group(1))
#     return default


# def _parse_link_quality(text: str) -> str:
#     text_l = text.lower()
#     if "weak" in text_l or "poor" in text_l or "congested" in text_l:
#         return "weak"
#     if "strong" in text_l or "high speed" in text_l or "good link" in text_l:
#         return "strong"
#     return "normal"


# def _parse_nodes(text: str) -> NodeConfig:
#     text_l = text.lower()

#     sensors = _extract_first_int_near_keyword(text_l, "sensor", default=10)
#     edges = _extract_first_int_near_keyword(text_l, "edge", default=2)

#     sites = _parse_sites(text_l, default=1)
#     cloud = 1  # keep simple for now

#     return NodeConfig(sensors=sensors, edges=edges, sites=sites, cloud=cloud)


# def parse_intent_to_config(intent_text: str) -> ScenarioConfig:
#     """
#     Main entry point: convert raw natural language intent into ScenarioConfig.

#     This is deliberately simple and robust:
#     - if something can't be parsed, sensible defaults are used.
#     - it never throws on weird input, it just falls back to defaults.
#     """
#     text = intent_text.strip()
#     if not text:
#         # Completely empty intent → fallback config
#         nodes = NodeConfig()
#         links = LinkProfile()
#         simulation = SimulationConfig()
#         objective = "balanced"
#         protocol = "auto"
#         note = "Empty intent; using default scenario configuration."
#         return ScenarioConfig(
#             raw_intent=intent_text,
#             objective=objective,
#             protocol=protocol,
#             nodes=nodes,
#             links=links,
#             simulation=simulation,
#             notes=note,
#         )

#     nodes = _parse_nodes(text)
#     objective = _parse_objective(text)
#     protocol = _parse_protocol(text)
#     links = LinkProfile(inter_site_quality=_parse_link_quality(text))
#     simulation = SimulationConfig(duration_s=_parse_duration(text))

#     note_parts: list[str] = []

#     note_parts.append(
#         f"Interpreted intent as {nodes.sensors} sensors, "
#         f"{nodes.edges} edges, {nodes.sites} site(s), "
#         f"objective='{objective}', protocol='{protocol}'."
#     )

#     if links.inter_site_quality != "normal":
#         note_parts.append(f"Inter-site link quality flagged as '{links.inter_site_quality}'.")

#     note = " ".join(note_parts)

#     return ScenarioConfig(
#         raw_intent=intent_text,
#         objective=objective,
#         protocol=protocol,
#         nodes=nodes,
#         links=links,
#         simulation=simulation,
#         notes=note,
#     )



import re

from .models import ScenarioConfig, NodeConfig, LinkProfile, SimulationConfig


def _extract_first_int_near_keyword(text: str, keyword: str, default: int) -> int:
    """
    Look for a number that appears near a given keyword.
    Very simple heuristic: find '<number> <keyword>' or '<keyword> <number>'.
    If nothing is found, return default.
    """
    pattern_before = rf"(\d+)\s+\w*{re.escape(keyword)}\w*"
    pattern_after = rf"\w*{re.escape(keyword)}\w*\s+(\d+)"

    match = re.search(pattern_before, text)
    if match:
        return int(match.group(1))

    match = re.search(pattern_after, text)
    if match:
        return int(match.group(1))

    return default


def _parse_objective(text: str) -> str:
    text_l = text.lower()
    if "reliab" in text_l or "robust" in text_l or "resilien" in text_l:
        return "reliability"
    if "latenc" in text_l or "fast" in text_l or "responsive" in text_l:
        return "latency"
    if "bandwidth" in text_l or "efficient" in text_l or "cost" in text_l:
        return "bandwidth_saving"
    return "balanced"


def _parse_protocol(text: str) -> str:
    text_l = text.lower()
    if "mqtt" in text_l:
        return "mqtt-like"
    if "coap" in text_l:
        return "coap-like"
    if "tcp" in text_l:
        return "tcp-like"
    if "udp" in text_l:
        return "udp-like"
    if "pub-sub" in text_l or "publish-subscribe" in text_l:
        return "mqtt-like"
    return "auto"


def _parse_duration(text: str, default: int = 120) -> int:
    """
    Parse phrases like 'for 5 minutes', 'run 60s', etc.
    Returns duration in seconds.
    """
    text_l = text.lower()
    m = re.search(r"(\d+)\s*(seconds?|secs?|s)\b", text_l)
    if m:
        return int(m.group(1))

    m = re.search(r"(\d+)\s*(minutes?|mins?|m)\b", text_l)
    if m:
        return int(m.group(1)) * 60

    return default


def _parse_sites(text: str, default: int = 1) -> int:
    text_l = text.lower()
    m = re.search(r"(\d+)\s+sites?", text_l)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+factories?", text_l)
    if m:
        return int(m.group(1))
    return default


def _parse_link_quality(text: str) -> str:
    text_l = text.lower()
    if "weak" in text_l or "poor" in text_l or "congested" in text_l:
        return "weak"
    if "strong" in text_l or "high speed" in text_l or "good link" in text_l:
        return "strong"
    return "normal"


def _parse_nodes(text: str) -> NodeConfig:
    text_l = text.lower()

    sensors = _extract_first_int_near_keyword(text_l, "sensor", default=10)
    edges = _extract_first_int_near_keyword(text_l, "edge", default=2)
    sites = _parse_sites(text_l, default=1)
    cloud = 1  # keep simple for now

    return NodeConfig(sensors=sensors, edges=edges, sites=sites, cloud=cloud)


def parse_intent_to_config(intent_text: str) -> ScenarioConfig:
    """
    Main entry point: convert raw natural language intent into ScenarioConfig.

    This is deliberately simple and robust:
    - if something can't be parsed, sensible defaults are used.
    - it never throws on weird input, it just falls back to defaults.
    """
    text = intent_text.strip()
    if not text:
        nodes = NodeConfig()
        links = LinkProfile()
        simulation = SimulationConfig()
        objective = "balanced"
        protocol = "auto"
        note = "Empty intent; using default scenario configuration."
        return ScenarioConfig(
            raw_intent=intent_text,
            objective=objective,
            protocol=protocol,
            nodes=nodes,
            links=links,
            simulation=simulation,
            notes=note,
        )

    nodes = _parse_nodes(text)
    objective = _parse_objective(text)
    protocol = _parse_protocol(text)
    links = LinkProfile(inter_site_quality=_parse_link_quality(text))
    simulation = SimulationConfig(duration_s=_parse_duration(text))

    note_parts: list[str] = []
    note_parts.append(
        f"Interpreted intent as {nodes.sensors} sensors, "
        f"{nodes.edges} edges, {nodes.sites} site(s), "
        f"objective='{objective}', protocol='{protocol}'."
    )
    if links.inter_site_quality != "normal":
        note_parts.append(f"Inter-site link quality flagged as '{links.inter_site_quality}'.")

    note = " ".join(note_parts)

    return ScenarioConfig(
        raw_intent=intent_text,
        objective=objective,
        protocol=protocol,
        nodes=nodes,
        links=links,
        simulation=simulation,
        notes=note,
    )
