# COGNITION

![Cognition AI](./designs/cognition-ai.jpg)

A modular, production-ready framework for building and deploying CrewAI agents with standardized patterns, dynamic tooling, and enterprise-grade features.

## Project Overview

Cognition is designed to solve common challenges in agent development by providing a structured, maintainable approach to building AI agents. It prevents the "agent graveyard" problem where one-off agents become unmaintainable and helps organizations standardize their agent development practices.

### Core Modules

#### 1. Cognition Core
The foundation layer that extends CrewAI with enterprise features:
- Configuration management with hot-reload capability
- Flexible memory systems (Redis, Firestore)
- Dynamic tool loading and management
- Standardized patterns for agent development
- Environment-aware deployment configurations

#### 2. Cognition API
REST and OpenAI-compatible interface layer:
- Standard REST endpoints for agent interaction
- OpenAI-compatible endpoints for easy integration
- Async task processing
- Built-in monitoring and security
- Production-ready deployment options

### Key Benefits

1. **Standardization**
   - Consistent patterns for agent development
   - Unified configuration management
   - Structured tool integration

2. **Maintainability**
   - Hot-reload configurations
   - Clear separation of concerns
   - Modular architecture

3. **Scalability**
   - Cloud-native design
   - Independent component scaling
   - Production-ready infrastructure

4. **Reusability**
   - Shared tool ecosystem
   - Common memory patterns
   - Standardized deployment practices

## Entry Layer

The architecture begins with an entry point that routes all requests through Portkey, which serves as our LLM management layer. This design choice provides several advantages:

The Portkey integration allows for sophisticated LLM routing and management, ensuring that requests are directed to the most appropriate model based on complexity and requirements. This layer acts as our first line of defense and optimization point for all AI interactions.

## Core Agent Container (Cloud Run)

The main agent runs in a Cloud Run container, which provides excellent scalability and managed infrastructure. Within this container, we have several key components:

### Configuration System
The configuration system consists of three main parts:
1. YAML Loader - Reads configuration files
2. Hot Reload - Monitors for configuration changes
3. Environment Manager - Handles environment variables and settings

This system allows for dynamic updates to the agent's behavior without requiring redeployment, which is crucial for maintaining flexibility in production.

### Core Crew
The heart of our agent contains three essential components:
1. Planner Agent - Handles high-level task planning
2. Task Router - Directs tasks to appropriate handlers
3. Executor Agent - Manages task execution

This structure leverages CrewAI's native capabilities while adding our own orchestration layer for better control and monitoring.

### Memory System
The memory system is designed with flexibility in mind:
1. Local Cache - Fast, in-memory storage
2. Short Term (Redis) - Distributed cache for scalability
3. Long Term (Firestore) - Persistent storage for important data

The system can switch between local and cloud storage based on deployment needs, providing both development simplicity and production scalability.

### Tool System
The tool system is designed for extensibility:
1. Tool Registry - Manages available tools
2. API Tool Wrapper - Standardizes tool interfaces
3. Response Validator - Ensures tool output quality

All tools are implemented as external APIs (Cloud Functions), allowing for independent scaling and maintenance.

## External Integration

### External APIs (Cloud Functions)
Tools are implemented as Cloud Functions, including:
- GSuite integration
- Trading functionality
- Finance operations

This approach allows each tool to:
- Scale independently
- Be maintained separately
- Be versioned individually
- Have its own resource allocation

### Persistence Layer
The persistence layer includes:
1. Redis - For distributed caching
2. Firestore - For long-term storage
3. Secret Manager - For secure credential storage

## Key Design Decisions

### Simplicity
1. Minimal custom code
2. Heavy reliance on CrewAI's native features
3. Clear separation of concerns

### Scalability
1. Cloud-native design
2. Independently scalable components
3. Flexible memory configuration

### Maintainability
1. Hot reload for configurations
2. External tools as APIs
3. Clear component boundaries

## Implementation Notes

### CrewAI Integration
The design leverages CrewAI's built-in features:
1. Memory management
2. Task planning
3. Tool integration
4. Error handling

### Tool Management
Tools are managed through:
1. External API endpoints
2. Standard interface definitions
3. Central registry
4. Response validation

### Configuration Management
Configurations are handled through:
1. YAML files for readability
2. Hot reload for updates
3. Environment variables for secrets

## Future Considerations

### Planned Improvements
1. Webhook endpoints for tool status updates
2. Enhanced monitoring capabilities
3. Expanded tool ecosystem

### Scaling Strategy
The architecture can scale in several ways:
1. Horizontal scaling of Cloud Run instances
2. Independent scaling of tool functions
3. Distributed memory system when needed

## Development Workflow

The architecture supports a clean development workflow:
1. Local development with local storage
2. Testing with cloud resources
3. Production deployment with full cloud integration

## Docker Image Creation

To build and run the Docker image for the Cognition API, follow these steps:

1. **Build the Docker Image**:
   ```bash
   docker build -t cognition .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8000:8000 cognition
   ```

This will start the Cognition API on port 8000.

## Environment Variables

The following environment variables can be configured for the Cognition API. They are optional, except for `PORTKEY_API_KEY` and `PORTKEY_VIRTUAL_KEY`, which are required:

- `ANTHROPIC_API_KEY`: Optional API key for Anthropic services.
- `HUGGINGFACE_API_TOKEN`: Optional token for Hugging Face services.
- `PORTKEY_API_KEY`: **Required** API key for Portkey integration.
- `PORTKEY_VIRTUAL_KEY`: Optional virtual key for Portkey.
- `LONG_TERM_DB_PASSWORD`: Optional password for long-term database access.
- `APP_LOG_LEVEL`: Optional log level for the application (default: DEBUG).
- `CHROMA_PASSWORD`: Optional password for Chroma services.

These variables can be set in the Docker container using the `-e` flag or in a `.env` file if needed.

## API Enhancements

The Cognition API now supports asynchronous task processing, allowing for non-blocking operations and improved scalability. Key features include:

- **Asynchronous Task Execution**: Tasks are processed in the background, enabling immediate API responses.
- **Task Status Tracking**: Check the status of tasks using the `/status/{task_id}` endpoint.
- **Integration with AWS SQS**: Optionally send task results to an external queue for persistence and further processing.

## Docker Hub

The Docker image for the Cognition API is available on Docker Hub. You can pull the latest image using:
   ```bash
   docker pull nestorcolt/cognition:latest
   ```