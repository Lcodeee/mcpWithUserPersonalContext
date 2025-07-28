#!/bin/bash

echo "🚀 Starting MCP-Mem0 Full Stack..."

# Build and run all containers
docker-compose up -d

echo "✅ All containers are ready!"
echo ""
echo "🔗 To run the advanced Gemini client:"
echo "   docker-compose exec gemini_client python3 advanced_gemini_client.py"
echo ""
echo "🔗 To run the simple client:"
echo "   docker-compose exec gemini_client python3 gemini_client.py"
echo ""
echo "🔗 To check MCP server logs:"
echo "   docker-compose logs mcp_server"
echo ""
echo "🔗 To enter the client container shell:"
echo "   docker-compose exec gemini_client bash"
echo ""
echo "🔗 To check all services status:"
echo "   docker-compose ps"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
