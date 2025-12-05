# DISTRIBUTED STORAGE & CONSENSUS
 
**Language:** Python  
**README Language:** English

---

## ⭐ Project Summary
This project is an implementation and evaluation of distributed storage strategies exploring **consistency**, **availability**, and **partition tolerance** (CAP theorem) trade-offs.  
It provides two primary modes: a **centralized** store with a master node and multiple slaves, and a **decentralized** setup where nodes coordinate without a single point of control. The code is intended for a Distributed Systems practical assignment (SDP2) and includes simulation/evaluation scripts to compare behaviors under different conditions.

The repository contains networked node implementations, configuration files, protobuf definitions for RPCs, and helper scripts to persist and inspect node state.

---

## 🧩 Technologies & Skills Demonstrated
- **Python 3** — core implementation language  
- **gRPC / Protocol Buffers** (proto/) — RPC interfaces and message schemas (if used)  
- **YAML configuration** — simple node/service configuration (`*_config.yaml`)  
- **Persistence with pickle** — sample node state snapshots (`.pkl`) for quick restarts and evaluation  
- **Distributed system concepts** — master/slave coordination, decentralized node interactions, replication strategies, failure handling, and CAP tradeoffs  
- **Evaluation tooling** — `eval/` scripts and tools to reproduce experiments

Skills gained:
- Designing message schemas and RPCs for distributed components  
- Implementing master/slave and decentralized architectures  
- Running reproducible experiments and analyzing distributed behavior

---

## 📁 Project Structure

```
SD-Distributed-Storage-Consensus/
├── centralized.py               → Centralized storage runner (master + slaves)
├── centralized_config.yaml      → Config for centralized setup (master + slaves)
├── decentralized.py             → Decentralized node runner / orchestrator
├── decentralized_config.yaml    → Config for decentralized setup
├── decentralized_nodes.py       → Helper utilities for decentralized nodes
├── master_node.py               → Master node implementation (centralized mode)
├── slave_node.py                → Slave node implementation (centralized mode)
├── store_bd.py                  → Storage backend / utilities
├── proto/                       → Protobuf definitions and generated code (if present)
├── state_node_*.pkl             → Example serialized node states
├── eval/                        → Evaluation scripts and experiment harness
└── README.md                    → Original project README (Catalan)
```

Notes:
- The `proto/` directory likely holds `.proto` files and generated stubs used for node communication.  
- Example `state_node_*.pkl` files provide saved states for quick testing or deterministic evaluation.

---

## 🔍 Project Details

### Modes of Operation
1. **Centralized mode**
   - A single `master_node` coordinates writes and replicates state to `slave_node` instances.
   - `centralized.py` boots the master and configured slaves using `centralized_config.yaml`.
   - Useful to study availability and consistency when a single coordinator is present.

2. **Decentralized mode**
   - Nodes interact peer-to-peer or using distributed protocols without a single coordinator.
   - `decentralized.py` and `decentralized_nodes.py` implement node logic and orchestration.
   - Useful to study partition tolerance and replication convergence.

### Configuration
- YAML config files (`centralized_config.yaml`, `decentralized_config.yaml`) define network endpoints (IP/port), node roles, and other runtime parameters. Edit them to match your environment before running.

### Persistence & State
- Example `.pkl` files show serialized Python objects representing node state. The codebase contains utilities to load/save state to enable deterministic experiments.

### Evaluation
- The `eval/` folder contains scripts to run scenarios, log metrics (latency, successful writes, data divergence), and produce outputs for analysis.

---

## ▶️ How to Build & Run

> Recommended: use a Python virtual environment.

1. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate    # Windows (PowerShell: venv\Scripts\Activate.ps1)
```

2. **Install dependencies**
Check `requirements.txt` or install typical dependencies:
```bash
pip install grpcio pyyaml
```
(If the repo includes generated gRPC code, `grpcio` is required. Add other packages as needed.)

3. **Configure network endpoints**
Edit `centralized_config.yaml` or `decentralized_config.yaml` to set IPs/ports for master and slave nodes appropriate to your environment (localhost for local testing).

4. **Run centralized setup**
```bash
python centralized.py centralized_config.yaml
```
This should start the master and spawn slaves according to the YAML file. Monitor logs on console.

5. **Run decentralized setup**
```bash
python decentralized.py decentralized_config.yaml
```
This will start the decentralized nodes and coordinate their peer communication.

6. **Run evaluation scripts**
Inspect `eval/` and run the scripts there to reproduce experiments:
```bash
python eval/run_experiment.py
```
(Replace with the actual script names present in the `eval/` directory.)

---

## 🛠️ Troubleshooting & Tips
- If you modify `.proto` files, regenerate Python stubs with `grpc_tools.protoc`:
```bash
python -m grpc_tools.protoc -I=proto --python_out=proto --grpc_python_out=proto proto/yourfile.proto
```
- Ensure ports used in configs are free and reachable (firewall, localhost limits).  
- Use the provided `.pkl` state files to bootstrap nodes in a known state for reproducible tests.

---

## ✔ Summary
This repository provides a compact experimental platform to explore distributed storage designs under CAP-related scenarios, offering both centralized and decentralized implementations, configuration-driven deployment, and evaluation tooling for lab-style experiments and demonstrations.

