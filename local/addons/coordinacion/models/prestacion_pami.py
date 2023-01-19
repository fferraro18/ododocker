class PrestacionPami:
    def __init__(self, id, descripcion, duracion):
        self.id = id
        self.descripcion = descripcion
        self.duracion = duracion
    
    def __str__(self):
        return f"cod: {self.id} - {self.descripcion} duracion: {self.duracion}"
    
    def getDuracion(self):
        return self.duracion

    # def __cmp__(self, other):
    #     return gt(self.duracion, other.duracion)