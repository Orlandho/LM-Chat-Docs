# Changelog

All notable changes to this documentation repository will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-14

### Added
- Initial release of comprehensive LM-Chat™ Technical Architecture and Design Specification suite.
- `01_HIGH_LEVEL_ARCHITECTURE.md`: High-Level Architecture Document (HLD) detailing 4-tier microkernel topology, 60 FPS async execution loop, and spatial C4 diagrams.
- `02_LOW_LEVEL_DESIGN.md`: Low-Level Design (LLD) specifying `core/interfaces.py`, Pydantic/dataclass schemas, ReAct self-healing state machine, and diagnostic taxonomy.
- `LM_CHAT_PRD.md`: Product Requirements Document (PRD) with user personas, MoSCoW functional requirements, and Gherkin Given-When-Then acceptance criteria.
- `LM_CHAT_QA_TEST_PLAN.md`: Comprehensive QA Test Plan, test matrix (P0-P3), engine-independent mock strategy, and Quality Gates QG-01 to QG-08.
- `LM_CHAT_OPERATIONS_RUNBOOK.md`: SRE Operations Runbook covering environment configurations, release packaging, diagnostic health checks, and incident recovery procedures.
- `LM_CHAT_UI_UX_SPEC.md`: UI/UX Design Handoff Spec for `omni.ui`, including NVIDIA Obsidian/Green design tokens, typography, component states, and accessibility guidelines.
- `SECURITY.md`: Production-grade AI & Spatial Computing Security Policy, including AST code sandboxing, MCP capability boundaries, secret vault management, and spatial injection defense.
- `sync_version.py`: Automated cross-repository SemVer synchronization utility for pairing with `omni.lm_chat`.
