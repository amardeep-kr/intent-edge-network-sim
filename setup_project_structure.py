# setup_project_structure.py

import os
from pathlib import Path

# root = current directory
ROOT = Path(__file__).parent

# folders to create
dirs = [
    ROOT / "backend",
    ROOT / "backend" / "orchestrator",
    ROOT / "backend" / "sim",
    ROOT / "dashboard",
    ROOT / "scenarios",
    ROOT / "outputs",
]

for d in dirs:
    d.mkdir(parents=True, exist_ok=True)

# minimal placeholder files
placeholders = {
    ROOT / "backend" / "__init__.py": "",
    ROOT / "backend" / "orchestrator" / "__init__.py": "",
    ROOT / "backend" / "orchestrator" / "main.py": """# Entry point for orchestrator API (FastAPI/Flask stub)\n\n""",
    ROOT / "backend" / "orchestrator" / "intent_parser.py": """# Placeholder for intent → config parser\n\n""",
    ROOT / "backend" / "orchestrator" / "models.py": """# Placeholder for config / status data models\n\n""",
    ROOT / "backend" / "sim" / "__init__.py": "",
    ROOT / "backend" / "sim" / "mininet_topology.py": """# Placeholder for Mininet topology builder\n\n""",
    ROOT / "backend" / "sim" / "processes.py": """# Placeholder for sensor/edge/cloud processes\n\n""",
    ROOT / "backend" / "sim" / "metrics.py": """# Placeholder for metrics collection logic\n\n""",
    ROOT / "backend" / "sim" / "agent.py": """# Placeholder for agent logic\n\n""",
    ROOT / "dashboard" / "app.py": """# Placeholder for Dash + Cytoscape dashboard\n\n""",
    ROOT / "scenarios" / "example_basic.yaml": "# Example scenario config will go here\n",
    ROOT / "requirements.txt": "# Add Python dependencies here later\n",
}

for path, content in placeholders.items():
    if not path.exists():
        path.write_text(content, encoding="utf-8")

print("Project structure created / updated.")
