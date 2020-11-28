class Conversion():
    def __init__(self):
        self.operations = []
    def byteConversion(self, value, form, target):
        value = int(value)
        if(form == 'b'):
            byte = value
        elif(form == 'kb'):
            byte = value*2**10
        elif(form == 'mb'):
            byte = value*2**20
        elif(form == 'gb'):
            byte = value*2**30
        elif(form == 'tb'):
            byte = value*2**40
        else:
            byte = value
            
            
        if(target == 'b'):
            return byte
        elif(target == 'kb'):
            return byte/2**10
        elif(target == 'mb'):
            print(byte/2**20)
            return byte/2**20
        elif(target == 'gb'):
            return byte/2**30
        elif(target == 'tb'):
            return byte/2**40

