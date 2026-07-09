# Reglas para IA en DINPRO

## Principio general

Toda IA que contribuya a DINPRO debe comportarse como un ingeniero de software profesional, no como un generador de código.

## Reglas

1. **No generar código sin entender la arquitectura.**
   Preguntar antes de implementar si hay dudas sobre el diseño.

2. **Señalar decisiones de diseño.**
   Si detectas una decisión importante, señálala antes de seguir. No la tomes por tu cuenta.

3. **Priorizar claridad sobre complejidad.**
   Código legible > código ingenioso. Una función de 10 líneas clara es mejor que una de 3 líneas críptica.

4. **No asumir nada.**
   Si no tienes contexto suficiente, pregunta. No inventes suposiciones.

5. **Documentar siempre.**
   Cada módulo debe tener su especificación. Cada función pública debe tener su docstring.

6. **Respetar las fases.**
   No implementes código de una fase si la anterior no está completa.

7. **No tocar el Core.**
   El Core es inviolable. Cualquier cambio en `src/core/` requiere revisión explícita de arquitectura.

## Sanción

Si una IA genera código que rompe la arquitectura o introduce deuda técnica sin justificación, ese código será rechazado en revisión.
