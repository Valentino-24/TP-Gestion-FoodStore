# MCP Servers Configuration

This folder contains MCP server configurations for Food Store project.

## Available MCPs

| MCP | Purpose | Required Env | Status |
|-----|---------|-----------|--------|
| **postgres** | Query PostgreSQL DB directly | DATABASE_URL | Disabled |
| **github** | GitHub API (issues, PRs, code) | GITHUB_TOKEN | Disabled |
| **context7-docs** | Library documentation lookup | - | Disabled |
| **filesystem** | File operations outside project | - | Disabled |
| **memory** | Persistent memory across sessions | - | Disabled |

## How to Enable

1. Edit `.mcp/config.json`
2. Set `"enabled": true` for the MCP you want
3. Add required environment variables in `.env`
4. Restart OpenCode

## Using Enabled MCPs

When enabled, reference them by name:
- PostgreSQL: "use the postgres tool to query..."
- GitHub: "use the github tool to search issues..."
- Context7: "use context7 to look up React documentation..."
- Filesystem: "use filesystem to read /path/to/file..."
- Memory: "use memory to save this insight..."

## Food Store Environment Variables

Add to `.env`:

```bash
# Database (required for postgres MCP)
DATABASE_URL=postgresql://user:password@localhost:5432/foodstore

# GitHub (optional, for github MCP)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

## Security Notes

- MCPs add tokens to context - enable only what you need
- Never commit tokens to git
- Database MCP is read-only by default
- Filesystem MCP scoped to current directory