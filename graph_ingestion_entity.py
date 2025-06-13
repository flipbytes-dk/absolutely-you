
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from pydantic import BaseModel, Field

# CONFIGURATION
logging.basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Loaded environment variables from .env file.")

neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')

logger.info(f"Graphiti connection config: uri={neo4j_uri}, user={neo4j_user}")

# Define Pydantic models for the nodes
class Procedure(BaseModel):
    """A cosmetic procedure offered by the clinic."""
    procedure_type: str | None = Field(None, description="Surgical, Non-Surgical …")
    cost_raw: str | None = Field(None, description="Original cost string, e.g. 'From $5,500'")
    recovery_time: str | None = Field(None, description="e.g. 'one to two weeks'")
    results_duration: str | None = Field(None, description="e.g. '3-6 months'")

class BodyArea(BaseModel):
    """An anatomical region that the procedure treats or alters."""
    anatomical_region: str | None = Field(None, description="e.g. 'Labia minora'")

class PaymentMethod(BaseModel):
    """A way the patient can pay for the procedure."""
    provider: str | None = Field(None, description="'Cash', 'Visa', 'AfterPay' …")

class Doctor(BaseModel):
    """A medical professional who performs or must authorise the procedure."""
    speciality: str | None = Field(None, description="e.g. 'Cosmetic Surgeon'")


# Ontology dictionaries
entity_types = {
    "Procedure": Procedure,
    "BodyArea": BodyArea,
    "PaymentMethod": PaymentMethod,
    "Doctor": Doctor,
}



def get_json_files(directory):
    files = [f for f in os.listdir(directory) if f.endswith('.json') and f not in ('all_links.json', '.DS_Store')]
    files.sort()
    return files

async def main():
    if not neo4j_uri or not neo4j_user or not neo4j_password:
        logger.error('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')
        raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

    logger.info("Opening connection to Graphiti...")
    graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    success_count = 0
    skip_count = 0
    fail_count = 0
    try:
        await graphiti.build_indices_and_constraints()
        docs_dir = "docs_kb"
        files = get_json_files(docs_dir)

        logger.info(f"Found {len(files)} files to process in '{docs_dir}'.")

        files = files[100:124]
        for i, fname in enumerate(files):
            fpath = os.path.join(docs_dir, fname)
            logger.info(f"[START] Processing file {i+1}/{len(files)}: {fname}")
            try:
                with open(fpath, 'r') as f:
                    data = json.load(f)
                content = data.get('json')
                if not content:
                    logger.warning(f"[SKIP] No 'json' field in {fname} (index {i})")
                    skip_count += 1
                    continue
                episode_body = content.copy()
                episode_name = content.get('procedure_name', f"Procedure {i+1}")
                logger.info(f"Adding episode: name='{episode_name}' from file '{fname}'")
                episode = await graphiti.add_episode(
                    name="Procedure",
                    episode_body=json.dumps(episode_body),
                    source=EpisodeType.json,
                    source_description='procedures metadata',
                    reference_time=datetime.now(timezone.utc),
                    group_id="procedures",
                    entity_types=entity_types
                )
                # Log the result appropriately
                if hasattr(episode, 'episodes') and episode.episodes:
                    logger.info(f"[SUCCESS] Added episode from {fname}: {episode.episodes[0].uuid}")
                else:
                    logger.info(f"[SUCCESS] Added episode from {fname}: {episode}")
                success_count += 1
            except Exception as e:
                import traceback
                logger.error(f"[ERROR] Failed to add {fname} (index {i}): {e}\n{traceback.format_exc()}")
                fail_count += 1
            logger.info(f"[END] Finished processing file {i+1}/{len(files)}: {fname}")
        logger.info(f"Processing complete. Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")
    finally:
        await graphiti.close()
        logger.info('Graphiti connection closed')

if __name__ == '__main__':
    asyncio.run(main()) 