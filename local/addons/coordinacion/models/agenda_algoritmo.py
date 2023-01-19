import datetime

SEMANAL = 0
QUINCENAL = 1
MENSUAL = 2

def generar_agenda(fecha_inicio, fecha_fin, condicion, tipo_agenda):
    delta = datetime.timedelta(days=1)
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        agregarRegistro = False
        if tipo_agenda == SEMANAL:
            agregarRegistro = cumple_condicion_semanal(fecha_actual, condicion)
        if (tipo_agenda == QUINCENAL) | (tipo_agenda == MENSUAL):
            agregarRegistro = cumple_condicion_quincenal(fecha_actual, condicion)
        if(agregarRegistro):
            agregar_registro_agenda(fecha_actual)
        fecha_actual += delta

def cumple_condicion_semanal (fecha,condicion):
      for dia_selecionado in condicion:
            if fecha.weekday() == dia_selecionado:
                return True
      return False

def cumple_condicion_quincenal(fecha, condicion):
    for dia_selecionado in condicion:
        if fecha == dia_selecionado:
            return True
    return False

def agregar_registro_agenda(dia):
    print('Se agrega registro para:' + dia.strftime('%a, %d %b %Y'))

# generar_agenda(datetime.datetime(2022, 10, 1), datetime.datetime(2022, 10,31),[0,2,4], SEMANAL )
# generar_agenda(datetime.datetime(2022, 10, 1), datetime.datetime(2022, 10,31),[datetime.datetime(2022, 10,1),datetime.datetime(2022, 10,16)], QUINCENAL )
generar_agenda(datetime.datetime(2022, 10, 1), datetime.datetime(2022, 10,31),[datetime.datetime(2022, 10,16)], MENSUAL )





