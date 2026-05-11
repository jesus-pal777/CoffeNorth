from Proceso import LoadData
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta


#Creamos el objeto
CargaData = LoadData()

#Carga de Archivo CSV
DataCSV = CargaData.Load_CSV('sales.csv')

CleanCSV = CargaData.CambioInt(DataCSV,['cantidad'])
#print(CleanCSV['monto'].dtype)
CleanCSV_1 = CargaData.CleanData(CleanCSV,['tienda_id','sku','venta_id'])



#Carga de Archivo Json con diccionario de DF
DataJson = CargaData.Load_Json('inventory.json')

dfTiendas = DataJson['dfTiendas']
dfSKU = DataJson['dfSKU']

# Se hizo un analisis previo y se determinnó realizar aplanados del json para poder abrir diccionarios anidados
dfCatalogo = DataJson['dfCatalogo']

dfCatalogoLimpio1 = CargaData.AplanadoJson(dfCatalogo,'productos')
print(f"Evidencia de Diccionario Anidado \n {dfCatalogoLimpio1.head(3)} \n ")

dfCatalogoLimpio2 = CargaData.SegAplanadoJson(dfCatalogoLimpio1,'cost_history')
print(f"Evidencia de df sin diccionarios anidados \n {dfCatalogoLimpio2.head(3)} \n ")

dfCorte = DataJson['dfCorte']



# Carga de Archivo Parquet
DataParquet = CargaData.LoadParquet('ecommerce_orders.parquet')




# Visualización rápida de los DF

"""
print(DataCSV.head(3))
print(DataCSV.columns.to_list())
print(dfTiendas.head(3))
print(dfTiendas.columns.to_list())
print(dfSKU.head(3))
print(dfSKU.columns.to_list())
print(dfCatalogoLimpio2.head(3))
print(dfCatalogoLimpio2.columns.to_list())
print(dfCorte.head(3))
print(dfCorte.columns.to_list())
print(DataParquet.head(3))
print(DataParquet.columns.tolist())
"""


# Top 10 skus




# Cambiamos el valor de la columna y nos aseguramos que sea en formato fecha y hora para nuestro archivo CSV y Parquet
CleanCSV_1['fecha_hora'] = pd.to_datetime(CleanCSV_1['fecha_hora'])
DataParquet['fecha'] = pd.to_datetime(DataParquet['fecha'])

# Realizamos un corte de los últimos 6 meses a partir de la última venta
corteCSV = CleanCSV_1['fecha_hora'].max() - relativedelta(months=6)
corteParquet = DataParquet['fecha'].max() - relativedelta(months=6)

# Se aplica el filtro para ambos archivos y restamos los últimos 6 meses
print(f'\n \n \n \n \n  VENTAS TIENDAS FÍSICAS ÚLTIMOS 6 MESES \n')
dfCSV_ventas6m = CleanCSV_1[CleanCSV_1['fecha_hora'] >= corteCSV].copy()
print(f"Última venta {dfCSV_ventas6m['fecha_hora'].max()} \n")
print(f"Primera venta {dfCSV_ventas6m['fecha_hora'].min()} \n")
print(f"Total de ventas {len(dfCSV_ventas6m)} \n")

print(f' VENTAS TIENDA SHOPIFY ÚLTIMOS 6 MESES \n')
dfParquet_ventas6 = DataParquet[DataParquet['fecha'] >= corteParquet].copy()
print(f"Última venta {dfParquet_ventas6['fecha'].max()} \n")
print(f"Primera venta {dfParquet_ventas6['fecha'].min()} \n")
print(f"Total de ventas {len(dfParquet_ventas6)} \n")


#HACEMOS UNA LIMPIEZA EN EL DF DE SKU
df_SKU_Clean = CargaData.CleanData(dfSKU,['sku_pos','sku_erp'])

#SE VALIDÓ QUE SE TIENEN VALORES NULOS DENTRO DEL DF POR LO QUE 
# LES ASIGNA UN VALOR 
#print(df_SKU_Clean[df_SKU_Clean['sku_erp'] == 'None'])
df_SKU_Clean.loc[df_SKU_Clean['sku_pos'] == 'CN-00006','sku_erp'] = 'ERP-PROV-MX-006-C'
df_SKU_Clean.loc[df_SKU_Clean['sku_pos'] == 'CN-00016','sku_erp'] = 'ERP-PROV-MX-016-C'
df_SKU_Clean.loc[df_SKU_Clean['sku_pos'] == 'CN-00026','sku_erp'] = 'ERP-PROV-MX-026-A'
df_SKU_Clean.loc[df_SKU_Clean['sku_pos'] == 'CN-00036','sku_erp'] = 'ERP-PROV-MX-036-A'
df_SKU_Clean.loc[df_SKU_Clean['sku_pos'] == 'CN-00046','sku_erp'] = 'ERP-PROV-MX-046-A'
#print(df_SKU_Clean.head(5))

#Vamos a dividir sku_erp después de cada "-" (guión)
df_SKU_Clean['divisor'] = df_SKU_Clean['sku_erp'].str.split('-').str[3]

# Unimos las 2 tablas SKU y Catalogo para tener una relación
df_sku_un1 = CargaData.UnionIzq(df_SKU_Clean,dfCatalogoLimpio2,'sku_erp','sku_erp')

df_sku_un1['handle']=df_sku_un1['handle'].fillna(df_sku_un1['categoria'])+'_'+df_sku_un1['divisor'].astype(str)

#Información de SKU actualizada sin valores nulos.
df_sku_info = df_sku_un1[['sku_pos','sku_erp','handle','nombre']].copy()



# ULTIMOS 6 MESES 

dfVentas = dfCSV_ventas6m.groupby('sku').agg({
  'cantidad':'sum',
  'monto':'sum',
}).reset_index()
# Reset index hace sku siga siendo columna

# Se agrega la información cuando se tiene cierto SKU ya que ese no se tiene en el df SKU
dfVentas_un1 = CargaData.UnionIzq(dfVentas,df_sku_info,'sku','sku_pos')
dfVentas_un1.loc[dfVentas_un1['sku'] == 'CN-00001','sku_erp'] = 'ERP-PROV-MX-001-A'
dfVentas_un1.loc[dfVentas_un1['sku'] == 'CN-00001','sku_pos'] = 'CN-00001'
dfVentas_un1.loc[dfVentas_un1['sku'] == 'CN-00001','handle'] = 'comida_caliente_001'
dfVentas_un1.loc[dfVentas_un1['sku'] == 'CN-00001','nombre'] = 'Sándwich Comida Caliente'

# Top venta de información de 10 skus en 6 meses tiendas físicas
dfVentas_un1_6m = dfVentas_un1[['sku','cantidad','sku_erp','nombre']]
print(f"\n \n TOP 10 SKU MÁS VENDIDOS EN 6M TIENDAS FÍSICAS \n {dfVentas_un1_6m.sort_values(by='cantidad', ascending=False).head(10)} \n \n")

# Se agrupa nuestros datos .parquet
dfVentasParquet = dfParquet_ventas6.groupby('product_handle').agg({
  'cantidad':'sum'
}).reset_index()

# Al no tener un sku lo que se hace es dividir la información de nuestro handle recopilando los últimos caracteres 001, 002 , 003 ...
dfVentasParquet_6m = dfVentasParquet[['product_handle','cantidad']]

# Aquí confirmamos que se tiene que conservar la última cadena y se coloca en una nueva columna llamada id
dfVentasParquet_6m['id'] = dfVentasParquet_6m['product_handle'].str.split('-').str[-1]

# Aquí dividmos en cadenas sobre el df de sku
df_sku_info['divisor'] = df_sku_info['sku_erp'].str.split('-').str[3]

# Junatamos nuestras tablas con los valores iguales que en este caso son id y divisor
dfVentasParquet_6m_1 = CargaData.UnionIzq(dfVentasParquet_6m,df_sku_info,'id','divisor')

# Creamos la variable con las columnas que queremos mostrar
dfVentasParquet_6m_2 = dfVentasParquet_6m_1[['sku_pos' , 'cantidad' , 'sku_erp' , 'nombre']]
print(f"\n \n TOP 10 SKU MÁS VENDIDOS EN 6M TIENDA SHOPIFY \n {dfVentasParquet_6m_2.sort_values(by='cantidad', ascending=False).head(10)} \n \n")










# Tiendas con quiebres

# Nos aseguramos que el formato de la fecha sea el correcto así como cambiando a valores númericos la cantidad del stock
dfCorte['fecha'] =pd.to_datetime(dfCorte['fecha'])
dfCorte['cantidad_en_stock'] = pd.to_numeric(dfCorte['cantidad_en_stock'], errors='coerce')

# Se ubica la primer compra (3 meses antes de la última compra)
dfCorte_Tri  = dfCorte['fecha'].max() - relativedelta(months=3)

# Nos quedamos solo con la información de los últimos 3 meses
dfCorte_Tri1 = dfCorte[dfCorte['fecha'] >= dfCorte_Tri].copy()
dfCorte_Tri2 = dfCorte_Tri1[(dfCorte_Tri1['cantidad_en_stock'].isna()) | (dfCorte_Tri1['cantidad_en_stock'] <= 0)].copy()


# Agrupamos nuestra información por tienda_id y por sku y con size vamos realizando una cuenta y lo vamos a guardar en una columna nueva llamda días sin stock
dfCorte_Tri3 = dfCorte_Tri2.groupby(['tienda_id','sku_erp']).size().reset_index(name='dias_sin_stock')

# Queremos solo cuando se tienen más de 3 días sin stock
dfCorte_Tri4 = dfCorte_Tri3[dfCorte_Tri3['dias_sin_stock']>3]

# Creamos una última variable con las tiendas para saber cuales fueron
dfCorte_Tri5 = CargaData.UnionIzq(dfCorte_Tri4,dfTiendas,'tienda_id','tienda_id')

#Creamos una segunda variable para la vista de las tiendas sin stock con el nombre de lo que no se tiene
dfCorte_Tri6 = CargaData.UnionIzq(dfCorte_Tri5,df_sku_un1,'sku_erp','sku_erp')
dfCorte_Tri6.loc[dfCorte_Tri6['sku_erp'] == 'ERP-PROV-MX-001-A','nombre'] = 'Sándwich Comida Caliente'
dfCorte_Tri6.loc[dfCorte_Tri6['sku_erp'] == 'ERP-PROV-MX-001-A','categoria'] = 'comida_caliente'

#Eliminamos valores duplicados. Esto sucede cuando se asocian con otras tablas
dfCorte_Tri7 = dfCorte_Tri6.drop_duplicates(subset=['tienda_id','sku_erp'])

# Creamos una segunda variable para una mejor vista de los datos (con vista de los )
print(f"\n \n TIENDAS SIN STOCK POR MÁS DE 3 DÍAS")
print(f"\n \n{dfCorte_Tri7[['tienda_id','ciudad','sku_erp','nombre','categoria','dias_sin_stock']].sort_values(by='dias_sin_stock',ascending=False).head(10)} \n \n")
print(f" Cantidad de stock fuera por más de 3 días {len(dfCorte_Tri7)} \n \n")





#  Crecimiento por Mes 



# Se cambia el periodo y se transforma a mensual
CleanCSV_1['mes'] = CleanCSV_1['fecha_hora'].dt.to_period('M')

# Generamos la variable con las ventas mensuales
dfVentaMensual = CleanCSV_1.groupby('mes')['monto'].sum().reset_index()

# Se calcula el porcentaje del crecimiento por mes, esto se hace con .pct_change el cual compara la fila actual con la anterior
dfVentaMensual['MoM_%'] = dfVentaMensual['monto'].pct_change() * 100
print(f" CRECIMIENTO MES A MES EN TIENDAS FÍSICA \n {dfVentaMensual.tail(12)} \n \n")


# Como ya se tenía el formato de fecha generado se cambia el periodo y se transforma a mensual
DataParquet['mes'] = DataParquet['fecha'].dt.to_period('M')

# Generamos la variable con las ventas mensuales
dfVentaMensualShopify = DataParquet.groupby('mes')['amount'].sum().reset_index()

# Se cálcula el porcentaje de crecimiento por mes
dfVentaMensualShopify['MoM_%'] = dfVentaMensualShopify['amount'].pct_change()*100
print(f" CRECIMIENTO MES A MES EN TIENDA SHOPIFY \n {dfVentaMensualShopify.tail(12)} \n \n")








# Productos con margen negativo


# Unimos las 2 tablas el csv con las ventas y nuestro catalgo donde tenemos el soporte del sku

dfCombinados = CargaData.UnionIzq(dfCatalogoLimpio2,df_sku_info,'sku_erp','sku_erp')


dfCombinados.loc[dfCombinados['sku_erp'] == 'ERP-PROV-MX-001-A','sku_pos'] = 'CN-00001'
dfCombinados.loc[dfCombinados['sku_erp'] == 'ERP-PROV-MX-001-A','handle'] = 'comida_caliente_001'
dfCombinados.loc[dfCombinados['sku_erp'] == 'ERP-PROV-MX-001-A','nombre'] = 'Sándwich Comida Caliente'

dfCombinados1 =dfCombinados[['sku_erp','nombre','categoria','costo_mxn','sku_pos','handle']]


# Aseguramos que el catálogo tenga los costos más recientes
df_costos_final = dfCombinados1.sort_values('sku_erp').drop_duplicates('sku_pos', keep='last')

# Hacemos el MERGE con tus ventas (CleanCSV_1)
df_fis_margen = pd.merge(
    CleanCSV_1, 
    df_costos_final[['sku_pos', 'nombre', 'costo_mxn']], 
    left_on='sku',      
    right_on='sku_pos',  
    how='left'
)


# 3. Cálculo de Margen Unitario
df_fis_margen['margen_unitario'] = (df_fis_margen['monto'] / df_fis_margen['cantidad']) - df_fis_margen['costo_mxn']


# 4. Filtramos los negativos
reporte_final_P4 = df_fis_margen[df_fis_margen['margen_unitario'] < 0].copy()


dfUnionUlt = CargaData.UnionIzq(reporte_final_P4,df_sku_info,'sku','sku_pos')
dfUnionUlt.loc[dfUnionUlt['sku'] == 'CN-00001','handle'] = 'comida_caliente_001'
dfUnionUlt1 = dfUnionUlt[['tienda_id','sku','handle','margen_unitario']]
dfUnionUlt2 = CargaData.UnionIzq(dfUnionUlt1,dfTiendas,'tienda_id','tienda_id')
dfUnionUlt3 = dfUnionUlt2[['tienda_id','ciudad','sku','handle','margen_unitario']]
print(f'PRODUCTOS CON MARGEN NEGATIVO \n \n {dfUnionUlt3}')


print(DataCSV[['sku','monto']].head(3))
print(dfCatalogoLimpio2[['sku_erp','costo_mxn']].head(3))

