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
  contraseña. La sesión guardada es un token de acceso, no tu contraseña.
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

STELLA verifica al iniciar si hay una versión nueva publicada. Cuando
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

- **Cambiar STELLA**: cierra la sesión actual, borra el token recordado y
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

La creación y modificación de usuarios y contraseñas la realiza el
administrador del sistema. Si olvidaste tu contraseña o necesitás cambiar de
rol, contactá al administrador del laboratorio.

## 11.7 Actualizaciones

Las actualizaciones se notifican al iniciar la aplicación (ver §2.5). Se
recomienda no desactivarlas: cada versión corrige errores y mejora la
estabilidad.

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

**Se cerró la sesión ¿dónde quedó guardada?**
En la carpeta de configuración de STELLA, como token de acceso temporal; no
se guarda tu contraseña en texto plano.

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
| Se cerró la sesión estando trabajando | Expiró el token o cambio de contraseña | Volvé a iniciar sesión; marcá Recordarme si la máquina es personal |
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
