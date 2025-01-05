import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage

def mail_at(konu, icerik, kisi):
    mesaj = EmailMessage()
    mesaj.set_content(icerik)
    mesaj['subject'] = konu
    mesaj['to'] = kisi

    kullanici = "kadiremirgungor7@gmail.com"
    mesaj['from'] = kullanici
    uygulama_sifresi = "--" #google dan alınması gereken 16 karakterlik şifre

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(kullanici, uygulama_sifresi)
    server.send_message(mesaj)

    server.quit()
    print("Bilgilendirme maili gönderildi.")

class IlanTakip:
    def __init__(self, search_url):
        self.search_url = search_url
        self.known_listings = set()

    def get_listings(self):
        print("İlanlar kontrol ediliyor...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.search_url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            listings = []
            for item in soup.select('.searchResultsItem'):
                try:
                    listing_id = item.get('data-id', '')
                    if not listing_id or listing_id in self.known_listings:
                        continue
                        
                    title = item.select_one('.searchResultsTagTitle').text.strip()
                    price = item.select_one('.searchResultsPriceValue').text.strip()
                    location = item.select_one('.searchResultsLocationValue').text.strip()
                    date = item.select_one('.searchResultsDateValue').text.strip()
                    link = f"https://www.sahibinden.com{item.select_one('a')['href']}"
                    
                    listings.append({
                        'id': listing_id,
                        'title': title,
                        'price': price,
                        'location': location,
                        'date': date,
                        'link': link
                    })
                    
                    self.known_listings.add(listing_id)
                    
                except Exception as e:
                    print(f"İlan ayrıştırma hatası: {str(e)}")
                    continue
            
            return listings
            
        except Exception as e:
            print(f"Bağlantı hatası: {str(e)}")
            return []

    def run(self):
        print("\n" + "="*50)
        print("IONIQ 6 Progressive İlan Takip Programı")
        print("="*50)
        print("\nProgram başlatıldı.")
        print("Her saat başı kontrol yapılacak.")
        print("="*50 + "\n")
        
        while True:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"\nYeni kontrol başlatılıyor... (Saat: {current_time})")
            
            new_listings = self.get_listings()
            
            if new_listings:
                print(f"\n{len(new_listings)} Yeni ilan bulundu!")
                
                # Mail içeriğini hazırla
                mail_icerik = "Görmek istediğin mail başlığı:\n\n"
                for listing in new_listings:
                    mail_icerik += f"Başlık: {listing['title']}\n"
                    mail_icerik += f"Fiyat: {listing['price']}\n"
                    mail_icerik += f"Konum: {listing['location']}\n"
                    mail_icerik += f"Tarih: {listing['date']}\n"
                    mail_icerik += f"Link: {listing['link']}\n"
                    mail_icerik += "-" * 50 + "\n"
                    
                    # Konsola da yazdır
                    print("\n" + "-"*50)
                    print(f"Başlık: {listing['title']}")
                    print(f"Fiyat: {listing['price']}")
                    print(f"Konum: {listing['location']}")
                    print(f"Tarih: {listing['date']}")
                    print(f"Link: {listing['link']}")
                
                # Mail gönder
                mail_at("Yeni IONIQ 6 İlanları!", mail_icerik, "ulaşmasını istediğin mail adresi")
            else:
                print("\nYeni ilan bulunamadı.")
            
            print("\nBir sonraki kontrol için 1 saat bekleniyor...")
            time.sleep(3600)  # kontrol sıklığı saniye cinsinden değiştirilebilir.

if __name__ == "__main__":
    search_url = "takip edilmesini istediğin sitenin URL'si. "
    tracker = IlanTakip(search_url)
    tracker.run()