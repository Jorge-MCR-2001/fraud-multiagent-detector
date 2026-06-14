# Políticas internas de fraude

Documento base para recuperación aumentada por generación RAG.

Este documento contiene las políticas internas oficiales utilizadas por el sistema multi-agente de detección de fraude ambiguo en transacciones financieras.

Las políticas aquí descritas deben ser utilizadas como fuente interna trazable para sustentar decisiones, explicaciones y auditoría.

---

## FP-01 — Challenge por monto y horario inusual

**policy_id:** FP-01  
**chunk_id:** policy-fp01-001  
**version:** 2025.1  
**acción sugerida:** CHALLENGE  

### Regla oficial

Monto > 3x promedio habitual y horario fuera de rango → CHALLENGE.

### Interpretación operativa

Cuando una transacción supera tres veces el promedio habitual del cliente y además ocurre fuera del horario usual de operación, el sistema debe solicitar una validación adicional.

Esta política no implica bloqueo inmediato. La acción recomendada es aplicar un challenge o mecanismo de validación adicional.

### Señales asociadas

- `signal_a`: Monto fuera de rango.
- `signal_b`: Horario no habitual.

### Condición de aplicación

La política FP-01 aplica cuando se detectan simultáneamente `signal_a + signal_b`.

### Uso en auditoría

Esta política debe citarse cuando la decisión final esté relacionada con monto inusual y horario fuera del patrón habitual del cliente.

---

## FP-02 — Escalamiento por país inusual y dispositivo desconocido

**policy_id:** FP-02  
**chunk_id:** policy-fp02-001  
**version:** 2025.1  
**acción sugerida:** ESCALATE_TO_HUMAN  

### Regla oficial

Transacción internacional y dispositivo nuevo → ESCALATE_TO_HUMAN.

### Interpretación operativa

Cuando una transacción ocurre desde un país no habitual para el cliente y además utiliza un dispositivo no reconocido, el sistema debe escalar el caso a revisión humana obligatoria.

Esta política representa un escenario de mayor ambigüedad y riesgo, porque combina cambio geográfico con cambio de dispositivo.

### Señales asociadas

- `signal_c`: País inusual.
- `signal_d`: Dispositivo desconocido.

### Condición de aplicación

La política FP-02 aplica cuando se detectan simultáneamente `signal_c + signal_d`.

### Uso en auditoría

Esta política debe citarse cuando la decisión final esté relacionada con país inusual, dispositivo desconocido o revisión humana obligatoria.

---

## Nota de gobernanza

Este documento conserva únicamente las dos políticas oficiales del desafío técnico:

- FP-01
- FP-02