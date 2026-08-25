# Engineering Documentation

## Repository Analysis

For repository analysis, use the `repository_analyzer.py` script located in the `tools/repository/` directory. This script replaces all temporary generator scripts and provides a comprehensive analysis of the repository.

### Usage

To analyze the repository, run the following command:

```bash
python3 tools/repository/repository_analyzer.py --all
```

This command will generate a detailed report of all files, directories, functions, classes, components, hooks, routes, services, middleware, models, utilities, payload builders, request builders, response builders, knowledge base components, CRM components, PDF components, receipt components, security components, and AI components.

### Supported Options

- `--files`: List all files in the repository.
- `--directories`: List all directories in the repository.
- `--functions`: List all functions in the repository.
- `--classes`: List all classes in the repository.
- `--components`: List all React components in the repository.
- `--hooks`: List all React hooks in the repository.
- `--routes`: List all routes in the repository.
- `--services`: List all services in the repository.
- `--middleware`: List all middleware in the repository.
- `--models`: List all models in the repository.
- `--utilities`: List all utilities in the repository.
- `--payload-builders`: List all payload builders in the repository.
- `--request-builders`: List all request builders in the repository.
- `--response-builders`: List all response builders in the repository.
- `--knowledge-base`: List all knowledge base components in the repository.
- `--crm`: List all CRM components in the repository.
- `--pdf`: List all PDF components in the repository.
- `--receipts`: List all receipt components in the repository.
- `--security`: List all security components in the repository.
- `--ai`: List all AI components in the repository.
- `--all`: Generate a comprehensive report of all components.

### Deprecated Scripts

The following scripts have been deprecated and should no longer be used:

- `generate_component_index.py`
- `generate_hook_index.py`
- `generate_route_index.py`
- `generate_service_index.py`

Use `repository_analyzer.py` instead.