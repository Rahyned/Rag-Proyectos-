# portafolio-web

Documento público de portafolio-web, el sitio LAUTARO.DEV. Sirve para responder preguntas de visitantes. Describe la página publicada, no el trabajo interno de desarrollo.

## Qué es

portafolio-web es el sitio personal de Lautaro Rodriguez, desarrollador web y de sistemas en Rosario, Argentina. El nombre visible es LAUTARO.DEV. La página presenta proyectos, servicios y una vía para pedir un trabajo, con estética de videojuego retro, sprites pixel art y textos en español o inglés.

El problema que resuelve portafolio-web es simple. Alguien que quiere conocer el trabajo de Lautaro, o encargarle un sitio, un sistema o una automatización, necesita ver ejemplos y escribirle sin perderse en un currículum plano. El sitio ordena los proyectos en cajas, explica cada uno con problema, solución y resultado, y cierra con un formulario de contacto.

## Funcionalidades

### Pantalla de arranque

Al abrir portafolio-web, una pantalla de encendido cubre la página y muestra una barra de progreso. Un clic o una tecla la salta. Si el sistema pide menos movimiento, la barra termina enseguida. Hasta que esa pantalla sale, el resto de portafolio-web no se marca como ya visto.

### Inicio y recorrido

El inicio de portafolio-web muestra el nombre Lautaro Rodriguez, la línea de oficio y una frase que se escribe sola: explorar proyectos y servicios. El botón Entrar a la PC baja hasta la zona de proyectos. Una barra de enlaces lleva a Inicio, Ficha, Servicios, PC y Contacto. El logo del encabezado vuelve arriba. Si la dirección no existe, portafolio-web muestra una página 404 con un botón para volver al inicio.

### Ficha de entrenador

La ficha de portafolio-web es la sección Sobre mí. Muestra la clase Desarrollador web y sistemas, un nivel de juego, años de experiencia, cantidad de proyectos, la zona Rosario y el estado de disponibilidad. Las medallas son el stack principal publicado: Python, React, Next.js, Tauri, FastAPI, TypeScript y Tailwind. La bio se escribe en pantalla y se puede saltear con una tecla. Esos números y el estado salen de los datos del sitio, así que pueden cambiar cuando se actualiza el contenido.

### Servicios

portafolio-web ofrece tres servicios.

Desarrollo web cubre landings, sitios institucionales y tiendas con catálogo y carrito, más WhatsApp, formularios, integraciones, SEO básico y la publicación.

Sistemas de gestión cubre programas de escritorio para Windows que reemplazan planillas y papel: clientes, inventario, cuentas corrientes, reportes en PDF o Excel, y facturación electrónica cuando el encargo lo pide. portafolio-web no es en sí un programa de facturación.

Automatizaciones y APIs cubren avisos, correo transaccional, sincronización entre herramientas y backends a medida.

Cada tarjeta tiene el botón Iniciar intercambio. Ese botón baja al formulario de portafolio-web y deja elegido el tipo de proyecto.

### PC de almacenamiento

La PC de almacenamiento de portafolio-web guarda los proyectos como las cajas de una PC de juego. Hay tres cajas. La primera es desarrollo web. La segunda es sistemas de gestión. La tercera es apps de escritorio. En cada caja se elige un slot y se abre la ficha. Los slots vacíos no hacen nada. En pantalla ancha la grilla muestra hasta seis lugares. En un teléfono, la grilla usa dos columnas.

La caja de desarrollo web incluye Abstractoshop, Florería Susi, Laboratorio RioDent y Pixel Sprite Editor. RioDent y el editor de sprites tienen demo pública. Las otras fichas de esa caja no.

La caja de sistemas incluye SolutionsCars, en uso, y STELLA, en desarrollo. STELLA puede abrir un asistente público de proyectos, distinto del chat que vive dentro de portafolio-web.

La caja de escritorio incluye Butterflies y Libreta. Esas fichas no tienen demo web. El código público, cuando existe, está en GitHub bajo el perfil Rahyned.

### Ficha de un proyecto

La ficha de un proyecto en portafolio-web muestra el título, la categoría, la fecha, el estado, el problema, la solución, el resultado y las tecnologías. Si hay una demo, el enlace se llama Live demo. Si no hay, ese botón queda apagado. Si el proyecto declara un asistente, aparece el enlace Asistente RAG. El enlace de GitHub abre el perfil o el repositorio publicado. Se cierra con la cruz, con Escape o con un clic fuera del cuadro. Hoy las fichas no cargan un video.

### Contacto e intercambio

El contacto de portafolio-web tiene dos partes. El PokéNav lista los canales publicados en la propia página: correo, LinkedIn, GitHub y WhatsApp. Esos botones abren el medio correspondiente.

El intercambio es el formulario. Pide nombre, email del visitante, tipo de proyecto, plazo, presupuesto y una descripción. Los tipos son web, sistema, automatización u otro. Los plazos son 2 a 4 semanas, 1 a 3 meses, o flexible. El presupuesto es pequeño, mediano o grande, sin montos. portafolio-web no publica precios.

Si el envío sale bien, la página avisa que van a responder al email del visitante. Si el servicio de envío no está disponible, se abre la aplicación de correo del visitante con el texto armado. Si el servidor falla de otro modo, portafolio-web ofrece un enlace para mandar el correo a mano. Los campos incompletos o inválidos se marcan y no se envían.

### Chat del Profesor Oak

El Profesor Oak es el asistente que vive dentro de portafolio-web. Se abre con el botón de chat del encabezado. Saluda y ofrece un menú: experiencia, proyectos destacados, stack y medallas, y datos de contacto. Esas cuatro opciones arman la respuesta con los datos del sitio y no gastan el cupo de inteligencia artificial.

También se puede escribir una pregunta libre. Esa pregunta va a un modelo de lenguaje y la respuesta aparece de a poco, como texto de juego. El cupo visible es de 10 consultas de ese tipo por día. El menú sigue disponible cuando el cupo se acaba. Si llegan muchas consultas seguidas, Oak pide esperar un minuto. Si el modelo no está configurado en el sitio publicado, Oak avisa que las consultas libres están pausadas y deja el menú.

Oak responde sobre Lautaro, sus proyectos y cómo contactarlo. No toma pedidos ni cobra.

### Terminal

portafolio-web incluye una terminal. La tecla T la abre y la cierra, salvo que el foco esté en un campo de texto. Los comandos son help, projects, skills, about, contact, cv, oak y clear. projects lista las cajas. cv abre el currículum. oak cierra la terminal y abre el chat del Profesor Oak. Un comando desconocido muestra un aviso.

### Idioma

portafolio-web está en español y en inglés. El botón del encabezado alterna ES y EN. La elección queda guardada en el navegador. En inglés cambian los textos de la interfaz y la prosa de bio, proyectos y servicios. Los identificadores del formulario no dependen del idioma.

### Tema, pantalla y sonido

El encabezado de portafolio-web deja elegir el tema ARCADE o el tema DARK. ARCADE es el tema inicial. La elección queda guardada. El cambio de tema lleva un destello breve. Si el sistema pide menos movimiento, el cambio es directo.

El botón de televisor enciende o apaga el efecto CRT, las líneas de barrido sobre la página. También queda guardado.

El botón de sonido silencia o activa los efectos 8-bit: clics, apertura de cajas y el aviso del código secreto. El silencio queda guardado. Al llegar por primera vez, el sonido está apagado hasta que el visitante lo activa.

### Código secreto

En portafolio-web, la secuencia clásica de un control de juego, arriba arriba, abajo abajo, izquierda derecha, izquierda derecha, B y A, lanza confeti y un aviso de modo misterio. No cambia el tema ni abre una sección nueva.

### Currículum imprimible

El pie de portafolio-web enlaza un CV en otra página. Esa página tiene un botón para imprimir o guardar PDF, y un enlace para volver al sitio. El CV toma el perfil publicado: oficio, bio, zona, experiencia, proyectos y disponibilidad.

## Cómo se usa

### Recorrer el sitio

1. Abrí portafolio-web y esperá la pantalla de arranque, o saltala con un clic.
2. Leé el inicio. El botón Entrar a la PC baja a los proyectos.
3. Usá la barra Inicio, Ficha, Servicios, PC y Contacto para saltar de sección.
4. En la ficha, leé la bio y las medallas.
5. En Servicios, mirá qué tipo de trabajo se ofrece.

### Ver un proyecto

1. En la PC de portafolio-web, elegí una caja: web, sistemas o escritorio.
2. Hacé clic en un proyecto ocupado.
3. Leé problema, solución, resultado y tecnologías.
4. Si Live demo está activo, abre el sitio público de ese trabajo. RioDent y Pixel Sprite Editor son los que hoy tienen demo.
5. GitHub abre el perfil público Rahyned o el repositorio de ese proyecto.
6. Cerrá la ficha con Escape, la cruz o un clic afuera.

### Pedir un trabajo

1. En Servicios de portafolio-web, pulsá Iniciar intercambio en la tarjeta que se parece a tu encargo. El formulario queda con ese tipo.
2. También podés bajar directo a Contacto y elegir el tipo a mano.
3. Completá nombre, tu email, plazo, presupuesto en rango y una descripción del trabajo.
4. Confirmá el intercambio.
5. Si la página dice que el intercambio se inició, el mensaje salió y la respuesta llega a tu email.
6. Si se abre tu correo, enviá ese mensaje desde tu aplicación.
7. Si aparece un error de servidor, usá el enlace de correo manual que muestra la misma pantalla.
8. El PokéNav sirve si preferís escribir por los canales que la propia página publica, sin usar el formulario.

### Preguntarle al Profesor Oak

1. En portafolio-web, pulsá el botón de chat del encabezado.
2. Elegí una opción del menú si querés una respuesta armada con los datos del sitio.
3. O escribí una pregunta y enviala. Eso consume una de las 10 consultas con inteligencia artificial del día.
4. Si Oak dice que las consultas libres están pausadas, seguí con el menú o con el formulario de contacto.
5. Si pide esperar un minuto, no reintentes enseguida.

### Usar la terminal, el idioma y el CV

1. Con el foco fuera de un campo, pulsá T en portafolio-web.
2. Escribí help para ver los comandos, projects para listar trabajos, o oak para abrir el chat.
3. El botón ES o EN del encabezado cambia el idioma y lo recuerda.
4. ARCADE o DARK cambian el tema. El televisor controla el efecto CRT. El altavoz controla el sonido.
5. En el pie, abrí el CV y usá el botón de imprimir si querés un PDF.

## Tecnologías

### Sitio que ve el visitante

La página publicada de portafolio-web está hecha con React 19 y Vite 8, en JavaScript, sin TypeScript. El estilo es CSS propio, no un framework de utilidades, para controlar la estética pixel y los temas. Vite arma el sitio estático. React ordena las secciones, el formulario y los overlays en componentes.

Hay una versión anterior en HTML, CSS y JavaScript sin empaquetar. Sigue en el repositorio como respaldo para abrir el sitio sin un servidor de desarrollo. Lo que ven los visitantes del sitio publicado es la app React.

### Textos e idiomas

Los textos en español de portafolio-web viven en un archivo de datos: perfil, proyectos, servicios y canales. La app lo pide al cargar. Si esa lectura falla, usa una copia incluida en la propia app, así la página no queda vacía. El inglés de la prosa está en otro archivo y se superpone cuando el idioma es EN. Los rótulos de botones y mensajes de error están traducidos en los dos idiomas.

### Formulario, chat y publicación

El formulario de portafolio-web se envía a una función del mismo sitio, que valida los campos y manda el correo con un cliente SMTP. Si el correo de salida no está configurado, la función responde que no está disponible y la página pasa al correo del visitante.

El chat del Profesor Oak usa otra función del mismo sitio. Habla con un modelo de lenguaje por una API compatible con el formato de chat habitual, y devuelve la respuesta en un flujo continuo. En el sitio publicado, el cupo del chat depende de un almacén remoto. Si ese almacén o el modelo no están listos, las preguntas libres quedan pausadas.

portafolio-web se publica en Vercel. El build es el de la app React. Un servidor Express aparte existe solo para pruebas locales y no es el runtime del sitio publicado.

Los sonidos salen del audio del navegador, sin archivos externos. El medidor de visitas es Google Analytics 4 y solo se carga si el archivo de datos trae un identificador. Hoy ese identificador está vacío, así que la medición no se activa.

## Arquitectura

### Piezas

portafolio-web publicado tiene tres piezas visibles para un visitante. La primera es la aplicación de una sola página: encabezado, inicio, ficha, servicios, PC, contacto, chat, terminal y CV. La segunda es el archivo de datos que alimenta esos textos. La tercera son dos funciones en el mismo dominio: una para el formulario y otra para el Profesor Oak.

El navegador pide la aplicación, luego pide los datos, y solo llama a una función cuando hay un envío o una pregunta libre. El menú de Oak no llama al modelo.

### Cómo se hablan

La app de portafolio-web y las funciones comparten el origen del sitio. El formulario manda un JSON con nombre, email, tipo, plazo, presupuesto y descripción. La función responde si salió bien, si faltan campos, si hay que esperar, o si el envío no está disponible. El chat manda el historial corto de la conversación y el idioma, y recibe el texto en partes.

STELLA, dentro de la PC, puede abrir otro asistente, el de documentos públicos de proyectos. Ese asistente no es el Profesor Oak. Oak está embebido en portafolio-web y contesta con los datos de esta página. El otro asistente es un sitio aparte, pensado para preguntas de visitantes sobre los proyectos.

No hay base de usuarios ni cuentas. Lo que el visitante elige, tema, idioma, CRT y sonido, queda en su navegador.

## Seguridad y calidad

### Revisión automática

Cada cambio de la app de portafolio-web que entra al repositorio pasa por un control automático: instalación limpia, análisis del código, pruebas y build, con Node 22. Las pruebas cubren el formulario y el chat en sus respuestas esperadas, más un control de que las funciones cargan sus dependencias. El estilo del código lo revisa oxlint. No hay una base de datos de visitantes que respaldar. El contenido público es archivos versionados en el repositorio.

### Validación y límites de uso

El formulario de portafolio-web se valida en la página y otra vez en el servidor. Hacen falta nombre, un email con forma válida, un tipo conocido, un plazo conocido, un presupuesto conocido y una descripción dentro de un tamaño máximo. El servidor también limita la cantidad de envíos para frenar el abuso. Los secretos de correo y del modelo no están en el repositorio. Viven en la configuración del alojamiento.

El chat valida el idioma y el tamaño de los mensajes, aplica un cupo diario y un freno si llegan muchas preguntas juntas. El sitio publicado envía encabezados del navegador para reducir riesgos comunes de contenido activo.

## Historial

El historial público de portafolio-web sale del registro de cambios del repositorio. Las fechas de abajo son hitos de ese registro, no versiones numeradas del producto.

### 5 de octubre de 2026

En portafolio-web, el formulario de contacto y el chat del Profesor Oak quedaron con validación estable de tipo, plazo y presupuesto. Se sumaron pruebas automáticas y un flujo de integración continua para la app. El sitio publicado pasó a enviar encabezados de seguridad del navegador.

## Preguntas frecuentes

### ¿Qué es esta página?

Es portafolio-web, el sitio LAUTARO.DEV de Lautaro Rodriguez. Muestra proyectos, servicios y un formulario para encargar un trabajo, con look de juego retro.

### ¿Quién lo hizo y de dónde es?

portafolio-web presenta a Lautaro Rodriguez, desarrollador web y de sistemas. La ficha pública dice Rosario, Argentina.

### ¿Está disponible para laburar?

En los datos públicos de portafolio-web el estado dice disponible para proyectos. Conviene confirmarlo por el formulario, porque ese texto se edita con el contenido del sitio.

### ¿Sirve para facturar?

portafolio-web no factura ni emite comprobantes. Es una página de presentación. Entre los servicios hay sistemas de gestión que pueden incluir facturación electrónica, como el caso publicado de SolutionsCars. El alta de ese tipo de sistema se conversa por el contacto, no se hace desde esta página.

### ¿Cómo hago un pedido?

En portafolio-web no se compra con carrito. Un pedido de trabajo es el formulario de Contacto: tipo, plazo, rango de presupuesto y descripción. También podés apretar Iniciar intercambio en una tarjeta de Servicios.

### ¿Cuánto sale?

portafolio-web no publica precios. El formulario pide un rango: pequeño, mediano o grande, sin montos. El número se habla después, por el email que dejes.

### ¿Cuánto tarda?

El formulario de portafolio-web deja elegir 2 a 4 semanas, 1 a 3 meses, o flexible. Es el plazo que vos marcás como preferencia, no una fecha prometida de entrega.

### ¿Qué onda con el Profesor Oak?

El Profesor Oak es el chat de portafolio-web. El menú responde con los datos del sitio. Si escribís libre, usa inteligencia artificial, con 10 de esas preguntas por día. Si el modelo está pausado, el menú sigue. Oak no cierra contratos.

### ¿Qué onda con el asistente de proyectos?

La ficha de STELLA en portafolio-web puede abrir un asistente público de proyectos, distinto del Profesor Oak. Ese asistente lee documentos como este. El pedido de un trabajo sigue en el formulario de contacto.

### ¿Cómo lo contacto si no quiero el formulario?

El PokéNav de portafolio-web muestra correo, LinkedIn, GitHub y WhatsApp. Los datos concretos están en esa sección de la página, no en este documento. GitHub público: https://github.com/Rahyned

### ¿Dónde veo los proyectos?

En portafolio-web, bajá a la PC de almacenamiento o pulsá Entrar a la PC. Hay tres cajas: desarrollo web, sistemas de gestión y apps de escritorio.

### ¿Qué proyectos de webs hay?

En la caja web de portafolio-web están Abstractoshop, Florería Susi, Laboratorio RioDent y Pixel Sprite Editor. RioDent está en producción y tiene demo. El editor de sprites también tiene demo. Abstractoshop y Florería Susi figuran como trabajos completados de tienda y de landing, sin demo cargada en la ficha.

### ¿Qué es RioDent en este portafolio?

Laboratorio RioDent, dentro de portafolio-web, es un sitio para un laboratorio dental: catálogos, pedidos, toma de color, cursos y contacto, en más de un idioma. La ficha lo marca en producción y enlaza la demo pública.

### ¿Qué proyectos de sistemas hay?

La caja de sistemas de portafolio-web tiene SolutionsCars, un sistema de escritorio para un taller, en uso, y STELLA, un sistema para un laboratorio odontológico, en desarrollo.

### ¿Hay apps de escritorio?

Sí. portafolio-web muestra Butterflies, un editor de dibujo, y Libreta, un diario de películas para usar en la computadora. No tienen demo en el navegador.

### ¿Puedo ver el código?

Varias fichas de portafolio-web enlazan GitHub en https://github.com/Rahyned. Eso abre el perfil o el repo publicado de ese trabajo. No todos los encargos tienen el código abierto.

### ¿Hay blog?

portafolio-web no muestra un blog en la página publicada.

### ¿Hay videos?

Hoy las fichas no tienen video cargado.

### ¿Funciona en el celular?

Sí. portafolio-web reacomoda la PC de proyectos a dos columnas en pantallas chicas y el formulario se usa igual. La terminal con la tecla T está pensada para teclado.

### ¿Cómo cambio el idioma, el color o el sonido?

En el encabezado de portafolio-web: ES o EN para el idioma, ARCADE o DARK para el tema, el ícono de televisor para las líneas CRT, y el altavoz para el sonido. El navegador recuerda esas elecciones.

### ¿Qué es el código de las flechitas?

En portafolio-web, la secuencia arriba, arriba, abajo, abajo, izquierda, derecha, izquierda, derecha, B, A muestra confeti y un aviso. Es un guiño. No desbloquea precios ni proyectos ocultos.

### ¿Dónde está el CV?

En el pie de portafolio-web hay un enlace al CV. Desde ahí se puede imprimir o guardar como PDF.

### ¿La página me dice que Oak está pausado?

Pasa cuando portafolio-web no tiene listo el modelo o el cupo del sitio publicado. El menú de Oak, la PC de proyectos y el formulario siguen disponibles.

### ¿Me quedé sin preguntas en el chat?

portafolio-web permite 10 preguntas libres al Profesor Oak por día. El menú de opciones no entra en esa cuenta. Al día siguiente el cupo vuelve. Para un encargo, el camino es el formulario.

### ¿El formulario no se envía?

Revisá nombre, email, presupuesto y descripción en portafolio-web. Si el servicio no está disponible, se abre tu correo con el texto listo: tenés que enviarlo vos. Si hay un error de servidor, la misma pantalla deja un enlace para escribir a mano.

### ¿Guardan mi mensaje en una cuenta?

portafolio-web no crea cuentas de visitante. El formulario manda un correo para responderte. Tema, idioma y sonido quedan solo en tu navegador.

### ¿Trabajan con AFIP?

Lautaro ofrece, entre los sistemas de gestión publicados en portafolio-web, encargos que incluyen facturación electrónica. Este sitio no explica ni opera ese circuito. Si lo necesitás, describilo en el formulario.

## Glosario

### portafolio-web

Nombre del repositorio y de este proyecto. Es el sitio publicado como LAUTARO.DEV.

### LAUTARO.DEV

Nombre de marca que muestra el encabezado de portafolio-web.

### Ficha de entrenador

Sección Sobre mí de portafolio-web: oficio, nivel de juego, experiencia, zona, disponibilidad, medallas y bio.

### Medallas

Insignias del stack principal en la ficha de portafolio-web. No son certificados externos.

### PC de almacenamiento

Zona de proyectos de portafolio-web. También se la llama PC, al estilo de la PC donde un juego guarda criaturas. El botón Entrar a la PC lleva ahí.

### Caja

Pestaña dentro de la PC de portafolio-web. Hay caja de desarrollo web, caja de sistemas y caja de apps de escritorio.

### Slot

Casillero de una caja en portafolio-web. Si tiene proyecto, se puede abrir. Si está vacío, no hace nada.

### Intercambio

Nombre retro del formulario de contacto de portafolio-web. Iniciar intercambio elige un servicio y baja a ese formulario.

### PokéNav

Bloque de canales directos en el contacto de portafolio-web: correo, LinkedIn, GitHub y WhatsApp.

### Profesor Oak

Chat dentro de portafolio-web. Menú con datos del sitio, más preguntas libres con cupo diario.

### Asistente RAG

En una ficha de portafolio-web, enlace a un asistente público de proyectos, separado del Profesor Oak. Hoy lo declara la ficha de STELLA.

### CRT

Efecto de líneas de monitor viejo en portafolio-web. Se apaga con el botón del televisor en el encabezado.

### ARCADE

Tema visual por defecto de portafolio-web. La otra opción del encabezado es DARK.

### Terminal

Consola de texto de portafolio-web. Se abre con la tecla T. Comandos: help, projects, skills, about, contact, cv, oak, clear.

### Boot

Pantalla de arranque de portafolio-web, con barra de progreso, saltable con clic o tecla.
