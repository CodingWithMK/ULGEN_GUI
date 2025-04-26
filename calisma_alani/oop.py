class Araba:
    def __init__(self, marka, model, yil):
        self.marka = marka
        self.model = model
        self.yil = yil

    def bilgileri_goster(self):
        print(f"Marka: {self.marka}, Model: {self.model}, Yıl: {self.yil}")
    
    def arac_listesi_olustur(self):
        arac_listesi = list()
        arac_listesi.append(self.marka)
        arac_listesi.append(self.model)
        arac_listesi.append(self.yil)
        return arac_listesi
    

# Nesne oluşturma
araba1 = Araba("Toyota", "Corolla", 2020)
araba2 = Araba("Ford", "Mustang", 2021)

# Nesne bilgilerini gösterme
araba1.bilgileri_goster()
araba2.bilgileri_goster()

# Nesne listesi oluşturma
araba_listesi1 = araba1.arac_listesi_olustur()
araba_listesi2 = araba2.arac_listesi_olustur()
araba_listesi = [araba_listesi1, araba_listesi2]
print(araba_listesi)
