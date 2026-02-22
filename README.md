# 🃏 Buraco - Contador de Puntajes

Aplicación de escritorio para llevar el marcador del juego de cartas **Buraco**. Desarrollada en Python puro con `tkinter`, sin dependencias externas. Corre en cualquier PC que tenga Python instalado, o directamente como ejecutable `.exe` generado con PyInstaller.

---

## Requisitos

- Python **3.10 o superior**
- No se requiere ningún paquete adicional (`tkinter` viene incluido con Python)

## Instalación y uso

```bash
# Cloná el repositorio
git clone https://github.com/rarraga/buraco_score_tracker.git
cd buraco_score_tracker

# Ejecutá la aplicación
python main.py
```

La aplicación se abre en **pantalla completa** automáticamente. Si se reduce el tamaño de la ventana, el contenido se adapta dinámicamente y permite scroll con la rueda del mouse.

---

## Generar ejecutable (.exe)

Si querés distribuir la app sin necesidad de tener Python instalado:

**Windows** — doble click en `build.bat`

**Linux / macOS**:
```bash
chmod +x build.sh
./build.sh
```

El ejecutable queda en la carpeta `dist/`. Es completamente standalone y puede copiarse a cualquier máquina sin instalar nada.

> ⚠️ El ejecutable se genera para el sistema operativo donde se compila. Para generar para Windows, corré `build.bat` desde Windows.

---

## Estructura del proyecto

```
buraco-score/
├── main.py          # Punto de entrada
├── ui.py            # Interfaz principal (ventana, menú, historial)
├── round_dialog.py  # Diálogo para ingresar puntajes de una mano
├── calculator.py    # Calculadora de fichas con subtotales en tiempo real
├── game.py          # Lógica del juego y modelos de datos
├── build.bat        # Script de build para Windows
├── build.sh         # Script de build para Linux/macOS
├── .gitignore
├── .gitattributes
└── README.md
```

---

## Cómo usar la aplicación

### 1. Nueva partida
Hacé click en **🆕 Nueva Partida** (o `Ctrl+N`) e ingresá los nombres de los dos equipos.

### 2. Registrar una mano
Al terminar cada mano del juego, hacé click en **➕ Nueva Mano**. Se abre un formulario con dos pestañas (una por equipo) donde ingresás:

- **Fichas bajadas** → puntos a favor (podés tipear el total o usar 🧮 para contar ficha por ficha)
- **Fichas en mano del compañero** → las que quedaron sin bajar (se restan automáticamente)
- **Cierre**, **canastas puras**, **canastas impuras**
- **El Muerto** → si hubo muerto disponible y quién lo compró

El subtotal estimado se actualiza en tiempo real mientras completás los datos.

### 3. Confirmar
Hacé click en **✔ Confirmar mano** y el marcador se actualiza. La aplicación detecta automáticamente cuando un equipo llega a 3000 puntos.

### 4. Deshacer
Si cometiste un error en la última mano, usá **↩ Deshacer última mano** para revertirla — incluso si esa mano había terminado la partida.

### 5. Guardar y cargar
Desde el menú **Partida** podés guardar la partida en un archivo `.json` y retomarla más tarde.

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

| Jugada             | Puntos |
|--------------------|--------|
| Cierre             | +100   |
| Canasta Impura     | +100   |
| Canasta Pura       | +200   |
| Muerto comprado    | +100   |
| Muerto NO comprado | −100   |

### Cálculo por mano

```
Puntaje = fichas_bajadas
        − fichas_en_mano_del_compañero
        + cierre (si aplica)
        + canastas_puras × 200
        + canastas_impuras × 100
        ± 100 (según si se compró el muerto o no)
```

### Fin de partida

- El objetivo es llegar a **3000 puntos**.
- Para poder **cerrar**, el equipo debe tener al menos una canasta (pura o impura) y haber comprado el muerto.
- Si ambos equipos superan 3000 en la misma mano, gana el de mayor puntaje.

---

## Funcionalidades

- ✅ Marcador en tiempo real con barra de progreso verde
- ✅ Interfaz a pantalla completa con ajuste dinámico a cualquier resolución
- ✅ Ingreso guiado de puntajes por mano
- ✅ Calculadora de fichas integrada (ficha por ficha con subtotales)
- ✅ Preview del subtotal estimado antes de confirmar cada mano
- ✅ Historial completo con puntajes por mano y acumulados
- ✅ Deshacer última mano (incluso si era la mano ganadora)
- ✅ Guardar y cargar partidas en `.json`
- ✅ Detección automática del ganador