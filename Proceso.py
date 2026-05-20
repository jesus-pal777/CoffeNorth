import pandas as pd
import json

class LoadData:

  def __init__(self):
    pass
  
  # Método para poder realizar carga de archivo csv
  def Load_CSV(self ,FileCSV):
    try:
      df = pd.read_csv(FileCSV)
      print(f"Se realizó carga de datos correctamente desde archivo csv")
      return df
    except FileNotFoundError :
      print(f"No se encontró el {FileCSV} favor de colocar uno correcto")
      return None
    except Exception as A:
      print(f"Error al cargar el archivo {FileCSV} debido a {A}")
      return None
  

  # Método para poder realizar la carga de Json y aplanarlo
  def Load_Json(self,FileJson):

    """ Hacemos la carga del JSON con la libreria json. Al final optamos por la opción de guardar 
        los DFs generados en una lista para poder realizar la manipulación fuera del objeto.
    """
    
    try:
      with open(FileJson,'r',encoding='utf-8') as j:
        datosCrudos = json.load(j)

        TablasJson = {        
        "dfTiendas" : pd.DataFrame(datosCrudos['tiendas_info']),
        "dfSKU": pd.DataFrame(datosCrudos['sku_mappings']),
        "dfCatalogo":  pd.DataFrame(datosCrudos['catalogo']),
        "dfCorte": pd.DataFrame(datosCrudos['snapshots']) 
        }
        print(f"Se realiazó la carga de datos correctamente del archivo json")
        return TablasJson
    except FileNotFoundError :
      print(f"No se encontró el archivo {FileJson} favor de colocar uno correcto")
      return None
    except Exception as A:
      print(f"Error al cargar el archivo {FileJson} debido a {A} ")
      return None
    
  def AplanadoJson(self, dfJson, NameColumn):
    try:
      
      dfJsonLimpio = pd.json_normalize(dfJson[NameColumn])
      return dfJsonLimpio

    except Exception as E:
      print(f'Se tuvo un problema al realizar el aplanado del json tipo {E}')
      return None
    
  def SegAplanadoJson(self,df,columna):
    try:
        df_Exploratorio = df.explode(columna).reset_index(drop=True)
        df_ExploratorioColumnas =  df_Exploratorio[columna].apply(lambda x: x if isinstance(x, dict) else {}).tolist()
        df_Aplanado = pd.json_normalize(df_ExploratorioColumnas)
        df_AplanadoLimpio = pd.concat([df_Exploratorio.drop(columns = [columna]),df_Aplanado], axis =1)
        return df_AplanadoLimpio
    except Exception as E:
        print(f"Se tuvo un error al realizar el aplanado del json {E}")
        return None

  # Método para poder realizar carga de archivo parquet
  def LoadParquet(self,FileParquet):

    try:
      df = pd.read_parquet(FileParquet)
      print(f"Se realizó carga de datos correctamente con formato Parquet")
      return df
    except FileNotFoundError :
      print(f"No se encontró el {FileParquet} favor de colocar uno correcto")
      return None
    except Exception as A:
      print(f"Error al cargar el archivo {FileParquet} debido a {A} ")
      return None
    

  # Método para realizar úniones
  def UnionIzq(self,tablaIzq,tablaDerecha,keyIzq,keyDerecha):
    dfUnion = pd.merge(
    tablaIzq,
    tablaDerecha,
    left_on = keyIzq,
    right_on= keyDerecha,
    how= 'left'
    )
    return dfUnion
    
  def UnionDer(self,tablaIzq,tablaDerecha,keyIzq,keyDerecha):
    dfUnion = pd.merge(
    tablaIzq,
    tablaDerecha,
    left_on = keyIzq,
    right_on= keyDerecha,
    how= 'right'
    )
    return dfUnion    
  

  # Métodos para la limpieza de datos
  def CleanData(self,tabla,columnas):
    for c in columnas:
      if c in tabla.columns:
        tabla[c] = tabla[c].astype(str).str.strip()
      else:
        print(f"No se encontré la columna {c}")
    return tabla
  
  def CambioInt(self,tabla,columnas):
    for c in columnas:
      if c in tabla.columns:
        tabla[c] = pd.to_numeric(tabla[c], errors ='coerce').fillna(0).astype(int)
      else:
        print(f"No se encontró las columnas en la tabla")
    return tabla
