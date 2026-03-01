# 🃏 Buraco - Contador de Puntajes

Aplicación de escritorio para llevar el marcador del juego de cartas **Buraco**. Desarrollada en Python puro con `tkinter`, sin dependencias externas. Corre en cualquier PC que tenga Python instalado, o directamente como ejecutable `.exe` generado con PyInstaller.

---

## Requisitos

- Python **3.10 o superior**
- No se requiere ningún paquete adicional (`tkinter` viene incluido con Python)

## Instalación y uso

```bash
# Cloná el repositorio
git clone https://github.com/tu-usuario/buraco-score.git
cd buraco-score

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
> Cada vez que se actualice el código es necesario volver a correr el script de build para obtener el ejecutable actualizado.

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
Hacé click en **🆕 Nueva Partida** (o `Ctrl+N`). Se abre un diálogo donde elegís la cantidad de jugadores y los nombres:

- **2 jugadores** → partida individual entre dos personas
- **3 jugadores** → partida individual entre tres personas, cada uno con su propio marcador
- **4 jugadores** → dos equipos de dos personas, ingresás el nombre de cada equipo

> Si hay una partida en curso al iniciar una nueva, la app te preguntará si querés guardarla antes de continuar.

### 2. Registrar una mano
Al terminar cada mano, hacé click en **➕ Nueva Mano**. Se abre un formulario con una pestaña por equipo/jugador donde ingresás:

- **Fichas bajadas** → puntos a favor (podés tipear el total o usar 🧮 para contar ficha por ficha)
- **Fichas en mano del compañero** → las que quedaron sin bajar (se restan automáticamente)
- **Cierre**, **Compró el Muerto**, **canastas puras**, **canastas impuras**

El subtotal estimado se actualiza en tiempo real mientras completás los datos. Si no ingresaste ningún dato, el subtotal muestra `—` para evitar confusiones.

### 3. Confirmar
Hacé click en **✔ Confirmar mano** y el marcador se actualiza. La aplicación detecta automáticamente cuando un equipo/jugador llega a 3000 puntos.

> Si varios jugadores superan 3000 en la misma mano, gana el de mayor puntaje. El mensaje final muestra los puntajes de todos los que llegaron para que la decisión sea transparente.

### 4. Deshacer
Si cometiste un error en la última mano, usá **↩ Deshacer última mano** para revertirla — incluso si esa mano había terminado la partida.

### 5. Guardar y cargar
Desde el menú **Partida** podés guardar la partida en un archivo `.json` y retomarla más tarde con **Abrir partida**.

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
- Para poder **cerrar**, el equipo/jugador debe tener al menos una canasta (pura o impura) y haber comprado el muerto.
- Si varios jugadores superan 3000 en la misma mano, gana el de **mayor puntaje**.

---

## Funcionalidades

- ✅ Soporte para 2, 3 o 4 jugadores con marcador dinámico
- ✅ Marcador en tiempo real con barra de progreso verde
- ✅ Interfaz a pantalla completa con ajuste dinámico a cualquier resolución
- ✅ Aviso al iniciar nueva partida si hay una partida en curso (con opción de guardar)
- ✅ Ingreso guiado de puntajes por mano con pestaña por equipo/jugador
- ✅ Calculadora de fichas integrada (ficha por ficha con subtotales)
- ✅ Preview del subtotal estimado antes de confirmar cada mano
- ✅ Historial completo con puntajes por mano y acumulados
- ✅ Deshacer última mano (incluso si era la mano ganadora)
- ✅ Guardar y cargar partidas en `.json`
- ✅ Detección automática del ganador con manejo correcto de empates en 3000+

---