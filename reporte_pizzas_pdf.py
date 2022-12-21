 # Importo las librerías necesarias para llevar acabo el programa
from fpdf import FPDF
import pandas as pd
import numpy as np
import re, math
from datetime import datetime
import matplotlib.pyplot as plt

# Creo la clase del pdf
class PDF(FPDF):
    def header(self): # Defino la función que establece la cabecera de las páginas con el logo de la empresa
        self.image('Logo pizzería.png', 155, 5, 50)
    
    def portada(self): # Defino la función que crea la portada
        self.set_font('Times', 'B', 36) # Establezco la fuente y el tamaño de la letra del tipo 
        self.set_y(60) # Defino en que coordenada y comienzo a escribir
        self.cell(0, 40, 'PIZZAS MAVEN', 0, 0, 'C') # Escribo el título de manera centrada y sin recuadrar
        self.ln(20) # Dejo un doble interliniado para escribir el subtítulo
        self.set_font('Times', 'B', 24) # Establezco la fuente y el tamaño de la letra del tipo 
        self.set_text_color(100) # Cambio el color del subtítulo a un gris
        self.cell(0, 30, 'REPORTE EJECUTIVO 2016', 0, 0, 'C') # Escribo el subtítulo de manera centrada y sin recuadrar
        self.image('imagen.png', 55, 120, 100, 90) # Pinto el logo de la empresa 

    def footer(self): # Defino la función que establece el pie de página
        self.set_y(-25)
        self.set_font('Times', 'I', 11) # Escribo en cursiva
        self.set_text_color(50) # Cambio el color a un gris más oscuro
        self.cell(0, 10, 'Elena Ardura Carnicero - Adquisición de Datos', 0, 0, 'C') 
        self.ln(6)
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C') # Escribo el número de página
    
    def titulo(self,num, label): # Defino la función que establece el título de cada apartado
        self.set_font('Times', 'U', 14)
        self.set_text_color(0,0,0)
        self.cell(0, 6, '%d. %s' % (num, label), 0, 0, 'L')
        self.ln(6)

    def texto_apartado(self, texto): # Defino la función que escribe el primer párrafo del apartado 
        self.set_font('Times','', 11)
        self.multi_cell(150, 6, texto)

    def imprimo_apartado(self, num, title, texto): # Defino la función que escribe el primer apartado, creando una página
        self.add_page()
        self.titulo(num, title)
        self.texto_apartado(texto)
    
    def tabla_basica(self,df): # Defino la función que crea una tabla
        ancho_pagina = self.w - 60 # Establezco el ancho de la tabla
        columnas, filas = list(df.columns), list(df.index) # Defino las columnas y las filas de la tabla
        ancho_columna = ancho_pagina / len(columnas) # Defino el ancho de cada columna dividiendo el ancho disponible entre el número de columnas a pintar
        self.set_font('times', 'B', 12)
        self.ln(7) 
        for col in columnas:
            self.cell(ancho_columna, 5, str(col), 1, 0, 'C') # Escribo el nombre de las columnas en negrita
        self.ln()
        self.set_font('times', '', 11)
        for fila in filas:
            for col in columnas:
                self.cell(ancho_columna, 5, str(df.loc[fila, col]), 1, 0, 'C') # Escribo cada entrada de la tabla
            self.ln()        
    
    def grafico_barras(self, x, y, titulo, xlabel, ylabel, nombre):  # Defino la función que pinta un gráfico de barras simple
        plt.figure(1, figsize=(12, 6)) # permite indicar el nº de la figura y las dimensiones (ancho y alto)
        plt.bar(x, y, color = '#01696E') # Defino los datos y de que color quiero que sea la gráfica
        plt.title(titulo) # Establezco el título
        plt.xticks(rotation = 90,  fontsize= 5) # Establezco la orientación y el tamaño del nombre de los datos en el eje horizontal
        plt.xlabel(xlabel) # Establezco el título del eje x
        plt.ylabel(ylabel) # Establezco el título del eje y
        plt.savefig(nombre) # Guardo la imagen creada en la carpeta de manera que luego la podamos utilizar
        plt.clf() # Reinicio los datos de la librería matplotlib
        
def arreglar_dataframes(orders, order_details, pizzas, pizza_types):  # Creo la función que va a formatear los datos para devolverlos como queremos 
    # Establezco todos los formatos de fechas para ir transformando la columna de la fecha
    formatos = ['%B %d %Y', '%b %d %Y', '%Y-%m-%d', '%d-%m-%y %H:%M:%S', '%A,%d %B, %Y', '%a %d-%b-%Y']
    # Junto los df de los orders y los orders_details para poder trabajar con todo a la vez
    order_details = order_details.merge(orders, on = 'order_id')
    # Creo un dataframe con los valores en los que el id de la pizza no es nan
    order_details = order_details[order_details['pizza_id'].notna()]
    # Limpio todos los datos mal puestos de la columna del id de cada pizza sustituyendo los guiones por barras bajas
    # los espacios por barras bajas, los @ por a, los 3 por e y los ceros por o
    order_details['pizza_id'] = order_details['pizza_id'].apply(lambda x: re.sub('-', '_', x))
    order_details['pizza_id'] = order_details['pizza_id'].apply(lambda x: re.sub(' ', '_', x))
    order_details['pizza_id'] = order_details['pizza_id'].apply(lambda x: re.sub('@', 'a', x))
    order_details['pizza_id'] = order_details['pizza_id'].apply(lambda x: re.sub('3', 'e', x))
    order_details['pizza_id'] = order_details['pizza_id'].apply(lambda x: re.sub('0', 'o', x))
    # Limpio todos los datos de la columna de quantity y para ello primero relleno todos los nan con un 1 
    # y para los One / one pongo un 1 y para los two / Two pongo un 2, por último cambio los negativos a positivos
    order_details['quantity'] = order_details['quantity'].fillna(1)
    order_details['quantity'] = order_details['quantity'].apply(lambda x: re.sub('one', '1',  str(x).lower() ))
    order_details['quantity'] = order_details['quantity'].apply(lambda x: re.sub('two', '2', x.lower()))
    order_details['quantity'] = order_details['quantity'].apply(lambda x: abs(int(x))) 
    # Ordeno el datafrmae según el id del pedido para poder establecer las fechas que falten 
    order_details_ord = order_details.sort_values('order_details_id', ascending = True).reset_index()
    order_details_ord['week number'] = None  # Creo una columna que va a guardar el número de la semana
    for fecha in range(0,len(order_details_ord['date'])):
        # Para cada pedido formateo el tipo del dato de la fecha
        try:
            # Intento arreglar la fecha con la funcion fromtimestamp de la libreria datetime
            fecha_arreglada = float(order_details_ord['date'].iloc[fecha])
            fecha_final = datetime.fromtimestamp(fecha_arreglada)
            order_details_ord['date'].iloc[fecha] = fecha_final
        # si salta un error es porque o bien la fecha es un nan o no está en el formato indicado 
        except ValueError as error:
            tipo = 0
            # Para cada uno de los formatos que puede tener una fecha
            while 0 <= tipo < len(formatos):
                try: # Intentamos transformar la fecha en ese formato
                    # Si podemos transformarlo, lo transformamos y lo cambiamos en nuestro dataframe
                    fecha_final = datetime.strptime(order_details_ord['date'].iloc[fecha], formatos[tipo])
                    order_details_ord['date'].iloc[fecha] = fecha_final
                    tipo = -1 # Salgo del bucle
                except: 
                    # Si no es ese tipo probamos con el siguiente hasta probar con todos los tipos
                    tipo += 1
            if tipo != -1: # Si el tipo no es ninguno de los definifos en la lista
                if fecha == 0: # La fecha es la primera del datafrmae establezco como la fecha el uno de enero del
                    # año ya que sabemos que es el primer pedido realizado en el año por haberlo ordenado previamente 
                    fecha_final = datetime.strptime('01-01-2016', '%d-%m-%Y')
                else:
                    # Si no es el primer pedido del año, entonces establecemos la misma fecha que el pedido anterior
                    fecha_final = order_details_ord['date'].iloc[fecha-1]
                order_details_ord['date'].iloc[fecha] = fecha_final
        # Para cada pedido guardo en que semana se realizó
        numero_semana = int(order_details_ord['date'].iloc[fecha].strftime('%W'))
        order_details_ord['week number'].iloc[fecha] = numero_semana
    pizzas = pizzas.merge(pizza_types, on = 'pizza_type_id') # Junto los df con los detalles de cada pizza
    pedidos_informacion = order_details_ord.merge(pizzas, on = 'pizza_id') #Junto todos los datos en uno mismo
    return order_details_ord, pizzas, pedidos_informacion # Devuelvo los dfs transformador y con los datos formateados

def ingredientes_pizzas(pizzas): # Creo la función que guarda en un dataframe qué ingredientes tiene cada pizza
    tipos_pizza = pizzas['pizza_id'].unique().tolist() # Establezco los tipos de pizza que existen en el restaurante
    ingredientes = set() # Creo un set en el que voy a añadir los ingredientes que se pueden añadir a las pizzas
    for i in range(len(pizzas)): 
        # Recorro el dataframe añadiendo a mi set los ingredientes de forma única
        for ing in [ing.strip() for ing in pizzas['ingredients'].iloc[i].split(',')]:
            ingredientes.add(ing)
    matriz = [] # Creo la matriz que va a definir mi dataframe de las pizzas con sus ingredientes
    for fila in range(len(pizzas)): # Para cada fila del df de las pizzas
        tipo = [] 
        for ingrediente in ingredientes:
            # Para cada tipo de pizza guardo un 1 si contiene al ingrediente o un 0 si no
            if ingrediente in [ing.strip() for ing in pizzas['ingredients'].iloc[fila].split(",")]:
                tipo.append(1)
            else:
                tipo.append(0)
        matriz.append(tipo)
    matriz = np.array(matriz)
    # Creo el dataframe en el que las filas son los tipos de pizza (distinguiendo por tamaño) y las columnas son cada uno de los ingredientes
    ingre_pizzas = pd.DataFrame(data = matriz, index = tipos_pizza, columns = [ingrediente for ingrediente in ingredientes])
    return ingre_pizzas

def ingredientes_semana(order_details, ingre_pizzas): # Creo la función que me calcula la cantidad de cada ingrediente por semana
    semanas = []
    multiplicadores = {'s': 1, 'm': 2, 'l': 3} 
    # Establezco que si la pizza es mediana necesite el doble de cantidad que una pizza pequeña y que si es grande necesite el triple
    orders_week = order_details.groupby(by= 'week number') # Divido todos los pedidos por semanas
    for week in orders_week: 
        # Para cada semana creo una copia de la tabla que indica que ingredientes tiene cada pizza para completarla con la semana en cuestion 
        df_nuevo = ingre_pizzas.copy()
        # Creo una tabla de contingencia para contar el número de pizzas de cada tipo que hay según el número por pedido
        contingencia = pd.crosstab(week[1].pizza_id, week[1].quantity)
        indices = contingencia.index # Guardo los nombres de las pizzas
        for indice in indices: 
            # Para cada tipo de pizza guardo el multiplicador, es decir, el valor por el que voy a multiplicar en función del tamaño de la pizza 
            multiplicador = multiplicadores[indice[-1]]
            numero = 0
            columnas = contingencia.columns
            # Calculo el número de pizzas de cada tipo por semana en proporción a si todas fuesen de tamaño pequeño 
            for columna in columnas: 
                numero += (contingencia[columna][indice]) * columna
            # Multiplico la fila del dataframe que guarda que ingredientes contiene cada pizza por el número de pizzas que tengo que hacer esa semana
            df_nuevo.loc[indice] = df_nuevo.loc[indice].mul(multiplicador*numero)
        # Devuelvo una lista con todos los df de los ingredientes por semana
        semanas.append(df_nuevo)
    return semanas, orders_week

def crear_recuento_semana(semanas): # Creo la función que me hace un recuento de los ingredientes por semana
    diccionario = {} 
    for semana in semanas: 
        columnas = semana.columns
        # Para cada semana hago el recuento de cada ingrediente y lo añado  a diccionario que contiene como claves los ingredientes y como valores
        # una lista con la cantidad del ingrediente necesaria para cada semana en función del número de pizzas (cada posicion de la lista es una semana)
        for columna in columnas:
            if columna not in diccionario:
                diccionario[columna] = []
            contador = semana[columna].sum()
            diccionario[columna].append(contador)
    # Devuelvo el diccionario con todos los ingredientes y sus respectivas cantidades
    dict_medias = {}
    for clave in diccionario: # Para cada ingrediente predigo la cantidad necesaria en una semana 
        # Para predecir los ingredientes necesarios por semana hago la media de los necesitados en cada semana del año
        dict_medias[clave] = math.ceil(np.array(diccionario[clave]).mean()) 
    return dict_medias

def extract(): # Creo la función que extrae los datos (la E de mi ETL)
    # Guardo cada archivo de tipo .csv en un dataframe, teniendo en cuenta el encoding y el separador necesario para que lo pueda leer sin problemas
    order_details = pd.read_csv('order_details.csv', sep = ';')
    orders = pd.read_csv('orders.csv', sep = ';')
    pizzas = pd.read_csv('pizzas.csv', sep = ',')
    pizza_types = pd.read_csv('pizza_types.csv', sep = ',', encoding = 'unicode_escape')
    return order_details, orders, pizzas, pizza_types

def load(dict_medias, pedidos_info): # Creo la función que va a cargar la predicción en un archivo pdf
    pdf=PDF('P', 'mm', 'A4') # Creo el pdf en vertical, de tamaño A4 y con las dimensiones en milímetros 
    pdf.alias_nb_pages() # Contador de páginas
    pdf.set_margins(30, 40, 30) # Estbalezco los márgenes
    pdf.add_page() # Añado una página nueva para pintar la portada
    pdf.portada()
    texto1 = "\nEn este apartado analizaremos el número de ingredientes necesarios de cada tipo en función del tamaño de las pizzas. En este caso calculamos el total de ingredientes necesarios de forma que si al pizza es mediana la cantidad de ingredientes necesarios para esa pizza será el doble y si es grande, el triple.\n\nEn la siguiente tabla podemos observar la predicción acerca de la cantidad de cada ingrediente que la empresa va a necesitar en una semana. Para realizar esta predicción se ha calculado la media de las pizzas de cada tipo vendidas en 2016 en una semana y por ende, que cantidad de ingredientes se necesita para hacerlas, por lo que el gráfico solo muestra una aproximación, no es el número exacto."
    capitulo1 = 'INGREDIENTES'
    
    pdf.imprimo_apartado(1, capitulo1, texto1) # Escribo en el pdf el primer apartado
    # Defino el dataframe que me va a permitir hacer el gráfico
    # Creo un dataframe con los ingredientes y el número de pizzas que deberíamos poder hacer con ese ingrediente
    df = pd.DataFrame([[clave, dict_medias[clave]] for clave in dict_medias.keys()], columns=['Ingredientes', 'Nº pizzas en proporción todas s'])
    df = df.sort_values('Nº pizzas en proporción todas s', ascending = False) # Ordeno el df para pintar la gráfica de forma ordenada
    titulo = 'Cantidad de ingredientes en función del número de pizzas en proporción a todas tamaño s' # Establezco el título de la gráfica
    # Creo el gráfico de barras
    pdf.grafico_barras(df['Ingredientes'], df['Nº pizzas en proporción todas s'], titulo, 'Ingredientes', 'Número de pizzas', 'Ingredientes_cantidad')
    # Creo el segundo gráfico de barras
    titulo2 = 'Cantidad de ingredientes en función del número de pizzas en proporción a todas tamaño s (50gr de cada ingrediente/pizza)'
    pdf.grafico_barras(df['Ingredientes'], [numero*50 for numero in df['Nº pizzas en proporción todas s']], titulo2, 'Ingredientes', 'Gramos', 'Ingredientes_cantidad_gramos')

    pdf.tabla_basica(df) # Imprimo una tabla en el pdf con los datos de mi dataframe
    pdf.ln() 
    texto_cantidad= "En el siguiente gráfico podemos observar cuántas pizzas de tamaño pequeño deberíamos poder hacer para cada ingrediente. Como se puede ver la empresa necesitaría comprar ajo (garlic) en las proporciones para hacer un total de 1000 pizzas aproximadamente"
    pdf.set_font('Times','', 11)
    pdf.multi_cell(150, 6, texto_cantidad) # Escribo en el archivo una pequeña explicación de la gráfica
    pdf.image('Ingredientes_cantidad.png', w = 150) # Pego la gráfica creada previamente en el archivo
    pdf.ln()
    texto_gramos = "Equivalentemente al gráfico de barras anterior, en el siguiente podemos observar cuántos gramos de cada ingrediente debe comprar la empresa a la semana. Esta estimación está calculada suponiendo que a cada pizza pequeña se le echan 50 gramos de cada ingrediente. esta proporción es una generalización muy grande ya que una pizza lleva de media de queso en la base 150 gramos y, sin embargo, no llega a 50 gramos de tomate. Por lo tanto, la empresa, que es quien conoce las proporciones de cada ingrediente en la pizza, debería ajustar estos cálculos. Siguiendo esta estimación, como se puede ver, la empresa necesitaría comprar 50.000 gramos de ajo (garlic) aproximadamente."
    pdf.multi_cell(150, 6, texto_gramos) 
    pdf.image('Ingredientes_cantidad_gramos.png', w = 150)
    # Escribo el segundo apartado acerca del número de pizzas vendidas en función del tipo y el tamaño en una semana
    texto2 = "\nEn este apartado analizaremos el número de pizzas de cada tipo en función del tamaño que se predice que la empresa va a vender en una semana.\n\nEn la siguiente tabla podemos observar la predicción acerca del número de pizzas de cada tipo que va a vender la empresa en una semana en total, sin importar el tamaño. Para realizar esta predicción se ha calculado la media de las pizzas de cada tipo vendidas en 2016, por lo que el gráfico solo muestra una aproximación, no es el número exacto."
    capitulo2 = 'TIPO DE PIZZA Y SU TAMAÑO'
    pdf.imprimo_apartado(2, capitulo2, texto2)
    # Creo los dataframes con los datos necesarios para poder pintar las nuevas gráficas
    tipos_pizza = pd.Series(pedidos_info['pizza_type_id'].value_counts().divide(len(pedidos_info['week number'].unique().tolist())).apply(np.ceil)).rename_axis('tipos_pizza')
    tabla_tamaños_pizzas = (pd.crosstab(pedidos_info['pizza_type_id'], pedidos_info['size'])/len(pedidos_info['week number'].unique().tolist())).apply(np.ceil).rename_axis('Tipos pizzas').reset_index()
    tipos_pizza = tipos_pizza.reset_index(name = 'cantidad')
    tabla_tamaños_pizzas = tabla_tamaños_pizzas.reindex(columns = ['Tipos pizzas', 'S', 'M', 'L', 'XL', 'XXL'])
    titulo3 = 'Cantidad de pizzas en función de los distintos tipos'
    # Creo el nuevo gráfico de barras
    pdf.grafico_barras(tipos_pizza['tipos_pizza'], tipos_pizza['cantidad'], titulo3, 'Tipos pizza', 'Cantidad', 'Cantidad_de_cada_tipo_pizza.png')
    # Escribo en el pdf la tabla con los tipos de pizzas y el número total de pizzas pedidas de media de ese tipo en una semana
    pdf.tabla_basica(tipos_pizza)
    pdf.ln()
    texto_cantidad = "En el siguiente gráfico podemos observar cuántas pizzas de los distintos tipos se preparan aproximadamente en la pizzería a la semana. Como se puede ver, el tipo de pizza que más piden los clientes es la 'clásica deluxe' y la que menos la del tipo 'brie-carre'."
    pdf.multi_cell(150, 6, texto_cantidad)
    pdf.image('Cantidad_de_cada_tipo_pizza.png', w = 150) 
    
    pdf.ln()
    # Añado una explicación de la tabla siguiente
    texto_tamaños1 = "A continuación, vamos a analizar el número de pizzas vendido en función del tipo y el tamaño. En esta tabla podemos ver que hay pizzas que se venden en mayor cantidad pero todas en menor tamaño que otras que se venden menos pero en tamaños más grandes."
    pdf.multi_cell(150, 6, texto_tamaños1)
    # Creo en el pdf la tabla que contiene el número de pizzas de cada tipo en función de su tamaño que se piden de media en una semana
    pdf.tabla_basica(tabla_tamaños_pizzas)
    pdf.ln()
    texto_tamaños2 = "Basándonos en la tabla anterior, podemos observar un gráfico de barras en función de los tipos de las pizzas pedidas y el tamaño. el gráfico presenta una leyenda que muestra cada color siendo el menor tamaño el color más oscuro y el mayor tamaño el más claro. Podemos ver que, por ejemplo, la pizza 'cinco quesos' solo se vende en tamaño grande (L) mientras que la pizza 'big_meat' solo se vende en tamaño pequeño (S) pero en mayor cantidades."
    pdf.multi_cell(150, 6, texto_tamaños2)
    # Ordeno los datos de manera correcta para poder pintar el gráfico de barras apiladas tal y como quiero
    grupos = tabla_tamaños_pizzas.iloc[:,0]
    datos_matriz = tabla_tamaños_pizzas.iloc[:,1:].to_numpy().transpose()
    # Establezco los colores de las barras en función del tamaño
    colores = ['#014D50', '#01696E', '#01969D', '#02AEB6', '#02D7E2']
    # Al ser un gráfico de barras apilado no creo la gráfica con la función si no que lo hago directamente aquí
    plt.figure(1, figsize=(12, 6))
    for i in range(datos_matriz.shape[0]):
        # Por cada columna imprimo una barra superpuesta sobre la anterior acerca de cada tipo de pizza y así poder ver el total de pizzas de cada tipo en función del tamaño
        plt.bar(grupos, datos_matriz[i], bottom = np.sum(datos_matriz[:i], axis = 0), color = colores[i], label = tabla_tamaños_pizzas.columns[i+1] )
    # Establezco las características del gráfico
    plt.title('Cantidad de pizzas en función de los distintos tipos y tamaños')
    plt.xticks(rotation = 90,  fontsize= 5)
    plt.ylim(0, 45)
    plt.xlabel('Tipos de pizzas')
    plt.ylabel('Cantidad')
    plt.legend() # Creo una legenda para saber que tamaño representa cada color
    plt.savefig('Tipos_pizzas_tamaño.png')
    pdf.image('Tipos_pizzas_tamaño.png', w = 150)

    pdf.output('reporte_ejecutivo_2016.pdf', 'F') # Exporto el pdf
    
if __name__ == "__main__":
    order_details, orders, pizzas, pizza_types = extract() # Llamo a extract para extraer todos los datos 
    # LLamo a la función que me formatea los dataframes y los datos 
    order_details, pizzas, pedidos_info = arreglar_dataframes(orders, order_details, pizzas, pizza_types) 
    ingre_pizzas = ingredientes_pizzas(pizzas) # Llamo a la función que me genera el dataframe con los ingredientes que contiene cada pizza
    # Llamo a la función que me genera un df por cada semana con los ingredientes necesarios para dicha semana
    semanas, orders_week = ingredientes_semana(order_details, ingre_pizzas) 
    # Creo el diccionario que contiene para cada ingrediente una lista con la cantidad necesaria para cada semana
    diccionario = crear_recuento_semana(semanas) 
    # LLamo a load para hacer la predicción y cargarsela al cliente en un archivo pdf
    load(diccionario, pedidos_info)
