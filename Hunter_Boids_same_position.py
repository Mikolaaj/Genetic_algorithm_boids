import tkinter as tk # Biblioteka GUI dla języka Python, umożliwia tworzenie interfejsów użytkownika (nazwa jako tk)
import math # Biblioteka matematyczna
import random #Biblioteka do generowania liczb losowych

#Klasa ta reprezentuje szkielet obiektu
class Creature:
    def __init__(self, canvas, x, y, color, sensing_radius, direction, speed): #Konstruktor, inicjalizacja obiektu z określonymi parametrami
        self.canvas = canvas #zmienna do naniesienia na plansze
        self.id = canvas.create_oval(x, y, x+20, y+20, fill=color) #Stworzenie okregu na planszy o danych parametrach
        self.direction = direction #Zmienna kierunku
        self.speed = speed #Zmienna prędkości
        self.sensing_radius = sensing_radius #Zmienna strefy czucia
        self.sensing_circle = canvas.create_oval(x-1, y-1, x+1, y+1, outline='gray') #Stworzenie strefy czucia na plaszny
        self.arrow = canvas.create_line(x, y, x, y, arrow=tk.LAST) #Zmienna do wizualizacji kierunku

    def move(self): #Zawijanie ekranu
        dx = self.speed * math.cos(math.radians(self.direction)) #Zmiana położenia w osi X
        dy = self.speed * math.sin(math.radians(self.direction)) #Zmiana położenia w osi Y
        x1, y1, x2, y2 = self.canvas.coords(self.id) #Pobranie współrzędnych lewej gónej i prawej dolnej

        #Zawijanie ekranu
        new_x1 = (x1 + dx) % self.canvas.winfo_width() #nowa współrzędna lewa górna x1
        new_y1 = (y1 + dy) % self.canvas.winfo_height() #nowa współrzędna lewa górna y1
        new_x2 = (x2 + dx) % self.canvas.winfo_width() #nowa współrzędna prawa górna x1
        new_y2 = (y2 + dy) % self.canvas.winfo_height() #nowa współrzędna prawa górna y1

        self.canvas.coords(self.id, new_x1, new_y1, new_x2, new_y2) #Ustawienie nowych współrzędnych
        self.canvas.move(self.arrow, new_x1 - x1, new_y1 - y1) #Dostosowanie strzałki pokazującej kierunek
        self.update_sensing_radius() #aktualizacja strefy czucia

    def update_sensing_radius(self): #Funkcja aktualizująca strefe czucia
        x1, y1, x2, y2 = self.canvas.coords(self.id) #Pobranie współrzędnych lewej gónej i prawej dolnej
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2 #Obliczanie środka obiektu
        self.canvas.coords(self.sensing_circle, center_x - self.sensing_radius, center_y - self.sensing_radius,
                            center_x + self.sensing_radius, center_y + self.sensing_radius) #Aktualizacja współrzędnych strefy czucia 
        arrow_length = 20 #Długość strzałki
        arrow_end_x = center_x + arrow_length * math.cos(math.radians(self.direction)) #Obliczenie nowej współrzędnej x dla końca strzałki na podstawie kierunku obiektu 
        arrow_end_y = center_y + arrow_length * math.sin(math.radians(self.direction)) #Obliczenie nowej współrzędnej y dla końca strzałki na podstawie kierunku obiektu 
        self.canvas.coords(self.arrow, center_x, center_y, arrow_end_x, arrow_end_y) #Aktualizacja współrzędnych strzałki na płótnie

#Klasa Boid która dziedziczy z klasy Creature
class Boid(Creature):
    def __init__(self, canvas, x, y, sensing_radius): #Konstruktor klasy boid
        direction = random.uniform(0, 360) #Zmienna kierunku generowana losowo
        speed = random.uniform(1, 3) #Zmienna prędkości generowana losowo
        super().__init__(canvas, x, y, 'blue', sensing_radius, direction, speed) #Wywołanie funkcji z klasy Creature i ustawienie wartości danych zmiennych
        self.x = x #Współrzędna X
        self.y = y #Współrzędna Y
        self.is_caught = False #Zmienna sprawdzająca czy boid jest złapany czy nie
        self.hunter_who_caught_me = None #Zmienna pamiętająca który Hunter złapał boida

    def follow_hunter(self, hunter): #Obsługa ruchu boida w kierunku łowcy
        if not self.is_caught: #Czy zostałzłapany
            boid_x, boid_y, _, _ = self.canvas.coords(self.id) #Pobranie współrzędnych Boida
            hunter_x, hunter_y, _, _ = self.canvas.coords(hunter.id) #Pobranie współrzędnych Huntera

            distance = math.sqrt((boid_x - hunter_x) ** 2 + (boid_y - hunter_y) ** 2) #Liczenie odległości między Boidem a Hunterem

            if distance <= float(self.sensing_radius): #Czy w strefie Boida jest Hunter
                angle = math.atan2(boid_y - hunter_y, boid_x - hunter_x) #Obliczanie kąta między Boidem a Hunterem
                self.direction = math.degrees(angle) #Zmiana kierunku na obliczony kąt
                self.speed = hunter.speed #Nastawienie prędkości na prędkośc Huntera
                self.is_caught = True #Ze został złapany
                self.hunter_who_caught_me = hunter #Przypisanie Boida do łowcy
                self.change_color() #Zmiana Koloru 
                self.hunter_who_caught_me.zlapane_boidy += 1 #Zwiększenie ilosci złapanych

    def change_color(self): #Funkcja do zmiany koloru
        self.canvas.itemconfig(self.id, fill='green')

    def follow_caught_hunter(self): #Obsługa ruchu boida złapanego przez łowce
        if self.is_caught and self.hunter_who_caught_me: #Czy Boid został złapany i czy istnieje łowca który go złapał
            hunter_x, hunter_y, _, _ = self.canvas.coords(self.hunter_who_caught_me.id) #Pobranie aktulanych współrzędnych łowcy
            angle = math.atan2(hunter_y - self.y, hunter_x - self.x) #Obliczanie kąta między boidem a hunterem
            self.direction = math.degrees(angle) #Ustawienie kierunku na wyliczony kąt
            self.speed = self.hunter_who_caught_me.speed #Przypisanie predkosci huntera do boida
            self.move() #wywołanie funkcji ruchu 
            self.x, self.y, _, _ = self.canvas.coords(self.id) #aktualizacja współrzędncyh boida

#Klasa Hunter która dziedziczy z klasy Creature
class Hunter(Creature): 
    def __init__(self, canvas, x, y, sensing_radius): #Konstruktor
        direction = random.uniform(0, 360) #Zmienna kierunku, gerneowana losowo
        speed = random.uniform(1, 3) #Zmienna predkosci, generowana losowo
        super().__init__(canvas, x, y, 'red', sensing_radius, direction, speed) #Wywołanie konstruktora z klasy Creature
        self.base_speed = speed #Zapisanie zmiennej predkosci 
        self.zlapane_boidy = 0 #Liczba złapanych boidów
        self.traveled_distance = 0  #Liczba przebytej drogi
        self.fitness = 0 #Wspolczynnik fitness
        self.iterations_in_rotation = 0 #Ilosc iteracji

    def update_traveled_distance(self, distance): #Funkcja aktualizujaca przebyta droge
        self.traveled_distance += distance #Dodanie drogi do drogi calkowitej

    def update_fitness(self): #Funkcja aktualizujaca wspolczynnik fitness
        if self.iterations_in_rotation > 0: #Sprawdzenie czy Hunter zrobil przynajmniej jedna rotacje
            self.fitness = self.traveled_distance / self.iterations_in_rotation #Obliczanie zmiennej fitness

    def chase_boid(self, boid): #Funkcja scigania boida
        if not boid.is_caught: #Sprawdzenie czy boid zostal zlapany
            boid_x, boid_y, _, _ = self.canvas.coords(boid.id) #pobranie wspolrzednych boida
            hunter_x, hunter_y, _, _ = self.canvas.coords(self.id) #pobranie wspolrzednych Huntera

            distance = math.sqrt((boid_x - hunter_x) ** 2 + (boid_y - hunter_y) ** 2) #Liczenie odleglosci miedzy boidem a Hunterem

            if distance <= self.sensing_radius: #Sprawdzenie czy boid jest w strefie czucia Huntera
                angle = math.atan2(boid_y - hunter_y, boid_x - hunter_x) #Liczenie kąta między Hunterem a boidem 
                self.direction = math.degrees(angle) #Zmiana kierunku na wyliczony
                self.speed = min(self.speed + 0.5, self.base_speed * 2) #Zwiekszenie predkosci Huntera
                self.update_traveled_distance(distance)  #Aktualizuj przebytej drogi
                self.update_fitness()  #Aktualizacja wspolczynnika fitnes
                self.move() #Ruch Huntera w danym kierunku(czyli na boida)

    def move(self): #Zawijanie ekranu
        dx = self.speed * math.cos(math.radians(self.direction)) #Obliczanie przesuniecia w osi X 
        dy = self.speed * math.sin(math.radians(self.direction)) #Obliczanie przesuniecia w osi Y
        x1, y1, x2, y2 = self.canvas.coords(self.id) #Pobieranie aktualnych wspolrzednych Huntera

        #Zawijanie ekranu
        new_x1 = (x1 + dx) % self.canvas.winfo_width() #Obliczanie nowej lewej wspolrzednej x1
        new_y1 = (y1 + dy) % self.canvas.winfo_height() #Obliczanie nowej lewej wspolrzednej y1
        new_x2 = (x2 + dx) % self.canvas.winfo_width() #Obliczanie nowej prawej wspolrzednej x2
        new_y2 = (y2 + dy) % self.canvas.winfo_height() #Obliczanie nowej prawej wspolrzednej y2

        self.canvas.coords(self.id, new_x1, new_y1, new_x2, new_y2) #Ustawienie nowych wspołrzędnych
        self.canvas.move(self.arrow, new_x1 - x1, new_y1 - y1) #Przesunięcie strzalki kierunku
        self.update_sensing_radius() #Aktualizacja strefy czucia
        self.update_traveled_distance(math.sqrt(dx**2 + dy**2))  #Aktualizacja drogi
        self.update_fitness()  # Aktualizuj współczynnika fitness

    def follow_caught_boids(self, boids):
        for boid in boids: #Iteracja po boidach
            if boid.is_caught and boid.hunter_who_caught_me == self: #Czy boid został złapany
                boid.follow_caught_hunter() #Boid leci za hunterem
                self.speed = self.base_speed # Przywrocenie bazowej prędkości huntera po złapaniu boida

    def get_fitness(self): 
        return self.fitness #Zwaraca fitness
    
    def count_boids_in_sensing_area(self, boids):
        count = 0 #Liczba boidow w strefie czucia Huntera
        distances = []  # Lista odległości pomiędzy łowcą a boidami w strefie czucia

        hunter_x, hunter_y, _, _ = self.canvas.coords(self.id) #Aktualne wspolrzedne Huntera

        for boid in boids: #Iteracja po boidach
            if not boid.is_caught: #Czy boid nie został złapany
                boid_x, boid_y, _, _ = self.canvas.coords(boid.id) #Aktualne wspolrzedne boida 
                distance = math.sqrt((boid_x - hunter_x) ** 2 + (boid_y - hunter_y) ** 2) #Obliczanie odleglosci pomiedzy Hunterem i boidem

                if distance <= self.sensing_radius: #Czy boid jest w strefie czucia Huntera
                    count += 1 #Zwiekszenie ilosci boidow w strefie czucia
                    distances.append(distance) #dodanie drogi do listy drog

        return count, distances #Zwracanie liczby boidów w strefie czucia oraz listę odległości między łowcą a boidami w tej strefie

#Klasa służąca do wyświetlania interfejsu użytkownika
class SimulationApp:
    def __init__(self, root): #konstruktor
        self.root = root #przyspianie okna głównego
        self.root.title("Boids and Hunters Simulation") #Tytuł okna

        # Dodanie obszaru informacji na lewej stronie planszy
        self.info_canvas = tk.Canvas(root, width=200, height=600, bg='lightgray')
        self.info_canvas.pack(side=tk.LEFT, padx=10)

        # Dodanie obszaru informacji na prawa stronie planszy
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack(side=tk.RIGHT)  

        self.boids = [] #inicjalizacja pustej listy Boidow
        self.hunters = [] #inicjalizacja pustej listy Hunterow

        self.boid_sensing_radius = tk.StringVar() #Utworzenie obiektu do przechowywania stref czucia Boidow
        self.hunter_sensing_radius = tk.StringVar() #Utworzenie obiektu do przechowywania stref czucia Hunterow

        self.initial_boids_info = []  #Lista początkowych informacji o Boidach
        self.initial_hunters_info = []  #Lista początkowych informacji o Hunterach

        self.simulation_running = False #Ustawienie samo odpalania symulacji na nie
        self.iteration_count = 0 #Ilość iteracji programu
        self.restart_count = 0 #Ilość rotacji programu

        self.create_input_fields() #Utworzenie pól wejsciowych w interfejsie 
        self.create_buttons() #Utworzenie przyciskow w interfejsie
        self.update_info_canvas() #Uaktualnianie informacji na ekranie

    def create_input_fields(self): #Tworzenie pól wejsciowych 
        #Strefa czucia Boidów
        boid_sense_label = tk.Label(self.root, text="Boid Sensing:")
        boid_sense_label.pack(side=tk.TOP, padx=10, pady=5) 
        self.boid_sense_entry = tk.Entry(self.root, textvariable=self.boid_sensing_radius)
        self.boid_sense_entry.pack(side=tk.TOP, padx=10, pady=5)
        #Strefa czucia Huntera
        hunter_sense_label = tk.Label(self.root, text="Hunter Sensing:")
        hunter_sense_label.pack(side=tk.TOP, padx=10, pady=5)
        self.hunter_sense_entry = tk.Entry(self.root, textvariable=self.hunter_sensing_radius)
        self.hunter_sense_entry.pack(side=tk.TOP, padx=10, pady=5)

    def create_buttons(self): #Dodawanie przyciskow
        #Dodanie Boida
        add_boid_button = tk.Button(self.root, text="Add Boid", command=self.add_boid)
        add_boid_button.pack(side=tk.TOP, padx=10, pady=5)
        #Dodanie Huntera
        add_hunter_button = tk.Button(self.root, text="Add Hunter", command=self.add_hunter)
        add_hunter_button.pack(side=tk.TOP, padx=10, pady=5)
        #Usuniecie Boida
        remove_boid_button = tk.Button(self.root, text="Remove Boid", command=self.remove_boid)
        remove_boid_button.pack(side=tk.TOP, padx=10, pady=5)
        #Usuniecie Huntera
        remove_hunter_button = tk.Button(self.root, text="Remove Hunter", command=self.remove_hunter)
        remove_hunter_button.pack(side=tk.TOP, padx=10, pady=5)
        #Ustawienie strefy czucia Boidow
        boid_sense_button = tk.Button(self.root, text="Boid Sensing", command=self.adjust_boid_sensing)
        boid_sense_button.pack(side=tk.TOP, padx=10, pady=5)
        #Ustawienie strefy czucia Hunterow
        hunter_sense_button = tk.Button(self.root, text="Hunter Sensing", command=self.adjust_hunter_sensing)
        hunter_sense_button.pack(side=tk.TOP, padx=10, pady=5)
        #Przycisk Start
        start_button = tk.Button(self.root, text="Start", command=self.start_simulation)
        start_button.pack(side=tk.TOP, padx=10, pady=5)
        #Przycisk Stop
        stop_button = tk.Button(self.root, text="Stop", command=self.stop_simulation)
        stop_button.pack(side=tk.TOP, padx=10, pady=5)

    def update_info_canvas(self): #Aktualizacjia interfejsu
        # Wyczyszczenie obszaru informacji
        self.info_canvas.delete("all")
        # Obecna ilość nieprzechwyconych boidów
        boids_not_caught = sum(1 for boid in self.boids if not boid.is_caught)
        self.info_canvas.create_text(100, 30, text=f"Boids not caught: {boids_not_caught}", fill='blue')
        # Obecna ilość przechwyconych boidów
        boids_caught = sum(1 for boid in self.boids if boid.is_caught)
        self.info_canvas.create_text(100, 60, text=f"Boids caught: {boids_caught}", fill='green')
        # Ilość dodanych boidów i hunterów
        all_boids_count = len(self.boids)
        all_hunters_count = len(self.hunters)
        self.info_canvas.create_text(100, 120, text=f"All Boids: {all_boids_count}", fill='blue')
        self.info_canvas.create_text(100, 150, text=f"All Hunters: {all_hunters_count}", fill='red')
        # Informacja o liczbie iteracji i restartów
        self.info_canvas.create_text(100, 180, text=f"Iterations: {self.iteration_count}")
        self.info_canvas.create_text(100, 210, text=f"Restarts: {self.restart_count}")

        for i, hunter in enumerate(self.hunters): #Iteracja po Hunterach
            boids_in_sensing_area, distances = hunter.count_boids_in_sensing_area(self.boids)
            # Wyświetl ilość boidów w strefie czucia dla każdego Huntera
            self.info_canvas.create_text(
                100, 300 + i * 60,
                text=f"Boids in sensing area: {boids_in_sensing_area}",
                fill='purple'
            )
            # Wyświetl odległości pomiędzy łowcą a boidami
            for j, distance in enumerate(distances):
                self.info_canvas.create_text(
                    100, 330 + i * 60 + j * 20,
                    text=f"Distance to Boid {j+1}: {distance:.2f}",
                    fill='purple'
                )
            # Wyświetl resztę informacji o łowcy (liczbę złapanych boidów, przebytą odległość, fitness)
            self.info_canvas.create_text(
                100, 240 + i * 60,
                text=f"Hunter {i+1} - Caught boids: {hunter.zlapane_boidy}",
                fill='purple'
            )
            self.info_canvas.create_text(
                100, 260 + i * 60,
                text=f"Traveled Distance: {hunter.traveled_distance:.2f}",
                fill='purple'
            )
            self.info_canvas.create_text(
                100, 280 + i * 60,
                text=f"Fitness: {hunter.get_fitness():.2f}",
                fill='purple'
            )

    def add_boid(self): #Dodawanie Boida na plansze
        sensing_radius = int(self.boid_sensing_radius.get()) #pobierania wartosci strefy czucia boida
        x, y = random.randint(50, 750), random.randint(50, 550) #Losowanie początkowych współrzędnych
        boid = Boid(self.canvas, x, y, sensing_radius) #Tworzenie obiektu Boid
        self.boids.append(boid) #Dodawanie boida do listy
        self.update_info_canvas() #aktualizacja planszy

    def add_hunter(self): #Dodawanie Huntera na plansze
        sensing_radius = int(self.hunter_sensing_radius.get()) #pobierania wartosci strefy czucia Huntera
        x, y = random.randint(50, 750), random.randint(50, 550) #Losowanie początkowych współrzędnych
        hunter = Hunter(self.canvas, x, y, sensing_radius) #Tworzenie obiektu Hunter
        self.hunters.append(hunter) #dodawanie huntera do listy
        self.update_info_canvas() #aktualizacja planszy

    def remove_boid(self): #Usuwanie Boida z planszy
        if self.boids: #Czy istnieje
            boid = self.boids.pop() #Usuwa ostatniego z listy
            self.canvas.delete(boid.id) #Usuwanie Boida z planszy
            self.canvas.delete(boid.sensing_circle) #Usuwanie strefy czucia Boida z planszy
            self.canvas.delete(boid.arrow) #Usuwanie strzałki Boida z planszy
            self.update_info_canvas() #Aktualizacja planszy

    def remove_hunter(self): #Usuwanie Huntera z planszy
        if self.hunters: #Czy istnieje
            hunter = self.hunters.pop() #Usuwa ostatniego z listy
            self.canvas.delete(hunter.id) #Usuwanie Huntera z planszy
            self.canvas.delete(hunter.sensing_circle) #Usuwanie strefy czucia Huntera z planszy
            self.canvas.delete(hunter.arrow) #Usuwanie strzałki Huntera z planszy 
            self.update_info_canvas() #Aktualizacja planszy

    def adjust_boid_sensing(self): #Dostosowywanie strefy czucia Boidów
        sensing_radius = int(self.boid_sensing_radius.get()) #Pobieranie wartości promienia i konwersja na int
        for boid in self.boids: #Iteracja po wszystkich Boidach
            boid.sensing_radius = sensing_radius #Ustawianie nowego promienia
            boid.update_sensing_radius() #Aktualizacja strefy czucia na planszy
        self.update_info_canvas() #Aktualizacja informacji na planszy

    def adjust_hunter_sensing(self): #Dostosowywanie strefy czucia Hunterów
        sensing_radius = int(self.hunter_sensing_radius.get()) #Pobieranie wartości promienia i konwersja na int
        for hunter in self.hunters: #Iteracja po wszystkich Hunterach
            hunter.sensing_radius = sensing_radius #Ustawianie nowego promienia
            hunter.update_sensing_radius() #Aktualizacja strefy czucia na planszy
        self.update_info_canvas() #Aktualizacja informacji na planszy

    def start_simulation(self): #Start symulacji
        self.simulation_running = True #Włączenie symulacji
        self.iteration_count = 0 #Ilosc iteracji
        self.restart_count = 0 #Ilosc rotacji
        self.initial_boids_info = [(boid.x, boid.y, boid.direction, boid.speed) for boid in self.boids] #Zapisuje informacje o poczatkowych pozycjach Boidach
        self.initial_hunters_info = [(self.canvas.coords(hunter.id)[0], self.canvas.coords(hunter.id)[1],
                                      hunter.direction, hunter.speed) for hunter in self.hunters] #Zapisuje informacje o poczatkowych pozycjach Hunterow
        self.update_simulation() #Aktualizacja symulacji

    def stop_simulation(self): #Zatrzymanie symulacji
        self.simulation_running = False #Wyłaczenie symulacji

    def print_coordinates_after_rotation(self): #Funkcja wypisująca parametry
        print(f"\nAfter Rotation: {self.restart_count + 1}") #Ilosc rotacji
        for i, hunter in enumerate(self.hunters):
            hunter_x, hunter_y, _, _ = self.canvas.coords(hunter.id)  #Pobranie aktualnych wspolrzednych Huntera
            print(f"Hunter {i + 1} - Coordinates: ({hunter_x:.2f}, {hunter_y:.2f})") #Wypisanie tych wspolrzednych

        for i, boid in enumerate(self.boids):
            boid_x, boid_y, _, _ = self.canvas.coords(boid.id) #Pobranie aktualnych wspolrzednych Boidow
            print(f"Boid {i + 1} - Coordinates: ({boid_x:.2f}, {boid_y:.2f})") #Wypisanie tych wspolrzednych

        print(f"Iterations in Rotation: {hunter.iterations_in_rotation}") #Wypisanie Ilosci iteracji
        print(f"Traveled Distance: {hunter.traveled_distance:.2f}") #Wypisanie przebytej drogi
        print(f"Fitness: {hunter.get_fitness():.2f}") #Wypisanie fitnessu

    def update_simulation(self): #Aktualizacja symulacji
        if self.simulation_running: #Czy symulacja jest w trakcie działania
            all_boids_caught = all(boid.is_caught for boid in self.boids) #Czy wszystkie boidy zostaly zlapane

            if all_boids_caught: #Zlapane
                for hunter in self.hunters:
                    hunter.iterations_in_rotation += 1  #Aktualizacja ilości iteracji przed zakończeniem rotacji
                self.print_coordinates_after_rotation()  # Wywołanie funkcję wypisującą współrzędne po rotacji
                self.restart_simulation() # Restart symulację
            else: #Nie zlapane
                self.iteration_count += 1 #Inkrement licznika iteracji
                for boid in self.boids:  # Pętla po boidach, aby śledziły każdego Huntera
                    for hunter in self.hunters:
                        boid.follow_hunter(hunter)

                for hunter in self.hunters: # Pętla po Hunterach, aby ścigał boidy i się poruszał
                    self.hunter_chase_boids(hunter)
                    hunter.move()

                for boid in self.boids: # Pętla po boidach, aby śledziły Huntera ktory je zlapal
                    boid.follow_caught_hunter()
                    boid.move()

                for hunter in self.hunters: # Pętla po Hunterach, aby zaktualizować liczbę iteracji w rotacji i fitness
                    hunter.iterations_in_rotation += 1
                    hunter.update_fitness()

                self.root.after(50, self.update_simulation) # Zaplanowanie ponownego wykonania funkcji po 50 milisekundach
                self.update_info_canvas() # Aktualizacja planszy

    def restart_simulation(self):
        self.restart_count += 1 #Inkrementuj licznik restartów
        self.iteration_count = 0 #Reset iteracji

        # Usuwa wszystkie boid i Huntera z planszy
        for boid in self.boids:
            self.canvas.delete(boid.id)
            self.canvas.delete(boid.sensing_circle)
            self.canvas.delete(boid.arrow)
        for hunter in self.hunters:
            self.canvas.delete(hunter.id)
            self.canvas.delete(hunter.sensing_circle)
            self.canvas.delete(hunter.arrow)

        # Czyści listy boidów i Huntera
        self.boids.clear()
        self.hunters.clear()
        
        #Przywraca początkowe wartosci zmiennych w boidach
        for info in self.initial_boids_info:
            x, y, direction, speed = info
            boid = Boid(self.canvas, x, y, int(self.boid_sensing_radius.get()))  # Convert to integer
            boid.direction = direction
            boid.speed = speed
            self.boids.append(boid)

        #Przywraca początkowe wartosci zmiennych w Hunterach
        for info in self.initial_hunters_info:
            x, y, direction, speed = info
            hunter = Hunter(self.canvas, x, y, int(self.hunter_sensing_radius.get()))  # Convert to integer
            hunter.direction = direction
            hunter.speed = speed
            self.hunters.append(hunter)

        #Inicjuje odległość drogi Hunterow
        for hunter in self.hunters:
            hunter.traveled_distance = 0

        #Zaplanowane uaktualnienie planszy po 50 milisekundach
        self.root.after(50, self.update_simulation)
        self.update_info_canvas()

    def hunter_chase_boids(self, hunter): #Sciganie boidow nie zlapanych przez Huntera
        for boid in self.boids: #Iteracja po boidach
            if not boid.is_caught: #Czy jest zlapany
                boid_x, boid_y, _, _ = self.canvas.coords(boid.id) #Pobranie aktualnych wspolrzednych Boida
                hunter_x, hunter_y, _, _ = self.canvas.coords(hunter.id) #Pobranie aktualnych wspolrzednych Huntera

                distance = math.sqrt((boid_x - hunter_x) ** 2 + (boid_y - hunter_y) ** 2) #Obliczanie odleglosci miedzy boidem a Hunterem

                if distance <= hunter.sensing_radius and not boid.is_caught: #Czy boid jest w strefie czucia
                    hunter.update_traveled_distance(distance) # Aktualizacja odległości Huntera
                    hunter.speed = min(hunter.speed + 0.5, hunter.base_speed * 6) # Zwiększ prędkość Huntera
                    sorted_boids = sorted([boid for boid in self.boids if not boid.is_caught],
                                        key=lambda boid: self.calculate_distance(hunter, boid)) # Sortowanie nieprzechwyconych boidów według odległości od Huntera
                    if sorted_boids: #Sprawdzenie czy istnieją nieprzechwycone boidy
                        closest_boid = sorted_boids[0] #Wybor na najblizszego boida 
                        boid_x, boid_y, _, _ = self.canvas.coords(closest_boid.id) #Pobiera aktualne wspolrzedne Boida
                        hunter_x, hunter_y, _, _ = self.canvas.coords(hunter.id) #Pobiera aktualne wspolrzedne Huntera
                        angle = math.atan2(boid_y - hunter_y, boid_x - hunter_x) #Obliczanie kierunku Huntera na najblizszego Boida
                        hunter.direction = math.degrees(angle) #Nastawienie kierunku Huntera na najblizszego Boida

                        # Wyświetla informację o najbliższym boidzie
                        self.info_canvas.create_text(
                            100, 360 + len(self.hunters) * 30,
                            text=f"Red: Hunters - Chasing Boid {self.boids.index(closest_boid) + 1}",
                            fill='red'
                        )

    def calculate_distance(self, creature1, creature2): #Obliczanie odległości między dwoma obiektami
        x1, y1, _, _ = self.canvas.coords(creature1.id) #Pobranie współrzędnych pierwszego obiektu
        x2, y2, _, _ = self.canvas.coords(creature2.id) #Pobranie współrzędnych drugiego obiektu
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) #Obliczenie odległości między nimi

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()