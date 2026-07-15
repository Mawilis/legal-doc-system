import logging
from pathlib import Path
import sys
sys.path.append('/Users/wilsonkhanyezi/legal-doc-system/tools/repository/core')

import repository_walker

logging.basicConfig(level=logging.DEBUG)

def main():
    repo_walker = repository_walker.RepositoryWalker()
    knowledge_base_dir = Path('/Users/wilsonkhanyezi/legal-doc-system/knowledge-base')
    if not knowledge_base_dir.exists():
        logging.error(f'Knowledge Base directory not found: {knowledge_base_dir}')
        return

    repo_walker.walk(knowledge_base_dir)
    summary = repo_walker.get_summary()
    print(summary)

if __name__ == '__main__':
    main()