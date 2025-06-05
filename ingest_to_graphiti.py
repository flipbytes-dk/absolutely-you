"""
Copyright 2025, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from logging import INFO

from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

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
        files = get_json_files(docs_dir)[101:122]

        logger.info(f"Found {len(files)} files to process in '{docs_dir}'.")

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
                    name=episode_name,
                    episode_body=json.dumps(episode_body),
                    source=EpisodeType.json,
                    source_description='procedure metadata',
                    reference_time=datetime.now(timezone.utc),
                    group_id="absolute_cosmetic_procedures"
                )
                # Log the result appropriately
                if hasattr(episode, 'episodes') and episode.episodes:
                    logger.info(f"[SUCCESS] Added episode from {fname}: {episode.episodes[0].uuid}")
                else:
                    logger.info(f"[SUCCESS] Added episode from {fname}: {episode}")
                success_count += 1
            except Exception as e:
                logger.error(f"[ERROR] Failed to add {fname} (index {i}): {e}")
                fail_count += 1
            logger.info(f"[END] Finished processing file {i+1}/{len(files)}: {fname}")
        logger.info(f"Processing complete. Success: {success_count}, Skipped: {skip_count}, Failed: {fail_count}")
    finally:
        await graphiti.close()
        logger.info('Graphiti connection closed')

if __name__ == '__main__':
    asyncio.run(main()) 