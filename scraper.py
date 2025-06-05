import os
import types
from firecrawl import FirecrawlApp, JsonConfig
from pydantic import BaseModel, Field
import json

# Initialize the FirecrawlApp with your API key
app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

class ExtractSchema(BaseModel):
    procedure_name: str
    explanation: str
    treatment_overview: str
    procedure_type: str
    cost: str
    recovery_time: str
    results_duration: str
    miscellaneous_information: str

json_config = JsonConfig(
    schema=ExtractSchema.model_json_schema()
)

def make_json_safe(obj):
    """Recursively remove non-serializable fields (like functions) from dicts/lists."""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items() if not isinstance(v, types.FunctionType)}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif hasattr(obj, "model_dump"):
        return make_json_safe(obj.model_dump())
    elif hasattr(obj, "to_dict"):
        return make_json_safe(obj.to_dict())
    else:
        return str(obj)  # fallback: convert to string

crawl_url = "https://www.absolutecosmetic.com.au/procedures/"
map_result = app.map_url(crawl_url)

# Save all links to a file for inspection
all_links_path = os.path("all_links.json")
with open(all_links_path, "w") as f:
    json.dump(map_result.links, f, indent=2)
print(f"Saved {len(map_result.links)} links to {all_links_path}")

output_dir = "docs_kb"
os.makedirs(output_dir, exist_ok=True)

for i, url in enumerate(map_result.links):
    llm_extraction_result = app.scrape_url(
        url,
        formats=["json"],
        json_options=json_config
    )
    # Use model_dump if available, else to_dict, else as-is
    if hasattr(llm_extraction_result, "model_dump"):
        serializable_result = llm_extraction_result.model_dump()
    elif hasattr(llm_extraction_result, "to_dict"):
        serializable_result = llm_extraction_result.to_dict()
    else:
        serializable_result = llm_extraction_result
    serializable_result = make_json_safe(serializable_result)
    print(json.dumps(serializable_result, indent=2))
    file_path = os.path.join(output_dir, f"{i+63}.json")
    with open(file_path, "w") as f:
        json.dump(serializable_result, f, indent=2)
    print(f"Saved: {file_path}")

