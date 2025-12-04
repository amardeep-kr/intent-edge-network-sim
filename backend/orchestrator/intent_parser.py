import re

from .models import ScenarioConfig, NodeConfig, LinkProfile, SimulationConfig

from typing import Dict, Any

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}



def _extract_int_before_keyword(text: str, keyword: str, default: int | None = None) -> int | None:
    """
    Find an integer (digit or word) immediately before a keyword.
    E.g. 'three industrial sites' or '3 sites' or '20 sensors per site'.
    """
    text_low = text.lower()

    # digit form
    m = re.search(rf"(\d+)\s+{keyword}", text_low)
    if m:
        return int(m.group(1))

    # word form
    m = re.search(rf"\b({'|'.join(NUMBER_WORDS.keys())})\s+{keyword}", text_low)
    if m:
        return NUMBER_WORDS[m.group(1)]

    return default


# def parse_intent_to_config(intent_text: str) -> Dict[str, Any]:
#     """
#     Very lightweight parser that turns free-text intent into a ScenarioConfig-like dict.

#     Handles phrases like:
#       - '3 industrial sites with 20 sensors per site'
#       - 'two sites and ten sensors per site'
#       - '15 sensors total, 2 edges'
#     """
#     text = intent_text.strip()
#     low = text.lower()

#     # --- sites / edges ---

#     # Try to detect 'X sites' / 'X industrial sites'
#     sites = _extract_int_before_keyword(low, "industrial sites")
#     if sites is None:
#         sites = _extract_int_before_keyword(low, "sites", default=None)

#     # If still unknown, fall back to 1
#     if sites is None or sites <= 0:
#         sites = 1

#     # Edges: by default one edge per site, unless explicitly specified
#     edges = _extract_int_before_keyword(low, "edges", default=None)
#     if edges is None or edges <= 0:
#         edges = sites

#     # --- sensors ---

#     # Case 1: '20 sensors per site'
#     sensors_per_site = _extract_int_before_keyword(low, "sensors per site", default=None)

#     if sensors_per_site is not None:
#         sensors = sensors_per_site * sites
#     else:
#         # Case 2: '60 sensors' (total)
#         sensors_total = _extract_int_before_keyword(low, "sensors", default=None)
#         if sensors_total is None:
#             sensors_total = 4 * sites  # small default
#         sensors = sensors_total

#     # --- duration ---

#     duration_s = 300  # default 5 minutes
#     m = re.search(r"(\d+)\s*(seconds|second|sec|s)\b", low)
#     if m:
#         duration_s = int(m.group(1))
#     else:
#         m = re.search(r"(\d+)\s*(minutes|minute|min)\b", low)
#         if m:
#             duration_s = int(m.group(1)) * 60

#     # --- objective / protocol / link quality ---

#     objective = "balanced"
#     if "reliab" in low or "resilien" in low:
#         objective = "reliability"
#     elif "latency" in low or "delay" in low:
#         objective = "latency"
#     elif "throughput" in low or "bandwidth" in low:
#         objective = "throughput"

#     protocol = "generic"
#     if "mqtt" in low:
#         protocol = "mqtt-like"
#     elif "coap" in low:
#         protocol = "coap-like"
#     elif "http" in low or "rest" in low:
#         protocol = "http-like"

#     link_quality = "normal"
#     if "weak inter-site" in low or "congested" in low:
#         link_quality = "weak"
#     elif "strong inter-site" in low or "high quality link" in low:
#         link_quality = "strong"

#     config: Dict[str, Any] = {
#         "raw_intent": text,
#         "objective": objective,
#         "protocol": protocol,
#         "nodes": {
#             "sensors": sensors,
#             "edges": edges,
#             "sites": sites,
#             "cloud": 1,
#         },
#         "links": {
#             "inter_site_quality": link_quality,
#         },
#         "simulation": {
#             "duration_s": duration_s,
#         },
#         "notes": (
#             f"Interpreted as {sites} site(s), {edges} edge node(s), "
#             f"{sensors} sensor(s) total, objective='{objective}', "
#             f"protocol='{protocol}', link_quality='{link_quality}'."
#         ),
#     }

#     return config


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


# def _parse_sites(text: str, default: int = 1) -> int:
#     text_l = text.lower()
#     m = re.search(r"(\d+)\s+sites?", text_l)
#     if m:
#         return int(m.group(1))
#     m = re.search(r"(\d+)\s+factories?", text_l)
#     if m:
#         return int(m.group(1))
#     return default

def _parse_sites(text: str, default: int = 1) -> int:
    text_l = text.lower()

    # Try '3 industrial sites', '3 edge sites', etc.
    sites = _extract_int_before_keyword(text_l, "industrial sites", default=None)
    if sites is None:
        sites = _extract_int_before_keyword(text_l, "edge sites", default=None)
    if sites is None:
        # plain '3 sites'
        sites = _extract_int_before_keyword(text_l, "sites", default=None)
    if sites is None:
        # fallback: factories as a synonym
        sites = _extract_int_before_keyword(text_l, "factories", default=default)

    if sites is None or sites <= 0:
        sites = default

    return sites


def _parse_link_quality(text: str) -> str:
    text_l = text.lower()
    if "weak" in text_l or "poor" in text_l or "congested" in text_l:
        return "weak"
    if "strong" in text_l or "high speed" in text_l or "good link" in text_l:
        return "strong"
    return "normal"


# def _parse_nodes(text: str) -> NodeConfig:
#     text_l = text.lower()

#     sensors = _extract_first_int_near_keyword(text_l, "sensor", default=10)
#     edges = _extract_first_int_near_keyword(text_l, "edge", default=2)
#     sites = _parse_sites(text_l, default=1)
#     cloud = 1  # keep simple for now

#     return NodeConfig(sensors=sensors, edges=edges, sites=sites, cloud=cloud)


def _parse_nodes(text: str) -> NodeConfig:
    text_l = text.lower()

    # 1) How many sites?
    sites = _parse_sites(text_l, default=1)

    # 2) Sensors: try "X sensors per site" first
    per_site = None
    m = re.search(r"(\d+)\s+sensors?\s+per\s+site", text_l)
    if m:
        per_site = int(m.group(1))

    if per_site is not None:
        sensors = per_site * max(sites, 1)
    else:
        # fallback: any "X sensors" pattern
        sensors = _extract_first_int_near_keyword(text_l, "sensor", default=10)

    # 3) Edges: explicit number near "edge" if present
    edges = _extract_first_int_near_keyword(text_l, "edge", default=0)

    # if no explicit edges but we have sites, assume one edge per site
    if edges == 0 and sites > 0:
        edges = sites
    if edges == 0:
        edges = 2  # absolute last fallback

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
