
Plan: Integrate Google NotebookLM MCP into Nanobot
Context
Nanobot is an ultra-lightweight AI assistant framework that already has robust MCP support (stdio/SSE/streamableHttp). The user wants nanobot to work with Google NotebookLM — a Google product for organizing sources, querying them, and generating audio overviews/podcasts.

There is no official Google NotebookLM API. All community implementations use reverse-engineered internal APIs with cookie-based auth. The best option is notebooklm-mcp-cli (3k+ stars, 35 MCP tools, Python/PyPI, actively maintained).

Recommended Approach: Config-Only Integration
Since nanobot already fully supports MCP servers, no code changes are needed. The integration is purely configuration + a dedicated nanobot skill for discoverability and UX.

Step 1: Install notebooklm-mcp-cli
uv tool install notebooklm-mcp-cli
# or: pip install notebooklm-mcp-cli
Step 2: Authenticate with Google
nlm login
# Opens Chromium browser → log in to Google → cookies extracted automatically
Step 3: Add MCP Server to Nanobot Config
Add to ~/.nanobot/config.json:

{
  "tools": {
    "mcpServers": {
      "notebooklm": {
        "command": "notebooklm-mcp",
        "toolTimeout": 120,
        "enabledTools": ["*"]
      }
    }
  }
}
Key settings:

toolTimeout: 120 — NotebookLM operations (especially audio generation) can be slow
Transport: stdio (auto-detected since command is set)
Step 4: Create a Nanobot Skill for NotebookLM
Create nanobot/skills/notebooklm/ with a skill prompt that teaches the agent how to effectively use NotebookLM tools. This provides:

Discoverability: users can see NotebookLM as a capability
Better UX: the skill prompt guides the agent on tool usage patterns
Workflow templates: common patterns like "research → create notebook → add sources → generate podcast"
Files to create:
nanobot/skills/notebooklm/skill.json

{
  "name": "notebooklm",
  "description": "Google NotebookLM integration — create notebooks, add sources, query knowledge, generate audio overviews",
  "version": "0.1.0"
}
nanobot/skills/notebooklm/prompt.md

Instructions for the agent on available NotebookLM MCP tools
Tool categories: Notebooks, Sources, Querying, Studio (audio/video), Research, Notes, Sharing
Common workflow patterns
Error handling guidance (auth expiry, timeouts)
Step 5: Document Setup in README
Add a section to the README or a dedicated doc explaining:

Prerequisites (install notebooklm-mcp-cli, authenticate)
Config snippet
Example usage commands
Caveats (unofficial API, cookie auth expiry, rate limits)
Critical Files
File	Action
~/.nanobot/config.json	Add notebooklm MCP server config
nanobot/skills/notebooklm/skill.json	Create — skill metadata
nanobot/skills/notebooklm/prompt.md	Create — agent instructions
nanobot/agent/tools/mcp.py	No changes needed (existing MCP support)
nanobot/config/schema.py	No changes needed (existing MCPServerConfig)
Available NotebookLM MCP Tools (35 total)
Category	Tools
Notebooks	notebook_list, notebook_create, notebook_get, notebook_describe, notebook_rename, notebook_delete
Sources	source_add, source_list_drive, source_sync_drive, source_delete, source_describe, source_get_content
Querying	notebook_query, chat_configure
Studio	studio_create, studio_status, studio_delete, studio_revise
Downloads	download_artifact
Research	research_start, research_status, research_import
Notes	note
Sharing	notebook_share_status, notebook_share_public, notebook_share_invite
Batch	batch, cross_notebook_query
Pipelines	pipeline
Tags	tag
Auth	refresh_auth, save_auth_tokens
Caveats & Risks
Unofficial API — uses reverse-engineered Google internal endpoints; can break anytime
Cookie-based auth — sessions expire, requiring periodic nlm login
No Google support — community-maintained only
Rate limits — heavy usage may be throttled
Best for personal/experimental use, not production
Verification
Install: uv tool install notebooklm-mcp-cli && nlm login
Start nanobot: nanobot agent (or nanobot gateway)
Check logs for: MCP server 'notebooklm': connected, N tools registered
Test: ask nanobot "list my notebooks" → should call mcp_notebooklm_notebook_list
Test: ask nanobot "create a notebook called 'Test'" → should call mcp_notebooklm_notebook_create
Test: ask nanobot "add this URL as a source to Test: https://example.com" → should call mcp_notebooklm_source_add