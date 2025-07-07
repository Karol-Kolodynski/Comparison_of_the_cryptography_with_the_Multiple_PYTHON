import os
import time
import psutil
import threading
from multiprocessing import Pool
from dataclasses import dataclass
from typing import List
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial

# Stałe
ROZMIAR_FRAGMENTU = 2 * 1024 * 1024  # 2MB
OVERLAP_SIZE = 256


# Struktury danych
@dataclass
class KMP_Preprocessed:
    lps: List[int]
    pattern: str


@dataclass
class Metrics:
    count: int
    czas: float
    cpu_usage: float
    ram_usage: int


# Funkcje pomocnicze
def get_cpu_time() -> float:
    return time.process_time()


def get_memory_usage() -> int:
    return psutil.Process().memory_info().rss


def odczytaj_caly_plik(sciezka: str) -> str:
    with open(sciezka, 'rb') as file:
        return file.read().decode(errors='ignore')


def podziel_na_fragmenty(buffer: str) -> List[str]:
    fragmenty = []
    poz = 0
    while poz < len(buffer):
        start = max(0, poz - OVERLAP_SIZE)
        end = min(poz + ROZMIAR_FRAGMENTU, len(buffer))
        fragmenty.append(buffer[start:end])
        poz = end
    return fragmenty


# Implementacja KMP
def przygotuj_wzorzec(slowo: str) -> KMP_Preprocessed:
    m = len(slowo)
    lps = [0] * m
    length = 0

    for i in range(1, m):
        while length > 0 and slowo[i] != slowo[length]:
            length = lps[length - 1]

        if slowo[i] == slowo[length]:
            length += 1
            lps[i] = length
        else:
            lps[i] = 0

    return KMP_Preprocessed(lps, slowo)


def liczba_slow_we_fragmencie(fragment: str, wzorzec: KMP_Preprocessed) -> int:
    if not wzorzec.pattern:
        return 0

    count = 0
    m = len(wzorzec.pattern)
    n = len(fragment)
    i = j = 0

    while i < n:
        if wzorzec.pattern[j] == fragment[i]:
            i += 1
            j += 1

        if j == m:
            count += 1
            j = wzorzec.lps[j - 1]
        elif i < n and wzorzec.pattern[j] != fragment[i]:
            if j != 0:
                j = wzorzec.lps[j - 1]
            else:
                i += 1

    return count


# Implementacje wersji
def liczba_slow_sekwencyjny(sciezka_pliku: str, slowo: str) -> Metrics:
    start_cpu = get_cpu_time()
    start_time = time.time()
    start_mem = get_memory_usage()

    buffer = odczytaj_caly_plik(sciezka_pliku)
    fragmenty = podziel_na_fragmenty(buffer)
    wzorzec = przygotuj_wzorzec(slowo)

    total = sum(liczba_slow_we_fragmencie(frag, wzorzec) for frag in fragmenty)

    end_time = time.time()
    end_cpu = get_cpu_time()
    end_mem = get_memory_usage()

    czas = end_time - start_time
    num_cpus = os.cpu_count() or 1
    cpu_usage = (end_cpu - start_cpu) / (czas * num_cpus) * 100
    ram_usage = end_mem - start_mem

    return Metrics(total, czas, cpu_usage, ram_usage)


def liczba_slow_Watki(sciezka_pliku: str, slowo: str, liczba_watkow: int) -> Metrics:
    start_cpu = get_cpu_time()
    start_time = time.time()
    start_mem = get_memory_usage()

    buffer = odczytaj_caly_plik(sciezka_pliku)
    fragmenty = podziel_na_fragmenty(buffer)
    wzorzec = przygotuj_wzorzec(slowo)

    wyniki = [0] * liczba_watkow
    watki = []
    frag_na_watek = (len(fragmenty) + liczba_watkow - 1) // liczba_watkow

    def worker(id):
        start = id * frag_na_watek
        end = min(start + frag_na_watek, len(fragmenty))
        wyniki[id] = sum(liczba_slow_we_fragmencie(fragmenty[i], wzorzec) for i in range(start, end))

    for i in range(liczba_watkow):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        watki.append(t)

    for t in watki:
        t.join()

    total = sum(wyniki)

    end_time = time.time()
    end_cpu = get_cpu_time()
    end_mem = get_memory_usage()

    czas = end_time - start_time
    num_cpus = os.cpu_count() or 1
    cpu_usage = (end_cpu - start_cpu) / (czas * num_cpus) * 100
    ram_usage = end_mem - start_mem

    return Metrics(total, czas, cpu_usage, ram_usage)


def liczba_slow_Procesy(sciezka_pliku: str, slowo: str, liczba_watkow: int) -> Metrics:
    start_cpu = get_cpu_time()
    start_time = time.time()
    start_mem = get_memory_usage()

    buffer = odczytaj_caly_plik(sciezka_pliku)
    fragmenty = podziel_na_fragmenty(buffer)
    wzorzec = przygotuj_wzorzec(slowo)

    with Pool(liczba_watkow) as pool:
        results = pool.starmap(liczba_slow_we_fragmencie, [(frag, wzorzec) for frag in fragmenty])

    total = sum(results)

    end_time = time.time()
    end_cpu = get_cpu_time()
    end_mem = get_memory_usage()

    czas = end_time - start_time
    num_cpus = os.cpu_count() or 1
    cpu_usage = (end_cpu - start_cpu) / (czas * num_cpus) * 100
    ram_usage = end_mem - start_mem

    return Metrics(total, czas, cpu_usage, ram_usage)


def liczba_slow_ThreadPool(sciezka_pliku: str, slowo: str, liczba_watkow: int) -> Metrics:
    start_cpu = get_cpu_time()
    start_time = time.time()
    start_mem = get_memory_usage()

    buffer = odczytaj_caly_plik(sciezka_pliku)
    fragmenty = podziel_na_fragmenty(buffer)
    wzorzec = przygotuj_wzorzec(slowo)

    with ThreadPoolExecutor(max_workers=liczba_watkow) as executor:
        worker = partial(liczba_slow_we_fragmencie, wzorzec=wzorzec)
        results = list(executor.map(worker, fragmenty))

    total = sum(results)

    end_time = time.time()
    end_cpu = get_cpu_time()
    end_mem = get_memory_usage()

    czas = end_time - start_time
    num_cpus = os.cpu_count() or 1
    cpu_usage = (end_cpu - start_cpu) / (czas * num_cpus) * 100
    ram_usage = end_mem - start_mem

    return Metrics(total, czas, cpu_usage, ram_usage)


def liczba_slow_ProcessPool(sciezka_pliku: str, slowo: str, liczba_watkow: int) -> Metrics:
    start_cpu = get_cpu_time()
    start_time = time.time()
    start_mem = get_memory_usage()

    buffer = odczytaj_caly_plik(sciezka_pliku)
    fragmenty = podziel_na_fragmenty(buffer)
    wzorzec = przygotuj_wzorzec(slowo)

    with ProcessPoolExecutor(max_workers=liczba_watkow) as executor:
        worker = partial(liczba_slow_we_fragmencie, wzorzec=wzorzec)
        results = list(executor.map(worker, fragmenty))

    total = sum(results)

    end_time = time.time()
    end_cpu = get_cpu_time()
    end_mem = get_memory_usage()

    czas = end_time - start_time
    num_cpus = os.cpu_count() or 1
    cpu_usage = (end_cpu - start_cpu) / (czas * num_cpus) * 100
    ram_usage = end_mem - start_mem

    return Metrics(total, czas, cpu_usage, ram_usage)


# Interfejs użytkownika
def liczenie_slow():
    os.system('chcp 65001 > nul' if os.name == 'nt' else '')  # UTF-8 dla Windows

    nazwa_uzytkownika = input("Podaj nazwe uzytkownika: ")
    liczba_watkow = int(input("Podaj ilosc watkow: "))
    liczba_slow = int(input("Podaj ilosc slow do sprawdzenia: "))

    slowa = [input(f"Podaj {i + 1}. slowo: ") for i in range(liczba_slow)]

    sciezka_pliku = input("Podaj nazwe pliku (na pulpicie): ")
    sciezka_pliku = os.path.join("C:\\Users", nazwa_uzytkownika, "Desktop", sciezka_pliku)

    # Inicjalizacja zmiennych dla wszystkich metod
    total_seq = total_wat = total_proc = total_tp = total_pp = 0
    time_seq = time_wat = time_proc = time_tp = time_pp = 0.0
    cpu_seq = cpu_wat = cpu_proc = cpu_tp = cpu_pp = 0.0
    ram_seq = ram_wat = ram_proc = ram_tp = ram_pp = 0

    for slowo in slowa:
        # Wywołanie wszystkich metod
        result_seq = liczba_slow_sekwencyjny(sciezka_pliku, slowo)
        result_wat = liczba_slow_Watki(sciezka_pliku, slowo, liczba_watkow)
        result_proc = liczba_slow_Procesy(sciezka_pliku, slowo, liczba_watkow)
        result_tp = liczba_slow_ThreadPool(sciezka_pliku, slowo, liczba_watkow)
        result_pp = liczba_slow_ProcessPool(sciezka_pliku, slowo, liczba_watkow)

        print(f"\nSlowo: {slowo}")
        print(f"Sekwencyjnie: {result_seq.count} (czas: {result_seq.czas:.2f}s, CPU: {result_seq.cpu_usage:.1f}%, RAM: {result_seq.ram_usage} B)")
        print(f"Wątki: {result_wat.count} (czas: {result_wat.czas:.2f}s, CPU: {result_wat.cpu_usage:.1f}%, RAM: {result_wat.ram_usage} B)")
        print(f"Procesy: {result_proc.count} (czas: {result_proc.czas:.2f}s, CPU: {result_proc.cpu_usage:.1f}%, RAM: {result_proc.ram_usage} B)")
        print(f"ThreadPool: {result_tp.count} (czas: {result_tp.czas:.2f}s, CPU: {result_tp.cpu_usage:.1f}%, RAM: {result_tp.ram_usage} B)")
        print(f"ProcessPool: {result_pp.count} (czas: {result_pp.czas:.2f}s, CPU: {result_pp.cpu_usage:.1f}%, RAM: {result_pp.ram_usage} B)")

        # Agregacja wyników
        total_seq += result_seq.count
        total_wat += result_wat.count
        total_proc += result_proc.count
        total_tp += result_tp.count
        total_pp += result_pp.count

        time_seq += result_seq.czas
        time_wat += result_wat.czas
        time_proc += result_proc.czas
        time_tp += result_tp.czas
        time_pp += result_pp.czas

        cpu_seq += result_seq.cpu_usage
        cpu_wat += result_wat.cpu_usage
        cpu_proc += result_proc.cpu_usage
        cpu_tp += result_tp.cpu_usage
        cpu_pp += result_pp.cpu_usage

        ram_seq += result_seq.ram_usage
        ram_wat += result_wat.ram_usage
        ram_proc += result_proc.ram_usage
        ram_tp += result_tp.ram_usage
        ram_pp += result_pp.ram_usage

    avg = len(slowa)
    print("\nPodsumowanie:")
    print(f"Sekwencyjnie: {total_seq} (czas: {time_seq:.2f}s, średnie CPU: {cpu_seq / avg:.1f}%, RAM: {ram_seq} B)")
    print(f"Wątki: {total_wat} (czas: {time_wat:.2f}s, średnie CPU: {cpu_wat / avg:.1f}%, RAM: {ram_wat} B)")
    print(f"Procesy: {total_proc} (czas: {time_proc:.2f}s, średnie CPU: {cpu_proc / avg:.1f}%, RAM: {ram_proc} B)")
    print(f"ThreadPool: {total_tp} (czas: {time_tp:.2f}s, średnie CPU: {cpu_tp / avg:.1f}%, RAM: {ram_tp} B)")
    print(f"ProcessPool: {total_pp} (czas: {time_pp:.2f}s, średnie CPU: {cpu_pp / avg:.1f}%, RAM: {ram_pp} B)")


if __name__ == "__main__":
    liczenie_slow()