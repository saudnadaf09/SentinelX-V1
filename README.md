# ◈ SentinelX V1
### SIEM & XDR-Lite | Security Operations Monitoring Platform

<p align="center">
  <strong>Centralized Security Visibility • Threat Detection • Incident Management • Security Investigation</strong>
</p>

<p align="center">
  <a href="https://sentinelx-2ej8.onrender.com/">Live Demo</a> •
  <a href="https://github.com/saudnadaf09/SentinelX-V1">GitHub Repository</a>
</p>

---

## 1. Project Overview

**SentinelX** is a Security Information and Event Management (SIEM) and XDR-lite platform developed to provide centralized visibility into security events and support essential Security Operations Center (SOC) workflows.

The platform brings together security event management, rule-based threat detection, alert monitoring, incident tracking, asset visibility, audit logs, reporting, and AI-assisted investigation interfaces in a unified security operations dashboard.

SentinelX is designed with a modular backend and frontend architecture, allowing its security monitoring and investigation capabilities to be extended as the project evolves.

The objective is to simplify security operations by bringing important monitoring and investigation workflows into one centralized workspace.

### Project Information

| Attribute | Details |
|---|---|
| Project Name | SentinelX |
| Version | V1 |
| Category | Cybersecurity / SIEM / XDR-Lite |
| Platform | Web-based Security Operations Dashboard |
| Backend | Python |
| Frontend | React + TypeScript |
| API | REST API |
| Detection Engine | Rule-based Detection |
| Deployment | Render |
| Development | Windows / Local Environment |
| Repository | GitHub |

---

## 2. Live Demo

<https://sentinelx-2ej8.onrender.com/>

**Explore the deployed SentinelX V1 application.**

The live application is hosted on Render. Availability and performance depend on the hosting plan and service status.

**Note:** The current free Render deployment uses an ephemeral filesystem. Data stored locally on the instance may not persist across restarts or redeployments. Do not use this deployment as a production SOC environment or upload sensitive organizational telemetry.

---

## 3. Core Objectives

SentinelX aims to provide a centralized environment for:

- Monitoring security-related events.
- Organizing and analyzing incoming event data.
- Identifying suspicious activity through detection rules.
- Managing security alerts.
- Tracking security incidents.
- Maintaining asset visibility.
- Supporting security investigations.
- Reviewing audit activity.
- Organizing security operations through a unified dashboard.

The project focuses on practical SOC workflows and provides a foundation for further development toward a more scalable security monitoring platform.

---

## 4. Key Features and Modules

### 4.1 Security Operations Dashboard

The Overview dashboard provides a centralized view of security operations.

Key areas include:

- Security event overview.
- Alert visibility.
- Incident overview.
- Asset information.
- Security activity monitoring.
- Centralized navigation to investigation modules.

The dashboard is designed to provide analysts with a single starting point for reviewing security activity.

### 4.2 Event Management

The Events module provides an interface for exploring security event information.

Related backend components include:

- Event API.
- Event ingestion API.
- Event serialization.
- Event normalization.
- Event processing services.

The ingestion and processing architecture provides the foundation for handling structured security event data.

### 4.3 Threat Detection Engine

SentinelX includes a rule-based detection architecture.

Detection rules are maintained in YAML files and organized by security category.

Detection rule categories include:

| Category | Examples |
|---|---|
| Authentication | New account, privileged group activity, brute-force patterns |
| Network | Port scanning, suspicious outbound activity |
| Process | Suspicious PowerShell, script interpreters, temporary-path execution |
| Persistence | Scheduled task and service-related activity |
| Correlation | Related event correlation |

Detection rules are stored in:

`detection-rules/`

The detection engine includes rule loading, rule evaluation, normalization, and correlation components.

Detection outcomes depend on the event data supplied to the application and the active processing configuration.

### 4.4 Alert Management

The Alerts module provides a centralized interface for reviewing security alerts.

It includes:

- Alert listing.
- Alert detail views.
- Alert investigation workflows.
- Alert-related backend services.
- Alert API endpoints.

The module supports the security alert review process within the SOC dashboard.

### 4.5 Incident Management

The Incidents module provides a dedicated workspace for security incident tracking.

It includes:

- Incident listing.
- Incident detail views.
- Incident-related API endpoints.
- Incident management services.
- Incident investigation interface.

This module provides a structured workflow for reviewing and managing security incidents.

### 4.6 Asset Management

The Assets module provides an interface for viewing and managing security-related asset information.

It includes:

- Asset dashboard.
- Asset API.
- Asset-related data models.
- Asset management interface.

Asset visibility is an important part of centralized security operations.

### 4.7 AI Investigator

The AI Investigator module provides an interface for AI-assisted security investigation.

Related components include:

- AI API endpoints.
- AI service layer.
- AI analysis domain logic.
- Investigation interface.

The actual availability of AI analysis depends on the configured provider, API credentials, and supported implementation.

AI-generated results should be reviewed against the underlying security evidence.

### 4.8 MITRE ATT&CK Integration Components

SentinelX includes MITRE-related backend components and a dedicated MITRE interface.

These components provide a foundation for organizing threat-related information and mapping detection activity to relevant techniques where supported by the implementation.

### 4.9 Threat Hunting

The project includes a dedicated Threat Hunting interface for security investigation workflows.

It provides a starting point for reviewing security activity and investigating potentially suspicious behavior.

### 4.10 Response Center

The Response Center provides a centralized interface for response-related security operations.

Related components include:

- Response API.
- Response service.
- Response action domain logic.
- Response management interface.

**Important:** The availability of a response interface does not automatically mean that a real endpoint has been isolated, a process terminated, or a firewall rule applied. Actual execution requires a supported integration and verification.

### 4.11 Audit Logs

The Audit Logs module provides an interface for reviewing security-related audit activity.

Related backend components include:

- Audit API.
- Audit service.
- Audit-related data models.

Audit visibility supports operational review and accountability.

### 4.12 Reports

SentinelX includes a reporting interface and report service.

These components provide the foundation for organizing and accessing security-related reports.

### 4.13 System and Configuration Management

The backend includes configuration, security, middleware, permissions, and system-related components.

These support the application's internal configuration and API operation.

---

## 5. System Architecture

SentinelX follows a modular frontend/backend architecture.

```text
                   SENTINELX V1
                         |
             +-----------+-----------+
             |                       |
          FRONTEND                 BACKEND
             |                       |
       React + TypeScript        Python API
             |                       |
       SOC Dashboard             API Layer
             |                       |
             |              +--------+--------+
             |              |        |        |
             |            Events  Detection   AI
             |              |        |        |
             |              +--------+--------+
             |                       |
             |                Processing Layer
             |                       |
             |                Storage Layer
             |                       |
             +---------- REST API ---+
                         |
                Security Operations
                         |
          Events / Alerts / Incidents
              Assets / Audit / Reports
```

### Backend Architecture

The backend is separated into functional modules:

| Directory | Responsibility |
|---|---|
| `api/` | API routing and request handling |
| `core/` | Configuration, security, middleware and permissions |
| `db/` | Database connectivity and base configuration |
| `domain/` | Detection, normalization, correlation and analysis logic |
| `infra/` | Storage and infrastructure adapters |
| `models/` | Database models |
| `schemas/` | API data schemas and validation |
| `services/` | Application business logic |
| `workers/` | Background processing components |
| `tests/` | Backend tests |

### Frontend Architecture

The frontend follows a component-based architecture using React and TypeScript.

Its main areas include:

- Application entry point.
- Authentication context.
- Shared UI components.
- Centralized API services.
- Dashboard pages.
- Security monitoring interfaces.
- Investigation and management interfaces.

---

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| React | Frontend framework |
| TypeScript | Frontend programming language |
| Vite | Frontend development and build tooling |
| REST API | Frontend/backend communication |
| SQLite | Local database storage implementation |
| SQLAlchemy | Database model and ORM layer |
| Alembic | Database migrations |
| YAML | Detection rule definitions |
| Pytest | Backend testing |
| Git | Version control |
| GitHub | Source code management |
| Render | Cloud deployment |

### Additional Infrastructure Components

The repository also contains infrastructure adapters for:

- Redis queue integration.
- OpenSearch storage integration.
- SQLite storage.

Their presence in the source code does not mean all services are enabled in the default deployment.

---

## 7. Project Directory Structure

```text
SentinelX-V1/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── ai.py
│   │   │       ├── alerts.py
│   │   │       ├── assets.py
│   │   │       ├── audit.py
│   │   │       ├── auth.py
│   │   │       ├── dashboard.py
│   │   │       ├── events.py
│   │   │       ├── incidents.py
│   │   │       ├── ingest.py
│   │   │       ├── mitre.py
│   │   │       ├── reports.py
│   │   │       ├── response.py
│   │   │       ├── rules.py
│   │   │       ├── system.py
│   │   │       └── users.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── domain/
│   │   ├── infra/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   ├── main.py
│   │   └── samples.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── alembic.ini
│
├── detection-rules/
│   ├── authentication/
│   ├── correlation/
│   ├── network/
│   ├── persistence/
│   └── process/
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── INGESTION.md
│
├── frontend/
│   ├── src/
│   │   ├── auth/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
│
├── infrastructure/
│   └── nginx/
│       └── nginx.conf
│
├── sample-data/
├── scripts/
│
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── run.bat
├── run.sh
├── start.bat
├── start.sh
├── .dockerignore
├── .env.example
├── .env.lite.example
├── .gitignore
├── README.md
├── SETUP.md
├── START-HERE.txt
└── TROUBLESHOOTING.md
```

---

## 8. Installation and Local Development

### Prerequisites

Install the following software:

| Software | Version / Requirement |
|---|---|
| Python | 3.13.7 used during development |
| Node.js | 24.19.0 used during development |
| npm | Compatible with installed Node.js |
| Git | Required for repository management |
| Windows | Supported development environment |

Other operating systems may require adapting the startup commands.

### Step 1: Clone the Repository

```bash
git clone https://github.com/saudnadaf09/SentinelX-V1.git
```

Move into the project directory:

```bash
cd SentinelX-V1
```

### Step 2: Configure Environment Variables

Create a local environment file using the supplied template:

```cmd
copy .env.example .env
```

Review the environment configuration and fill in the required values.

If the backend uses a separate environment file, follow `SETUP.md` and the backend configuration instructions.

Never commit real credentials or production secrets.

### Step 3: Start SentinelX on Windows

The repository includes Windows startup scripts.

From the project root:

```cmd
run.bat
```

Follow the instructions displayed by the startup script.

For the alternative startup workflow, inspect:

```cmd
start.bat
```

### Step 4: Manual Setup

If you prefer manual installation, use the setup documentation and the dependency files:

```text
backend/requirements.txt
backend/requirements-dev.txt
frontend/package.json
```

Refer to `SETUP.md` for the project's actual installation and startup requirements.

### Troubleshooting

If the application fails to start, check:

- Python installation and PATH.
- Node.js and npm installation.
- Backend dependency installation.
- Frontend dependency installation.
- Environment variables.
- Database initialization.
- Port conflicts.
- Backend and frontend startup logs.

Additional guidance is available in:

- `START-HERE.txt`
- `SETUP.md`
- `TROUBLESHOOTING.md`

---

## 9. Detection Rules

SentinelX uses YAML-based rule definitions organized by security category.

Example directory:

```text
detection-rules/
│
├── authentication/
│   ├── new-account.yml
│   ├── privileged-group.yml
│   ├── ssh-bruteforce.yml
│   ├── success-after-failures.yml
│   └── windows-bruteforce.yml
│
├── correlation/
│   └── correlation.yml
│
├── network/
│   ├── port-scan.yml
│   └── suspicious-outbound.yml
│
├── persistence/
│   └── scheduled-task-service.yml
│
└── process/
    ├── defense-evasion.yml
    ├── script-interpreter.yml
    ├── suspicious-powershell.yml
    └── temp-path-execution.yml
```

These rules provide a structured foundation for identifying security-related patterns in supported event data.

---

## 10. API Architecture

The backend provides versioned API modules under:

```text
/api/v1/
```

The repository includes the following API modules:

| API Module | Purpose |
|---|---|
| `auth` | Authentication |
| `users` | User-related operations |
| `dashboard` | Dashboard information |
| `events` | Security event operations |
| `ingest` | Event ingestion |
| `alerts` | Alert operations |
| `incidents` | Incident operations |
| `assets` | Asset operations |
| `rules` | Detection rule operations |
| `ai` | AI investigation |
| `mitre` | MITRE-related operations |
| `response` | Response operations |
| `audit` | Audit records |
| `reports` | Reporting |
| `system` | System-related operations |

For API behavior, request schemas, authentication requirements, and available endpoints, refer to the backend source code and API configuration.

---

## 11. Database and Data Storage

The repository includes:

- SQLAlchemy database components.
- Database models.
- SQLite storage implementation.
- Alembic migration configuration.
- Database session management.

SQLite is suitable for local development and evaluation.

**Deployment consideration:** The current Render Free deployment uses ephemeral storage. Local database files should not be treated as permanent production storage.

For a persistent production deployment, a managed PostgreSQL database and a tested database migration strategy should be implemented.

---

## 12. Render Deployment

SentinelX V1 is deployed using Render.

**Live URL:**

<https://sentinelx-2ej8.onrender.com/>

### Deployment Configuration

The repository contains a `render.yaml` Blueprint configuration.

Current configuration:

- Service type: Web Service.
- Runtime: Docker.
- Plan: Free.
- Health check path: `/api/v1/health`.
- Secret key: Generated by Render.
- Bootstrap administrator email: Configured through environment variables.
- Bootstrap administrator password: Entered privately in the Render dashboard.
- Demo data: Controlled through `LOAD_DEMO_DATA`.

### Environment Variables

Configure the following values in the Render dashboard:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Application secret |
| `BOOTSTRAP_ADMIN_EMAIL` | Bootstrap administrator email |
| `BOOTSTRAP_ADMIN_PASSWORD` | Bootstrap administrator password |
| `LOAD_DEMO_DATA` | Controls demo data loading |

Do not expose secret values in source code, screenshots, logs, or public documentation.

### Important Render Limitations

The current Free deployment has important limitations:

1. Free services can spin down after inactivity.
2. Free instances do not support persistent disks.
3. Files stored on the instance may be lost after restart or redeployment.
4. SQLite files on ephemeral storage are not suitable for permanent production records.
5. Background monitoring cannot be assumed to operate continuously when the service is sleeping.

For production use, configure persistent storage, database backups, secure telemetry ingestion, monitoring, and suitable always-on infrastructure.

---

## 13. Security Considerations

Security is an essential part of any SIEM platform.

When deploying or extending SentinelX, follow these practices:

- Keep API keys and passwords outside the repository.
- Use strong, unique administrator credentials.
- Generate a secure application secret.
- Restrict access to administrative interfaces.
- Use HTTPS for production deployments.
- Validate incoming API data.
- Apply appropriate authentication and authorization.
- Protect database credentials.
- Avoid exposing sensitive event data.
- Review logs before sharing them.
- Use authorized data sources and monitoring environments.
- Verify response actions before reporting them as successful.

Never use SentinelX to monitor systems or networks without proper authorization.

---

## 14. Testing

The backend includes a Pytest test suite.

Test files are located in:

```text
backend/tests/
```

The repository includes tests covering areas such as:

- API flows.
- Domain logic.
- Event normalization.
- Detection rules.
- Other domain functionality.

Install development dependencies according to the project setup instructions and execute tests from the appropriate backend environment.

Example:

```bash
pytest
```

Test results should be evaluated in the target environment before relying on the platform for operational security monitoring.

---

## 15. Current Scope and Limitations

SentinelX V1 is an evolving security monitoring project.

The following distinctions are important:

| Area | Current Scope / Consideration |
|---|---|
| SOC Dashboard | Included |
| Event Management | Included |
| Event Ingestion Components | Included |
| Rule-Based Detection | Included |
| Alert Management | Included |
| Incident Management | Included |
| Asset Management | Included |
| AI Investigator Interface | Included; provider configuration required |
| MITRE Components | Included |
| Response Center | Included; real execution depends on integration |
| Audit Logs | Included |
| Reporting | Included |
| Endpoint Fleet Monitoring | Requires suitable endpoint telemetry integration |
| Network Packet Capture | Requires a supported network sensor or capture integration |
| Persistent Cloud Storage | Requires persistent database infrastructure |
| Enterprise Multi-Tenancy | Not claimed as production-ready |
| Continuous Production Monitoring | Requires always-on infrastructure and operational validation |

The presence of a dashboard module or API does not by itself establish that a corresponding external integration is operational.

Likewise, sample data, simulated activity, and actual telemetry must be clearly distinguished.

---

## 16. Future Development Roadmap

The following are potential future development directions, not claims about completed V1 functionality.

- Persistent PostgreSQL-backed production storage.
- Secure Windows and Linux endpoint telemetry agents.
- Centralized multi-endpoint monitoring.
- Network sensor and firewall log integrations.
- Improved event normalization and correlation.
- Advanced detection engineering.
- Multi-organization architecture and tenant isolation.
- Role-based access control enhancements.
- Background processing and job management.
- Improved AI investigation and evidence references.
- Production-grade monitoring and observability.
- Secure response integrations.
- Data retention and backup management.
- Expanded automated testing and deployment workflows.

---

## 17. Contributing

Contributions, suggestions, and technical feedback are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a separate feature branch.
3. Make your changes.
4. Test the relevant functionality.
5. Submit a pull request with a clear description.

For significant architectural changes, discuss the proposal before implementation.

---

## 18. Responsible Use

SentinelX is intended for defensive cybersecurity, security monitoring, and authorized security operations.

Users are responsible for ensuring they have appropriate permission to collect, process, and analyze the security data handled by the platform.

Do not use the platform for unauthorized access, surveillance, or monitoring of systems outside your approved scope.

---

## 19. Project Links

| Resource | Link |
|---|---|
| Live Application | [SentinelX V1](https://sentinelx-2ej8.onrender.com/) |
| GitHub Repository | [SentinelX-V1](https://github.com/saudnadaf09/SentinelX-V1) |
| Architecture Documentation | [ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Ingestion Documentation | [INGESTION.md](docs/INGESTION.md) |
| Setup Guide | [SETUP.md](SETUP.md) |
| Troubleshooting | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |

---

## 20. License

Please refer to the repository's [LICENSE](LICENSE) file for the applicable license and usage terms.

---

<p align="center">

  **SENTINELX V1**

  *Centralized Visibility. Structured Detection. Better Security Operations.*

  Built as a cybersecurity engineering project.

</p>
