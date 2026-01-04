# 📊 Data & DB Schema (Table Blueprint)
Source: D:\projects\Monewment\src\models.py


## 🧱 Table: `Organization`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `name` : **String**
  - `plan_type` : **String**

## 🧱 Table: `User`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `email` : **String**
  - `hashed_password` : **String**
  - `role` : **Enum**
  - `org_id` : **Integer**

## 🧱 Table: `Project`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `name` : **String**
  - `org_id` : **Integer**
  - `installed_features` : **JSON**

## 🧱 Table: `ProjectMember`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `project_id` : **Integer**
  - `user_id` : **Integer**
  - `role` : **String**
  - `allowed_features` : **JSON**
  - `joined_at` : **DateTime**

## 🧱 Table: `PolicyPreset`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `name` : **String**
  - `rules` : **JSON**

## 🧱 Table: `Room`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `name` : **String**
  - `status` : **Enum**
  - `k8s_namespace` : **String**
  - `org_id` : **Integer**
  - `policy_id` : **Integer**

## 🧱 Table: `AuditLog`
- Columns:
  - `__tablename__` : **(Defined Value)**
  - `id` : **Integer**
  - `timestamp` : **DateTime**
  - `action_type` : **String**
  - `details` : **JSON**
  - `room_id` : **Integer**
  - `user_id` : **Integer**