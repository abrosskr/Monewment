# 📅 Next Session Tasks

## 🚀 Goals for Next Session
Based on `masterplan.md`, the next major milestone is **Phase 6: DeepVault & DeepRender Core**.

### 1. DeepVault (Secure Storage)
- [ ] **Infrastructure**: Deploy MinIO or similar Object Storage (or start with local filesystem simulation).
- [ ] **API**: Implement `/api/v1/vault/upload` and `/download`.
- [ ] **Encryption**: Integrate `AntSecurity` for client-side encryption before storage.

### 2. DeepRender (Distributed Computing)
- [ ] **Job Queue**: Set up Redis Stream for rendering tasks.
- [ ] **Worker**: Create `render_worker.py` (Blender CLI wrapper).
- [ ] **Scheduling**: Connect `ClusterManager` to distribute jobs to KubeVirt VMs.

### 3. Cleanup & Optimization
- [ ] **Refactor**: Split `src/models.py` if it grows too large (currently handling Auth, Metering, Payment, Billing).
- [ ] **Testing**: Add unit tests for `BillingService` (currently verified via script).
