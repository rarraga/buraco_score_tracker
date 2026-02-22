# 🃏 Buraco - Contador de Puntajes

Aplicación de escritorio para llevar el marcador del juego de cartas **Buraco**. Desarrollada en Python con `tkinter` (sin dependencias externas).

---

## Requisitos

- Python **3.10 o superior** (para usar el tipo `X | Y`)
- No se requiere ningún paquete adicional (`tkinter` viene incluido con Python)

## Instalación y uso

```bash
# Cloná el repositorio
git clone https://github.com/tu-usuario/buraco-score.git
cd buraco-score

# Ejecutá la aplicación
python main.py
```

---

## Estructura del proyecto

```
buraco-score/
├── main.py          # Punto de entrada
├── ui.py            # Interfaz principal (ventana, menú, historial)
├── round_dialog.py  # Diálogo para ingresar puntajes de una mano
├── calculator.py    # Calculadora de fichas
├── game.py          # Lógica del juego y modelos de datos
└── README.md
```

---

## Reglas implementadas

### Valores de fichas

| Ficha      | Puntos |
|------------|--------|
| As (1)     | 15     |
| 2          | 20     |
| 3 al 7     | 5      |
| 8 al 13    | 10     |
| Comodín    | 50     |

### Jugadas especiales

| Jugada             | Puntos  |
|--------------------|---------|
| Cierre             | +100    |
| Canasta Impura     | +100    |
| Canasta Pura       | +200    |
| Muerto comprado    | +100    |
| Muerto NO comprado | −100    |

### Cálculo por mano

```
Puntaje = fichas_bajadas
        − fichas_en_mano_del_compañero
        + cierre (si aplica)
        + canastas_puras × 200
        + canastas_impuras × 100
        + 100 (si compró el muerto)
        − 100 (si no compró el muerto, cuando estuvo disponible)
```

### Fin de partida

- El objetivo es llegar a **3000 puntos**.
- Para poder **cerrar**, el equipo debe tener al menos una canasta (pura o impura) y haber comprado el muerto.
- Si ambos equipos superan 3000 en la misma mano, gana el de mayor puntaje.

---

## Funcionalidades

- ✅ Marcador en tiempo real con barra de progreso
- ✅ Ingreso guiado de puntajes por mano (fichas bajadas, fichas en mano, jugadas especiales)
- ✅ Calculadora de fichas integrada (contás ficha por ficha y calcula solo)
- ✅ Historial completo de manos con acumulados
- ✅ Deshacer última mano
- ✅ Guardar y cargar partidas (formato `.json`)
- ✅ Detección automática del ganador

---

## Capturas

> La interfaz es cross-platform y funciona en Windows, macOS y Linux.

---