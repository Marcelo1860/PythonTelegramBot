

import time, datetime
import telepot
from telepot.loop import MessageLoop
import pandas as pd
import numpy as np


df = pd.read_excel('productos.xlsx') #se lee el excel y se carga como dataframe
df.fillna('*',inplace=True)
pro_busc={} # se crea diccionario donde se almacenan el chat_id y el ultimo comando enviado
marc_busc={} # se crea diccionario donde se almacenan el chat_id y el comando de marca enviado

def on_chat_message(msg): #funcion que se activa al mandar un mensaje
    command = msg['text'] # se guarda el contenido del mensaje en command
    #command = command.lower() # se pasa a minusculas 
    content_type, chat_type, chat_id = telepot.glance(msg) # se obtienen varias variables asociadas al mensaje de las cuales se va a usar chat_id
    print('Comando recibido: %s' % command) # se muestra en pantalla 
    print(content_type, chat_type, chat_id)  # se muestra en pantalla 
    print(pro_busc)  # se muestra en pantalla 
    c = '0'# se inicia la variable c con el contenido "0"

   
    now = datetime.datetime.now()
   
    if command == '/start': # si el mensaje escrito es /start se envía un respuesta explicando el bot brevemente
        telegram_bot.sendMessage (chat_id, str("Hola soy Wally"))
        time.sleep(1)
        telegram_bot.sendMessage (chat_id, str("Un asistente Virtual creado por Marcelo"))
        time.sleep(2)
        telegram_bot.sendMessage (chat_id, str("Podes consultar un listado de precio de distintos elementos de pinturería. Que desearías buscar?"))


    elif command == "/buscar_otro_producto": # si el mensaje escrito es /buscar_otro_producto se envia una respuesta orientativa 
                                             # de que "ingrese otro producto" y se elimina el elemento del diccionario que tenia el chat_id de ese usuario
       
        telegram_bot.sendMessage(chat_id, str("Ingrese el producto a buscar"))
        del pro_busc[chat_id]
        del marc_busc[chat_id]
    

    else: #cuando se ingresa cualquier otro comando 
        for elem in pro_busc: # primero se verifica si el chat_id ya esta en el diccionario para saber si es la primera vez que busca el producto
                    if elem == chat_id: #si se encontró el chat_id en el diccionario, se ve si es /ver_resultados o si es otro (suelen ser los numeros de cada producto)
                        if command == "/ver_resultados": #si es /ver_resultados se le da el valor de "result" a c para poder diferenciar luego la salida a mostrar
                            c = 'result'
                        elif command[-1]=="_":
                            c= command
                        else:    # en el otro caso se le asigna a c el valor de command para poder mostrar con mas detalle el producto seleccionado
                            c=command
                            marc_busc[chat_id]=command[1:]
                        command = pro_busc[elem] # en ambos casos para poder filtrar nuevamente df se le asigna el valor del producto previamente guardado a command
                    else: # si no se encuentra el chat_id en el diccionario se le da el valor 0 a c
                        c='0'
        command = command.lower()            
        
    
        try: # para realizar la busqueda se aplica "try" para filtrar errores en caso de que el excel no contenga lo buscado
            command = command.lower() # se pasa a minusculas 
            cont_art = 0 # se inicia un contador para moverse dentro del arreglos art_array
            art_array=['','','','','',''] # se crea el areglo art_array para separar command en varios string y buscar con mejor calidad
            i = 0 # se inicia una variable i para controlar la buqueda del producto
            elementos = 0
            busc_marca = False # boleano que permite saber si se esta buscando en una marca
            palabra_marca=""
            for char in command: # se busca espacios o letras con tilde para ser cambiadas y en caso de no encontrar ninguna se añade ese caracter al elemento acrode del arreglo
                if char ==' ': # cuando se detecta un espacio se aumenta el contador para indicar que hay que separar de string
                    cont_art+=1
                        
                elif char == 'á':
                        art_array[cont_art]= art_array[cont_art] + "a"
                        
                elif char == 'é':
                        art_array[cont_art]= art_array[cont_art] + "e"
                        
                elif char == 'í':
                        art_array[cont_art]= art_array[cont_art] + "i"
                        
                elif char == 'ó':
                        art_array[cont_art]= art_array[cont_art] + "o"
                        
                elif char == 'ú':
                        art_array[cont_art]= art_array[cont_art] + "u"
                

                elif char == "*":
                    busc_marca = True     
                        
                else:
                        art_array[cont_art]= art_array[cont_art] + char
       

            df['Producto']=df['Producto'].str.lower() # se pone en minusculas todas las letras de df para mejorar la busqueda


            filtra = df[['Producto', 'Precio','Marca']].loc[df['Producto'].str.contains(art_array[0])] # se realiza el primer filtrado de df teniendo como criterio el priemr elemento del art_array
            
            elementos = len(filtra.index) # se toma el largo del dataframe resultante para poder mostrar el numero asociado a cada producto
            
            while cont_art >= 0: # se completa la busqueda con todos los elementos del array
                    filtra = filtra[['Producto', 'Precio','Marca']].loc[df['Producto'].str.contains(art_array[i])]
                    cont_art -= 1
                    i+=1
   
                    def aplicarDes(precio): # se aplica el 28% de descuento 
                        descuento = precio * 0.28
                        return(descuento)
                    filtra['Descuento'] = filtra['Precio'].apply(aplicarDes) # se genera colmumna nueva en df

                    def calcularCosto(fila): # se calcula el costo de cada producto
                        result = fila['Precio']-fila['Descuento']
                        result = result * 1.21
                        return(result)
                    filtra['Costo'] = filtra.apply(calcularCosto, axis=1) # se genera colmumna nueva en df

                    def calcularPrecioCont(costo): # se calcla el precio al contado del producto
                        preciocont = costo * 1.4
                        return(round(preciocont))
                    filtra['Precio al contado'] = filtra['Costo'].apply(calcularPrecioCont)# se genera colmumna nueva en df

                    def calcularPrecioTar(preciocont): # se calcula el precio con tarjeta del producto
                        preciotar = preciocont * 1.25
                        return(round(preciotar))
                    filtra['Precio con tarjeta'] = filtra['Precio al contado'].apply(calcularPrecioTar) # se genera colmumna nueva en df
                
                    elementos = len(filtra.index) # se toma el largo del dataframe resultante para poder mostrar el numero asociado a cada producto

            if busc_marca == True:
                if c == 'result':
                    palab = marc_busc[chat_id]
                    #palab = palab.capitalize()
                else:    
                    palab = c[1:]
                    if palab[-1] == "_":
                        busc_marca = False
                        t = palab[:-1]
                        palab = marc_busc[chat_id]
                        #palab = palab.capitalize()
                        print(t)
                    #else:
                        #palab = palab.capitalize()
                for char in palab:
                    if char == "_":
                        char = " "
                    elif char == "*":
                        char = ""      
                    palabra_marca = palabra_marca + char
                print(palabra_marca)
                print(palab)
                filtra= filtra[['Producto', 'Precio','Precio al contado','Precio con tarjeta']].loc[df['Marca'].str.contains(palabra_marca)]  
                elementos = len(filtra.index)
                
            if c != '0': # si c es distinto de 0 es decir que se entra por segunda o tercera vez en la busqueda
                    if c == 'result': # si es igual a result significa que se quiere ver los resultados por lo que se realiza un dataframe con solo el nombre del producto.
                                      #luego se muestra eso y al costado un numero con / para poder enviar respuestas
                        filtra_pro = filtra['Producto']
                        elementos = len(filtra.index)
                        for b in range(0, elementos):                
                            str_tres = filtra_pro.iloc[b]
                            telegram_bot.sendMessage (chat_id,str(str_tres) + ' ' + '/' + str(b) + '_')
                        
                        telegram_bot.sendMessage (chat_id, str('Si desea buscar otro articulo presione /buscar_otro_producto, si desea obtener info de los articulos enlistados presione en el numero'))

                        pro_busc[chat_id] = command     

                    else: #en caso de uqe c tenga otro valor significa que se esta buscando mas detalles de un producto en particular.
                          #se mostrará un mensaje con el nombre, precio al contado y precio con tarjeta de un porducto especifico
                          if busc_marca == True:
                              telegram_bot.sendMessage (chat_id, str('Se encotraron ' + str(elementos) +  ' resultados de busqueda. Para obtener la lista presione /ver_resultados'))
                              telegram_bot.sendMessage (chat_id, str('De lo contrario /buscar_otro_producto'))
                              pro_busc[chat_id] = command 
                          else:  
                                
                                preciofil = filtra[['Producto','Precio al contado','Precio con tarjeta']]
                                
                                if palabra_marca != "":
                                        str_tres = preciofil.iloc[int(t)]
                                        print("si")
                                else:
                                        c=c[:-1]
                                        t = c[1]
                                        largo = len(c)
                                        if largo > 2:
                                            for l in range(2,largo):
                                                t = t + c[l]
                                        str_tres = preciofil.iloc[int(t)]
                                        print("no")

                                # largo = len(palabra_marca)
                                # if largo > 2:
                                #     for l in range(2,largo):
                                #         t = t + palabra_marca[l]
                                
                                telegram_bot.sendMessage (chat_id,str(str_tres))
                                telegram_bot.sendMessage (chat_id, str('Si desea buscar otro articulo presione /buscar_otro_producto, si desea obtener info de los articulos enlistados presione en el numero'))
                    c=='0'
            else: # en caso de que c sea 0 significa que se realiza por primera vez la busqueda
                if elementos >= 30: # si el resultado obtenido presenta mas de 30 elementos se le sugiere al usuario agregar mas informacion a la busqueda
                    marc=filtra.groupby(["Marca"]).agg({'Precio al contado':"mean"})
                    def calcularPrecioRe(preciocont): # se calcula el precio redondeado
                        preciocontre = round(preciocont) 
                        return(preciocontre)
                    marc['Precio al contado'] = marc['Precio al contado'].apply(calcularPrecioRe) # se genera colmumna nueva en df
                    marc['Marca'] = marc.index
                    marc = marc[['Marca','Precio al contado']]
                    def uni_colum(fila): # une el contenido de dos columnas
                        palabra = '/'
                        for char in fila['Marca']:
                                if char == " ":
                                    char = "_"
                                palabra = palabra + char
                        result = palabra + "---> " +  "$" + str(fila['Precio al contado'])
                        return(result)
                    marc_comb= marc.apply(uni_colum, axis=1) # se genera colmumna nueva en df
                    elementos = len(marc.index)
                    marc['Numeros']=np.arange(len(marc))
                    marc.set_index('Numeros',inplace=True)
                    telegram_bot.sendMessage (chat_id,'Se encotraron demasiadas coincidencias')
                    telegram_bot.sendMessage (chat_id,'A continuación se mostrará un listado de las marcas asociadas a ese producto con su precio promedio')
                    for b in range(0, elementos):                
                        str_tres = marc_comb.iloc[b]
                        telegram_bot.sendMessage (chat_id,str(str_tres))
                    pro_busc[chat_id] = command + "*"   
                    telegram_bot.sendMessage (chat_id,'Si no quiere ver las marcas presione /buscar_otro_producto')
                else: # en caso contrario se la avisa la cantidad de resultados obtenidos y que pueden verlos apretando /ver_resultados
                          # si no puede buscar otro producto apretando /buscar_otro_producto
                        telegram_bot.sendMessage (chat_id, str('Se encotraron ' + str(elementos) +  ' resultados de busqueda. Para obtener la lista presione /ver_resultados'))
                        telegram_bot.sendMessage (chat_id, str('De lo contrario /buscar_otro_producto'))
                        pro_busc[chat_id] = command   
        except:# esta excepcion aparece cuando el elemento que se quiere buscar no esta en df.
             
              if elementos > 0:
                  alternativa = art_array[0]
                  if i > 0:
                    for r in range(1, i):
                        alternativa = alternativa + ' ' + art_array[r]            
                  telegram_bot.sendMessage (chat_id, str('Este articulo no se encuentra en nuestra lista pero pero se encontraron resultados de ' + '**'+ alternativa + '**'))
                  telegram_bot.sendMessage (chat_id, str('Ingrese otro articulo que necesite saber'))
              else: 
                  telegram_bot.sendMessage (chat_id, str('Este articulo no se encuentra en nuestra lista' ))
                  telegram_bot.sendMessage (chat_id, str('Ingrese otro articulo que necesite saber')) 
               
def on_callback_query(msg): #funcion disponible para agregar boton
    #chat_id = msg['keyboard']['id']
    query_id, from_id, query_data = telepot.glance(msg, flavor ='callback_query')
    #telegram_bot.sendMessage (chat_id, str('Este articulo no se encuentra en nuestra lista'))
   
    telegram_bot.answerCallbackQuery(query_id,text="no hay info aun")        

   


telegram_bot = telepot.Bot('5214493358:AAFibNHdbuef3b6AKyU_RtrM_CID6kdZlFY') #funcion que hace referencia al bot que usa el programa
print (telegram_bot.getMe())

MessageLoop(telegram_bot,{'chat': on_chat_message,'callback_query':on_callback_query }).run_as_thread() #loop que esta alerta a los mensajes
print( 'Bot corriendo!!')

while 1: # espera de tiempo 
    time.sleep(10)
