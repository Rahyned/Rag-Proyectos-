# Manual de Usuario — STELLA

**ERP de gestión para laboratorios odontológicos**

Versión 1.6.4 · Septiembre 2026

---

# Índice

1. Introducción
2. Primeros pasos
3. La ventana principal
4. Dashboard
5. Clientes
6. Productos y rubros
7. Proveedores
8. Trabajos
9. Cuentas corrientes
10. Documentos y comprobantes
11. Configuración y respaldos
12. Preguntas frecuentes
13. Solución de problemas
14. Glosario
15. Acerca de

---

# 1. Introducción

## 1.1 ¿Qué es STELLA?

STELLA es un sistema de gestión integral (ERP) diseñado para las operaciones
diarias de un laboratorio odontológico. Centraliza en una sola aplicación el
control de los odontólogos que envían trabajos, las órdenes de trabajo del
laboratorio, el catálogo de servicios y precios, los proveedores de materiales,
las cuentas corrientes de cada cliente y la documentación que se imprime
(tickets, comandas y comprobantes).

En lugar de llevar planillas sueltas para los trabajos, otras para los precios
y una libreta para las deudas, STELLA mantiene todo en una base de datos local
con respaldos automáticos, de modo que la información del laboratorio queda
consistente, consultable y respaldada.

## 1.2 Para quién es

STELLA está pensado para:

- **Laboratorios odontológicos** chicos y medianos que reciben órdenes de
  varios consultorios.
- **Administradores** que necesitan ver números: trabajos activos, saldos a
  cobrar, productos más usados, informes mensuales.
- **Estaciones de trabajo** donde recepción da de alta trabajos, los
  consultores solo consultan y los odontólogos siguen sus propias órdenes.

## 1.3 Características principales

| Característica | Descripción |
|---|---|
| Control de clientes | Alta, edición, búsqueda e importación de odontólogos y consultorios |
| Órdenes de trabajo | Ciclo completo: nuevo → en proceso → terminado → entregado |
| Catálogo de productos | Servicios por rubro con precios de lista y precios de cliente |
| Proveedores | Gestión por rubro con importación desde Excel |
| Cuentas corrientes | Debe, haber y saldo automático por cliente o proveedor |
| Documentos | Tickets, comandas y comprobantes listos para imprimir |
| Dashboard | Métricas, gráficos, ranking e informe mensual |
| Respaldos | Copias automáticas al iniciar y respaldo opcional en la nube |
| Temas | Modo claro y modo oscuro |
| Multi-estación | Estación Maestra (con servidor) y Estaciones de Consulta |

## 1.4 Conceptos clave

Antes de usar el sistema, conviene tener claros cinco términos que aparecen en
todo el manual:

**Cliente.** En STELLA un *cliente* es el odontólogo o consultorio que envía
trabajos al laboratorio, no el paciente. Cada orden de trabajo sí registra el
paciente por separado.

**Trabajo u orden.** Es la pieza que el laboratorio recibe para fabricar: por
ejemplo "corona de cerámica A2 en pieza 21 para el paciente María Gómez,
ingresada por el Dr. Pérez". Cada trabajo tiene número de orden propio, estado,
precio y fechas de entrada y salida.

**Rubro.** Agrupa productos y proveedores según el tipo de material o
proceso: híbridas, implantología, ceramage, ataches, pernos, metales,
prótesis removibles, acrílicas, flexibles y de cromo.

**Ficha.** Documento identificador que acompaña a un trabajo o ticket dentro
del laboratorio. Cada ticket tiene su número de ficha y su número de ticket
únicos.

**Cuenta corriente.** El libro de movimientos deudores y pagos de un cliente o
proveedor. Todo movimiento deja un *debe* (le deben al laboratorio) o un
*haber* (pagos y anticipos) y el saldo se calcula solo.

## 1.5 Cómo usar este manual

Cada capítulo corresponde a una pantalla o módulo de STELLA. Si llegás por
primera vez, seguí el orden: primero *Primeros pasos*, después *La ventana
principal* y *Dashboard*, y luego los módulos que te toquen en tu sector. Las
páginas finales reúnen preguntas frecuentes, problemas comunes y un glosario
con los términos odontológicos y del sistema.

## 1.6 STELLA frente a la planilla

Muchos laboratorios arrancan con un Excel compartido y una libreta de
deudas. Qué cambia al pasar a STELLA:

| Con planillas sueltas | Con STELLA |
|---|---|
| El precio "se actualiza" en un archivo y otro sigue con el viejo | Un único catálogo: el precio se carga una vez y lo usan todas las estaciones |
| El estado del trabajo se sabe "por boca del técnico" | Estado explícito en cada orden: nuevo, en proceso, terminado, entregado |
| La cuenta corriente se arma sumando filas a mano | Saldo automático con debe, haber y comprobante de cada movimiento |
| Si se rompe el notebook, se pierde el histórico | Respaldos automáticos al abrir y respaldo opcional en la nube |
| Buscar "la corona de Juan" es mirar tres archivos | Una búsqueda en Trabajos responde con la orden completa |
| El resumen del mes se arma la noche del cierre | Dashboard e informe mensual con el resumen ya calculado |

El valor no es solo "guardar datos en la computadora": es que un solo
registro alimenta la tabla, el dashboard, los documentos impresos y la
cuenta corriente, sin volver a tipear la misma información en cuatro
lados.

## 1.7 El flujo completo de un trabajo

Para entender cómo se conectan los módulos, conviene seguir el recorrido
completo de una orden, desde que entra por la puerta hasta que se cobra:

1. **Ingreso (Recepción).** Llega el odontólogo o su asistente con una pieza
   y una indicación. En el módulo Trabajos se da de alta la orden con el
   cliente, el paciente, el artículo, el color, la pieza y el precio. El
   trabajo nace en estado *Nuevo*. Al mismo tiempo se imprime el **ticket de
   ingreso**: una copia para el cliente y otra que acompaña la pieza.
2. **Preparación (Laboratorio).** Desde la ficha se imprime la **comanda** y
   la orden se coloca en la mesa correspondiente. Recepción o el encargado
   cambia el estado a *En proceso*.
3. **Fabricación.** El técnico trabaja según la comanda. Si surge una duda
   con el color o la indicación, el trabajo tiene notas visibles para todo
   el equipo y la ficha del cliente muestra el historial para orientarse.
4. **Control y entrega.** Al estar listo, el estado pasa a *Terminado*; el
   sistema lo refleja en el dashboard (tarjeta "Terminados") y en el filtro
   de la tabla. Cuando el consultorio retira la pieza, el estado finaliza en
   *Entregado* y se imprime el comprobante si corresponde.
5. **Cobro.** El trabajo genera el cargo en la **cuenta corriente** del
   cliente. Cuando el cliente paga (efectivo, transferencia, tarjeta o
   cheque), se registra el movimiento de *haber* con su comprobante y el
   saldo baja automáticamente.
6. **Seguimiento.** El dashboard resume todo: trabajos activos, terminados,
   saldo por cobrar y los gráficos de período. El **informe mensual** cierra
   el mes con números para la toma de decisiones.

Si un trabajo se anula, entra en estado *Cancelado* en cualquier punto del
flujo y no sigue avanzando; su cargo en cuenta corriente no se genera (o se
retira si se cancela después de cobrado).

Este mismo flujo se repite decenas de veces por día, y es lo que STELLA
automatiza: un solo registro alimenta la tabla, el dashboard, los documentos
impresos y la contabilidad.

---

# 2. Primeros pasos

## 2.1 Requisitos

STELLA es una aplicación de escritorio que corre en Windows. Para
instalarla necesitás:

- Windows 10 o 11 (64 bits).
- Espacio libre en disco para la aplicación y sus respaldos.
- Conexión a la red local si otras estaciones van a usar la misma base.
- Permisos de usuario normal (no se requiere ejecutar como administrador).

Los datos se guardan en la propia máquina, en la carpeta de datos del sistema
de Windows, por lo que no dependés de internet para trabajar.

## 2.2 Instalación y primer arranque

1. Descargá el instalador de STELLA desde el enlace entregado por tu
   administrador o desde la página de descargas del proyecto.
2. Ejecutá el instalador. Los archivos se instalan en una carpeta del usuario
   y se crea el acceso directo en el escritorio y en el menú Inicio.
3. Abrí STELLA desde el acceso directo. La primera vez se crea la base de
   datos local y la pantalla de inicio de sesión.

Si trabajás desde el código fuente en lugar del instalador, los requisitos son
Python 3.8 o superior y las dependencias listadas en `requirements.txt`; la
aplicación se inicia con `python main.py`.

## 2.3 La pantalla de inicio de sesión

Al abrir STELLA aparece la pantalla de login con tu usuario y contraseña:

1. Ingresá el **usuario** que te asignó el administrador del sistema.
2. Ingresá tu **contraseña**.
3. Marcá **Recordarme** si querés que la sesión se mantenga abierta en esta
   computadora.
4. Tocá **Iniciar sesión**.

Detalles importantes del login:

- **Las credenciales las entrega el administrador.** No hay contraseña
  genérica de fábrica: si es tu primera vez, pedile tu usuario y contraseña
  al administrador del laboratorio.
- **Recordarme**: cuando está marcado, la sesión se guarda por **30 días** en
  esa computadora y STELLA te entra directo al dashboard sin volver a pedir la
  contraseña.
- **Cerrar sesión**: al salir, el sistema pregunta si querés *Cerrar STELLA*
  (cierra la aplicación y conserva la sesión recordada) o *Cambiar de usuario*
  (borra la sesión y vuelve a la pantalla de login).
- Si la contraseña es incorrecta aparece un mensaje de error; verificá
  mayúsculas y minúsculas. Después de varios intentos fallidos, esperá unos
  minutos o contactá al administrador.

## 2.4 Roles y permisos

Cada usuario ingresa con un rol que define qué puede ver y qué puede hacer.
El rol lo asigna el administrador y se valida en el servidor: aunque la
pantalla de login muestre pestañas de rol, lo que manda es el rol real del
usuario.

| Rol | Qué puede hacer |
|---|---|
| **Admin** | Acceso total: crea, edita y elimina clientes, productos, proveedores, trabajos y movimientos; ve el dashboard completo, los informes y la configuración |
| **Consultor** | Solo lectura: consulta clientes, trabajos, productos y saldos, pero no modifica datos |
| **Odontólogo** | Ve y consulta solamente sus propios trabajos |
| **Recepción** | Gestiona clientes y trabajos de ingreso diario: da de alta órdenes, busca clientes y consulta estados |

Si necesitás que tu rol cambie (por ejemplo, pasar de consultor a recepción),
el administrador actualiza tu usuario.

### Qué hace cada rol en el día a día

- **Admin**: revisa el dashboard cada mañana, carga productos y precios
  nuevos, resuelve duplicados, respalda la base antes de operaciones grandes
  e revisa el informe mensual.
- **Recepción**: vive en el módulo Trabajos: da de alta las órdenes del día,
  imprime tickets y comandas, cambia estados a medida que avanzan y registra
  los cobros en Ctas. Ctes.
- **Consultor**: consulta saldos, trabajos propios y estados desde su
  estación sin riesgo de modificar datos.
- **Odontólogo**: entra para ver el estado de sus órdenes y el historial de
  sus pacientes sin ver la información de otros consultorios.

## 2.5 Actualizaciones automáticas

También se pregunta como: ¿Cómo funcionan las actualizaciones automáticas? En STELLA el programa verifica al iniciar si hay una versión nueva publicada. Cuando está
disponible, te avisa y podés descargar la actualización en segundo plano sin
bloquear el trabajo. Al cerrar la aplicación se aplica; si algo falla, el
sistema conserva la versión anterior. Verificá la versión actual en la
pantalla de configuración: este manual corresponde a la **versión 1.6.4**.

---

# 3. La ventana principal

## 3.1 Distribución

Al iniciar sesión aparece la ventana principal, organizada en dos zonas:

- **Barra superior**: título de la aplicación con el nombre del laboratorio,
  el usuario que tiene la sesión abierta y el botón de cerrar sesión.
- **Barra lateral (sidebar)**: los accesos a los módulos, siempre en el mismo
  orden:

| Icono | Módulo | Función |
|---|---|---|
| 🏠 | **Dashboard** | Métricas, gráficos y trabajos recientes |
| 👥 | **Clientes** | Alta y gestión de odontólogos |
| 📦 | **Productos** | Catálogo de servicios y precios |
| 🔧 | **Proveedores** | Gestión de proveedores por rubro |
| 📋 | **Trabajos** | Órdenes de trabajo y sus estados |
| 💰 | **Ctas. Ctes.** | Movimientos de deuda y pagos |
| ⚙️ | **Configuración** | Tema, respaldos, atajos y logs |

El contenido del módulo seleccionado se muestra en el área principal. Los
roles con permisos de solo lectura ven los mismos módulos pero sin botones de
alta, edición o eliminación.

## 3.2 Tema claro y tema oscuro

STELLA incluye dos temas visuales: **oscuro** (por defecto) y **claro**, con
acordes suaves pensados para ambientes de laboratorio con poca o mucha luz.
Se cambia desde **Configuración → Tema de la aplicación**, con un botón de
toggle; el cambio se aplica en todo el sistema al instante y queda guardado
para la próxima vez que abras la aplicación.

Elegí el tema que mejor se adapte a la iluminación de tu lugar de trabajo: el
tema oscuro reduce la luminosidad de la pantalla en oficinas con poca luz; el
claro es más cómodo con luz natural directa.

## 3.3 Atajos de teclado

La sección **Configuración → Atajos de teclado** muestra los atajos activos y
permite reasignarlos: seleccioná el atajo, presioná la nueva combinación de
teclas y guardá. Para cancelar una captura en curso, presioná **Esc**.

Entre los atajos más usados encontrás la apertura rápida de módulos y
acciones frecuentes de las tablas (buscar, agregar, refrescar). La lista
completa de atajos vigentes se muestra en la propia pantalla de configuración.

## 3.4 Cerrar sesión o salir

El botón de cierre (esquina superior derecha) presenta dos opciones:

- **Cambiar STELLA**: cierra la sesión actual, borra la sesión recordada y
  vuelve a la pantalla de login para que ingrese otro usuario.
- **Cerrar STELLA**: cierra la aplicación completa conservando la sesión
  recordada, de modo que la próxima apertura en esta computadora entre
  directo (si se abrió con *Recordarme*).

Es recomendable usar *Cambiar de usuario* cuando compartís la computadora con
otras personas del laboratorio.

---

# 4. Dashboard

## 4.1 Primer pantallazo

El Dashboard es la pantalla de inicio y resume la salud del laboratorio en
cuatro tarjetas de métricas:

| Tarjetas | Qué muestra |
|---|---|
| **Trabajos totales** | Órdenes registradas en el período seleccionado |
| **Activos** | Trabajos en estado *nuevo* o *en proceso* |
| **Terminados** | Trabajos listos o entregados |
| **Por cobrar** | Saldo pendiente de cobro de clientes |

Debajo de las tarjetas aparece la **lista de trabajos recientes**, con número
de orden, cliente, artículo, estado y fecha de ingreso, para tener a la vista
lo que entró y lo que sale.

## 4.2 Filtros y gráficos

El encabezado del dashboard incluye filtros de fecha (desde / hasta) y
desplegables para acotar los datos; los indicadores y gráficos se recalculan
según el rango elegido. Entre los gráficos encontrarás:

- **Barras**: trabajos por estado o por período.
- **Torta (donut)**: distribución por rubro o por cliente.
- **Líneas**: evolución de ingresos o saldos a lo largo del tiempo.
- **Ranking**: clientes o artículos más frecuentes del período.

Dos botones acompañan a los filtros: **Actualizar**, que recalcula las
métricas, y **Exportar**, que descarga la información visible en formato de
planilla para tu propio análisis.

### Cómo leerlos en la práctica

Un ejemplo: filtrás del 1 al 15 de septiembre y ves 12 trabajos *En
proceso*, 5 *Terminados* esperando entrega y el gráfico de barras con la
mayoría de pedidos en el rubro híbridas. Si la torta muestra que el 70 % de
los trabajos sale de dos clientes, conviene revisar la lista de precios de
esos dos (§6.2); si la línea de ingresos se mantiene plana pero el ranking
sube, es señal de que entraron muchos trabajos chicos: el dashboard no dice
qué hacer, pero te muestra dónde mirar primero.

## 4.3 Saldo pendiente a cobrar

La tarjeta de *Por cobrar* suma el **saldo final de cada cliente** con saldo
positivo, es decir: cuánto debe cada cuenta corriente sumado una sola vez por
titular. Un cliente que tiene varios movimientos en la cuenta corriente no se
cuenta duplicado: se toma su último saldo. Este indicador es el número a mirar
para saber cuánta plata hay que recuperar esta semana.

## 4.4 Informe mensual

El módulo de **Informe mensual** (disponible para administradores) genera un
resumen del mes: trabajos ingresados y entregados, montos, saldos de clientes
y proveedores, y comparativa respecto del mes anterior. Está pensado para la
reunión de cierre mensual del laboratorio: exportalo, imprimilo o guardalo
como respaldo del análisis.

---

# 5. Clientes

## 5.1 Qué es un cliente en STELLA

Un cliente es el odontólogo o consultorio que envía trabajos al laboratorio.
La ficha de cliente guarda sus datos de contacto, en qué lista de precios
compra y cuánto crédito tiene disponible. Los pacientes no son clientes: se
registran dentro de cada trabajo.

## 5.2 Ver la lista de clientes

Al entrar al módulo **Clientes** se muestra la tabla con todos los clientes
activos: nombre completo, domicilio, celular, correo electrónico y lista de
precio. La tabla tiene paginación para que se mantenga ágil con cientos de
registros.

- **Búsqueda**: escribí en el campo de búsqueda por nombre, mail o celular y
  la tabla filtra mientras escribís.
- **Orden**: tocá el encabezado de una columna para ordenar por esa columna.
- Los clientes dados de baja lógica (inactivos) no aparecen en la lista
  normal.

## 5.3 Agregar un cliente

1. Tocá **Agregar Cliente**.
2. Completá los campos:
   - **Nombre completo**: apellido y nombre del odontólogo o razón social del
     consultorio.
   - **Domicilio**: dirección del consultorio.
   - **Celular**: número de contacto principal.
   - **Mail**: correo electrónico para envíos.
   - **Lista de precio**: *cliente* (con descuento) o *no cliente* (precio de
     lista). Ver §6.2.
   - **Límite de crédito**: monto máximo que el laboratorio le respalda en
     cuenta corriente.
3. Tocá **Guardar**.

Si el campo obligatorio está vacío o el formato del mail es inválido, el
sistema muestra el aviso y no guarda hasta corregirlo.

## 5.4 Editar y eliminar

- **Editar**: seleccioná la fila y tocá **Acciones → Editar** (o hacé doble
  clic sobre la fila) para corregir cualquier dato de la ficha.
- **Eliminar**: desde **Acciones → Eliminar**, con confirmación previa. El
  cliente queda inactivo y deja de aparecer en las búsquedas, pero su
  historial de trabajos y su cuenta corriente **se conservan**: no se borra
  información contable al dar de baja un cliente.

Antes de eliminar, verificá que el cliente no tenga trabajos activos ni saldo
pendiente.

## 5.5 Ficha del cliente

La **ficha de cliente** (doble clic o *Ver ficha*) abre un diálogo con la
información completa agrupada:

- Datos personales y de contacto.
- Lista de precio y límite de crédito.
- Saldo actual de la cuenta corriente.
- Historial de trabajos enviados por ese cliente, con estados y montos.

Es la pantalla más útil para responder "¿cuánto debe el Dr. X?" o "¿qué
trabajos le entregamos este mes?" sin navegar a otros módulos.

## 5.6 Importar clientes desde Excel

Si ya tenés los clientes en una planilla, no hace falta cargar uno por uno:

1. Tocá **Importar** en la barra de acciones.
2. Seleccioná el archivo de Excel o TXT.
3. El sistema detecta las columnas automáticamente (nombre, mail, celular,
   domicilio, etc.) sin importar que se llamen un poco distinto en tu
   planilla: acepta variantes como "nombre", "apellido y nombre", "razón
   social", "email", "teléfono" y similares.
4. Revisá el resumen de filas a importar y confirmá.

Las filas con datos inválidos se reportan fila por fila sin frenar la
importación del resto. También podés usar **Descargar Excel** para exportar
la lista actual y usarla como plantilla de importación.

---

# 6. Productos y rubros

## 6.1 El catálogo de servicios

El módulo **Productos** administra el catálogo de servicios que ofrece el
laboratorio: cada producto tiene nombre, rubro, precio base y estado. Los
rubros predefinidos son:

| Rubro | Tipo de trabajo |
|---|---|
| HÍBRIDAS | Prótesis híbridas sobre implante |
| IMPLANTOLOGIA | Componentes y piezas de implantología |
| CERAMAGE | Restauraciones de cerámica estratificada |
| ATACHES | Ataches y anclajes |
| PERNOS | Pernos y núcleos |
| METALES | Trabajos en aleaciones metálicas |
| PROTESIS REMOVIBLE | Prótesis removibles |
| PROTESIS ACRILICA | Prótesis acrílicas totales o parciales |
| PROTESIS FLEXIBLE | Prótesis de resina flexible |
| PROTESIS CROMO | Prótesis de cromo-cobalto |

Para qué sirve cada rubro, en términos prácticos del laboratorio:

- **Híbridas**: trabajos combinados, típicamente una estructura interna (a
  veces sobre implante) revestida con dientes y encías de resina. Suelen ser
  de los pedidos más frecuentes en consultorios con pacientes edéntulos.
- **Implantología**: piezas y componentes relacionados con implantes:
  pilar, tornillo, muñón artificial y prótesis atornilladas o cementadas
  sobre implante. Requieren precisión milimétrica y control de números de
  serie o medidas.
- **Ceramage**: restauraciones de cerámica estratificada capa a capa (coronas,
  carillas, incrustaciones) donde el técnico aplica encías y esmaltes para
  imitar el diente natural. El color A2, A3 y compañías son aquí la clave.
- **Ataches**: sistemas de retención mecánica (botones, anclajes, barras) que
  fijan una prótesis removible a dientes o implantes; se trabajan con
  tolerancias muy ajustadas.
- **Pernos**: núcleos y pernos que refuerzan un diente debilitado antes de
  colocar la corona; pueden ser de fibra o metálicos.
- **Metales**: prótesis y estructuras en aleaciones (níquel-cromo,
  cobalto-cromo, otros) obtenidas por colada; el ajuste final se controla
  sobre el modelo de yeso.
- **Prótesis removible**: aparatos que el paciente se saca (placas
  parciales o totales), con dientes artificiales y base acrílica sobre
  structurales metálicos o sin ellos.
- **Prótesis acrílica**: base de resina acrílica, la opción clásica para
  rehabilitaciones totales; se colorea y pulido para imitar la encía.
- **Prótesis flexible**: parciales en resina termoelástica, sin metal, más
  estéticas y cómodas para casos cortos.
- **Prótesis de cromo**: parciales esqueléticas de cromo-cobalto, ligeras y
  de larga duración, con brazos de retención sobre los dientes naturales.

Conocer el rubro ayuda a elegir el filtro correcto al buscar precios, a
armar reportes por línea de trabajo y a saber dónde cae cada pedido nuevo.

## 6.2 Regla de precios

La regla de precios de STELLA es simple y se aplica en todo el sistema:

| Concepto | Cálculo | Ejemplo con precio base $20.000 |
|---|---|---|
| **Precio base (lista)** | Precio de lista del producto | $20.000 |
| **Precio cliente** | Precio base × 0,85 (15 % de descuento) | $17.000 |
| **Precio no cliente** | Precio base, sin descuento | $20.000 |

Quién paga precio de cliente o precio de lista lo determina el **tipo de
lista del cliente** configurado en su ficha (§5.3). El descuento no se carga
a mano: se calcula automáticamente al momento de facturar o imprimir.

## 6.3 Alta y edición de productos

1. Tocá **Agregar**.
2. Ingresá el nombre del producto o servicio (por ejemplo, "Corona
   cerámica-stratificada").
3. Elegí el **rubro** en el desplegable.
4. Cargá el **precio base**. STELLA deriva solo los precios de cliente y no
   cliente.
5. Guardá.

Para modificar un precio, editá la fila directamente en la grilla o desde la
ficha del producto; los precios derivados se recalculan al instante. El botón
**Eliminar** da de baja el producto del catálogo; los trabajos históricos que
lo usaron conservan su precio y nombre de origen.

## 6.4 Importar y exportar

Como en los demás módulos, la barra de acciones ofrece:

- **Importar**: carga masiva desde Excel con detección automática de columnas
  ("producto", "artículo", "descripcion", "precio", "valor", "importe",
  "total" y variantes).
- **Descargar**: exporta el catálogo a Excel (plantilla o copia de seguridad).
- **Imprimir**: genera la lista de precios para llevar al consultorio.
- **Filtros**: los desplegables por rubro permiten ver solo un segmento del
  catálogo.

### Columnas reconocidas en la importación

El detector de columnas normaliza los encabezados (minúsculas, sin acentos)
y acepta sinónimos frecuentes:

| Campo del sistema | Ejemplos de encabezado aceptados |
|---|---|
| Número de orden | orden, nro orden, work order, folio |
| Cliente | cliente, cliente nombre, razón social, empresa |
| Artículo | artículo, producto, tarea, descripción |
| Precio | precio, valor, importe, monto, total |

La misma lógica se aplica en clientes, proveedores, productos y trabajos.
Si dos columnas califican con un puntaje parecido, el sistema te pedirá
confirmar el mapeo antes de importar; si ninguna supera el mínimo de
similitud, la columna se ignora y sus datos no se importan (mejor perder una
columna ambigua que mezclar nombres con precios).

---

# 7. Proveedores

## 7.1 Gestión por rubro

El módulo **Proveedores** administra a los proveedores de materiales e
insumos, agrupados por los mismos rubros del catálogo (híbridas, implantología,
ceramage, ataches, pernos, metales y prótesis). Cada proveedor guarda nombre,
domicilio, celular, mail y rubro principal.

## 7.2 Alta, edición y búsqueda

- **Agregar**: completá nombre, rubro y datos de contacto.
- **Búsqueda**: por nombre, mail o celular, con filtro mientras escribís.
- **Editar / Eliminar**: desde **Acciones**, con confirmación. Al eliminar, el
  proveedor queda inactivo sin borrar sus movimientos en cuenta corriente
  (ver §9).

## 7.3 Importación y utilidades

La barra de acciones del módulo ofrece **Importar** (Excel con detección
automática de columnas), **Descargar** (exportación a Excel), **Imprimir**
(listado por rubro) y **Acciones** para editar o eliminar la fila
seleccionada.

Los proveedores también pueden tener cuenta corriente: los pagos por
materiales se registran en el módulo Ctas. Ctes. con tipo *Proveedor*
(ver §9.5).

## 7.4 Flujo típico de compras y pagos

Un recorrido habitual del módulo:

1. **Llega el material** (resina, cerámica, aleación): el proveedor queda
   asociado al rubro que abastece; si es nuevo, se da de alta con
   **Agregar**.
2. **Se registra el pago** o anticipo en Ctas. Ctes. con tipo *Proveedor*
   y método correspondiente; el comprobante queda en Historial de
   documentos.
3. **Al cierre del mes**, el saldo de cada proveedor aparece en el informe
   mensual junto con los saldos de clientes: la diferencia es la caja real
   del período.
4. Si el proveedor tiene cuenta corriente, su ficha refleja los movimientos
   igual que la de un cliente.

Mantener el rubro correcto en cada proveedor además alimenta los reportes
por línea de materiales: saber cuánto se compra en ceramage por mes es tan
útil como saber cuánto se factura.

---

# 8. Trabajos

## 8.1 Qué es un trabajo

Un **trabajo** es una orden de fabricación recibida del laboratorio: registra
qué se hizo, para quién, para qué paciente, en qué pieza, con qué material y
a qué precio. Es el corazón de STELLA: casi todos los reportes y la cuenta
corriente se alimentan de aquí.

## 8.2 Ciclo de vida de un trabajo

Todo trabajo avanza por un conjunto fijo de estados:

```
        ┌─────────────────────────────────────────────┐
        │                                             │
  NUEVO ──→ EN_PROCESO ──→ TERMINADO ──→ ENTREGADO    │
                     │                               │
                     └──────────→ CANCELADO          │
        └─────────────────────────────────────────────┘
```

| Estado | Significado |
|---|---|
| **Nuevo** | Recién ingresado, aún no se empezó a fabricar |
| **En proceso** | En la mesa: se está confeccionando |
| **Terminado** | Listo para retirar, esperando al cliente |
| **Entregado** | Entregado al consultorio; cierra el ciclo |
| **Cancelado** | Anulado (por error de carga o decisión del cliente); no sigue avanzando |

El estado se elige en el diálogo de alta (desplegable con los estados
posibles) y se actualiza a lo largo del día desde la tabla o la ficha del
trabajo.

## 8.3 Campos de una orden

| Campo | Contenido |
|---|---|
| **Número de orden** | Identificador único del trabajo |
| **Cliente** | Odontólogo o consultorio que lo envía |
| **Paciente** | Nombre del paciente (no confundir con el cliente) |
| **Artículo** | Qué se fabrica (tomado del catálogo de productos o texto libre) |
| **Rubro** | Agrupación del artículo |
| **Color** | A1, A2, A3, A3.5, A4, B1, B2, C2, D2 o Blanco |
| **Pieza dental** | Número de pieza según notación FDI, del 11 al 58 |
| **Precio** | Precio acordado (acepta coma o punto decimal: "1500,50") |
| **Fechas** | Entrada y salida del trabajo |
| **Estado** | Ver §8.2 |
| **Notas** | Indicaciones del odontólogo o internotas del laboratorio |

## 8.4 Dar de alta un trabajo

1. Entrá al módulo **Trabajos** y tocá **Agregar**.
2. Cargá el cliente (buscador con autocompletado) y el paciente.
3. Elegí el artículo; si está en el catálogo, se completan rubro y precio de
   referencia.
4. Seleccioná color y pieza dental.
5. Cargá el precio final acordado.
6. Elegí el estado inicial (por defecto *Nuevo*).
7. Agregá notas si hace falta y **Guardá**.

El trabajo queda listo en la tabla con su número de orden y aparece en el
dashboard y en la cuenta corriente del cliente.

## 8.5 Editar, avanzar estado y cancelar

- **Ficha de trabajo**: doble clic sobre la fila abre la ficha con todos los
  datos para editarlos.
- **Cambio de estado**: desde la ficha o desde el menú de acciones; el
  sistema guarda la transición y refresca la tabla.
- **Precio**: si editás el precio de un trabajo, la cuenta corriente se
  ajusta en el mismo momento (se crea o elimina el cargo correspondiente).
  Editar el precio de un trabajo cancelado no genera movimientos.
- **Cancelar**: disponible en el diálogo de alta y en acciones; siempre con
  confirmación.

## 8.6 Importación masiva de trabajos

Para migrar desde una planilla anterior:

1. **Importar** en la barra de acciones del módulo.
2. Seleccioná el archivo; el sistema detecta columnas como "orden", "nro
   orden", "folio", "cliente", "articulo", "producto", "precio", "valor",
   "importe" y variantes.
3. Revisá el resumen: cada fila se valida individualmente (cliente existente,
   estado válido, precio no negativo). Las filas inválidas se rechazan con
   su número de fila; las válidas se importan igual.
4. Confirmá.

Nunca se asigna un cliente por defecto a una fila sin cliente: si falta, la
fila se rechaza para que no se cuelen datos en la cuenta equivocada.

## 8.7 Búsqueda y acciones de la tabla

La tabla de trabajos ofrece búsqueda por número de orden, paciente, cliente o
artículo; filtro por estado; orden por columna; y paginación. Desde la barra
de acciones: **Agregar**, **Importar**, **Descargar** (exportación a Excel),
**Imprimir** y **Acciones** (ficha, editar, eliminar, imprimir documentación
del trabajo).

## 8.8 Ejemplo completo: ingreso y entrega

Caso real para ver todos los campos en acción:

> El consultorio de la Dra. Gómez entrega una corona de cerámica para el
> paciente Juan Pérez, pieza 21, color A2, con un precio acordado de
> $18.500.

1. **Trabajos → Agregar**.
2. Cliente: buscás "Gómez" y la autocompletado carga su ficha (su lista de
   precio es *cliente*, así que los productos del catálogo le aplican el 15 %
   de descuento).
3. Paciente: "Juan Pérez".
4. Artículo: "Corona cerámica" (o el nombre exacto de tu catálogo); rubro
   CERAMAGE; precio sugerido $17.000 — pero el acordado es $18.500, así que
   lo editás.
5. Color: A2. Pieza: 21. Estado inicial: *Nuevo*.
6. Nota: "Paciente alérgico a metales; evitar contacto con níquel."
7. **Guardar** → se imprime el ticket de ingreso y la comanda.
8. Estado *En proceso* cuando el técnico la toma; *Terminado* al día
   siguiente; *Entregado* cuando la Dra. Gómez retira.
9. En Ctas. Ctes. aparece el cargo de $18.500; al cobrar, se registra el
   pago y el saldo baja.

Si la Dra. Gómez llamará diciendo que la pieza es para otra paciente, la
corrección se hace en la ficha antes de *Terminado*; si se cancela, el cargo
desaparece de la cuenta corriente.

## 8.9 Consejos para trabajar la tabla con muchas órdenes

Cuando el laboratorio lleva cientos de trabajos del mes:

- **Ordená por fecha de entrada** para ver primero lo más nuevo, o por
  estado para barrer los *Terminados* pendientes de entrega.
- **Buscá por paciente o número de orden**: es más rápido que recorrer la
  lista; el filtro de estado acota el resultado.
- **Exportá antes de las reuniones**: Descargar Excel con el filtro del
  período te da el insumo del informe sin tipear nada.
- **Cambiá de estado en bloque del día**: al cerrar la jornada, repasá los
  *Terminados* y marcalos *Entregados* cuando salgan; así el dashboard del
  día siguiente arranca limpio.
- **Usá las notas**: una indicación escrita ("revisar ajuste con el
  modelo 2") evita idas y vueltas entre recepción y la mesa.

---

# 9. Cuentas corrientes

## 9.1 Debe, haber y saldo

La cuenta corriente es el libro de deudas y pagos del laboratorio con cada
titular (cliente o proveedor). Todo movimiento tiene dos caras:

- **Debe**: un cargo a favor del laboratorio (un trabajo facturado, un
  material comprado al proveedor).
- **Haber**: un pago o anticipo recibido.

El saldo se calcula solo:

```
saldo = debe − haber

saldo > 0  →  el titular debe dinero al laboratorio
saldo < 0  →  el titular tiene crédito a favor
saldo = 0  →  cuenta al día
```

## 9.2 Registrar un movimiento

También se pregunta como: quiero cobrarle a un dentista. En STELLA ese cobro se anota en la cuenta corriente del consultorio.

1. Entrá al módulo **Ctas. Ctes.**
2. Tocá **Agregar movimiento**.
3. Elegí el tipo y el titular (cliente o proveedor, con buscador).
4. Completá fecha, importe, número de comprobante si corresponde, si es debe
   o haber, y el **método de pago**.
5. Guardá: el saldo del titular se recalcula automáticamente.

Los trabajos facturados generan sus movimientos de debe desde el propio
módulo de trabajos; acá registrás los cobros y los pagos.

## 9.3 Métodos de pago

| Método | Cuándo usarlo |
|---|---|
| **Efectivo** | Pagos en dinero físico en el mostrador |
| **Transferencia** | Depósitos y transferencias bancarias |
| **Tarjeta** | Pagos con débito o crédito |
| **Cheque** | Cheques a nombre del laboratorio |

El método queda registrado en el movimiento y permite filtrar después por
tipo de cobro.

## 9.4 Eliminar movimientos

El botón **Eliminar** sobre un movimiento ofrece tres opciones:

1. **Eliminar todos los movimientos del titular** — limpia la cuenta completa
   de ese cliente o proveedor (uso frecuente al reiniciar una cuenta).
2. **Solo este movimiento** — borra únicamente la fila seleccionada.
3. **Cancelar** — no hace nada.

La opción masiva pide confirmación extra, porque borra toda la historia de
esa cuenta. Los movimientos importados desde Excel respetan las mismas reglas.

## 9.5 Cuentas de proveedores

Los proveedores también tienen cuenta corriente: los pagos de materiales
quedan como *haber* y los consumos como *debe*, con tipo *Proveedor*. El
desplegable de tipo de la cabecera permite ver solo clientes, solo
proveedores o la mezcla completa.

## 9.6 Saldos a la vista

- La tabla muestra el **saldo actual** de cada titular, calculado con el
  último movimiento.
- El dashboard resume el **saldo pendiente a cobrar** sumando un solo saldo
  por titular (ver §4.3), evitando duplicidades por tener varios movimientos.
- La ficha del cliente muestra su saldo junto con el historial, y la ficha
  del trabajo muestra los cargos que generó.

## 9.7 Ejemplo: una cuenta en movimiento

Cuenta corriente del Dr. Hernández durante un mes:

| Fecha | Concepto | Debe | Haber | Saldo |
|---|---|---|---|---|
| 02/09 | Corona pieza 21 — $15.000 | 15.000 | — | $15.000 |
| 05/09 | Prótesis inferior — $42.000 | 42.000 | — | $57.000 |
| 10/09 | Pago en efectivo | — | 30.000 | $27.000 |
| 18/09 | Dos carillas — $24.000 | 24.000 | — | $51.000 |
| 25/09 | Transferencia | — | 51.000 | $0 |

Al 25/09 la cuenta queda al día. Si en el dashboard filtrás septiembre, la
tarjeta "Por cobrar" **no** sumará $15.000 + $42.000 + $24.000 (los cargos
individuales): tomará el **saldo final del titular** ($0) una sola vez.
Un titular con varios movimientos nunca duplica el indicador.

Para revisar qué pasó en algún día, se filtra la tabla por fecha o se abre
la ficha del cliente con el historial completo; para reimprimir el
comprobante de un pago, se usa Historial de documentos (§10.4).

---

# 10. Documentos y comprobantes

## 10.1 Tickets

El **ticket** es la ficha de ingreso del trabajo: identifica la pieza dentro
del laboratorio con un número de ficha autoincremental y un número de ticket
único, ligados al trabajo y al cliente. Cada ticket está *activo* o
*anulado*. Se imprime al momento de recibir el trabajo y acompaña la pieza
hasta su entrega.

## 10.2 Comandas

La **comanda** es la orden de fabricación impresa que queda en la mesa de
trabajo: paciente, pieza, color, artículo e indicaciones del odontólogo. Es
el documento con el que el técnico trabaja; se genera desde la ficha del
trabajo con un botón de imprimir.

## 10.3 Comprobantes

El **comprobante** documenta un pago o movimiento de cuenta corriente: monto,
método de entrega, fecha y titular. Es el resguardado que se le entrega al
cliente al cobrar y el respaldo contable del movimiento registrado en §9.

## 10.4 Historial de documentos

El módulo de **historial de documentos** reúne los tickets, comandas y
comprobantes ya emitidos, con su fecha, número y estado. Permite volver a
imprimir un documento perdido o verificar si un ticket sigue activo o fue
anulado, sin regenerarlo.

## 10.5 Contenido de cada documento

Para verificar que imprimiste el correcto, estos son los datos que lleva
cada documento:

| Documento | Campos principales |
|---|---|
| **Ticket** | Número de ficha, número de ticket, trabajo asociado, cliente, estado (activo/anulado) |
| **Comanda** | Paciente, cliente, artículo, color, pieza dental, precio, notas e indicaciones, estado |
| **Comprobante** | Fecha, titular (cliente o proveedor), importe, método de pago, número de comprobante, saldo resultante |

El número de ficha del ticket es autoincremental (cada ingreso suma uno) y
el número de ticket es único por trabajo; ante cualquier reclamo, esos dos
números identifican la pieza sin lugar a dudas.

## 10.6 Impresión

- Todos los documentos salen en tamaño papel estándar, con el encabezado del
  laboratorio.
- Antes de imprimir aparece la vista previa: revisá márgenes y cantidad de
  copias.
- Si la impresora falla o se acaba el papel, el documento no se pierde: está
  en el historial y puede reimprimirse.

---

# 11. Configuración y respaldos

## 11.1 Tema de la aplicación

**Configuración → Tema** alterna entre modo oscuro y modo claro con un botón.
El cambio es inmediato en toda la interfaz y persistente entre sesiones.

## 11.2 Backups locales

La sección **Backups** gestiona las copias de seguridad de la base de datos:

- **Automáticos**: STELLA crea una copia local cada vez que iniciás la
  aplicación, sin que tengas que acordarte.
- **Crear Backup Ahora**: botón para generar una copia en el momento (por
  ejemplo, antes de una importación masiva o del cierre del mes).
- **Ver Backups**: abre el listado de copias disponibles con su fecha; desde
  ahí se puede **Restaurar** una copia seleccionada.

> ⚠️ **Restaurar reemplaza todos los datos actuales** por los de la copia
> elegida. El sistema pide confirmación antes de ejecutarlo. Si dudás, creá
> primero un backup nuevo (así tenés una copia del estado previo) y luego
> restaurá.

Las copias locales se guardan en la carpeta de datos de la aplicación, en la
misma máquina.

## 11.3 Backups en la nube (opcional)

Para tener una copia fuera de la computadora, STELLA puede conectar un
respaldo en la nube (Google Drive): la sección **Backups en la nube** permite
conectar la cuenta, ver las copias subidas y restaurarlas igual que las
locales. Requiere que el administrador haya configurado la credencial de la
aplicación en la máquina; si aparece "no configurada", pedile al administrador
copiar el archivo de credencial correspondiente.

La estrategia recomendada es combinar ambos: locales para lo inmediato
(recuperación rápida ante un error), nube para lo importante (robo, daño de
la máquina, siniestro).

## 11.4 Atajos de teclado

Ver §3.3: la lista de atajos se muestra y se reasigna desde
**Configuración → Atajos de teclado**.

## 11.5 Carpeta de logs

El botón **Abrir carpeta de logs** abre la ubicación de los archivos de
registro (`stella.log`) que usan el equipo de soporte para diagnosticar
problemas. Si STELLA se comporta raro, abrir esta carpeta y enviar el último
log acelera enormemente la resolución.

## 11.6 Contraseñas y usuarios

También se pregunta como: ¿Cómo restablezco la contraseña de un usuario? En STELLA no hay una pantalla para cambiarla ni para crear usuarios. La creación y modificación de usuarios y contraseñas la realiza el administrador del sistema, por fuera del menú. Si la clave no entra, el mensaje es Usuario o contraseña incorrectos. Si olvidaste tu contraseña o necesitás cambiar de rol, contactá al administrador del laboratorio.

## 11.7 Actualizaciones

El aviso al abrir STELLA y la descarga en segundo plano están en la sección 2.5 de este manual. Esta nota no describe otro mecanismo.

## 11.8 Buenas prácticas de respaldo y cierre

Una rutina simple de respaldos cubre el 99 % de los accidentes:

1. **Al abrir la app**: ya tenés copia del día anterior (respaldo
   automático).
2. **Antes de cualquier importación masiva**: Crear Backup Ahora. Si la
   planilla viene mal, restaurás y seguís como si nada.
3. **Antes del cierre mensual**: otra copia manual; es tu punto de retorno
   si el informe sale con datos que no cerraban.
4. **Semanales a la nube**: si la nube está conectada, verificá en la lista
   que aparezcan copias recientes.
5. **Al reportar un problema**: no borres ni restaures; abrí la carpeta de
   logs y adjuntá `stella.log`.

Y la regla de oro: **restaurar es destructivo**. Antes de restaurar, creá un
backup del estado actual; así siempre podés volver atrás dos veces.

---

# Guía de uso diario

Estos pasos siguen las pantallas de STELLA tal como están en la versión que muestra Configuración, en Actualizaciones, como versión actual.

## Tareas paso a paso

### Cómo entro a STELLA

1. Abrí STELLA. La ventana se llama Laboratorio RioDent.
2. Completá Usuario y Contraseña. El ojo del campo muestra u oculta la clave.
3. Si la computadora es la de siempre, marcá Recordarme. STELLA vuelve a entrar sola durante 30 días.
4. Tocá Ingresar. El botón pasa a Validando… y después abre el programa.
5. Si la cuenta es Admin, el título queda Laboratorio RioDent - Admin. Si no, Laboratorio RioDent - Consulta.

Resultado: el menú de la izquierda muestra Dashboard, Proveedores, Clientes, Productos, Trabajos, Cuentas Corrientes y Configuración, con el rol y el usuario arriba.

Nota: las pestañas Admin y Consultor de la pantalla de ingreso no cambian el permiso. Manda el rol de la cuenta. STELLA no publica un usuario ni una contraseña de fábrica.

### Cómo agrego un cliente en STELLA

1. Entrá con una cuenta Admin y abrí Clientes.
2. Tocá ➕ Agregar Cliente. Se abre Nuevo Cliente.
3. Completá Nombre Completo, Domicilio, Celular y Mail. Los cuatro son obligatorios.
4. Tocá Guardar.

Resultado: STELLA dice OK Cliente agregado y la fila aparece con Tipo Lista Precio en General. Ese tipo no se pide en el formulario; se puede cambiar después con doble clic en la celda.

Nota: si falta un campo, el mensaje es Completa todos los campos. El buscador dice Buscar cliente… y la lista pagina de a 100.

### Cómo corrijo un cliente en STELLA

1. En Clientes de STELLA, como Admin, hacé doble clic en la celda (nombre, domicilio, celular, mail o tipo de lista).
2. Escribí el valor nuevo y confirmá el cuadro ¿Cambiar de … a …?.
3. Para borrar la fila, seleccionala y tocá 🗑️ Eliminar. STELLA pregunta ¿Eliminar este cliente?.

Resultado: si aceptás, la grilla se actualiza. Si el borrado no puede hacerse, aparece Error al eliminar.

Nota: Consultor no ve Agregar ni Eliminar, y la tabla de clientes queda bloqueada.

### Cómo cargo un paciente en STELLA

En STELLA el paciente no tiene una pantalla propia. Va dentro del trabajo.

1. Abrí Trabajos y tocá ➕ Agregar. El cuadro se llama Nuevo Trabajo.
2. En Paciente escribí el nombre de la persona.
3. Completá el resto (cliente, número de orden, artículo, precio, estado y fecha de salida) y tocá Guardar.

Resultado: la columna Paciente del listado muestra ese nombre. Color y pieza pueden quedar vacíos; el paciente no.

Nota: si todavía no hay odontólogos cargados, STELLA no abre el formulario y dice No hay clientes cargados. Creá primero un cliente en la sección Clientes.

### Cómo doy de alta un trabajo en STELLA

1. Como Admin, abrí Trabajos y tocá ➕ Agregar.
2. En Cliente / Odontólogo elegí un cliente. El odontólogo del trabajo queda con ese nombre.
3. Completá N° Orden, Paciente, Artículo, Precio y Fecha de Salida. El formato de la fecha es dd/mm/yyyy, por ejemplo 25/12/2024.
4. Estado ofrece en_proceso, terminado o cancelado. Color y Pieza son opcionales.
5. Tocá Guardar.

Resultado: STELLA dice OK Trabajo agregado correctamente. La fecha de entrada es la del momento. Si el precio es mayor que cero y el estado no es cancelado, el importe queda cargado en la cuenta corriente de ese cliente.

Nota: Completa todos los campos, incluida la Fecha de Salida; Formato de fecha inválido. Usa dd/mm/yyyy; o El precio debe ser un número válido.

### Cómo cambio el estado de un trabajo en STELLA

1. En Trabajos de STELLA, como Admin, seleccioná la fila.
2. Doble clic, o ⚙️ Acciones y después 📑 Editar. Se abre la pestaña Detalle.
3. En Estado elegí en_proceso, terminado o cancelado. Ahí también se pueden corregir Odontólogo y Paciente.
4. Tocá 💾 Guardar cambios.

Resultado: el listado muestra el estado nuevo. Si pasás el trabajo a cancelado, STELLA saca el cargo de la cuenta corriente de ese trabajo.

Nota: si no hay fila elegida, Detalle dice Seleccioná una fila en la pestaña Listado para ver su detalle.

### Cómo busco un trabajo en STELLA

1. Abrí Trabajos.
2. Escribí en Buscar trabajo… (número, odontólogo o paciente).
3. El botón que dice Todos abre En Proceso, Terminado o Cancelado.
4. Si hace falta, F5 recarga la lista. Son 50 filas por página.

Resultado: el cartel indica Hay un total de N trabajos con lo que coincide.

Nota: un filtro dejado en Terminado esconde el resto. Volvé a Todos.

### Cómo cargo un producto en STELLA

1. Como Admin, abrí Productos y tocá ➕ Agregar. El cuadro es Nuevo Producto.
2. Completá Artículo/Tarea.
3. En Rubro elegí uno de la lista. No dejes -- Selecciona un rubro --.
4. Cargá Precio Noviembre y Precio N. Noviembre. Si los dejás vacíos, quedan en 0.
5. Tocá ✅ Guardar.

Resultado: el artículo entra al catálogo. El precio de cliente de cada lista es el precio cargado con 15 % menos (se multiplica por 0,85). El de no cliente es el precio cargado, sin ese descuento.

Nota: Completa el campo Artículo/Tarea, Debes seleccionar un rubro, o Los precios deben ser números válidos. El precio del trabajo no se copia solo desde acá: en la orden se tipea aparte.

### Cómo creo un rubro en STELLA

1. En Productos, como Admin, tocá ➕ Rubro.
2. En el cuadro Nuevo Rubro escribí el nombre (el ejemplo de la pantalla es CERAMAGE).
3. Guardá.

Resultado: el rubro aparece en el botón 📂 Rubros y se puede elegir al dar de alta un artículo.

Nota: el filtro 📂 Rubros, puesto en un rubro, deja fuera los demás. Para ver todo, volvé a la opción Rubros.

### Cómo veo el precio de cliente en STELLA

1. Abrí Productos.
2. El botón 👤 Cliente cambia entre Cliente y No Cliente.
3. El botón 📅 Noviembre cambia entre Noviembre y N. Noviembre.
4. La columna Precio muestra el importe de esa combinación.

Resultado: con Cliente ves el precio con el 15 % de descuento. Con No Cliente ves el precio de lista de ese mes.

Nota: el buscador dice Buscar producto o artículo… y la lista pagina de a 100.

### Cómo agrego un proveedor en STELLA

1. Como Admin, abrí Proveedores.
2. Tocá el botón de alta. El cuadro se llama Nuevo Proveedor.
3. Completá Nombre Completo, Domicilio, Celular y Mail.
4. Guardá.

Resultado: la fila queda en la lista. El buscador dice Buscar proveedor….

Nota: el alta pide los mismos cuatro datos que el cliente. Si falta uno, no guarda.

### Cómo registro un cobro en STELLA

También se pregunta como: ¿Cómo registro que me pagaron? En STELLA el cobro baja el saldo de la cuenta.

1. Como Admin, abrí Cuentas Corrientes.
2. Tocá ➕ Agregar Movimiento. El cuadro es Nuevo Movimiento - Cuenta Corriente.
3. En Tipo elegí Cliente o Proveedor. En Seleccionar, la persona.
4. Importe (valor del trabajo) es el cargo. Haber (pago del cliente) es lo que pagó. Podés cargar solo el haber si ya existía la deuda.
5. Método de Pago: Efectivo, Tarjeta, Cheque, Transferencia u Otro.
6. Tocá Guardar.

Resultado: STELLA muestra Importe, Debe, Haber y Saldo. El texto de la pantalla aclara que el debe se calcula sumando trabajos anteriores. Un trabajo nuevo con precio mayor que cero ya deja su cargo; el haber es el pago.

Nota: si no elegís persona, dice Selecciona un Cliente o Selecciona un Proveedor.

### Cómo veo lo que me deben en STELLA

También se pregunta como: ¿Dónde veo lo que me deben? En STELLA esa deuda está en Cuentas Corrientes, columna Saldo, y en Dashboard, tarjeta Pendiente. Ingresos, en el dashboard, es lo ya cobrado en el período, no la deuda.

1. Abrí Cuentas Corrientes. La tabla tiene N° Ficha, Nombre, Tipo y Saldo.
2. El botón Todos filtra Cliente o Proveedor.
3. El buscador dice Buscar por cliente, proveedor o número de ficha….
4. Doble clic en la fila (Admin) abre Detalle, la ficha de esa cuenta.
5. En Dashboard, la tarjeta Pendiente muestra el saldo pendiente de cobro.

Resultado: el saldo de la fila es lo que queda. En el dashboard, Ingresos es lo cobrado en el período.

Nota: la lista pagina de a 100. Si no está, limpiá la búsqueda y el filtro de tipo.

### Cómo imprimo un ticket en STELLA

1. En Trabajos, seleccioná la orden.
2. ⚙️ Acciones y 🎫 Generar Ticket, o en Detalle el botón 🎫 Generar Ticket.
3. En Ticket de Trabajo elegí 👁️ Preview / Imprimir o 📄 Exportar PDF.

Resultado: la vista previa se llama Preview — Ticket. Si exportás, STELLA dice OK PDF guardado y pide dónde dejar el archivo.

Nota: sin fila elegida, Acciones dice Selecciona una fila primero.

### Cómo imprimo una comanda en STELLA

1. En Trabajos de STELLA, seleccioná la orden.
2. ⚙️ Acciones y 📋 Generar Comanda, o en Detalle 📋 Generar Comanda.
3. En Comanda de Trabajo usá Preview / Imprimir o Exportar PDF.

Resultado: la comanda lleva paciente, odontólogo, trabajo, color y pieza. La vista previa es Preview de la comanda. El PDF confirma OK PDF guardado.

Nota: hace falta una fila seleccionada. Consultor ve el botón, pero si la fila no queda marcada el aviso es Selecciona una fila primero.

### Cómo saco un comprobante de pago en STELLA

1. En Cuentas Corrientes, seleccioná el movimiento.
2. ⚙️ Acciones y 🎫 Generar Comprobante de Pago. Esa opción solo aparece para Admin con una fila elegida.
3. En Comprobante de Pago usá 👁️ Preview / Imprimir o 📄 Exportar PDF.

Resultado: la vista previa se llama Preview — Comprobante de Pago. Exportar confirma OK PDF guardado.

Nota: sin fila, el menú de acciones no ofrece el comprobante: solo descargar, exportar o imprimir la tabla.

### Cómo reabro un documento ya generado en STELLA

1. En el Detalle del trabajo, tocá 📚 Ver historial.
2. El cuadro Historial de Documentos lista Tipo (ticket, comanda o comprobante), Archivo, Fecha y N° Ficha.
3. Elegí la fila y tocá 👁️ Abrir o 💾 Descargar. Doble clic también descarga.

Resultado: se abre o se guarda el PDF que ya se había generado para esa orden.

Nota: si no hay nada, dice Sin documentos guardados para este trabajo. Admin puede 🗑️ Eliminar un documento de esa lista.

### Cómo miro el dashboard de STELLA

1. Abrí Dashboard. Es la primera pantalla después de entrar.
2. Período: Hoy, Ayer, Última semana, Último mes, Últimos 3 meses, Último año o Personalizado. Después Aplicar.
3. Comparar puede ser Sin comparación, Período anterior, Mismo período año pasado o Personalizado.
4. Las tarjetas son Ingresos, Pendiente, Tiempo Entrega y Trabajos. Un clic explica qué suma cada una.
5. Más abajo están Evolución de Ingresos, Top Clientes, Top Odontólogos, Top Productos, el rubro y los trabajos urgentes.

Resultado: Pendiente es el saldo que falta cobrar. Ingresos es lo cobrado en el período. Si no hay urgentes, dice Sin trabajos urgentes.

Nota: Refrescar arranca en Manual. También hay 1 min, 5 min, 10 min y 30 min. Si los números no se mueven, tocá Aplicar.

### Cómo cierro el mes en STELLA

1. Abrí Cuentas Corrientes y la pestaña Cierre de Mes.
2. Elegí el mes y el año. Tocá Actualizar.
3. Revisá Personas con Movimiento, Trabajos del Mes y Movimientos de la Cuenta.
4. Como Admin, tocá 🔒 Cerrar Mes y confirmá. El texto dice que los datos del período quedan protegidos.
5. 📥 Descargar Informe de Mes baja el informe. 🔓 Reabrir Mes vuelve a dejar el período modificable, también con confirmación.

Resultado: el estado pasa a Mes Cerrado y figura quién lo cerró. Reabrir dice que el mes quedó reabierto.

Nota: los movimientos en gris están fuera del período y no entran en el saldo. Consultor ve la pestaña; cerrar y reabrir no hacen nada si no sos Admin.

### Cómo exporto a Excel en STELLA

1. En Clientes, Proveedores, Productos, Trabajos o Cuentas Corrientes, abrí ⚙️ Acciones o, en trabajos, 📤 Importar/Exportar.
2. Elegí 📥 Descargar Excel o 📄 Exportar CSV/JSON.
3. En el cuadro Guardar Excel indicá el nombre y aceptá.

Resultado: STELLA dice OK Archivo descargado y muestra dónde quedó. En el detalle de un trabajo también está 📥 Exportar Excel.

Nota: si la exportación no tiene filas, puede decir No hay datos para exportar. Imprimir abre Vista Previa de la tabla, no un PDF.

### Cómo importo una planilla en STELLA

1. Como Admin, en el módulo que corresponda, elegí 📤 Importar o 📤 Importar Excel.
2. El cuadro se llama Importar Clientes, Importar Trabajos o el del módulo que abriste.
3. Abrí el archivo. Si el tipo no sirve, dice Formato no soportado.
4. Asigná las columnas. STELLA avisa si falta una obligatoria: La columna '…' es obligatoria.
5. Confirmá Se van a importar N registros.

Resultado: al terminar dice Importación Completada. Conviene Crear Backup Ahora en Configuración antes de importar.

Nota: No hay archivo cargado o No se encontraron datos para importar frenan el proceso. En trabajos, el estado tiene que ser en_proceso, terminado o cancelado.

### Cómo hago una copia de seguridad en STELLA

1. Entrá como Admin y abrí Configuración.
2. Abrí la sección Backups. El texto dice que los respaldos locales se crean al iniciar STELLA.
3. Tocá Crear Backup Ahora.
4. El renglón de último backup deja de decir Cargando… y muestra el resultado.

Resultado: queda una copia de la base en esa computadora, además de la que STELLA hace sola al abrir.

Nota: Consultor no ve Backups ni Mantenimiento. Sí ve tema, atajos y actualizaciones.

### Cómo restauro una copia en STELLA

1. En Configuración, sección Backups, tocá 📂 Ver Backups.
2. Si no hay nada, dice No hay backups disponibles.
3. Elegí una copia y tocá ↩️ Restaurar seleccionado.
4. Confirmá. Restaurar reemplaza los datos actuales por los de esa copia.

Resultado: STELLA vuelve al estado de la copia elegida.

Nota: antes de restaurar, hacé Crear Backup Ahora del estado de hoy, por si la copia vieja no era la que buscabas. 📄 Abrir carpeta de logs abre los registros; no hace falta buscar la carpeta a mano.

### Cómo subo la copia a la nube en STELLA

1. En Backups, mirá el estado de la nube.
2. Si dice No conectado, tocá 🔗 Conectar a la nube. STELLA abre el navegador y espera la autorización.
3. Cuando responde, el aviso es Conectado a la nube correctamente y el estado queda Conectado, con la última sync.
4. ☁️ Subir ahora manda la copia. 📂 Restaurar desde la nube lista las copias de afuera. Subir automáticamente queda disponible recién conectado.

Resultado: la copia queda fuera de la computadora y se puede traer de nuevo desde esa lista.

Nota: Backup a Google Drive deshabilitado, No configurado, Error al iniciar autenticación o Tiempo de espera agotado. Intentá de nuevo. Si el estado dice API no disponible, STELLA no está llegando a su propio servicio.

### Cómo actualizo STELLA

1. Abrí Configuración y la sección Actualizaciones.
2. Ahí figura Versión actual. Tocá 🔍 Buscar actualizaciones.
3. Si hay una más nueva, pregunta ¿Descargar e instalar ahora?.
4. El cuadro Actualizando STELLA muestra la descarga. Después: La actualización se descargó correctamente y pregunta si continuar. STELLA se cierra, instala y vuelve a abrir. El aviso dice que la base no se modifica.

Resultado: al entrar de nuevo, Versión actual es la nueva. Si ya estabas al día, dice Ya tenés la última versión de STELLA.

Nota: No se pudo verificar actualizaciones o No se pudo descargar la actualización piden conexión. No se pudo iniciar la instalación aparece si el instalador no arranca. Hacé una copia antes.

### Cómo cambio el tema y los atajos en STELLA

1. El tema también se cambia en el ingreso, con 🌙 Tema oscuro o ☀️ Tema claro.
2. Adentro, Configuración, Tema de la aplicación, el botón Oscuro o Claro. Mientras aplica dice Aplicando….
3. En Atajos de teclado, el lápiz de una fila abre Editar atajo. STELLA dice Presioná la nueva combinación de teclas….
4. 🔄 Restablecer valores por defecto vuelve a Ctrl+N (nuevo), Ctrl+F (buscar), Ctrl+S (guardar), F5 (recargar) y Escape (minimizar).

Resultado: el tema queda para la próxima vez. El atajo nuevo se usa en las tablas que lo tienen (alta, búsqueda, guardado y recarga).

Nota: si la combinación no se acepta, el cuadro de atajo avisa y no la guarda.

### Qué puede hacer cada rol en STELLA

1. La cuenta Admin abre Laboratorio RioDent - Admin: alta, edición, borrado, backups, nube y mantenimiento.
2. Cualquier otro rol abre Laboratorio RioDent - Consulta. No aparecen ➕ Agregar ni 🗑️ Eliminar.
3. En Clientes y Productos la tabla del consultor no se edita.
4. Cerrar sesión pregunta Cerrar STELLA (deja Recordarme) o Cambiar de usuario (vuelve al ingreso).

Resultado: el encabezado del menú muestra el rol y el usuario, por ejemplo el texto con el nombre entre corchetes.

Nota: STELLA no tiene una pantalla para crear usuarios ni para cambiar la contraseña. Esas altas no se hacen desde el menú.

## Problemas comunes y soluciones

### No me deja entrar a STELLA

También se pregunta como: No me deja entrar. En STELLA eso es el ingreso, no un cierre de sesión a mitad del trabajo.

STELLA muestra Usuario o contraseña incorrectos cuando el usuario no existe o la clave no coincide.

1. Revisá mayúsculas y el ojo de la contraseña.
2. Si el campo está vacío, antes dice Ingresá tu nombre de usuario o Ingresá tu contraseña.
3. Si dice Cuenta desactivada, la cuenta existe pero está dada de baja. No hay en la pantalla un botón para reactivarla.
4. Si dice Error del servidor (429), esperá y volvé a intentar más tarde. No reintentes seguido.

### Me dice que el servidor no está

En el ingreso, STELLA puede quedar en Conectando al servidor… y pasar a Servidor no disponible. Si tocás Ingresar igual, el cuadro Sin conexión dice No se pudo conectar a la API y pide verificar que el servidor esté corriendo.

1. Cerrá STELLA y volvé a abrirla: el programa levanta su propio servicio al arrancar.
2. Esperá a que el cartel de conexión desaparezca antes de Ingresar.
3. Si sigue, como Admin abrí Configuración, Backups, y 📄 Abrir carpeta de logs.

### STELLA no abre

Si STELLA no puede iniciar su sesión segura, muestra un mensaje y no sigue.

1. Cerrá y volvé a abrir.
2. Si el mensaje habla de permisos de la carpeta de STELLA, tenés que poder escribir en tu carpeta de usuario de Windows.
3. No borres archivos a mano para “arreglarlo”.

### No me aparecen Agregar ni Eliminar

Eso pasa cuando la cuenta no es Admin. La ventana dice Laboratorio RioDent - Consulta y el menú no muestra los botones de alta ni de borrado. En Clientes y Productos la grilla además queda bloqueada.

1. Salí con Cambiar de usuario.
2. Entrá con la cuenta Admin. Las pestañas de la pantalla de ingreso no alcanzan: el rol lo trae la cuenta.

### No aparece el cliente

También se pregunta como: No aparece el cliente. En STELLA el odontólogo está en Clientes; si la lista parece vacía, el dato puede estar en otra página o tapado por el buscador.

1. En Clientes, borrá el texto de Buscar cliente….
2. Mirá las páginas de abajo: la lista muestra 100 por vez.
3. El cartel Hay un total de N clientes dice si el dato existe y no está en esta página.
4. Si dice No se pudo actualizar. Verificá la conexión, el servicio de STELLA no respondió. Reintenta solo un par de veces y después muestra ese texto.

### No me deja cargar un trabajo

STELLA abre el aviso No hay clientes cargados. Creá primero un cliente en la sección Clientes.

1. Andá a Clientes y da de alta al odontólogo, con nombre, domicilio, celular y mail.
2. Volvé a Trabajos y tocá ➕ Agregar.
3. En Cliente / Odontólogo tiene que haber un nombre elegido. Si no, dice Seleccioná un cliente.

### Me pide completar todos los campos

En un cliente o proveedor, Completa todos los campos: faltan nombre, domicilio, celular o mail.

En un trabajo, Completa todos los campos, incluida la Fecha de Salida. Color y pieza pueden ir vacíos. El precio y la fecha no.

En un producto, Completa el campo Artículo/Tarea o Debes seleccionar un rubro.

### La fecha o el precio dan error

En Nuevo Trabajo, Formato de fecha inválido. Usa dd/mm/yyyy significa que Fecha de Salida no se leyó. El ejemplo de la pantalla es 25/12/2024.

El precio debe ser un número válido, o en productos Los precios deben ser números válidos. Probá con punto si la coma no entra en el casillero.

Un trabajo con precio mayor que cero y estado distinto de cancelado deja el cargo en la cuenta. Precio 0 no genera ese cargo.

### La lista no se actualiza

El cartel de la tabla dice No se pudo actualizar. Reintentando… y, si sigue, No se pudo actualizar. Verificá la conexión.

1. Tocá F5 o volvé a entrar al módulo.
2. Si el ingreso también decía Servidor no disponible, cerrá STELLA y abrilo de nuevo.
3. Una búsqueda o un filtro (estado, rubro, tipo de cuenta) dejan la lista corta a propósito. Limpiálos.

### El dashboard no cambia

Refrescar está en Manual hasta que elijas 1 min, 5 min, 10 min o 30 min. Los números salen del período elegido, que arranca en Último mes.

1. Cambiá Período o las fechas y tocá Aplicar.
2. Mientras carga, el botón dice Cargando… y el pie Actualizando….
3. Un clic en la tarjeta Ingresos, Pendiente, Tiempo Entrega o Trabajos explica qué está sumando.

### No se actualiza el programa

También se pregunta como: No se actualiza el programa. En STELLA el programa es la aplicación, no la grilla de una pantalla.

1. Configuración, Actualizaciones, 🔍 Buscar actualizaciones.
2. Ya tenés la última versión de STELLA significa que no hay otra publicada. El renglón dice Estás en la última versión disponible.
3. No se pudo verificar actualizaciones: no hubo conexión al publicar la búsqueda. Reintentá con internet.
4. Si la descarga falla: No se pudo descargar la actualización. Si el archivo bajó pero no instala: No se pudo iniciar la instalación.
5. La base no se toca en la actualización. Igual, Crear Backup Ahora antes de aceptar.

### La nube no conecta

En Backups el estado puede decir No conectado, No configurado, Backup a Google Drive deshabilitado, Error al iniciar autenticación, Tiempo de espera agotado o API no disponible.

1. No conectado: tocá 🔗 Conectar a la nube y terminá la autorización en el navegador. El aviso de éxito es Conectado a la nube correctamente.
2. No configurado o Backup a Google Drive deshabilitado: en esa instalación la nube no está habilitada. Las copias locales, Crear Backup Ahora y Ver Backups, siguen sirviendo.
3. Tiempo de espera agotado: volvé a tocar Conectar a la nube.

### Me dice que seleccione una fila

Generar Ticket, Generar Comanda o Editar responden Selecciona una fila primero cuando no hay orden marcada.

1. Hacé clic en la fila del listado, no solo en el buscador.
2. Con Admin, el doble clic abre Detalle directo.
3. En Cuentas Corrientes, Generar Comprobante de Pago solo entra al menú si hay una fila elegida y sos Admin.

### El mes está cerrado y no me deja corregir

En Cierre de Mes el estado Mes Cerrado dice que el período quedó protegido, y Mes Abierto dice Los datos de este período pueden modificarse.

1. Elegí el mes y el año correctos y tocá Actualizar.
2. Para volver a editar, Admin toca 🔓 Reabrir Mes y confirma. El aviso es que el mes quedó reabierto.
3. Los movimientos en gris están fuera del período y no forman parte del saldo. No son un error de suma.

### La importación de Excel falla

STELLA avisa y no importa todo a ciegas.

1. Formato no soportado o Error al leer archivo: el archivo no se pudo abrir. Usá la planilla que exportaste con Descargar Excel como modelo.
2. La columna '…' es obligatoria: falta asignar ese campo en el mapeo.
3. No hay archivo cargado o No se encontraron datos para importar: no hay filas para guardar.
4. En trabajos, un estado que no sea en_proceso, terminado o cancelado se rechaza en esa fila.
5. Si ya importaste de más, restaurá el backup que hiciste antes.

### No hay documentos para reimprimir

En Historial de Documentos, Sin documentos guardados para este trabajo significa que esa orden todavía no generó ticket, comanda o comprobante.

1. En Detalle, Generar Ticket o Generar Comanda, y exportá o imprimí para que quede registrado.
2. El comprobante de pago se genera desde Cuentas Corrientes, no desde Trabajos.
3. Imprimir del menú Acciones es la vista previa de la tabla (Vista Previa - …), no el PDF del ticket.

### Se cortó la luz

Lo que ya habías guardado está en la base de la computadora. Lo que estaba a medio escribir en un cuadro, sin Guardar, no.

1. Volvé a abrir STELLA. Al iniciar hace una copia local sola.
2. Revisá el trabajo o el movimiento: si no está, cargalo de nuevo.
3. Si la base quedó inutilizable, en Configuración, Ver Backups, restaurá una copia anterior. Eso reemplaza todo lo actual.
4. STELLA no emite factura electrónica. Un corte no deja un trámite fiscal a medias porque ese trámite no existe en el programa.

### Borré algo y no hay deshacer

STELLA no tiene un botón Deshacer.

1. Un cliente o un movimiento eliminado no vuelve solo.
2. Cancelar un trabajo saca su cargo de la cuenta. Volver a ponerlo en en_proceso o terminado puede recrear el cargo si el precio es mayor que cero.
3. Para volver atrás del todo, restaurá un backup. Antes, Crear Backup Ahora del estado actual.
4. En Historial de Documentos, Admin puede borrar un PDF guardado. Generarlo de nuevo lo vuelve a crear.

## Preguntas frecuentes

### ¿Se puede deshacer en STELLA?

No hay deshacer. Lo guardado se corrige editando la fila, o se vuelve atrás restaurando un backup desde Configuración. Restaurar pisa los datos de ahora.

### ¿Qué pasa si se corta la luz con STELLA abierto?

Queda lo último que STELLA llegó a guardar en la computadora. El formulario sin Guardar se pierde. Al volver a abrir, STELLA hace una copia local. Si la base no abre, se restaura desde Ver Backups.

### ¿STELLA hace facturas de AFIP?

No. STELLA no emite factura A, factura B ni otro comprobante electrónico. El papel del laboratorio es el ticket, la comanda y el comprobante de pago. La deuda y el cobro viven en Cuentas Corrientes.

### ¿Puedo hacer un presupuesto en STELLA?

No hay un documento llamado presupuesto. Para pasarle un precio al consultorio se puede imprimir la lista de Productos (Acciones, Imprimir) o anotar el importe en el trabajo. Imprimir un trabajo no lo autoriza ante nadie: solo muestra la orden.

### ¿Cómo entro la primera vez a STELLA?

Abrís el programa, completás el usuario y la contraseña que te dio quien administra el laboratorio, y tocás Ingresar. STELLA no muestra una clave inicial en la pantalla. Recordarme guarda la sesión 30 días en esa máquina.

### ¿Para qué son las pestañas Admin y Consultor?

Están en la pantalla de ingreso de STELLA, pero no eligen el permiso. Al validar, el programa usa el rol de la cuenta. Admin abre la ventana de administración. El resto abre Laboratorio RioDent - Consulta, sin altas ni borrados.

### ¿Qué es el cliente en STELLA?

El odontólogo o el consultorio que manda el trabajo, no el paciente. El paciente es un campo de la orden. Por eso un cliente se carga en Clientes y el paciente se escribe en Nuevo Trabajo.

### ¿STELLA tiene vehículos o patentes?

No. STELLA es de laboratorio odontológico. No hay pantalla de vehículos, dominios ni obleas. Lo equivalente al “caso” es el trabajo: orden, paciente, artículo, color y pieza.

### ¿Cuánto es el descuento de clientes en STELLA?

En Productos, el precio de cliente es el de la lista menos 15 % (el cargado por 0,85). No cliente muestra el precio sin ese descuento. Los botones Cliente / No Cliente y Noviembre / N. Noviembre eligen cuál columna estás viendo. El precio de la orden no se rellena solo: se escribe en el trabajo.

### ¿Qué estados tiene un trabajo en STELLA?

en_proceso, terminado y cancelado. El filtro del listado los muestra como En Proceso, Terminado y Cancelado, más Todos. No hay estado nuevo ni entregado en esa lista.

### ¿Al cargar un trabajo ya queda la deuda?

Sí, si el precio es mayor que cero y el estado no es cancelado. STELLA crea el movimiento en la cuenta del cliente. Un precio 0 no genera cargo. Cancelar el trabajo saca ese cargo.

### ¿Puedo imprimir sin guardar el trabajo?

El ticket y la comanda salen de una orden que ya está en la lista. Imprimir, en Acciones, es otra cosa: abre la vista previa de la tabla que estás viendo, sin crear un PDF de ticket.

### ¿Dónde quedó el PDF?

Al exportar, STELLA dice OK PDF guardado y muestra la ruta que elegiste en el cuadro de guardar. Para volver a abrirlo sin buscar el archivo, Detalle del trabajo, Ver historial, Abrir o Descargar.

### ¿Se puede reimprimir la comanda?

Sí. Si ya se generó, Ver historial la lista. Si dice Sin documentos guardados para este trabajo, hay que Generar Comanda otra vez desde el detalle.

### ¿Cómo sé cuánto produjo el mes?

Dashboard, período Último mes o Personalizado, y Aplicar. Trabajos cuenta las órdenes del período. Ingresos, lo cobrado. Para cerrar el número, Cuentas Corrientes, Cierre de Mes, y Descargar Informe de Mes.

### ¿Quién cierra el mes?

Solo Admin. El botón es Cerrar Mes, con una pregunta de confirmación. El estado pasa a Mes Cerrado. Reabrir Mes lo deja editable de nuevo. Consultor puede mirar la pestaña, no cerrarla.

### ¿Cómo hago una copia de seguridad?

Configuración, Backups, Crear Backup Ahora. Además, STELLA copia la base sola cada vez que se abre. Ver Backups lista las copias y Restaurar seleccionado vuelve a una de ellas.

### ¿Restaurar borra lo que cargué hoy?

Sí. Restaurar reemplaza los datos actuales por los de la copia. Conviene Crear Backup Ahora antes, para no perder el día si elegiste la copia equivocada.

### ¿La nube es obligatoria?

No. Si el estado dice No configurado o Backup a Google Drive deshabilitado, STELLA igual trabaja y guarda copias locales. Conectar a la nube es optativo y abre el navegador para autorizar.

### ¿Cómo actualizo sin perder los datos?

Buscar actualizaciones, aceptar la descarga y confirmar la instalación. El cuadro dice que la base no se modifica. Si no hay versión nueva, el mensaje es Ya tenés la última versión de STELLA.

### ¿Funciona sin internet?

El trabajo de todos los días (clientes, órdenes, cuentas) queda en la computadora. Internet hace falta para buscar actualizaciones y para la nube. Si el ingreso dice Servidor no disponible, el problema es el servicio de STELLA en esa máquina, no la web.

### ¿Puedo usar STELLA en otra computadora del laboratorio?

Cada instalación guarda su base en esa computadora. No hay en el menú un botón para elegir otra máquina. Las copias se pasan restaurando un backup o, si la nube está conectada, desde Restaurar desde la nube.

### ¿Qué miro a la mañana?

Dashboard: Pendiente (lo que falta cobrar), Trabajos del período y la lista de urgentes. Si dice Sin trabajos urgentes, no hay órdenes marcadas como atrasadas. Después, Trabajos con el filtro En Proceso.

### ¿Cómo busco la corona de un paciente?

Trabajos, Buscar trabajo…, el nombre del paciente o el número de orden. El filtro de estado no tiene que estar dejando afuera Terminado o Cancelado. Volvé a Todos si la lista parece vacía.

### ¿Puedo cambiar el color o la pieza después?

Sí, mientras seas Admin. Abrí el detalle de la orden, desplegá el artículo y editá Color, N° Pieza, Estado o Precio $. Guardar en esa ficha. Reimprimí la comanda si el técnico ya tenía la vieja.

### ¿Qué pasa si pongo el precio en cero?

En un trabajo que ya tenía precio, dejarlo en 0 saca el cargo de la cuenta corriente. STELLA pide confirmar esa anulación. Si el alta ya era con precio 0, no se crea cargo.

### ¿Se pueden cargar dos artículos en la misma orden?

Sí. El detalle de la orden lista los artículos de ese número, con precio y estado cada uno. Al dar de alta, el mismo N° Orden puede repetirse: STELLA numera los artículos de esa orden.

### ¿Cómo saco la lista de precios en papel?

Productos, Acciones, Imprimir. Se abre Vista Previa de la tabla, con el precio que esté mostrando Cliente o No Cliente y el mes elegido. Descargar Excel deja el mismo listado en un archivo.

### ¿El consultor puede facturar o cobrar?

No. En la ventana de consulta no están Agregar Movimiento ni Eliminar. Tampoco el alta de trabajos. Para cobrar hace falta la cuenta Admin.

### ¿Por qué la tabla de clientes no se puede tocar?

Porque entraste como Consultor. STELLA desactiva esa grilla y la de productos. Admin sí edita con doble clic y confirma el cambio.

### ¿Cada cuánto se respalda solo?

Cada vez que se abre STELLA, según el texto de Configuración, Backups. Crear Backup Ahora suma una copia en el momento, por ejemplo antes de importar o de cerrar el mes.

### ¿Dónde están los atajos?

Configuración, Atajos de teclado. De fábrica: Ctrl+N nuevo registro, Ctrl+F buscar, Ctrl+S guardar, F5 recargar, Escape minimizar. El lápiz cambia la combinación. Restablecer valores por defecto los vuelve atrás.

### ¿Cómo pongo el tema claro?

En el ingreso, el botón Tema claro / Tema oscuro. Adentro, Configuración, Tema de la aplicación. El cambio dice Aplicando… y queda guardado.

### ¿Qué es el número de ficha?

En Cuentas Corrientes la primera columna es N° Ficha. En el historial de documentos también hay N° Ficha, junto al tipo de PDF. Sirve para encontrar el movimiento o el papel de esa orden. Se busca desde el casillero Buscar por cliente, proveedor o número de ficha….

### ¿Puedo importar la planilla vieja?

Sí, como Admin, con Importar o Importar Excel en clientes, productos, proveedores, trabajos o cuentas. STELLA pide confirmar la cantidad de registros. Si el formato no sirve, dice Formato no soportado. Hacé un backup antes.

### ¿STELLA avisa si me equivoqué de cliente en la orden?

No corrige solo. En Detalle podés cambiar Odontólogo y Paciente y tocar Guardar cambios. El cliente del alta es el que quedó elegido en Cliente / Odontólogo. Si el cargo fue a otra cuenta, revisá Cuentas Corrientes.

### ¿Por qué dice que hay que seleccionar un rubro?

En Nuevo Producto el rubro arranca en -- Selecciona un rubro --. Sin elegir uno, Guardar responde Debes seleccionar un rubro. Si el rubro no existe, primero ➕ Rubro en Productos.

### ¿La sesión se cierra sola?

Con Recordarme, STELLA vuelve a entrar durante 30 días en esa computadora. Sin esa casilla, la próxima vez pide usuario y contraseña. Cerrar STELLA deja la sesión recordada. Cambiar de usuario la borra.

### ¿Qué hago si dice error del servidor 429?

Esperá y probá de nuevo más tarde. STELLA muestra Error del servidor (429) cuando hubo demasiados ingresos fallidos seguidos. No sirve cambiar de pestaña Admin o Consultor: eso no reinicia el intento.

### ¿Puedo ver solo mis trabajos?

La pantalla de consulta muestra el listado de trabajos del laboratorio, no un filtro por odontólogo automático. Para ver uno, usá Buscar trabajo…. Admin y Consultor no tienen en el menú un rol Odontólogo con órdenes propias.

### ¿Cómo salgo sin perder la sesión?

Cerrar Sesión, y en el cuadro Cerrar sesión elegí Cerrar STELLA. Cancelar no hace nada. Cambiar de usuario sí pide la clave la próxima vez.

### ¿El precio con coma funciona?

En cuentas, los montos aceptan coma decimal. En el alta de producto el casillero a veces no deja la coma: usá punto. Si igual falla, el mensaje es Los precios deben ser números válidos o El precio debe ser un número válido.

### ¿Qué miro si dos personas cargan a la vez?

STELLA en una computadora guarda todo en la misma base local. F5 recarga la lista. No hay en el menú un modo de varias cajas al mismo tiempo. Otra computadora no ve estos datos salvo que le restaures una copia.

### ¿Cómo sé la versión que tengo?

Configuración, Actualizaciones, el renglón Versión actual. Buscar actualizaciones dice si esa es la última o si hay otra para descargar.

# 12. Preguntas frecuentes

**¿Cuál es la contraseña por defecto de STELLA?**
No existe contraseña genérica: el administrador del laboratorio crea el
usuario y entrega la contraseña de cada persona. Nunca se comparte una clave
común entre usuarios.

**¿Cómo cambio mi contraseña?**
El administrador la regenera desde la gestión de usuarios. Contactá al
administrador del laboratorio.

**¿Puedo entrar desde otra computadora?**
Sí. STELLA trabaja en red: una computadora corre la Estación Maestra (con el
servidor) y las demás se conectan como Estaciones de Consulta.

**¿Qué diferencia hay entre Estación Maestra y Estación de Consulta?**
La Estación Maestra ejecuta el servidor de datos y la interfaz completa de
administración. La Estación de Consulta es solo interfaz: se conecta a la
maestra y opera con los mismos datos y permisos.

**¿Cuánto dura la sesión con "Recordarme"?**
30 días en esa computadora. Después volvés a ingresar tu contraseña.

**¿Cuánto descuento tienen los clientes?**
15 %: el precio de cliente es el precio base multiplicado por 0,85. Quién
tiene descuento lo define la lista de precio de su ficha.

**¿Qué pasa si elimino un cliente con trabajos?**
El cliente queda inactivo y desaparece de las búsquedas, pero sus trabajos y
su cuenta corriente se conservan.

**¿Cómo sé en qué estado está un trabajo?**
En la tabla Trabajos (filtro por estado) o en la ficha del trabajo; el
dashboard también muestra los activos y los terminados.

**No puedo avanzar un trabajo de estado ¿por qué?**
Verificá tu rol: solo Admin y Recepción modifican estados; los consultores
son de solo lectura.

**¿Los precios aceptan coma decimal?**
Sí. "1500,50" y "1500.50" se interpretan igual, tanto en el alta como en la
edición en la grilla y en la importación de Excel.

**¿Cómo calculo lo que me deben?**
Mirá el saldo de la cuenta corriente (debe − haber) en Ctas. Ctes., la ficha
del cliente o la tarjeta "Por cobrar" del dashboard.

**¿Se cuentan dos veces los saldos con varios movimientos?**
No. El indicador del dashboard toma un solo saldo final por titular.

**¿Qué es la pieza 21 o 46?**
Es la notación FDI internacional de los dientes; ver el glosario (§14).
STELLA acepta piezas del 11 al 58.

**¿Puedo deshacer un movimiento borrado por error?**
No hay deshacer: restaurá un backup anterior desde Configuración → Backups,
o volvé a cargar el movimiento. Por eso conviene crear un backup antes de
operaciones grandes.

**¿Dónde quedan los archivos de respaldo?**
En la carpeta de datos de STELLA en la máquina. La sección Backups los lista
con fecha; si conectaste la nube, también aparecen las copias subidas.

**¿Cada cuánto se respalda solo?**
Cada vez que se inicia la aplicación, además de los respaldos manuales que
crees con "Crear Backup Ahora".

**¿Cómo exporto datos a Excel?**
Todos los módulos con tabla tienen **Descargar** / **Descargar Excel** en la
barra de acciones, y el dashboard tiene **Exportar**.

**¿Se pueden importar mis planillas actuales?**
Sí: clientes, proveedores, productos y trabajos admiten importación desde
Excel con detección automática de columnas, y rechazan fila por fila los
datos inválidos sin frenar el resto.

**¿STELLA funciona sin internet?**
Sí: la base de datos es local. Solo necesitás conexión para la nube (respaldo
opcional) y para descargar actualizaciones.

**¿Cómo cambio a tema claro?**
Configuración → Tema de la aplicación → toggle claro/oscuro.

**¿Cómo reinicio todo?**
No hay "reiniciar todo" en el menú: restaurá un backup viejo desde
Configuración → Backups → Ver Backups → Restaurar.

**¿Puedo ver solo mis trabajos?**
Sí: si tu rol es Odontólogo, STELLA muestra únicamente las órdenes que
llevás vos. Los demás roles ven todo lo que su permiso alcance.

**¿Qué pasa si cargué el mismo trabajo dos veces?**
Cada trabajo tiene número de orden único. Localizá el duplicado en la tabla,
abrí su ficha y eliminalo (Acciones → Eliminar) con su confirmación; si
tenía cargo en cuenta corriente, se retira junto con el trabajo.

**¿Cómo encuentro un trabajo de hace tres meses?**
Usá la búsqueda de la tabla (número de orden, paciente o cliente) y el filtro
por estado o fecha; si necesitás exportarlo, Descargar Excel con esos filtros
aplicados.

**¿Se pueden ver los trabajos cancelados?**
Sí, con el filtro de estado de la tabla: los cancelados no avanzan en el
ciclo, pero quedan registrados para consulta.

**¿Los rubros se pueden agregar o modificar?**
Los rubros vienen predefinidos (§6.1). Si necesitás incorporar uno nuevo a
tu instalación, consultá con el administrador de STELLA.

**¿Cómo sé cuánto produjo el laboratorio en el mes?**
Con el Informe mensual (§4.4): trabajos, montos, saldos y comparativa con el
mes anterior.

**¿Puedo imprimir la lista de precios para un cliente?**
Sí: Productos → Imprimir genera el listado; también podés exportarlo a Excel
con Descargar.

**¿Y si dos estaciones cargan trabajo al mismo tiempo?**
STELLA trabaja en red contra la Estación Maestra: cada alta queda registrada
al confirmar y la tabla se refresca con F5 o el botón de actualizar. Las
cargas simultáneas en distintos módulos no interfieren entre sí.

**¿El sistema avisa si un cliente supera su límite de crédito?**
El límite de crédito se carga en la ficha del cliente como referencia de
gestión (§5.3); la revisión del saldo disponible la hacés en su ficha o en
Ctas. Ctes. antes de facturar un pedido grande.

**¿Puedo cambiar el color o la pieza después de ingresado?**
Sí, hasta que el trabajo se entrega: abrí la ficha y editá cualquier campo;
los cambios quedan reflejados en la comanda al reimprimir y en el
historial.

**¿Los precios se actualizan solos?**
No: el precio base lo cargás vos en el catálogo (o lo importás). Lo que sí
se calcula solo es el precio con descuento de cliente (base × 0,85) y su
propagación a los trabajos nuevos.

**¿Y si se mojó o se perdió una comanda?**
Volvé a Historial de documentos, ubicá el trabajo y reimprimila: el
documento no se genera de nuevo con otro número, se recupera el original.

**¿Qué miro primero los lunes a la mañana?**
Tres números del dashboard: *Por cobrar* (cuánto hay que recuperar),
*Activos* (cuánta producción está en la mesa) y *Terminados* (qué está
esperando entrega). Si los tres están bajos, el problema no es contable:
es de ingreso.

**¿Puedo operar solo con el teclado?**
Sí: los atajos son reasignables (§3.3) y las tablas se recorren con las
flechas; la búsqueda del módulo se enfoca con el atajo configurado para
"buscar".

---

# 13. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| La aplicación no abre | Falta una dependencia o instalación incompleta | Reinstalá desde el instalador oficial; revisá la carpeta de logs |
| "Credenciales inválidas" | Contraseña incorrecta o usuario inexistente | Verificá mayúsculas; pedí al administrador que reenvíe tu usuario |
| Entra pero no ve todos los módulos | Tu rol es de solo lectura o parcial | Revisá qué rol tenés con el administrador (§2.4) |
| Los datos no se guardan | Sin permisos de escritura en la carpeta de datos | Ejecutá STELLA con un usuario con permisos normales de Windows |
| La tabla está vacía aunque hay datos | Filtro activo o búsqueda con texto | Limpiá la búsqueda y los filtros de la cabecera |
| La importación de Excel falla | Formato no soportado o columnas sin reconocer | Usá .xlsx; descargá la plantilla con "Descargar" y completala |
| Algunas filas de la importación se rechazan | Cliente inexistente, estado inválido o precio negativo | Mirá el detalle por fila del resumen y corregí esas filas en la planilla |
| El precio con coma marca error en versiones viejas | Versión anterior a la 1.6.4 | Actualizá la aplicación |
| La impresión sale mal | Vista previa mal configurada | Revisá márgenes y escala en la vista previa antes de imprimir |
| No encuentro un documento impreso | Se perdió el papel | Abrí Historial de documentos y reimprimilo |
| Falta la opción de nube en Backups | Credencial de la aplicación no configurada en esta máquina | El administrador debe copiar el archivo de credencial a la carpeta de configuración |
| Error al restaurar un backup | Archivo corrupto o incompatible | Probá con otra copia de la lista; contactá soporte con la carpeta de logs |
| La app va lenta con muchas filas | Tabla muy grande sin filtrar | Usá búsqueda y paginación; el módulo cachea las consultas durante unos minutos |
| Se cerró la sesión estando trabajando | La sesión venció | Volvé a iniciar sesión; marcá Recordarme si la máquina es personal |
| El dashboard no refleja lo último cargado | Métricas sin recalcular | Tocá **Actualizar** de la cabecera del dashboard |
| El trabajo no aparece en Terminados | Filtro de estado activo | Limpiá el filtro o elegí "Todos los estados" |
| La Estación de Consulta no conecta | Estación Maestra apagada o red caída | Encendé la maestra y verificá que ambas estén en la misma red |
| Tras actualizar cambió algo de la interfaz | Nueva versión instalada | Revisá el aviso de versión y las novedades del changelog |
| Se mezclan datos de dos clientes parecidos | Carga con autocompletado mal elegido | Verificá el número de orden en la ficha; corregí el cliente desde la ficha antes de la entrega |

**Qué hacer ante cualquier problema:** 1) anotá el mensaje de error exacto,
2) abrí Configuración → Abrir carpeta de logs y ubicá `stella.log`, 3) no
borres nada ni restaures sin consultar, 4) contactá al administrador o al
soporte con esa información.

---

# 14. Glosario

**Atache.** Sistema de retención mecánica que fija una prótesis removible a
los dientes o implantes.

**Cancelado.** Estado de un trabajo anulado; no avanza en el ciclo de vida.

**Carilla.** Restauración estética delantera que se pega sobre la cara
visible del diente, tallada en cerámica o resina.

**Cerámica estratificada (Ceramage).** Técnica de restauraciones capa a capa
imitando el esmalte natural; rubro de productos propio de STELLA.

**Colada.** Proceso de vertido de metal fundido en el molde del modelo para
obtener una estructura protésica.

**Comanda.** Documento impreso con el detalle del trabajo para la mesa del
técnico: paciente, pieza, color e indicaciones.

**Corona.** Restauración que cubre todo el diente (la "funda" del tooth):
cerámica, metal o híbrida según el caso.

**Cuenta corriente.** Registro de deudas y haberes de un cliente o proveedor
con el laboratorio.

**Dashboard.** Pantalla inicial con métricas y gráficos del laboratorio.

**Debe.** Movimiento que incrementa lo que el titular le debe al laboratorio
(un trabajo facturado).

**Encía artificial.** Componente acrílico rosado de prótesis que imita la
encía natural, típico en híbridas.

**Estación de Consulta.** Computadora que corre solo la interfaz de STELLA y
se conecta a la Estación Maestra.

**Estación Maestra.** Computadora que ejecuta el servidor de datos y la
interfaz completa de administración.

**FDI (notación internacional).** Sistema de numeración de dientes de dos
dígitos: 11–18 (incisivo central superior derecho) hasta 48, pasando por
cuadrantes 2, 3 y 4; STELLA admite del 11 al 58. Ejemplos: 11 = incisivo
central superior derecho, 21 = incisivo central superior izquierdo, 36 =
primer molar inferior izquierdo, 46 = primer molar inferior derecho.

**Haber.** Movimiento que reduce la deuda: pago, anticipo o nota de crédito.

**Híbrida.** Prótesis combinada (a menudo sobre implante) con componente
metálica y estética acrílica o cerámica.

**Implante.** Estructura de titanio colocada en el hueso que reemplaza a la
raíz del diente; sobre ella se monta la prótesis.

**Incrustación.** Restauración parcial que se "encaja" dentro del diente
(inlay u onlay), en cerámica o composite.

**Modelo de yeso.** Réplica en yeso de la arcada del paciente sobre la cual
se verifica y ajusta la prótesis.

**Muñón.** Elemento (natural o de pilar) sobre el cual se cementa o atornilla
una corona.

**Orden (número de orden).** Identificador único de un trabajo ingresado.

**Paciente.** Persona atendida por el odontólogo; no confundir con el
cliente, que es el profesional o consultorio.

**Perno.** Estructura interna que refuerza una pieza antes de la restauración
definitiva.

**Pilar.** Componente (tornillo o conector) que une la prótesis con el
implante.

**Precio de cliente.** Precio base con 15 % de descuento (base × 0,85).

**Precio base.** Precio de lista del producto, sin descuentos.

**Rubro.** Categoría de agrupación de productos y proveedores (ver §6.1).

**Ticket.** Ficha impresa de ingreso de un trabajo, con número de ficha y
número de ticket únicos; puede estar activo o anulado.

**Trabajo.** Orden de fabricación de una pieza, con paciente, artículo,
pieza, color, precio y estado.

**Vita A1–D2.** Escala de colores de dientes naturales usada en odontología;
en STELLA: A1, A2, A3, A3.5, A4, B1, B2, C2, D2 y Blanco.

---

# 15. Acerca de

**STELLA — Sistema de gestión para laboratorios odontológicos**

Versión 1.6.4 · Septiembre 2026

Desarrollado por Lautaro Rodriguez para Laboratorio RioDent.

Este manual describe la operación diaria de STELLA y acompaña al software en
todas sus estaciones. Las imágenes y mensajes de la interfaz pueden variar
levemente entre versiones; consultá la versión instalada en
Configuración cuando este manual difiera de tu pantalla.

Elaborado como parte de la documentación técnica del proyecto STELLA.
