# 🧠 Plan Técnico: Reconocimiento y Gestión de Modelos de Razonamiento (Thinking Models)
# LM-Chat™ — Feature Specification & Implementation Plan

---

## 1. Identificación y Estado de la Tarea

| Metadato | Detalle |
| :--- | :--- |
| **Origen / Calendario:** | Google Tasks — *"Implementar código para que la extensión sea capaz de reconocer si la IA tiene capacidad razonadora o no"* |
| **Proyecto Histórico:** | LACFNO / LLM-Chat / LM-Chat |
| **ID del Plan:** | `PLAN-REASONING-01` |
| **Estado:** | 🟡 Parcialmente implementado en Backend (InferenceRouter / AgentManager) — Pendiente UI y Clasificación Unificada |
| **Prioridad:** | Alta (P1) |

---

## 2. Resumen Ejecutivo y Necesidad Técnica

Los modelos de frontera más recientes han introducido capacidades de **razonamiento explícito y tiempo de pensamiento extendido** (*Test-Time Compute / Extended Thinking*):
- **DeepSeek R1 / R1-Zero:** Emiten bloques de pensamiento delimitados por etiquetas `<think>...</think>`.
- **OpenAI o1, o3, o3-mini:** Operan con tokens ocultos de razonamiento (`reasoning_tokens`), sustituyen el parámetro `max_tokens` por `max_completion_tokens` y rechazan el parámetro `temperature`.
- **Anthropic Claude 3.7 Sonnet con Extended Thinking:** Emite bloques estructurados `thinking_delta`.
- **Google Gemini 2.0 / 2.5 / 3.8 Flash Thinking:** Emite bloques de razonamiento previos a la respuesta final.
- **Modelos Locales Cuantizados (QwQ-32B, DeepSeek-R1-Distill-Qwen):** Transmiten pensamientos en crudo dentro del flujo de streaming en LM Studio y Ollama.

### El Problema Actual
Si la extensión no distingue entre la fase de "pensamiento" y la "respuesta final":
1. El usuario ve cientos de líneas de razonamiento desordenado que dificultan leer el código o la respuesta.
2. Si el modelo genera código tentativo dentro de `<think>`, el extractor de expresiones regulares de LM-Chat podría intentar ejecutar código preliminar e incompleto en el Stage de Omniverse.
3. Las peticiones a modelos como `o3-mini` fallan si la extensión envía `temperature=0.7`.

---

## 3. Arquitectura Propuesta

```mermaid
flowchart TD
    MODEL_SELECT["Selección de Modelo en UI / Detección Automática"] --> CLASSIFY{"ReasoningDetector.is_reasoning_model(model_name)"}
    
    CLASSIFY -->|Sí| SET_PARAM["Ajuste de Parámetros:<br/>- Omitir temperature<br/>- Usar max_completion_tokens<br/>- Activar Parser de Pensamiento"]
    CLASSIFY -->|No| STD_PARAM["Modo Estándar Conversacional"]
    
    STREAM["Flujo de Streaming SSE (InferenceRouter)"] --> PARSE_CHUNKS{"¿Chunk pertenece a Pensamiento?"}
    
    PARSE_CHUNKS -->|Token de Razonamiento<br/>(<think> o reasoning_content)| ACCORDION["omni.ui Collapsible Frame<br/>('🧠 Proceso de Pensamiento...')"]
    PARSE_CHUNKS -->|Token de Respuesta Final| MSG_CANVAS["Burbuja Principal de Mensaje en Chat Canvas"]
    
    ACCORDION --> AUTO_COLLAPSE["Colapsar Automáticamente al Terminar Razonamiento"]
```

---

## 4. Cambios Propuestos en el Código

### 4.1. `logic/inference_router.py` — Clasificador Centralizado de Modelos Razonadores
```python
REASONING_MODEL_PATTERNS = [
    r"^o1(-mini|-preview)?",
    r"^o3(-mini)?",
    r"deepseek-r1",
    r"qwq",
    r".*thinking.*",
    r".*-r1.*"
]

def is_reasoning_model(model_name: str) -> bool:
    """Evalúa si un modelo cuenta con capacidades de razonamiento extendido."""
    if not model_name:
        return False
    clean_name = model_name.lower().strip()
    return any(re.search(pat, clean_name) for pat in REASONING_MODEL_PATTERNS)
```

### 4.2. `logic/agent_manager.py` — Separación de Buffers de Razonamiento y Salida
- Añadir eventos y callbacks de streaming diferenciados:
  - `on_reasoning_chunk(chunk: str)`: Envía texto al widget de pensamiento.
  - `on_content_chunk(chunk: str)`: Envía texto a la respuesta principal.
- Garantizar que el extractor de código `_PYTHON_CODE_PATTERN` ignore por completo el contenido del buffer de razonamiento.

### 4.3. `ui/chat_window.py` — Widget Visual de Pensamiento en `omni.ui`
- Crear un `ui.CollapsibleFrame` con estilo oscuro y borde verde sutil:
  - Título dinámico: `"🧠 Pensando... (X segundos)"` durante la generación.
  - Al completar la respuesta: `"🧠 Pensamiento analítico completado [Desplegar]"` colapsado por defecto.
  - Visor interno de texto con fuente monospace atenuada (`#A0AEC0`).

---

## 5. Plan de Verificación y Pruebas

| ID de Prueba | Escenario | Resultado Esperado |
| :--- | :--- | :--- |
| `TC-RSN-001` | Detección de `DeepSeek-R1-Distill-Qwen-14B` en LM Studio | `is_reasoning_model()` retorna `True`. |
| `TC-RSN-002` | Envío de payload a OpenAI `o3-mini` | No contiene campo `temperature`, contiene `max_completion_tokens`. |
| `TC-RSN-003` | Flujo con etiquetas `<think>...</think>` | El contenido interno se muestra en el acordeón colapsable y no en la burbuja principal. |
| `TC-RSN-004` | Código Python dentro de `<think>` | El código preliminar dentro de `<think>` es ignorado; solo se ejecuta el bloque fuera de las etiquetas. |
