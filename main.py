def main():
    print("Wybierz opcje:")
    print("1. Liczenie słów w pliku")
    print("2. Szyfrowanie RSA/AES")

    try:
        wybor = int(input())
    except ValueError:
        print("Nieprawidlowy wybor.")
        return

    if wybor == 1:
        from liczenie_slow import liczenie_slow
        liczenie_slow()
    elif wybor == 2:
        from rsa_aes import CryptoApp  # Zmiana importu
        crypto_app = CryptoApp()       # Tworzenie instancji klasy
        crypto_app.szyfrowanie()       # Wywołanie metody
    else:
        print("Nieprawidlowy wybor.")

if __name__ == "__main__":
    main()