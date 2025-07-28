# Important System Notes

## Mem0 Initialization Delay

**Issue**: The MCP server takes approximately **60 seconds** to fully initialize and start accepting HTTP requests.

**Root Cause**: The mem0 library initialization with Gemini LLM and HuggingFace embeddings requires significant time to:
- Download and load the sentence-transformers model
- Initialize the vector database connection
- Configure the Gemini API client
- Set up the memory storage system

**Impact**: 
- Server appears "broken" during the first 60 seconds after startup
- Health checks will fail until initialization completes
- Tests must wait at least 60 seconds after `docker-compose up` before running

**Solution**: 
- Always wait 60+ seconds after starting the server before testing
- Consider this normal behavior, not a bug
- Future optimization could implement lazy loading or caching

**Testing Commands**:
```bash
# Correct way to test after startup
docker-compose up -d
sleep 60  # CRITICAL: Wait for initialization
docker-compose exec gemini_client python test_memory.py
```

**Date**: 2025-01-28
**Status**: Known behavior - not a bug