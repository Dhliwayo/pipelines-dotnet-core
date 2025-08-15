# SQL Scripts for Deployment

This folder contains SQL Server scripts that will be executed by the Azure pipeline during deployment.

## Folder Structure

```
sql-scripts/
├── 001-schema/          # Database schema changes
├── 002-data/            # Data insertion/updates
├── 003-indexes/         # Index creation/optimization
├── 004-stored-procedures/ # Stored procedure updates
└── 005-views/           # View updates
```

## Script Naming Convention

Scripts should be named with a numeric prefix to ensure proper execution order:

- `001-` for schema changes
- `002-` for data operations
- `003-` for indexes
- `004-` for stored procedures
- `005-` for views

## Execution Order

Scripts are executed in alphabetical order within each subfolder. Ensure proper dependencies by using the numeric prefix.

## Example Scripts

See the sample scripts in each subfolder for reference.

## Important Notes

- All scripts should be idempotent (safe to run multiple times)
- Use proper error handling
- Include rollback logic where appropriate
- Test scripts in a development environment before deployment
