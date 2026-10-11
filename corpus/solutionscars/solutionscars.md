# SolutionsCars

Documento público para responder preguntas sobre el proyecto. Versión de la aplicación descrita: 2.3.16.

## Qué es

SolutionsCars es un programa de escritorio para el día a día de un taller mecánico, un centro de GNC o un lubricentro en Argentina. Reemplaza planillas sueltas y anotaciones en papel: el mismo sistema guarda clientes y vehículos, el stock de repuestos, los precios de los trabajos, el ingreso del auto al taller, la caja del día y los comprobantes.

El problema que resuelve SolutionsCars es que esas tareas suelen vivir en lugares distintos y se pierden vencimientos, stock o cobros. Está pensado para quien atiende el mostrador y para quien administra el taller. Puede usarse en una sola computadora o, si hace falta que varias personas trabajen a la vez, con una base compartida.

## Funcionalidades

### Ingreso y roles

SolutionsCars pide usuario y contraseña al abrir. Hay un rol de administrador y un rol de uso cotidiano. El administrador entra a Configuración; el resto del equipo trabaja en clientes, recepción, vencimientos y reportes. La primera vez que una cuenta debe renovar la clave, SolutionsCars pide una contraseña nueva antes de seguir. Si alguien se equivoca varias veces, el ingreso queda pausado un rato.

Inventario, lista de precios y facturación piden además un código numérico propio de cada usuario. Así no cualquiera que tenga la sesión abierta puede cambiar precios, stock o emitir un comprobante.

### Clientes, vehículos y proveedores

En SolutionsCars el módulo Clientes y Vehículos tiene tres pestañas: clientes, vehículos y proveedores. De cada cliente se guarda nombre, teléfono, correo, dirección, documento y condición frente al IVA. De cada vehículo, la patente (dominio), marca, modelo, año, kilometraje, datos de motor, regulador y chasis, y las fechas de vencimiento de la oblea GNC y de la prueba hidráulica.

Eso resuelve el problema de no saber a quién pertenece un auto ni cuándo vence un trámite. Un cliente no se borra si todavía tiene vehículos o comprobantes asociados. Las bajas son recuperables: el registro queda marcado y se puede restaurar.

### Inventario

El inventario de SolutionsCars lleva los productos físicos: aceites, filtros, repuestos. Cada ítem tiene un código (SKU, también se puede cargar con lector de barras), descripción, categoría, cantidad, stock mínimo, precio de costo, precio de venta, proveedor y transporte.

El problema que resuelve es quedarse sin repuesto sin enterarse, o no saber a qué precio se compró. La lista marca el stock en verde (normal), naranja (se está acabando) o rojo (hay que reponer). Se pueden ajustar precios de varios productos a la vez por porcentaje. Lo que se elimina va a una papelera y se puede restaurar. El precio de costo queda detrás del código de acceso del módulo.

### Lista de precios

La lista de precios de SolutionsCars no es el stock: son los trabajos del taller y lo que se cobra según el tipo de cliente. Viene con secciones de mecánica y GNC (frenos, embrague, cilindros, válvulas, electrónica, entre otras). Cada sección tiene columnas de precio distintas, por ejemplo público, servicio público y concesionaria.

Resuelve el problema de cotizar de memoria o con una planilla que no coincide con lo que se factura. Se pueden agregar secciones y columnas, imprimir o guardar un PDF por sección, y recuperar ítems desde una papelera. Borrar productos del inventario no vacía esta lista.

### Recepción de vehículos

La recepción de SolutionsCars se usa cuando entra un auto. Se elige cliente y vehículo, se anota el kilometraje (no puede ser menor al último registrado) y el trabajo a hacer. Después hay una inspección visual: aceites, líquidos, luces, neumáticos, frenos y otros ítems se marcan como sin revisar, bien o con atención. También se cargan niveles de líquidos.

Al generar el comprobante, SolutionsCars guarda la orden y arma un PDF. En el historial se busca por cliente, vehículo o fecha, se ve el detalle, se regenera el PDF y se cambia el estado: pendiente, en proceso, completado o cancelado. Así el taller no depende de un papel suelto para saber en qué estado quedó cada ingreso.

### Facturación

SolutionsCars emite cuatro tipos de documento: factura A, factura B, remito y presupuesto. Se elige cliente, vehículo si corresponde, condición de IVA, medio de pago (efectivo, transferencia, débito, crédito o QR) y quién atendió. Los ítems salen del inventario o se escriben a mano (descripción y precio); los escritos a mano no descuentan stock.

Guardar una factura A o B descuenta stock y, si la facturación electrónica está activa, pide la autorización fiscal. La factura A discrimina IVA: el precio del ítem es neto y se suma el impuesto. La factura B toma el precio del ítem como precio final, con el IVA ya incluido, para que el total que ve el cliente no crezca de más. Remitos y presupuestos no llevan IVA.

Imprimir arma un PDF para mostrar o probar, sin guardar ni autorizar. Guardar PDF solo deja el archivo en la computadora. El historial filtra por cliente, vehículo, categoría y período. Si se elimina un documento con productos de stock, la mercadería vuelve al inventario. Borrar en SolutionsCars una factura que ya fue autorizada no la anula ante el fisco: hay que hacer el trámite legal correspondiente con un contador.

### Caja y planilla diaria

La caja de SolutionsCars está en Facturación, en la pestaña Caja. Es la planilla del día: ingresos y egresos con entidad, concepto, monto, medio de pago y categoría (cobranza, adelanto, servicios, proveedores, impuestos, varios). Arriba se ve el total de ingresos, egresos y el balance.

Al cerrar la jornada, SolutionsCars muestra un resumen y pasa los movimientos a las transacciones de caja. Se puede reabrir una planilla del mismo día si hay que corregir algo, siempre que no haya otra abierta para esa fecha. Hay historial de planillas cerradas y un listado de movimientos con filtros.

### Vencimientos

SolutionsCars agrupa los vehículos según la oblea GNC y la prueba hidráulica: vencidos, los de esta semana y los de los próximos días. Cada tarjeta muestra dominio, modelo, cliente, teléfono, tipo de vencimiento y cuántos días faltan o pasaron.

El problema es perder clientes que tenían que volver a hacer el trámite. Desde cada tarjeta se abre WhatsApp con un mensaje listo o se previsualiza un correo antes de enviarlo. Cuántos días antes aparece cada alerta se ajusta en Configuración.

### Reportes

Los reportes de SolutionsCars muestran de un vistazo cuántos clientes, vehículos, repuestos, productos con stock bajo y órdenes hay. El balance se calcula por día, mes o año (ingresos, egresos y diferencia). Se exporta a Excel el balance del período, el inventario completo o los clientes con sus vehículos y vencimientos. Los archivos quedan en la carpeta de documentos del programa.

### Configuración del taller

Configuración en SolutionsCars es solo para el administrador. Ahí se cargan nombre del taller, razón social, dirección, teléfono, ingresos brutos, inicio de actividades y un lema que sale en el PDF fiscal. También están los días de alerta de oblea, prueba hidráulica y certificado fiscal; el punto de venta y el modo de facturación electrónica (prueba o producción); las copias de la base; la copia en la nube; y la búsqueda de actualizaciones del programa.

### Copias de seguridad y actualizaciones

SolutionsCars puede hacer una copia de la base en el momento o de forma automática a una hora elegida. Esas copias se listan, se restauran o se borran desde Configuración. Si se conecta una cuenta de Google Drive, cada backup puede subirse a la nube y restaurarse desde ahí.

Desde el mismo lugar se busca si hay una versión nueva. Si el administrador acepta, SolutionsCars descarga el instalador, se cierra, instala y al volver a abrir avisa si la versión quedó aplicada o hay que reintentar.

## Cómo se usa

### Entrar y moverse

1. Abrir SolutionsCars. A la izquierda está el logo; a la derecha, usuario y contraseña.
2. Iniciar sesión. Si el programa pide cambiar la contraseña, definir una nueva y confirmarla.
3. En Inicio hay tarjetas a cada módulo y, a un costado, la actividad reciente.
4. El menú lateral lleva a Inicio, Clientes y Vehículos, Inventario, Lista de Precios, Recepción, Facturación, Vencimientos, Reportes y Configuración.
5. F5 recarga la pantalla actual. Ctrl+S guarda cuando la pantalla lo permite.
6. Salir ofrece cerrar la sesión o cerrar el programa.

### Cargar un cliente y su auto

1. En SolutionsCars abrir Clientes y Vehículos.
2. Completar nombre (obligatorio) y el resto de los datos, incluida la condición frente al IVA, y guardar.
3. Pasar a Vehículos, elegir ese cliente y cargar dominio, marca, modelo, kilometraje y vencimientos.
4. Guardar. Desde la ficha del cliente se puede desplegar la lista de sus vehículos.
5. En Proveedores, el nombre y el alias son obligatorios.

### Dar de alta un repuesto

1. Entrar a Inventario en SolutionsCars e ingresar el código de acceso.
2. Completar SKU, descripción, categoría, cantidades y precios, y guardar.
3. Para reponer o corregir, usar el lápiz de la fila. Para sacar un producto del uso diario, el tacho lo manda a la papelera.
4. Ajustar precios elige categoría o búsqueda, los productos, si sube o baja, y el porcentaje.

### Recibir un vehículo

1. En Recepción de SolutionsCars elegir cliente y vehículo.
2. Anotar kilometraje y el trabajo.
3. Ir marcando cada ítem de la inspección (un toque: bien; otro: requiere atención; otro: sin revisar) y los niveles de líquidos.
4. Generar el comprobante PDF y elegir dónde guardarlo.
5. En Comprobantes generados, pasar la orden de pendiente a en proceso y después a completado.

### Hacer un presupuesto o una factura

1. Entrar a Facturación en SolutionsCars con el código de acceso.
2. Elegir tipo: presupuesto para cotizar, remito para entregar sin facturar todavía, factura A para responsable inscripto o factura B para consumidor final.
3. Elegir cliente, vehículo si hace falta, medio de pago y quien atendió.
4. Agregar productos del inventario o un ítem escrito a mano, con cantidad y categoría (repuestos, GNC, reparaciones o lubricentro).
5. Imprimir si solo hay que mostrarlo. Guardar cuando el comprobante tiene que quedar registrado. En factura A o B, Guardar es el paso que descuenta stock y busca la autorización fiscal.
6. En Historial, filtrar el período para ver totales.

### Cerrar la caja

1. En Facturación de SolutionsCars abrir la pestaña Caja.
2. Si no hay planilla del día, abrirla.
3. Cargar ingresos y egresos a medida que ocurren.
4. Al terminar la jornada, cerrar la planilla y confirmar el resumen.
5. Los movimientos también se consultan con filtro de medio de pago, tipo y fechas.

### Avisar un vencimiento

1. Abrir Vencimientos en SolutionsCars.
2. Revisar vencidos y los que caen pronto.
3. Usar WhatsApp o el correo de la tarjeta. El mensaje ya incluye el trámite, el vehículo y los días.
4. Si hace falta más o menos anticipación, el administrador lo cambia en Configuración, en alertas.

### Sacar un balance

1. En Reportes de SolutionsCars elegir día, mes o año y calcular.
2. Exportar el balance, el inventario o los clientes a Excel.
3. El archivo queda en la carpeta de documentos del programa.

## Tecnologías

SolutionsCars está escrito en Python (3.10 o superior; la integración continua usa 3.12) porque todo el producto, pantalla y reglas de negocio, vive en un solo lenguaje fácil de mantener en un taller chico.

La interfaz usa Flet 0.26, un marco de Python apoyado en Flutter. Se eligió para una aplicación de escritorio con un solo código, sin armar un sitio web aparte. En pantallas angostas el menú lateral muestra solo íconos para dejar más lugar a las listas.

Los datos usan SQLAlchemy 2. En una sola PC, SQLite evita instalar un servidor. Si varias computadoras tienen que compartir la información, se puede usar PostgreSQL. Los cambios de estructura van con migraciones Alembic, así una base vieja se actualiza al abrir el programa.

Los importes de SolutionsCars se calculan con Decimal y redondeo a dos decimales, no con números de punto flotante, para que los totales de IVA no desfasen centavos. El IVA de referencia del taller es el 21 %.

Los PDF (comprobantes de recepción, facturas y listas) se arman con ReportLab. Los Excel de reportes, con Pandas y Openpyxl. El registro de la aplicación usa loguru.

La facturación electrónica de Argentina se integra con la biblioteca pyafipws, en modo de prueba (homologación) o de producción. Los avisos al cliente usan un enlace de WhatsApp y correo por SMTP.

El instalador de Windows se genera con PyInstaller e Inno Setup, para que el taller instale SolutionsCars sin armar un entorno de Python. Los tests corren con pytest.

## Arquitectura

SolutionsCars está organizado en capas que se hablan en un solo proceso de escritorio.

La entrada es el programa principal: arma la ventana, el menú y el inicio, y decide qué pantalla mostrar. Las pantallas (vistas) dibujan formularios y listas y llaman a la lógica; no deberían inventar reglas de dinero ni de stock por su cuenta.

Los servicios concentran esa lógica: sesión de usuario, facturas, armado de PDF y Excel, vencimientos, avisos, caja, auditoría, caché de configuración, copias locales y copia en la nube, y la búsqueda de actualizaciones. Las vistas les piden el trabajo y muestran el resultado.

Los modelos describen las tablas (clientes, vehículos, inventario, órdenes, documentos, ítems, secuencias de numeración, transacciones, planillas, usuarios, configuración, lista de precios, movimientos de stock y registro de auditoría) y abren la sesión contra SQLite o PostgreSQL. Al iniciar, SolutionsCars crea o migra la base.

Hacia afuera, el programa habla con el servicio de facturación electrónica solo cuando se guarda una factura A o B, con WhatsApp y el correo cuando se avisa un vencimiento, con Google Drive si la nube está conectada, y con un manifiesto público de versiones cuando se busca una actualización. Los archivos PDF y Excel se escriben en la carpeta de documentos de la instalación.

## Seguridad y calidad

SolutionsCars no guarda contraseñas ni códigos de acceso en texto plano. El administrador es el único que abre Configuración. Inventario, lista de precios y facturación piden un código aparte. Varios intentos fallidos de ingreso pausan el acceso un tiempo.

Los textos de los formularios se validan antes de guardarse (por ejemplo kilometraje, días de alerta y punto de venta). Stock y caja de un mismo comprobante se confirman juntos: si el guardado falla, no queda a medias. Las bajas de clientes, vehículos y productos son lógicas, para poder revisarlas o restaurarlas. Cada alta, cambio o baja relevante queda en un registro de auditoría con usuario, momento y valores anteriores y nuevos.

Hay copia de la base al trabajar y se puede programar otra copia, además de subirla a la nube. Los secretos de conexión y los certificados fiscales no viajan dentro del código publicado: cada instalación los configura aparte. La facturación electrónica puede dejarse en modo de prueba hasta que el taller pase a producción.

La calidad se sostiene con una suite de tests automáticos de la aplicación, y con un control automático en cada cambio: revisión de código y tests en Linux. Los tests de facturación electrónica usan simulaciones; no emiten comprobantes reales.

## Historial

SolutionsCars llegó a la versión 2.3.16 en octubre de 2026. El núcleo (clientes, recepción con PDF, inventario, lista de precios, facturación interna, caja, vencimientos, reportes, roles y copias) ya estaba armado antes de los hitos de ese año. El manual de uso corresponde a la línea 2.x.

El 26 de septiembre de 2026 los importes pasaron a calcularse con decimales redondeados, se sumó la integración continua y se unificó el esquema de la base con migraciones. También se evitó pedir autorización fiscal si el total de una factura A o B no es mayor que cero.

El 27 de septiembre de 2026 se reforzó el circuito de facturas electrónicas que quedan pendientes de confirmación, para no duplicar un comprobante si la respuesta se corta, y la planilla diaria pasó a permitir una sola caja abierta por fecha. El respaldo de una base PostgreSQL quedó contemplado en las copias.

El 28 de septiembre de 2026 se ajustó el instalador de actualizaciones, el menú en pantallas de alrededor de 1360 píxeles, el diálogo de salir (cerrar sesión o cerrar el programa) y un error que volvía a pedir cambio de contraseña en cada arranque.

Entre el 29 de septiembre y el 2 de octubre de 2026 el PDF de factura A y factura B se alineó al comprobante fiscal (incluido el pie con el código de autorización), se permitieron ítems que no están en el inventario, y la factura B pasó a tratar el precio cargado como precio final con IVA incluido.

El 30 de septiembre de 2026 el administrador empezó a ver un aviso cuando el certificado fiscal está por vencer. El 1 de octubre se corrigió el arranque del instalador descargado. El 5 de octubre se afirmó el redondeo de la factura B y el pie del PDF. El 6 de octubre, en la 2.3.16, actualizar desde el programa cierra SolutionsCars, instala y al reabrir informa si la versión nueva quedó instalada.

En el horizonte siguen una agenda de turnos, el uso remoto por web, varios talleres en la misma instalación, un empaquetado con contenedores y una app móvil. La copia en Google Drive ya está en Configuración.

## Preguntas frecuentes

### ¿Qué es SolutionsCars?

SolutionsCars es un programa de escritorio para talleres mecánicos, GNC y lubricentros. Ordena clientes, vehículos, stock, precios de trabajos, recepción, facturas, caja y vencimientos en un solo lugar.

### ¿Sirve para facturar?

Sí. SolutionsCars hace presupuestos, remitos, factura A y factura B. Las facturas A y B pueden autorizarse de forma electrónica. Presupuesto y remito no son facturas fiscales.

### ¿Cómo hago un pedido?

En SolutionsCars el equivalente a “anotar el trabajo” es la recepción: se elige el cliente y el auto, se describe el trabajo y se genera el comprobante de ingreso. Si lo que se necesita es una cotización, se usa un presupuesto en Facturación. No es una tienda en línea de pedidos.

### ¿Qué onda con la caja?

La caja de SolutionsCars es la planilla diaria, dentro de Facturación. Se abre la del día, se cargan ingresos y egresos, y al cierre queda el balance. Sirve para saber si la jornada cerró a favor o en contra.

### ¿Anda con AFIP?

SolutionsCars puede emitir factura electrónica y guardar el código de autorización en el comprobante y en el PDF. Hay un modo de prueba y un modo de producción. El administrador elige el modo, el punto de venta y los datos del emisor en Configuración. Los certificados los instala el taller; no vienen resueltos solos con el programa.

### ¿Qué es el CAE?

El CAE es el código con el que el fisco autoriza una factura electrónica. En SolutionsCars aparece al guardar una factura A o B cuando la emisión está activa. Sin ese código, esa factura no queda autorizada.

### ¿Factura A o factura B?

En SolutionsCars la factura A es para un responsable inscripto: el IVA va discriminado y se suma al neto. La factura B es para consumidor final: el precio que se carga es el final, con el IVA ya incluido. La condición del cliente se toma de su ficha.

### ¿Puedo imprimir sin guardar?

Sí. En Facturación de SolutionsCars el botón Imprimir arma un PDF con lo que está en pantalla y no guarda el documento ni pide autorización. Sirve para mostrar un número al cliente antes de emitirlo.

### ¿Cómo entro la primera vez?

Quien instala SolutionsCars recibe un usuario administrador. En el primer ingreso el programa pide definir una contraseña propia. Las claves iniciales no se publican: las entrega quien configura el taller y hay que cambiarlas.

### ¿Qué es el código que me pide?

SolutionsCars pide un código numérico al abrir Inventario, Lista de Precios o Facturación. Es un PIN distinto de la contraseña de ingreso, para que solo personas autorizadas toquen stock, precios o comprobantes. Cada usuario tiene el suyo; lo administra el taller.

### ¿Olvidé la contraseña, qué hago?

En SolutionsCars no hay un botón público de “olvidé mi clave” en la pantalla de ingreso. Hay que pedir al administrador del taller que la restablezca.

### ¿Para qué sirve el inventario si ya tengo lista de precios?

En SolutionsCars el inventario es la mercadería física y el stock. La lista de precios es lo que se cobra por cada trabajo, con columnas según el tipo de cliente. Un aceite va al inventario; “hacer frenos” va a la lista de precios.

### ¿Cómo aviso que vence la oblea?

En Vencimientos, SolutionsCars lista obleas y pruebas hidráulicas por urgencia. En la tarjeta del vehículo se abre WhatsApp con el texto armado o se envía un correo después de ver la vista previa. El cliente necesita teléfono o correo cargado.

### ¿Se puede usar en red o en el celular?

SolutionsCars es de escritorio. En una sola PC usa una base local. Para que varias computadoras trabajen juntas hace falta una base PostgreSQL, configurada por quien administra el sistema. No tiene app móvil; el acceso remoto por web figura como idea a futuro, no como función actual.

### ¿Cómo hago una copia de seguridad?

En Configuración, el administrador de SolutionsCars puede hacer un backup en el momento, programarlo y, si conecta Google Drive, subir esas copias. Conviene una copia antes de actualizar. Restaurar reemplaza los datos actuales: hay que estar seguro antes de confirmar.

### ¿Cómo actualizo el programa?

En Configuración, SolutionsCars ofrece buscar actualizaciones. Si hay una versión nueva y se acepta, se descarga el instalador, el programa se cierra y al abrirlo de nuevo informa si quedó actualizado. Hacer una copia antes.

### ¿Qué pasa si se corta internet al facturar?

Si SolutionsCars no llega a confirmar la factura electrónica, el comprobante puede quedar pendiente en lugar de figurar como emitido. En Facturación se puede verificar ese pendiente o anularlo cuando corresponda, para no dejar la caja y el stock desfasados. Conviene revisar el mensaje en pantalla antes de intentar otra factura del mismo tipo.

### ¿Si borro una factura, se anula en AFIP?

No. Borrar el documento en SolutionsCars saca el registro local y devuelve el stock, pero no cancela una factura ya autorizada. El programa lo advierte. La anulación fiscal se hace con el comprobante que indique el contador.

### ¿Puedo cargar un ítem que no está en el stock?

Sí. En la facturación de SolutionsCars se puede escribir descripción y precio aunque el producto no exista en el inventario. Ese ítem no descuenta stock.

### ¿De qué color es el stock bajo?

En el inventario de SolutionsCars, verde es stock normal, naranja es que se está acabando y rojo es reponer. Arriba hay un resumen de cuántos productos hay en cada estado.

### ¿Quién configura el taller?

Solo el rol administrador abre Configuración en SolutionsCars: datos que salen en las facturas, alertas, facturación electrónica, copias, nube y actualizaciones. El resto del equipo usa los módulos de trabajo.

## Glosario

### SolutionsCars

Nombre del programa de gestión para taller mecánico, GNC y lubricentro. También se lo nombra SoluCars en materiales viejos de la interfaz. No es una página web ni una app de teléfono.

### GNC

Gas natural comprimido. En SolutionsCars aparece en la recepción, en categorías de facturación y en los vencimientos de oblea y prueba hidráulica de los equipos.

### Oblea

Habilitación periódica del equipo de GNC, en la práctica anual. En SolutionsCars se carga como fecha de vencimiento del vehículo y se alerta en el módulo Vencimientos. Sinónimos que usa la gente: “vto de oblea”, “la oblea del tubo”.

### Prueba hidráulica

Control del cilindro de GNC, en la práctica cada varios años. En SolutionsCars figura como P.H. o PH, junto a la oblea. Sinónimos: “la hidráulica”, “vencimiento del tubo”.

### Dominio

Patente del vehículo en SolutionsCars. Sinónimos: patente, chapa.

### SKU

Código único de un producto del inventario de SolutionsCars. Puede coincidir con un código de barras leído por escáner.

### Factura A

Comprobante de SolutionsCars para responsable inscripto, con IVA discriminado. Abreviatura en el sistema: FA.

### Factura B

Comprobante de SolutionsCars para consumidor final. El importe del ítem es precio final con IVA incluido. Abreviatura: FB.

### Remito

Documento de SolutionsCars para entregar mercadería o dejar asentado un trabajo sin emitir factura en ese momento.

### Presupuesto

Cotización de SolutionsCars. Se puede imprimir para el cliente sin convertirse solo por eso en factura.

### CAE

Código de autorización electrónico de una factura. SolutionsCars lo muestra en el comprobante cuando la factura quedó autorizada. Sinónimo coloquial: “el número de AFIP”.

### ARCA

Organismo que continuó las funciones de facturación que antes se identificaban como AFIP. En SolutionsCars los textos de comprobante y configuración pueden decir AFIP o ARCA; se refieren a la misma facturación electrónica.

### Punto de venta

Número fiscal del emisor con el que SolutionsCars numera las facturas electrónicas. Lo carga el administrador. No es la sucursal física como dirección.

### Planilla

En SolutionsCars, la caja del día: ingresos y egresos hasta el cierre. Sinónimos: planilla diaria, caja.

### PIN

Código numérico que SolutionsCars pide para Inventario, Lista de Precios y Facturación. No es la contraseña de entrar al programa. Sinónimos: código de acceso, clave del módulo.

### Papelera

En inventario y lista de precios de SolutionsCars, los ítems eliminados que todavía se pueden restaurar. Es una baja lógica, no un borrado inmediato del archivo.

### Homologación

Modo de prueba de la facturación electrónica en SolutionsCars. Los comprobantes de ese modo no son los de producción. Sinónimo en pantalla: modo prueba.

### Orden de trabajo

Registro que SolutionsCars crea al recepcionar un vehículo, con la inspección y el estado (pendiente, en proceso, completado o cancelado). Sinónimos: ingreso, comprobante de recepción.
