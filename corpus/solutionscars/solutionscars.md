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

### Hacer un presupuesto o una factura

1. Entrar a Facturación en SolutionsCars con el código de acceso.
2. Elegir tipo: presupuesto para cotizar, remito para entregar sin facturar todavía, factura A para responsable inscripto o factura B para consumidor final.
3. Elegir cliente, vehículo si hace falta, medio de pago y quien atendió.
4. Agregar productos del inventario o un ítem escrito a mano, con cantidad y categoría (repuestos, GNC, reparaciones o lubricentro).
5. Imprimir si solo hay que mostrarlo. Guardar cuando el comprobante tiene que quedar registrado. En factura A o B, Guardar es el paso que descuenta stock y busca la autorización fiscal.
6. En Historial, filtrar el período para ver totales.

### Sacar un balance

1. En Reportes de SolutionsCars elegir día, mes o año y calcular.
2. Exportar el balance, el inventario o los clientes a Excel.
3. El archivo queda en la carpeta de documentos del programa.

## Tareas paso a paso

### Cómo entro a SolutionsCars

1. Abrí SolutionsCars. A un lado está el logo y al otro los campos Usuario y Contraseña. El candado deja ver la clave.
2. Tocá Iniciar Sesión.
3. Si la cuenta debe renovar la clave, el cuadro Cambio de contraseña obligatorio pide Nueva contraseña y Confirmar contraseña. Tocá Guardar. Si no coinciden, dice Las contraseñas no coinciden.

Resultado: se abre Inicio, con tarjetas a los módulos. El menú lleva a Inicio, Clientes y Vehículos, Inventario, Lista de Precios, Recepción, Facturación, Vencimientos, Reportes y Configuración.

Nota: si faltan los dos campos, el aviso es Usuario y contraseña son requeridos. Si no coinciden, Usuario o contraseña incorrectos. Si insiste, puede decir Demasiados intentos y cuántos segundos esperar. SolutionsCars no publica usuario ni clave de fábrica.

### Cómo agrego un cliente en SolutionsCars

1. Abrí Clientes y Vehículos. La pestaña Clientes está primero.
2. Completá Nombre. También están Teléfono, Email, Dirección, DNI / CUIL y Condición frente al IVA.
3. Tocá Guardar cliente.

Resultado: el cliente queda en la lista de abajo. Si no hay ninguno, dice Sin clientes registrados.

Nota: Limpiar vacía el formulario sin guardar. Para sacarlo de la lista, SolutionsCars pregunta ¿Eliminar a …? y ofrece Cancelar o Eliminar. No se borra si todavía tiene vehículos o comprobantes asociados.

### Cómo cargo un vehículo en SolutionsCars

1. En Clientes y Vehículos de SolutionsCars, pasá a la pestaña Vehículos.
2. En Cliente escribí o elegí una sugerencia. El vehículo pide un cliente.
3. Completá Dominio, Marca, Modelo, Año y Kilometraje. Si corresponde, N° Cilindros, N° Motor, N° Regulador, N° Chasis, Vto. Oblea y Vto. P.H. Las fechas van dd/mm/aaaa.
4. Tocá Guardar vehículo.

Resultado: la tabla muestra dominio, marca/modelo, cliente y los vencimientos.

Nota: el kilometraje tiene que ser un número entero. Si es menor al que ya tenía ese auto, dice El kilometraje no puede ser menor al último registrado. Borrar pregunta ¿Eliminar el vehículo …? y avisa que no se puede deshacer.

### Cómo agrego un proveedor en SolutionsCars

1. En Clientes y Vehículos, abrí la pestaña Proveedores.
2. Completá Nombre y Alias. Teléfono, Email y Dirección son el resto del formulario.
3. Tocá Guardar proveedor.

Resultado: aparece en Proveedores registrados. Si la lista está vacía, dice Sin proveedores registrados.

Nota: el nombre y el alias son los datos que el formulario marca para el alta. Eliminar pregunta ¿Eliminar a …?.

### Cómo doy de alta un repuesto en SolutionsCars

1. Entrá a Inventario. El cuadro se llama Acceso a Inventario y dice Ingrese su código de acceso. El campo es Código. Tocá Aceptar.
2. Completá SKU, Descripción, Categoría, Cantidad, Stock Mín., P. Costo, P. Venta, Proveedor y Transporte.
3. Tocá Guardar producto.

Resultado: el producto entra a la lista. El color marca el stock: verde normal, naranja se está acabando, rojo hay que reponer.

Nota: si el código está vacío, el campo dice Ingrese su código. Si no sirve, Código inválido. El mismo cuadro de inventario abre también Lista de Precios. El precio de costo queda detrás de ese código.

### Cómo ajusto precios del inventario en SolutionsCars

1. En Inventario, abrí el ajuste de precios.
2. Elegí Categoría o escribí en Buscar producto.
3. Marcá los productos, o Seleccionar todos.
4. Completá Porcentaje (el ejemplo de la pantalla es 15) y Tipo de ajuste.
5. Tocá Aplicar Ajuste. Cancelar cierra sin cambiar.

Resultado: esos precios de venta se mueven el porcentaje elegido.

Nota: sacar un producto del uso diario abre Mover a papelera y pregunta si moverlo. Desde la papelera se puede Restaurar. Vaciar papelera avisa que no se podrán recuperar.

### Cómo armo un precio de trabajo en SolutionsCars

1. Abrí Lista de Precios. Pide el mismo acceso que Inventario: Acceso a Inventario y el Código.
2. Elegí la sección en Filtrar por sección, o cargá una nueva: Agregar seccion pide Nombre de la seccion y Columnas separadas por coma. El ejemplo de columnas es PRODUCTO, PUBLICO, CONCESIONARIA.
3. Guardá la fila del trabajo con su precio.
4. Para papel, Guardar PDF de esa sección.

Resultado: la lista de trabajos queda aparte del stock. Borrar un repuesto del inventario no vacía estas secciones.

Nota: Limpiar lista pregunta ¿Borrar todos los productos de todas las secciones?. La papelera de esta lista también se puede vaciar, y ese vaciado no se recupera.

### Cómo recibo un auto en SolutionsCars

También se pregunta como: ¿Cómo recibo un auto? En SolutionsCars el auto entra por Recepción, no por un pedido de tienda.

1. Abrí Recepción. La pestaña Nuevo Comprobante es la del ingreso.
2. Elegí Cliente y Vehículo. El vehículo es obligatorio.
3. Anotá Kilometraje y Descripción del trabajo.
4. Marcá la inspección. Cada toque pasa el ítem de estado.
5. Tocá Generar comprobante PDF y en Guardar comprobante como… elegí dónde dejarlo.

Resultado: queda la orden y el PDF. En Comprobantes Generados se busca por cliente, vehículo o fecha (DD/MM/YYYY), se ve el detalle y se puede Regenerar PDF.

Nota: si el kilometraje no es un entero, dice El kilometraje debe ser un número entero válido. Si es más bajo que el anterior, no deja guardarlo. El estado de la orden se cambia desde el comprobante: pendiente, en proceso, completado o cancelado. Cancelar pide Confirmar Cancelación.

### Cómo hago un presupuesto en SolutionsCars

1. Abrí Facturación. El cuadro Acceso a Facturación pide el código. Aceptar entra; Código inválido no.
2. En Tipo Documento elegí Presupuesto.
3. Elegí Cliente. Vehículo es opcional. Completá Método de pago y Atendido por.
4. En Producto escribí un SKU o una descripción del inventario, o un ítem a mano con Cant. y P. Unit. Categoría puede ser repuestos, GNC, reparaciones o lubricentro.
5. Imprimir arma el PDF para mostrarlo. Guardar lo deja registrado.

Resultado: el presupuesto no lleva IVA y no pide autorización fiscal. Imprimir no guarda ni autoriza.

Nota: si el precio del ítem es cero, SolutionsCars avisa Precio en cero y ofrece Cargar precio o Agregar con $0.

### Cómo hago una factura B en SolutionsCars

1. En Facturación de SolutionsCars, con el código aceptado, elegí Factura B en Tipo Documento.
2. Elegí el cliente. La condición frente al IVA sale de la ficha. DNI / CUIT no es obligatorio en la B.
3. Cargá los ítems. En la factura B el precio que escribís es el final, con el IVA ya incluido.
4. Elegí el medio de pago: efectivo, transferencia, débito, crédito o QR.
5. Imprimir solo muestra el PDF. Guardar es el paso que descuenta el stock de los productos del inventario y, si la facturación electrónica está activa, pide la autorización.

Resultado: si autoriza, el aviso es Factura autorizada y muestra el CAE. El ítem escrito a mano no descuenta stock. Remito y presupuesto no son esta factura.

Nota: en modo prueba el cuadro dice Modo HOMOLOGACIÓN (prueba) y hay que confirmar Continuar en homologación. En producción pregunta Facturar en AFIP Producción y Confirmar y Emitir.

### Cómo hago una factura A en SolutionsCars

1. En Facturación elegí Factura A.
2. El cliente tiene que tener CUIT. El campo DNI / CUIT dice Obligatorio solo en Factura A.
3. Cargá ítems. En la A el precio es neto y SolutionsCars suma el IVA.
4. Elegí medio de pago y quién atendió.
5. Guardar descuenta stock y busca la autorización. Imprimir no lo hace.

Resultado: el total discrimina el IVA. Si falta el CUIT, el mensaje es El cliente necesita CUIT para Factura A y no emite.

Nota: un ítem que no está en el inventario se puede escribir igual y no mueve el stock. Borrar después una factura ya autorizada no la anula ante el fisco: SolutionsCars lo advierte.

### Cómo registro un cobro en la caja de SolutionsCars

1. En Facturación abrí la pestaña de la caja. Ahí están Planilla y Movimientos.
2. Si no hay planilla del día, tocá Abrir Planilla del Dia.
3. Completá Entidad (quien pagó o a quien se pagó), Descripcion, Monto, Metodo de pago y Categoria. La categoría puede ser cobranza, adelanto, servicios, proveedores, impuestos o varios.
4. Tocá Agregar.

Resultado: arriba se ven ingresos, egresos y el balance del día. En Movimientos, Aplicar filtra por medio de pago, tipo y fechas.

Nota: la caja no reemplaza a la factura. Guardar una factura A o B es el comprobante; la planilla anota el movimiento de dinero del día.

### Cómo cierro la caja del día en SolutionsCars

También se pregunta como: ¿Cómo cierro la caja? En SolutionsCars la caja del día es la planilla de Facturación.

1. Con la planilla del día abierta en SolutionsCars, tocá Cerrar Planilla.
2. El cuadro Cerrar Planilla del Dia muestra el resumen. Confirmá.
3. En el historial, una planilla cerrada se puede VER. REABRIR la vuelve a abrir si no hay otra abierta de esa fecha. ELIMINAR pide una confirmación y después CONFIRMACION FINAL.

Resultado: los movimientos pasan a las transacciones de caja y la jornada queda cerrada.

Nota: no se pueden tener dos planillas abiertas para la misma fecha. Si hay que corregir, reabrí la de ese día.

### Cómo aviso un vencimiento en SolutionsCars

También se pregunta como: ¿Cómo aviso que vence la oblea? En SolutionsCars el aviso sale de Vencimientos, por WhatsApp o por correo.

1. Abrí Vencimientos.
2. Revisá las tarjetas de oblea y de prueba hidráulica: vencidos, esta semana y los próximos días. Actualizar recarga la lista.
3. En la tarjeta, el botón de WhatsApp abre el mensaje armado (el tooltip dice Enviar WhatsApp). El de correo abre Preview del Email; ahí se puede Cancelar o Enviar Email.

Resultado: el texto ya trae el trámite, el vehículo y los días. Si el mail sale, dice Email enviado a… con la dirección del cliente.

Nota: sin teléfono no hay WhatsApp útil, y sin correo el mail no tiene destino. Los días de anticipación los cambia el administrador en Configuración, en las alertas de oblea, P.H. y certificado.

### Cómo saco un balance en SolutionsCars

1. Abrí Reportes.
2. Elegí Día, Mes o Año y tocá Filtrar.
3. Exportar baja el balance de ese período. Desde el mismo módulo se puede exportar el inventario o los clientes con sus vehículos y vencimientos.

Resultado: el archivo queda en la carpeta de documentos del programa. Arriba se ve el conteo de clientes, vehículos, repuestos, stock bajo y órdenes.

Nota: el balance es ingresos, egresos y diferencia del período, no una factura.

### Cómo hago una copia de seguridad en SolutionsCars

1. Entrá como administrador y abrí Configuración. El resto del equipo no entra ahí.
2. En la parte de copias, hacé un backup en el momento o dejá Backup automático con la Hora (HH:MM).
3. La lista deja Restaurar o eliminar. Eliminar pregunta ¿Eliminar …?.

Resultado: queda una copia de la base. Restaurar backup pide confirmar porque reemplaza los datos actuales.

Nota: antes de actualizar o de una importación grande, conviene una copia nueva. Si conectás la nube, Conectar a la Nube y después se puede Restaurar desde la nube.

### Cómo actualizo SolutionsCars

1. En Configuración, buscá actualizaciones.
2. Si hay una, el cuadro Actualización disponible dice la versión y pregunta si continuar. Actualizar sigue; Cancelar no.
3. Después aparece Instalación en curso. SolutionsCars se cierra, instala y al abrir de nuevo avisa si quedó aplicada.
4. Si ya estabas al día, el texto es Estás en la última versión.

Resultado: la versión nueva queda instalada y los datos del taller siguen en la misma base.

Nota: hacé un backup antes. Si al reabrir el aviso dice que no quedó aplicada, se puede reintentar desde Configuración. Descartar aviso solo oculta el cartel, no instala.

### Cómo dejo los datos del taller en SolutionsCars

1. Como administrador, abrí Configuración.
2. Completá Nombre del taller, Dirección, Teléfono, Razón social, Ingresos brutos, Inicio de actividades y el lema del pie de factura. Esos textos salen en el PDF.
3. Cargá el punto de venta y el modo de facturación: prueba (homologación) o producción. Pasar a producción pide Confirmar.
4. Guardá.

Resultado: las facturas nuevas usan esos datos. El campo del emisor está en esta pantalla; no hace falta repetirlo en cada comprobante.

Nota: Configuración no la ve quien no es administrador. El certificado y el modo de prueba o producción los define el taller; SolutionsCars no los trae resueltos.

## Problemas comunes y soluciones

### No me deja entrar a SolutionsCars

El texto rojo bajo el formulario dice la causa.

1. Usuario y contraseña son requeridos: falta uno de los dos campos.
2. Usuario o contraseña incorrectos: revisá mayúsculas y el ojo de la contraseña.
3. Demasiados intentos. Espere … segundos: esperá ese tiempo y recién ahí volvé a Iniciar Sesión.
4. Error al iniciar sesión: cerrá SolutionsCars y volvé a abrirlo.

No hay en esa pantalla un botón de olvidé mi clave. La renueva quien administra el taller, o el propio cuadro de cambio si la cuenta está obligada a definir una nueva.

### Me obliga a cambiar la contraseña

SolutionsCars abre Cambio de contraseña obligatorio y no sigue hasta Guardar.

1. Escribí Nueva contraseña y la misma en Confirmar contraseña.
2. Si dice Las contraseñas no coinciden, repetilas iguales.
3. Si la nueva es demasiado corta, el aviso pide al menos 4 caracteres.

Esa clave nueva es la que vas a usar la próxima vez. No queda publicada en ningún cartel.

### Me dice código inválido

Inventario y Lista de Precios piden Acceso a Inventario. Facturación pide Acceso a Facturación. El campo se llama Código.

1. Si está vacío: Ingrese su código.
2. Si no es el de un usuario activo: Código inválido.
3. Cancelar vuelve a Inicio y no abre el módulo.

Es un código distinto de la contraseña de entrar. Lo tiene cada usuario; no es una clave única publicada del programa. El de facturación y el de inventario pueden no ser el mismo.

### No aparece el cliente

1. En Clientes y Vehículos, pestaña Clientes, borrá el Buscar.
2. Mirá si el cartel dice Sin clientes registrados: todavía no se guardó con Guardar cliente.
3. En Facturación el cliente se elige escribiendo y tocando una sugerencia. Si solo quedó texto suelto, no está elegido.
4. Un cliente con vehículos o comprobantes no se borra: si “desapareció”, puede estar en otra página de la lista.

### No me deja facturar

1. Sin el código de Acceso a Facturación, la pantalla no abre. Código inválido deja el cuadro ahí.
2. En Factura A, si el cliente no tiene CUIT, dice El cliente necesita CUIT para Factura A. Completalo en la ficha o en el campo DNI / CUIT y volvé a Guardar.
3. Elegí el cliente de la sugerencia, no solo el texto.
4. Imprimir no emite. Tiene que ser Guardar en una Factura A o Factura B.
5. Presupuesto y remito no piden autorización. Si esperabas un CAE, el tipo de documento no era factura.

### La factura salió con error de AFIP

El cuadro Factura rechazada por AFIP dice que AFIP devolvió errores y los muestra en un recuadro. Tocá Entendido.

1. Leé el texto del recuadro: es el motivo que volvió (datos del cliente, importes, punto de venta).
2. Corregí la ficha del cliente o los ítems y emití de nuevo con Guardar.
3. Si el taller está en prueba, el cuadro previo dice Modo HOMOLOGACIÓN (prueba). Un comprobante de prueba no es el de producción.
4. Pasar a producción se confirma en Configuración. No cambia solo.

SolutionsCars no muestra por dentro cómo se pide la autorización. Lo que ves es ese cuadro o el aviso Factura autorizada con el CAE.

### Quedó pendiente de AFIP

El título es Comprobante pendiente de AFIP: No se pudo confirmar la autorización. El comprobante quedó pendiente. Pide usar Verificar en AFIP en la lista antes de volver a emitir.

1. No hagas otra factura igual enseguida.
2. En el historial, abrí el pendiente y usá Verificar en AFIP.
3. Si corresponde anularlo, está Anular pendiente AFIP. Borrarlo como un documento común puede decir Pendiente AFIP — no se puede eliminar así o Eliminación no permitida.
4. Si el aviso es Error al emitir en AFIP y aclara que quedó pendiente, el paso es el mismo: verificar antes de reintentar.

A veces AFIP autorizó y el CAE quedó guardado en el pendiente, pero el registro local no cerró. El mensaje lo dice. Completá ese pendiente; no emitas un duplicado.

### Me aparece precio en cero

Al agregar un ítem sin importe, SolutionsCars abre Precio en cero.

1. Cargar precio vuelve al importe.
2. Agregar con $0 lo suma igual en cero. En una factura A o B, un total que no supera cero no pide autorización.
3. Para cotizar en serio, cargá P. Unit. antes de Guardar.

### No se actualiza el programa

1. En Configuración, buscá actualizaciones. Estás en la última versión significa que no hay otra.
2. Si aparece Actualización disponible, tocá Actualizar, no Cancelar.
3. Instalación en curso cierra SolutionsCars para instalar. Volvé a abrirlo y leé el aviso.
4. Si el aviso dice que no quedó instalada, repetí la búsqueda. Descartar aviso no instala.
5. Hacé un backup antes. Sin conexión, la búsqueda no puede ver si hay versión nueva.

### El kilometraje no me deja

En Recepción o en el vehículo, el número tiene que ser un entero.

1. El kilometraje debe ser un número entero válido: no uses letras ni decimales.
2. El kilometraje no puede ser negativo, ni pasar de 9.999.999.
3. El kilometraje no puede ser menor al último registrado, y el mensaje muestra ese último valor. Cargá un número igual o mayor.
4. Si el auto estaba mal cargado, corregí el kilometraje en la ficha del vehículo y recién ahí recepcioná.

### No puedo borrar la factura

1. Una factura autorizada, al borrarla en SolutionsCars, sale del programa y devuelve el stock, pero no se anula ante el fisco. El programa lo advierte. La anulación fiscal se hace con el comprobante que indique el contador.
2. Un pendiente de AFIP puede decir Pendiente AFIP — no se puede eliminar así. Usá Verificar en AFIP o Anular pendiente AFIP.
3. Eliminación no permitida: leé el texto del cuadro y tocá Entendido. No es un fallo de la lista.

### La copia no restaura o la nube no conecta

1. En Configuración, Restaurar backup pide confirmación. Si confirmás, los datos de ahora se reemplazan. Hacé antes una copia del estado actual.
2. Si la lista está vacía, todavía no hay backup. Creá uno en el momento.
3. Conectar a la Nube pide un Código de autorización en ese cuadro. Si no conecta, las copias locales siguen en la misma pantalla.
4. Restaurar desde la nube usa una copia ya subida. Sin haber conectado, ese botón no tiene de dónde traer.

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

También se pregunta como: ¿sirve para facturar?, ¿factura con AFIP?, ¿hace facturas?. Sí. SolutionsCars hace presupuestos, remitos, factura A y factura B. Las facturas A y B pueden autorizarse de forma electrónica. Presupuesto y remito no son facturas fiscales.

### ¿Cómo hago un pedido?

En SolutionsCars el equivalente a “anotar el trabajo” es la recepción: se elige el cliente y el auto, se describe el trabajo y se genera el comprobante de ingreso. Si lo que se necesita es una cotización, se usa un presupuesto en Facturación. No es una tienda en línea de pedidos.

### ¿Qué onda con la caja?

La caja de SolutionsCars es la planilla diaria, dentro de Facturación. Se abre la del día, se cargan ingresos y egresos, y al cierre queda el balance. Sirve para saber si la jornada cerró a favor o en contra.

### ¿Anda con AFIP?

También se pregunta como: el sistema del taller ¿anda con AFIP? En SolutionsCars la factura electrónica guarda el código de autorización en el comprobante y en el PDF. Hay un modo de prueba y un modo de producción. El administrador elige el modo, el punto de venta y los datos del emisor en Configuración. Los certificados los instala el taller; no vienen resueltos solos con el programa.

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

### ¿Dónde veo lo que me deben en SolutionsCars?

También se pregunta como: ¿Dónde veo lo que me deben? En SolutionsCars no hay una cuenta corriente aparte. Lo que te deben no es una pantalla propia: lo cobrado y lo pagado del día está en Facturación, pestaña de la caja, con ingresos, egresos y balance. Las facturas guardadas se buscan en el historial, con cliente, vehículo y período. Reportes, con Día, Mes o Año y Filtrar, muestra el balance de ese período.

### ¿Se puede deshacer en SolutionsCars?

No hay un botón Deshacer. Un cliente o un vehículo eliminado pregunta antes y, en el vehículo, avisa que no se puede deshacer. Un producto va a la papelera y se puede Restaurar, hasta que se vacíe la papelera. Para volver atrás del todo, en Configuración se restaura un backup, y eso reemplaza los datos de ahora.

### ¿Qué pasa si se corta la luz en SolutionsCars?

También se pregunta como: ¿Qué pasa si se corta la luz? En SolutionsCars queda lo que ya se guardó en la computadora. Un formulario sin Guardar, sin Guardar cliente o sin Generar comprobante PDF no quedó. Al abrir de nuevo, revisá la lista. Si se cortó internet al guardar una factura A o B, puede haber quedado un comprobante pendiente: verificalo antes de emitir otro. La caja del día, si no llegaste a cerrar la planilla, sigue abierta. Si la base no abre, Configuración permite restaurar un backup.

### ¿Qué pasa si se corta internet al guardar la factura?

En SolutionsCars, presupuesto y remito no hablan con el fisco. En factura A o B, si la autorización no se confirma, el cuadro se llama Comprobante pendiente de AFIP y pide Verificar en AFIP antes de emitir otra. No repitas el Guardar hasta revisar ese pendiente.

### ¿Cómo hago una factura B en el taller?

En Facturación de SolutionsCars, código de acceso, Tipo Documento en Factura B, cliente, ítems y Guardar. El precio que cargás es el final, con el IVA incluido. Imprimir solo muestra el papel y no autoriza. Si el modo es prueba, hay que confirmar Continuar en homologación.

### ¿El presupuesto descuenta el stock?

No. En SolutionsCars el presupuesto no lleva IVA ni autorización, y no es una factura. El stock de los productos del inventario baja al Guardar una factura A o B. Un ítem escrito a mano, aunque esté en una factura, no descuenta stock.

### ¿Qué es la homologación en SolutionsCars?

Es el modo de prueba de la facturación. Antes de emitir, el cuadro dice Modo HOMOLOGACIÓN (prueba). Esos comprobantes no son los de producción. El administrador elige el modo en Configuración. Pasar a producción pide confirmación.

### ¿Por qué me pide CUIT si ya puse el nombre?

En la factura A de SolutionsCars el campo DNI / CUIT dice Obligatorio solo en Factura A. Si falta, Guardar responde El cliente necesita CUIT para Factura A. En la factura B ese dato no es obligatorio. Se carga en la ficha del cliente o en ese campo.

### ¿Puedo facturar sin patente?

Sí. En Facturación de SolutionsCars el vehículo es opcional. En Recepción, en cambio, el vehículo es obligatorio para el ingreso del auto.

### ¿Imprimir ya dejó la factura hecha?

No. Imprimir en SolutionsCars arma el PDF de lo que está en pantalla y no guarda ni pide autorización. Guardar es el que registra la factura A o B, descuenta stock y busca el CAE si la emisión está activa.

### ¿Puedo reabrir la caja de hoy?

Sí, si ya la cerraste. En el historial de planillas de SolutionsCars está REABRIR, siempre que no haya otra abierta para esa fecha. VER mira el resumen. ELIMINAR pide dos confirmaciones.

### ¿Cómo busco una factura vieja?

En el historial de Facturación de SolutionsCars filtrá por cliente, vehículo, categoría y período, y tocá Aplicar. Limpiar saca los filtros. Ahí también está el pendiente, si la autorización no cerró.

### ¿Quién entra a Configuración?

Solo el administrador de SolutionsCars. Ahí están los datos del taller, las alertas, el punto de venta, el modo de facturación, las copias, la nube y las actualizaciones. El resto usa clientes, recepción, vencimientos y el resto del menú.

### ¿Cómo mando el recordatorio de la oblea?

En Vencimientos de SolutionsCars, en la tarjeta del auto, el botón de WhatsApp abre el mensaje ya escrito. El de correo abre Preview del Email y después Enviar Email. Hace falta teléfono o correo en la ficha. Actualizar refresca la lista.

### ¿Se puede dejar un ítem a cero pesos?

SolutionsCars pregunta Precio en cero. Cargar precio vuelve a poner el importe. Agregar con $0 lo suma igual. Una factura A o B cuyo total no es mayor que cero no pide autorización.

### ¿Borré un repuesto y lo necesito?

En el inventario de SolutionsCars, eliminar manda el producto a la papelera. Ahí está Restaurar. Vaciar papelera pregunta y avisa que no se podrán recuperar. Eso no borra la lista de precios de los trabajos.

### ¿La actualización me borra los autos?

No. Al actualizar, SolutionsCars se cierra, instala y al abrir dice si la versión quedó. Los datos siguen en la misma base. Igual, conviene un backup en Configuración antes de tocar Actualizar.

### ¿Puedo usar SolutionsCars en el celular?

No tiene app de teléfono. Es un programa de escritorio. WhatsApp del vencimiento sí puede abrirse en el teléfono porque es un enlace, no el programa. Varias computadoras juntas necesitan una base compartida, armada por quien administra el sistema.

### ¿Qué miro apenas abro el taller?

En Inicio están las tarjetas de cada módulo. Vencimientos muestra obleas y pruebas que ya vencieron o vencen pronto. Reportes resume clientes, vehículos, stock bajo y órdenes. La caja del día, si sigue abierta, está en Facturación.

### ¿Remito y factura son lo mismo?

No. En SolutionsCars el remito entrega o deja asentado sin factura y sin IVA. La factura A o B es la que, al Guardar, puede autorizarse y descontar stock. El presupuesto es la cotización. El tipo se elige en Tipo Documento.

### ¿Cómo cambio la clave la primera vez?

Si la cuenta debe renovarla, SolutionsCars no entra al taller: abre Cambio de contraseña obligatorio. Nueva contraseña, Confirmar contraseña y Guardar. Si no coinciden, lo dice. Después Iniciar Sesión usa esa clave.

### ¿El código de facturación es la contraseña?

No. La contraseña es la de Iniciar Sesión. El código es el que piden Acceso a Inventario (también para la lista de precios) y Acceso a Facturación. Si está mal, el campo dice Código inválido. Cada usuario tiene el suyo; no hay uno publicado para todos.

### ¿Qué hago si dice que AFIP autorizó pero no cerró el comprobante?

En SolutionsCars ese aviso aclara que la autorización salió y el CAE quedó en el documento pendiente, pero el registro no terminó. No emitas otra factura del mismo trabajo. Entrá al pendiente y usá Verificar en AFIP para completarlo.

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
