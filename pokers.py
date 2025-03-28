import tkinter as tk
from tkinter import messagebox
import random
import math

NUM_GIOCATORI_MAX = 9
CARTE_PER_GIOCATORE = 2
semi = ["Cuori", "Quadri", "Fiori", "Picche"]
valori = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

class CartaVisual:
    SIMBOLI_SEMI = {
        "Cuori": "♥",
        "Quadri": "♦",
        "Fiori": "♣",
        "Picche": "♠"
    }

    def __init__(self, valore, seme):
        self.valore = valore
        self.seme = seme
        self.colore = "red" if seme in ["Cuori", "Quadri"] else "black"

    def disegna(self, canvas, x, y, width=40, height=60):
        canvas.create_rectangle(x-width//2, y-height//2, x+width//2, y+height//2,
                              fill="white", outline="gray")
        canvas.create_text(x-width//2+8, y-height//2+12,
                          text=self.valore, fill=self.colore, font=("Arial", 10, "bold"))
        canvas.create_text(x, y,
                          text=self.SIMBOLI_SEMI[self.seme],
                          fill=self.colore, font=("Arial", 20))
        canvas.create_text(x+width//2-8, y+height//2-12,
                          text=self.valore, fill=self.colore, 
                          font=("Arial", 10, "bold"), angle=180)

class PokerTable:
    def __init__(self, root):
        self.root = root
        self.root.title("Tavolo da Poker")
        self.root.geometry("670x470")  
        self.root.minsize(530, 400)    
        self.mazzo = []
        self.giocatori = []
        self.postazioni = []
        self.board = []
        self.fase_board = 0
        self.partita_terminata = False
        self.mano_distribuita = False
        self.river_mostrato = False
        self.carte_visuali = {}
        self.inizializza_ui()
        self.nuovo_mazzo()
        self.crea_postazioni()
        self.canvas.bind("<Configure>", self.ridisegna_tavolo)
        self.root.after(100, self.ridisegna_tavolo)

    def inizializza_ui(self):
        self.main_frame = tk.Frame(self.root, bg="#808080")  
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.main_frame, bg="#808080", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.controlli_frame = tk.Frame(self.root)
        self.controlli_frame.pack(pady=5)
        self.btn_distribuisci = tk.Button(self.controlli_frame, text="Distribuisci Carte",
                                      command=self.distribuisci_mano, state=tk.DISABLED)
        self.btn_distribuisci.pack(side=tk.LEFT, padx=5)
        self.btn_board = tk.Button(self.controlli_frame, text="Mostra Board",
                                command=self.mostra_board, state=tk.DISABLED)
        self.btn_board.pack(side=tk.LEFT, padx=5)
        self.btn_reset_mano = tk.Button(self.controlli_frame, text="Nuova Mano",
                                     command=self.resetta_mano, state=tk.DISABLED)
        self.btn_reset_mano.pack(side=tk.LEFT, padx=5)
        self.btn_reset = tk.Button(self.controlli_frame, text="Reset Completo",
                                command=self.resetta_partita)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

    def crea_postazioni(self):
        self.postazioni = []
        for i in range(NUM_GIOCATORI_MAX):
            postazione = {
                'frame': tk.Frame(self.canvas),
                'carte_frame': tk.Frame(self.canvas),
                'btn_siediti': None,
                'btn_alzati': None,
                'occupata': False,
                'id_giocatore': None,
                'carte': []
            }
            self.postazioni.append(postazione)
        self.root.update_idletasks()
        self.aggiorna_pulsanti_postazioni()

    def aggiorna_pulsanti_postazioni(self):
        for i, postazione in enumerate(self.postazioni):
            if postazione['frame']:
                postazione['frame'].destroy()
            if postazione['carte_frame']:
                postazione['carte_frame'].destroy()
            postazione['frame'] = tk.Frame(self.canvas)
            postazione['carte_frame'] = tk.Frame(self.canvas)
            postazione['btn_siediti'] = tk.Button(postazione['frame'], text=f"P{i+1}",
                command=lambda idx=i: self.aggiungi_giocatore(idx), width=2, height=1)
            postazione['btn_siediti'].pack(side=tk.LEFT)
            postazione['btn_alzati'] = tk.Button(postazione['frame'], text="✖",
                command=lambda idx=i: self.rimuovi_giocatore(idx), state=tk.DISABLED,
                width=1, height=1)
            postazione['btn_alzati'].pack(side=tk.LEFT)

    def ridisegna_tavolo(self, event=None):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        scale_factor = min(0.80, 700 / max(width, height))
        tavolo_padding = 100 * scale_factor

        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, width, height, fill="#808080")

        oval_width = width - 2 * tavolo_padding
        oval_height = height - 2 * tavolo_padding
        oval_width *= 0.67
        oval_height *= 0.67

        padding_x = (width - oval_width) / 2
        padding_y = (height - oval_height) / 2

        self.canvas.create_oval(padding_x, padding_y, 
                              width - padding_x, height - padding_y,
                              outline="gold", width=3, fill="#696969")

        center_x = width // 2
        center_y = height // 2

        for i, postazione in enumerate(self.postazioni):
            angle = 2 * math.pi * i / NUM_GIOCATORI_MAX - (math.pi / 2)
            x_radius = (oval_width / 2) * 0.85
            y_radius = (oval_height / 2) * 0.85

            # Posizione dei controlli
            controls_x = center_x + (x_radius + 30) * math.cos(angle)
            controls_y = center_y + (y_radius + 30) * math.sin(angle)

            if postazione['occupata']:
                # Disegna l'icona del giocatore
                player_x = controls_x - 35
                player_y = controls_y

                # Posiziona le carte a destra dell'icona del giocatore
                cards_x = player_x + 70  # 25 (raggio icona) + 40 (larghezza carta/2) + 20px extra
                cards_y = player_y

                self.canvas.create_oval(player_x-25, player_y-25, player_x+25, player_y+25,
                                     fill="lightblue", tags=f"giocatore_{postazione['id_giocatore']}")
                self.canvas.create_text(player_x, player_y, text=f"G{postazione['id_giocatore']}",
                                     tags=f"label_{postazione['id_giocatore']}")

                # Posiziona i controlli sotto l'icona del giocatore
                controls_y_adjusted = player_y + 35  # 25 (raggio icona) + 10 (spazio)
                self.canvas.create_window(player_x, controls_y_adjusted, window=postazione['frame'])

                # Parametri per le carte
                card_width = 40
                card_spacing = 0  
                total_cards_width = CARTE_PER_GIOCATORE * card_width

                # Aggiusta la posizione delle carte per mantenerle sempre visibili
                margin = 20
                if cards_x + total_cards_width/2 > width - margin:
                    cards_x = width - margin - total_cards_width/2
                elif cards_x - total_cards_width/2 < margin:
                    cards_x = margin + total_cards_width/2

                # Disegna le carte
                for card_idx, carta_str in enumerate(postazione['carte']):
                    offset_x = card_idx * card_width
                    carta_x = cards_x + offset_x - (total_cards_width / 2)
                    valore, _, seme = carta_str.split(" ")
                    carta_visual = CartaVisual(valore, seme)
                    carta_visual.disegna(self.canvas, carta_x, cards_y)
            else:
                # Se non occupata, mostra solo i controlli
                self.canvas.create_window(controls_x, controls_y, window=postazione['frame'])

        # Disegna il board senza spazi tra le carte
        if self.board:
            board_scale = min(0.6, width / 1000)
            card_width = 40  # Larghezza carta

            # Calcola la larghezza totale del board
            total_width = len(self.board) * card_width

            # Calcola la posizione iniziale per centrare il board
            start_x = center_x - (total_width / 2)
            current_x = start_x

            for i, carta_str in enumerate(self.board):
                valore, _, seme = carta_str.split(" ")
                carta_visual = CartaVisual(valore, seme)
                carta_visual.disegna(self.canvas, current_x + card_width/2, center_y - 10)  # -50 + 40px
                current_x += card_width

    def resetta_mano(self):
        if not self.river_mostrato and self.mano_distribuita:
            messagebox.showwarning("Errore", "Non puoi resettare la mano prima del river!")
            return
        self.nuovo_mazzo()
        self.board = []
        self.fase_board = 0
        self.mano_distribuita = False
        self.river_mostrato = False
        for postazione in self.postazioni:
            postazione['carte'] = []
        if self.giocatori:
            self.btn_distribuisci.config(state=tk.NORMAL)
        self.btn_board.config(state=tk.DISABLED)
        self.btn_reset_mano.config(state=tk.DISABLED)
        self.ridisegna_tavolo()

    def aggiungi_giocatore(self, postazione_idx):
        if len(self.giocatori) >= NUM_GIOCATORI_MAX:
            messagebox.showwarning("Errore", "Tutte le postazioni sono occupate!")
            return
        postazione = self.postazioni[postazione_idx]
        if postazione['occupata']:
            return
        nuovo_id = len(self.giocatori) + 1
        self.giocatori.append(nuovo_id)
        postazione['occupata'] = True
        postazione['id_giocatore'] = nuovo_id
        postazione['btn_siediti'].config(state=tk.DISABLED)
        postazione['btn_alzati'].config(state=tk.NORMAL)
        if len(self.giocatori) > 0:
            self.btn_distribuisci.config(state=tk.NORMAL)
        self.ridisegna_tavolo()

    def rimuovi_giocatore(self, postazione_idx):
        postazione = self.postazioni[postazione_idx]
        if not postazione['occupata']:
            return
        if self.mano_distribuita and not self.river_mostrato and postazione['carte']:
            messagebox.showwarning("Errore", "Non puoi lasciare il tavolo prima del river!")
            return
        giocatore_id = postazione['id_giocatore']
        self.giocatori.remove(giocatore_id)
        postazione['occupata'] = False
        postazione['id_giocatore'] = None
        postazione['carte'] = []
        postazione['btn_siediti'].config(state=tk.NORMAL)
        postazione['btn_alzati'].config(state=tk.DISABLED)
        self.canvas.delete(f"giocatore_{giocatore_id}")
        self.canvas.delete(f"label_{giocatore_id}")
        for card_idx in range(CARTE_PER_GIOCATORE):
            self.canvas.delete(f"carta_{giocatore_id}_{card_idx}")
            self.canvas.delete(f"testo_{giocatore_id}_{card_idx}")
        if not self.giocatori:
            self.btn_distribuisci.config(state=tk.DISABLED)
            self.btn_board.config(state=tk.DISABLED)
            self.btn_reset_mano.config(state=tk.DISABLED)
        self.ridisegna_tavolo()

    def distribuisci_mano(self):
        if self.mano_distribuita:
            messagebox.showwarning("Errore", "Le carte sono già state distribuite!")
            return
        self.nuovo_mazzo()
        for postazione in self.postazioni:
            if postazione['occupata']:
                mano = []
                for _ in range(CARTE_PER_GIOCATORE):
                    if self.mazzo:
                        mano.append(self.mazzo.pop())
                postazione['carte'] = mano
        self.mano_distribuita = True
        self.btn_board.config(state=tk.NORMAL)
        self.ridisegna_tavolo()

    def mostra_board(self):
        fasi = [(1, 3), (1, 1), (1, 1)]
        if self.fase_board >= len(fasi):
            return
        scarto, mostra = fasi[self.fase_board]
        try:
            for _ in range(scarto):
                self.mazzo.pop()
            nuove_carte = [self.mazzo.pop() for _ in range(mostra)]
            self.board.extend(nuove_carte)
            self.fase_board += 1
            if self.fase_board >= len(fasi):
                self.river_mostrato = True
                self.btn_board.config(state=tk.DISABLED)
                self.btn_reset_mano.config(state=tk.NORMAL)
            self.ridisegna_tavolo()
        except IndexError:
            messagebox.showwarning("Errore", "Carte insufficienti nel mazzo!")

    def resetta_partita(self):
        self.nuovo_mazzo()
        self.giocatori = []
        self.board = []
        self.fase_board = 0
        self.mano_distribuita = False
        self.river_mostrato = False
        for postazione in self.postazioni:
            postazione['occupata'] = False
            postazione['btn_siediti'].config(state=tk.NORMAL)
            postazione['btn_alzati'].config(state=tk.DISABLED)
            postazione['carte'] = []
            postazione['id_giocatore'] = None
        self.canvas.delete("all")
        self.crea_postazioni()
        self.ridisegna_tavolo()
        self.btn_distribuisci.config(state=tk.DISABLED)
        self.btn_board.config(state=tk.DISABLED)
        self.btn_reset_mano.config(state=tk.DISABLED)

    def nuovo_mazzo(self):
        self.mazzo = [f"{valore} di {seme}" for valore in valori for seme in semi]
        random.shuffle(self.mazzo)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PokerTable(root)
        root.mainloop()
    except Exception as e:
        print(f"Errore durante l'esecuzione: {str(e)}")
        input("Premi Invio per uscire...")