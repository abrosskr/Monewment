# 🔌 Port Strategy & Registry

> **Standard Protocol**
> All services within the Monewment ecosystem must adhere to this port registry. Arbitrary changes are strictly prohibited.

## 1. Core Services
| Service | Port | Protocol | Description |
| :--- | :--- | :--- | :--- |
| **Frontend (GUI)** | `3000` | HTTP | Next.js Client Interface |
| **Backend (HUB)** | `8000` | HTTP | FastAPI Main Server |
| **PostgreSQL** | `5433` | TCP | Main Database (Local mapping) |
| **Redis** | `6379` | TCP | Message Broker & Cache |

## 2. Infrastructure
| Service | Port | Protocol | Description |
| :--- | :--- | :--- | :--- |
| **PostgreSQL (Internal)** | `5432` | TCP | Docker Internal Port |

## 3. Rules
1. **Strict Adherence**: Applications must default to these ports.
2. **No Conflicts**: Before starting, ensure these ports are free.
3. **Internal vs External**: 
    - `5433` is for accessing DB from host machine. 
    - `5432` is for service-to-service communication within Docker network.
