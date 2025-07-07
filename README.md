# 🐍 KryptoWątki-Python

Platforma badawcza napisana w języku **Python**, służąca do testowania wydajności algorytmów kryptograficznych (AES, RSA) oraz wielowątkowego przetwarzania tekstu. Projekt umożliwia analizę czasu wykonania, zużycia CPU i pamięci RAM w różnych scenariuszach.

---

## 📘 Opis projektu

Celem projektu jest ocena możliwości języka Python w zakresie:
- szyfrowania i deszyfrowania danych,
- przetwarzania tekstu z użyciem wielu wątków (ang. multithreading),
- pomiaru zasobożerności (czas, CPU, RAM),
- porównania wyników w różnych konfiguracjach.

---

## 🔍 Funkcjonalności

### 🛡 Tryb kryptograficzny:
- Obsługa szyfrowania i deszyfrowania z wykorzystaniem AES oraz RSA,
- Możliwość podania własnego tekstu lub generowania losowych danych,
- Konfiguracja: liczba haseł, długość tekstu, długość klucza.

### 🔄 Tryb wielowątkowego przetwarzania tekstu:
- Wyszukiwanie słów kluczowych w pliku tekstowym,
- Możliwość ustawienia liczby wątków, słów do wyszukania i pliku wejściowego,
- Raportowanie wyników i czasów działania.

### 📊 Pomiar wydajności:
- Czas wykonania (real/user/system),
- Zużycie CPU i RAM (przy użyciu biblioteki `psutil`).
