# Procesamiento Distribuido 3PC

## **Descripción**

Realizar el procesamiento de desenfoque (blurring) a una imagen de formato bmp mediante una interfaz gráfica, en la cual el usuario carga la imágen original y elige el número de capas de desenfoque que se desean aplicar.  Para esto utilizaremos una máscara de desenfoque, representada por medio de una matriz, la cual se aplicará a cada píxel de la imagen. El procesamiento de la imagen se implementará de manera paralela a través del número de máscaras indicadas por el usuario.

Además de lo anterior, se nos ha pedido crear una red de computadoras por medio de máquinas virtuales qué se conectarán entre sí con la ayuda de MPICH. Esta implementación permitirá la distribución del procesamiento de la imagen en diferentes nodos de la red, lo que acelerará significativamente el proceso.

Las matrices usadas para el procesamiento de desenfoque comenzarán con un valor de 11x11 en la primera capa de desenfoque y aumentará según el número de capas de elección del usuario hasta llegar a un valor de 104x104 en la capa número 50 de desenfoque. Con la implementación de MPI, se espera obtener resultados mucho más rápidos y eficientes que el procesamiento secuencial.

## **Metodología**

Para la solución propuesta 

1. Asignación de roles: El primer paso fue asignar la computadora que seria la Master tomando en cuenta las características de cada equipo,
2. Preparación de máquinas virtuales: En cada equipo se contaba con una máquina virtual Debian, por lo cual el siguiente paso fue descargar las dependencias necesarias para poder usar mpich con ayuda del tutorial proporcionado[1] .
3. Levantamiento de red: Utilizamos un switch para poder conectar 5 computadoras , excluyendo la computadora de la integrante que se encuentra de manera remota ya que no había manera de conectarla a la red sin tenerla de manera física en el laboratorio. A cada una le asignamos una dirección ip de la red 1.1.1.0 /24.
4. Conexión exitosa con MPICH: Una vez asegurada la conexión de red entre las computadoras, nos encargamos de que todos los slaves (esclavos) pudieran visualizar la carpeta y los archivos creados por el master para asi poder correr el código desarrollado para el desenfoque de la imagen con procesos distribuidos entre los diferentes equipo.
5. Se creó una interfaz gráfica, haciendo uso de Qt designer, en la cual se le permite al usuario hacer drag and drop de la imagen a la que desea aplicar los filtros de desenfoque, así como ingresar la cantidad de filtros de desenfoque que se desean aplicar. 
6. La interfaz gráfica, se convirtió mediante la librería pyuic5 el archivo de Qt Designer a código Python, con el cual se conecta la interfaz gráfica y su funcionalidad de procesamiento de imágenes. 
7. Fue necesario adaptarlo a la lógica de procesamiento de MPICH2, para esto, se asignó un proceso para cada imagen a ser generada, por lo que se usaron 40 procesadores entre las 3 computadoras para crear las 40 imágenes con distintas máscaras de desenfoque. Utilizando 1 proceso por imagen, también ayudó a disminuir la cantidad de ruido que el multiprocesamiento generaba.
8. El usuario puede interactuar con la interfaz gráfica y aplicar la cantidad de capas de desenfoque a la imagen deseada. 

Por la parte del código de procesamiento de la imagen, usamos la misma lógica usada en la actividad pasada. El programa recibe una imagen en formato bmp y regresa 40 imágenes, cada una con una capa de blurring diferente.

El código sigue la siguiente lógica:

1. Se lee el archivo BMP de entrada y se lee su encabezado de 54 bytes, que contiene información sobre el tamaño, ancho y alto de la imagen, entre otros detalles. Se calcula el relleno de la imagen para asegurarse de que cada fila tenga una longitud múltiple de 4 bytes.
2. Se asigna memoria dinámica para almacenar los datos de la imagen en una estructura de píxeles llamada "image_data", utilizando la función malloc.
3. Se paraleliza utilizando las variables que brinda Mpich, básicamente, cada procesador ejecuta el mismo código, por lo que para asignar una máscara diferente a cada imagen se toma el número de proceso y con ese valor como entrada se establece el kernel a calcular.
4. Se genera un nombre de archivo de salida utilizando la variable "n" que va desde 0 hasta 39, y se escribe en la variable "filename", con base en el número de proceso.
5. Se aplica un desenfoque gaussiano a la imagen utilizando un kernel de convolución de tamaño variable. El tamaño del kernel aumenta en 2 unidades con cada iteración del bucle principal, comenzando desde un tamaño de 11x11. Se calcula la suma de los valores del kernel para normalizar el kernel antes de aplicarlo a la imagen.
6. Se escribe el encabezado de 54 bytes de la imagen de salida en el archivo de salida.
7. Se realiza un bucle anidado que recorre todos los píxeles de la imagen de entrada. Para cada píxel, se aplica el kernel de convolución para obtener el valor del píxel desenfocado en los canales de rojo, verde y azul por separado. Luego, se escribe el valor de los canales desenfocados en el archivo de salida.
8. Después de escribir los valores de los píxeles en una fila de la imagen de salida, se escribe el relleno necesario para que la fila tenga una longitud múltiplo de 4 bytes.
9. Se imprime un mensaje de progreso cada 100 filas procesadas.
10. Finalmente, se cierran los archivos de entrada y salida, y se libera la memoria asignada dinámicamente.

![terminal](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/terminal.png)

Para realizar la interfaz gráfica se hizo uso de Qt Designer, la cual permite crear interfaces de usuario. Con esta herramienta, se diseñó y personalizó la interfaz de usuario, agregando dos graphicViews, una para la carga de la imágen y la otra para simular un carrusel para desplegar las imágenes resultantes. Así mismo cuenta con un comboBox que permite al usuario definir la cantidad de capas de desenfoque que se aplicarán a las imágenes. Se tiene un botón de Run, el cual se encarga de triggerear la acción de desenfoque en paralelo y finalmente se tienen 3 pushButton, que cambian de rojo a verde cuando la computadora en cuestión se encuentra en la red y lista para realizar el proceso de desenfoque. Por lo que el sistema, solamente repartirá el trabajo haciendo uso de las computadoras conectadas en ese momento y desplegará esta información en la interfaz. 

Se tienen 2 archivos que conforman la interfaz gráfica. El primero es main.py el cual contiene los componentes y su ubicación en la pantalla principal. El segundo archivo es cess.py el cual contiene las acciones que cada componente debe realizar.  El comportamiento de las funciones en estas últimas es el siguiente:
- hardwarestatus: esta función cambia el color de los botones pushButton, pushButton_4 y pushButton_5 según el estado de los dispositivos. Si están encendidos, el botón se volverá verde, y si están apagados, se volverá rojo.

- dragEnterEvent: es un método que se llama cuando se arrastra un objeto en el graphicsView. Este método comprueba si el objeto que se arrastra es una imagen. Si es así, se acepta la acción y se llama a la función dropEvent.

- dropEvent: es un método que se llama cuando se suelta el objeto en el graphicsView. El método obtiene la ruta de la imagen y llama a la función setImage para establecer la imagen en el graphicsView.

- getMaskNumber: es un método estático que devuelve el número de la máscara de desenfoque actual.

- getFolderImages: es un método estático que obtiene todas las imágenes en la carpeta nueva_blur y las almacena en la variable fileList.

- setImage: es un método que establece la imagen en el objeto Qt especificado.

- imageCarousel: esta función se encarga de mostrar las imágenes en la carpeta nueva_blur. Al hacer clic en los botones back y next, la función cambia la imagen en graphicsView_2.

- continuouslygetFolderImages: esta función se encarga de obtener las imágenes de la carpeta nueva_blur de forma continua hasta que se encuentre una imagen. Una vez que se encuentra una imagen, se llama a la función changeStatus.

- changeStatus: esta función cambia el estado de los botones back, next, run y reset dependiendo de si se ha seleccionado una imagen o no. Si no se ha seleccionado una imagen, los botones se desactivan. Si se ha seleccionado una imagen, los botones se activan.

La interfaz gráfica luce de la siguiente manera: 
![gui_inicial](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/gui_inicial.png)

El programa se ejecuta de la siguiente manera:
![gui_select_mask](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/gui_select_mask.png)

Se arrastra la imagen en formato bmp a la casilla de la izquierda, se selecciona la cantidad de máscaras a procesar y se presiona el boton de run para ejecutar el programa.

El programa después de su ejecución:
![gui_after_execution](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/gui_after_execution.png)

Se muestra la imagen original en la casilla de la derecha y, mediante el uso de las flechas de navegación se puede navegar a través de las imágenes procesadas donde la flecha de la derecha te lleva a la imagen con la siguiente máscara y la flecha de la izquierda muestra la anterior.

Ejecución en consola:
![terminal_executing](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/terminal_executing.png)

Cuando se presiona el botón de run se ejecutan los comandos de consola necesarios para realizar el procesamiento de imágenes y, al final de la ejecución, se imprimen en la terminal todos los procesos junto a la máquina que los ejecutó.

## **Resultados**

A pesar de que todas las computadoras están haciendo uso de una máquina virtual Debian, debido a las diferentes arquitecturas que tienen dos de los equipos, terminamos utilizando solamente tres para la actividad porque la forma de compilación no es compatible. Se utilizaron de la siguiente manera:

1. *Interfaz*: La interfaz permite realizar la cantidad de filtros asignados por el usuario de desenfoque a una imágen, asignando la paralización de procesos entre las máquinas que se encuentren conectadas a la red.
2. *Computadora UB1 (Master)* : Esta computadora fue asignada como la master y cuenta con la dirección IP 1.1.1.1. La interfaz se encarga de asignarle la cantidad de procesos entre las computadoras que estén conectadas. En caso de ser impar, se cargan más procesos a la computadora master.
3. *Computadora UB2 (Slave)* : Esta computadora fue asignada como un slave y cuenta con la dirección IP 1.1.1.2. La interfaz se encarga de asignarle la cantidad de procesos entre las computadoras que estén conectadas. 
4. *Computadora UB4 (Slave)* : Esta computadora fue asignada como un slave y cuenta con la dirección IP 1.1.1.4. No fue utilizada debido a la incompatibilidad con las otras máquinas.
5. *Computadora UB5 (Slave)* : Esta computadora fue asignada como un slave y cuenta con la dirección IP 1.1.1.5. La interfaz se encarga de asignarle la cantidad de procesos entre las computadoras que estén conectadas. En caso de ser impar, se cargan más procesos a la computadora master.

Al realizar pruebas del funcionamiento de la interfaz, notamos que al desconectar una computadora, había un pequeño error en la interfaz gráfica, ya que cuando la conexión ssh a dos hosts hacia timeout, la interfaz gráfica seguía marcando como activos dos hosts, pero la terminal mostraba el mensaje de time out como se puede observar en las imagenes siguientes:

![timed_out](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/timed_out.png)
![gui_to_fix](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/gui_tofix.png)

Para resolver esto, en el código se detectó el error en la lógica de la UI, en el fragmento de código siguiente se evalúa la cantidad de hosts activos (representados por la variable activeHosts), esto es necesario para crear un arreglo que representa los estados de cada host en la interfaz. Sin embargo, se  estaba enviando un arreglo con un host adicional (que simboliza la cantidad de hosts activos), dando así un total de dos hosts activos, cuando debería ser uno. Esto se puede observar en el siguiente fragmento de código:

![codigo](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/codigo.png)

Al cambiar el uno adicional por un 0, el estatus de la pc1 pasa a desconectado como se puede observar en la siguiente imagen. Logrando así una congruencia entre las conexiones exitosas y la información desplegada en la interfaz.

![gui_fixed](https://github.com/KarenRugerioA/ProcesamientoDistribuido3PC/blob/main/imagenes/gui_fixed.png)


## **Conclusiones**

### ***Myroslava Sanchez Andrade***

El uso de la herramienta MPICH para la programación en paralelo permitió hacer la distribución del trabajo del procesamiento de las máscaras de una imagen para su ejecución en múltiples computadoras virtuales. Esto mejoró de manera significativa el rendimiento y el tiempo de procesamiento. Además, la implementación de la interfaz gráfica desarrollada en pyqt facilitó la interacción con el sistema de blurring al evitar el uso de scripts ejecutados manualmente.

Además de una correcta sincronización y balanceo de cargas y el desarrollo de un algoritmo eficiente de desenfoque, otro aspecto importante a considerar es la comunicación entre la interfaz gráfica y el sistema de desenfoque para que funcionen de manera integrada correctamente. Es importante también destacar que el sistema es resiliente ya que aunque una o más máquinas virtuales fallen, el sistema continúa con la ejecución del proceso sin mayor complicación.

Esta actividad me  permitió darme cuenta de la importancia de programar concurrentemente  y con un enfoque en UX para sacar el máximo provecho posible de los recursos de sistemas actuales; sin embargo, hay que tener cuidado con mantener medidas resilientes para ser capaces de dar la mejor experiencia posible al usuario.


### ***María José***

El procesamiento distribuido funciona de manera en la cual nos permite tener varias computadoras trabajando al mismo tiempo para así poder llevar a cabo tareas qué para un solo equipo podrían resultar pesadas y complejas por lo cual también permite reducir el tiempo en el qué estas se llevan a cabo. Después de algunas pruebas se decidió qué la mejor estrategia para poder distribuir los procesos era asignar una imagen por proceso con cargas equilibradas. Con el objetivo de hacerlo más amigable al usuario, se desarrolló una interfaz gráfica con la ayuda de PyQt5 la cual le permite al usuario arrastrar imágenes, escoger la cantidad de capas de desenfoque e incluso visualizar los resultados por medio de un carrusel.  La implementación de la GUI fue un proceso iterativo que involucró la revisión y mejora continua de la interfaz para asegurar que fuera fácil de usar y entender para los usuarios. Al final, la combinación del procesamiento distribuido y la GUI resultó en una aplicación eficiente y fácil de usar para la tarea de procesamiento de imágenes. Por último, esta actividad nos permitió darnos cuenta de que una distribución adecuada de cargas puede ayudar de gran manera a reducir el tiempo de ejecución.


### ***Karen***

Para esta entrega final se realizó una interfaz gráfica haciendo uso de Qt Design, la cual permite una fácil interacción con el usuario ya que le permite al usuario hacer drag and drop de la imagen y elegir la cantidad de capas de desenfoque (desde 1 hasta 50), así como también facilita la visualización de cuántas máquinas se encuentran en la red para realizar el proceso de paralelización. La implementación del algoritmo de desenfoque en imágenes mediante programación paralela demostró ser una técnica altamente efectiva para reducir el tiempo de procesamiento en sistemas con múltiples núcleos de procesamiento. Se realizó la asignación de los procesos por imágen por parte de un equipo considerado como Master a sí mismo y a 2 computadoras (Slave). Lo que resultó en una mayor homogeneidad en los sistemas que ejecutaron los procesos distribuidos y una mayor integridad en las imágenes procesadas. Además, para equilibrar las cargas, en esta nueva implementación se distribuyeron las imágenes, de manera igualitaria, ya que siempre se debe aprovechar al máximo las computadoras conectadas a la red; esta técnica permite reducir significativamente el tiempo de aplicación de desenfoque de imágenes y desplegar de manera estética los resultados del desenfoque de las imágenes.

Los resultados obtenidos confirmaron la fácil interacción con la interfaz gráfica, la escalabilidad del código, ya que funciona con cualquier imagen y se aplica la cantidad de capas deseadas, así mismo se demuestra la eficacia de la implementación del algoritmo de desenfoque mediante programación paralela y la importancia crucial de la homogeneidad de los sistemas en los que se ejecutan los procesos distribuidos para lograr el objetivo de la tarea. Asimismo, se destacó la importancia de la distribución adecuada de las cargas y la minimización de la cantidad de comunicación entre los procesos para obtener un mayor rendimiento.


### ***Marco***

Con esta continuación de el ejercicio previo, pude ver de manera mas clara como la programación paralela ayuda a eficientar procesos de una manera significativa, como pudimos demostrar a la hora de poner en prueba este concepto con el algoritmo de desenfoque.  Además de esto, se implementó una interfaz gráfica con PyQt5 para facilitar la interacción del usuario con el algoritmo de desenfoque. Esta interfaz gráfica permite al usuario seleccionar la imagen de entrada con una simple interacción de drag aand drop, ajustar los parámetros de desenfoque, y visualizar la imagen de salida de  en tiempo real. La implementación de la interfaz gráfica con PyQt5 también permitió que el algoritmo de desenfoque fuera más accesible y fácil de usar para personas sin experiencia en programación, lo que mejoró su usabilidad y experiencia de usuario. En conjunto, la combinación de la programación paralela y la interfaz gráfica con PyQt5 permitió que el algoritmo de desenfoque fuera más eficiente y amigable para el usuario final. Debido a los resultados encontrados, llegué a la conclusión que a la hora de hacer 
programas que realicen tareas complejas, es muy importante tomar en cuenta quien va a ser el usuario final y sus conocimientos sobre las tecnologías seleccionadas, tomandonos el tiempo de crear herramientas que las hagan accesibles, como lo es una interfaz grafica simplificada. 



### ***Salvador***

El procesamiento distribuido es una técnica altamente efectiva que permite a múltiples computadoras trabajar en conjunto para abordar tareas complejas. En el caso estudiado, se examinaron dos enfoques diferentes para la distribución de tareas entre los procesos distribuidos: la división de la imagen en bloques y la asignación de una imagen por proceso con una distribución equilibrada de las cargas. Después de realizar pruebas y evaluaciones cuidadosas, se determinó que la asignación de una imagen por proceso fue la mejor opción, ya que se mantuvo una mayor homogeneidad en los sistemas que ejecutaron los procesos distribuidos, lo que aseguró una mayor integridad en las imágenes procesadas. Además, para equilibrar las cargas, se distribuyeron las imágenes más pesadas a los procesadores con mayor capacidad, lo que permitió reducir significativamente la cantidad de comunicación entre los procesos. En consecuencia, el experimento demostró una reducción del tiempo de ejecución gracias a la distribución adecuada de las cargas mediante el procesamiento distribuido, lo que destaca la importancia crucial de la homogeneidad de los sistemas en los que se ejecutan los procesos distribuidos para lograr el objetivo de la tarea. Para facilitar la interacción de los usuarios con el programa se creó una interfáz gráfica utilizando PyQt5 de manera que el usuario solo interactuara con la GUI y no tuviera que introducir comandos directamente en la consola a la vez que se desplegaban las imagenes procesadas en la misma GUI. Sin duda lo que más esfuerzo le costó al equipo de desarrollo fué el poder configurar correctamente la paquetería PyQt5 para que se pudiera ejecutar en la máquina virtual del master ya que por alguna razón no se detectaba el display y se tuvo que instalar un ambiente virtual de python para que la paquetería funcionara correctamente.




### ***Bryan***
Con el procesamiento distribuido se pueden manejar mejor las cargas entre varias computadoras, con la actividad pasada, se pudo corroborar que el tiempo de procesamiento disminuye considerablemente con la ayuda de otras computadoras. Al integrar la UI, el procesamiento hace mucho más sentido, porque se puede asimilar esta integración con otras aplicaciones usadas en la vida real. Por lo que se adquiere un sentido de valor hacia esta actividad.
Al finalizar esta actividad, se puede concluir que los resultados de esta actividad me han ayudado a comprender mejor toda la configuración que se necesita para crear un cluster y dividir las tareas logrando conectar los resultados con una interfaz gráfica para que un usuario pueda interactuar y disfrutar de los beneficios. Me quedo con mucha satisfacción de haber realizado esta actividad porque me ayudó a comprender mejor los sistemas distribuidos. 


