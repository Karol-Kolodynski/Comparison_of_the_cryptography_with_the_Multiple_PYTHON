import os
import random
import time
from Crypto.Cipher import AES
from Crypto.Util import Counter
import rsa
import rsa.pkcs1
import psutil


class CryptoApp:
    def __init__(self):
        random.seed(time.time())

    def EncryptDecryptAES(self, plaintext, keySize):
        if keySize not in [128, 192, 256]:
            print("Nieprawidłowy rozmiar klucza AES.")
            return

        try:
            key_length = keySize // 8
            key = os.urandom(key_length)
            iv = os.urandom(16)

            plaintext_bytes = plaintext.encode('utf-8')

            ctr = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            ciphertext = cipher.encrypt(plaintext_bytes)

            ctr_dec = Counter.new(128, initial_value=int.from_bytes(iv, byteorder='big'))
            cipher_dec = AES.new(key, AES.MODE_CTR, counter=ctr_dec)
            recovered_bytes = cipher_dec.decrypt(ciphertext)

            recovered = recovered_bytes.decode('utf-8')

            print("Tekst oryginalny:", plaintext)
            print("Klucz AES (hex):", key.hex())
            print("Wektor IV (hex):", iv.hex())
            print("Zaszyfrowany tekst (hex):", ciphertext.hex())
            print("Tekst odszyfrowany:", recovered)

            if plaintext != recovered:
                print("Błąd: Tekst odszyfrowany różni się od oryginalnego!")
                return False

            return True

        except Exception as e:
            print("Błąd podczas przetwarzania AES:", e)
            return False

    def EncryptDecryptRSA(self, plaintext, key_size_bits):
        if key_size_bits not in {512, 1024, 2048, 4096}:
            print("Nieprawidłowa długość klucza RSA. Dopuszczalne wartości: 512, 1024, 2048, 4096 bitów")
            return

        try:
            publicKey, privateKey = rsa.newkeys(key_size_bits)
        except Exception as e:
            print("Błąd generacji klucza RSA:", e)
            return

        str_private_key = privateKey.save_pkcs1().hex()
        str_public_key = publicKey.save_pkcs1().hex()

        print("Prywatny klucz RSA (szesnastkowo):\n" + str_private_key)
        print("Publiczny klucz RSA (szesnastkowo):\n" + str_public_key)
        print("Tekst oryginalny:", plaintext)

        try:
            ciphertext = rsa.encrypt(plaintext.encode(), publicKey)
            encoded = ciphertext.hex()
            print("Zaszyfrowany tekst (w heksadecymalnym):", encoded)

            decoded_cipher = bytes.fromhex(encoded)
            decrypted = rsa.decrypt(decoded_cipher, privateKey).decode()
            print("Tekst odszyfrowany:", decrypted)

            if plaintext != decrypted:
                print("Uwaga: Tekst odszyfrowany różni się od oryginalnego!")
                return False

            return True

        except Exception as e:
            print("Błąd podczas przetwarzania RSA:", e)
            return False

    def generateRandomText(self, min_length, max_length):
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(characters, k=length))

    def PrintResourceUsage(self, cpu_usage, memory_used):
        print(f"Uzycie procesora: {cpu_usage:.2f}%")
        print(f"Uzycie pamieci RAM: {memory_used} B")

    def szyfrowanie(self):
        print("Wybierz rodzaj szyfrowania: RSA lub AES")
        choice = input().lower()

        proc = psutil.Process()
        start_user = proc.cpu_times().user
        start_system = proc.cpu_times().system
        start_time = time.time()
        start_mem = proc.memory_info().rss

        if choice in ['rsa', 'r']:
            print("Czy chcesz podac wlasny tekst? (T/N)")
            yn = input().upper()

            if yn == 'T':
                plaintext = input("Podaj tekst: ")
                bytes = int(input("Podaj dlugosc klucza (512, 1024, 2048 lub 4096): "))
                while bytes < 512 or bytes > 4096:
                    bytes = int(input("Nieprawidlowa dlugosc! Podaj wartosc 512-4096: "))

                self.EncryptDecryptRSA(plaintext, bytes)
            else:
                ilosc = int(input("Podaj ilosc hasel: "))
                while ilosc <= 0:
                    ilosc = int(input("Ilosc musi byc wieksza od 0! Podaj ponownie: "))

                bytes = int(input("Podaj dlugosc klucza (512, 1024, 2048 lub 4096): "))
                while bytes < 512 or bytes > 4096:
                    bytes = int(input("Nieprawidlowa dlugosc klucza RSA. Dlugosc musi byc 512-4096 bitow: "))

                min_len = int(input("Podaj minimalna dlugosc tekstu (>=1): "))
                max_len = int(input("Podaj maksymalna dlugosc tekstu: "))
                while min_len < 1 or max_len < min_len:
                    print("Nieprawidlowy zakres! Podaj ponownie:")
                    min_len = int(input("Minimalna dlugosc (>=1): "))
                    max_len = int(input(f"Maksymalna dlugosc (>= {min_len}): "))

                for _ in range(ilosc):
                    text = self.generateRandomText(min_len, max_len)
                    self.EncryptDecryptRSA(text, bytes)

        elif choice in ['aes', 'a']:
            print("Czy chcesz podac wlasny tekst? (T/N)")
            yn = input().upper()

            if yn == 'T':
                plaintext = input("Podaj tekst: ")
                keySize = int(input("Podaj rozmiar klucza (128, 192 lub 256): "))
                while keySize not in [128, 192, 256]:
                    keySize = int(input("Nieprawidlowa dlugosc klucza AES. Dopuszczalne wartosci: 128, 192, 256: "))

                self.EncryptDecryptAES(plaintext, keySize)
            else:
                ilosc = int(input("Podaj ilosc hasel: "))
                while ilosc <= 0:
                    ilosc = int(input("Ilosc musi byc wieksza od 0! Podaj ponownie: "))

                keySize = int(input("Podaj rozmiar klucza (128, 192 lub 256): "))
                while keySize not in [128, 192, 256]:
                    keySize = int(input("Nieprawidlowa dlugosc klucza AES. Dopuszczalne wartosci: 128, 192, 256: "))

                min_len = int(input("Podaj minimalna dlugosc tekstu (>=1): "))
                max_len = int(input("Podaj maksymalna dlugosc tekstu: "))
                while min_len < 1 or max_len < min_len:
                    print("Nieprawidlowy zakres! Podaj ponownie:")
                    min_len = int(input("Minimalna dlugosc (>=1): "))
                    max_len = int(input(f"Maksymalna dlugosc (>= {min_len}): "))

                for _ in range(ilosc):
                    text = self.generateRandomText(min_len, max_len)
                    self.EncryptDecryptAES(text, keySize)
        else:
            print("Nieprawidlowy wybor szyfrowania!")
            return

        end_user = proc.cpu_times().user
        end_system = proc.cpu_times().system
        end_time = time.time()
        end_mem = proc.memory_info().rss

        cpu_user = end_user - start_user
        cpu_system = end_system - start_system
        total_cpu = cpu_user + cpu_system
        wall_time = end_time - start_time
        cpu_usage_percent = (total_cpu / wall_time) * 100 if wall_time > 0 else 0

        print("\n=== Statystyki wydajnosci ===")
        print(f"Czas wykonania: {wall_time:.2f} sekund")
        self.PrintResourceUsage(cpu_usage_percent, end_mem)


if __name__ == "__main__":
    app = CryptoApp()
    app.szyfrowanie()