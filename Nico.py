import json
import os
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

FILE_NAME = "users.json"

class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Application")
        self.geometry("600x500")
        self.current_user = None
        
        self.create_widgets()
        self.show_login_register()
        self.check_data_file()

    def check_data_file(self):
        if not os.path.exists(FILE_NAME):
            with open(FILE_NAME, "w") as file:
                json.dump([], file)

    def create_widgets(self):
        self.lr_frame = ttk.Frame(self)
        
        self.username = ttk.Entry(self.lr_frame)
        self.password = ttk.Entry(self.lr_frame, show="x")
        
        ttk.Label(self.lr_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.lr_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password.grid(row=1, column=1, padx=5, pady=5)
        
        self.login_btn = ttk.Button(self.lr_frame, text="Login", command=self.do_login)
        self.login_btn.grid(row=2, column=0, padx=5, pady=5)
        self.register_btn = ttk.Button(self.lr_frame, text="Register", command=self.show_register)
        self.register_btn.grid(row=2, column=1, padx=5, pady=5)

        self.reg_frame = ttk.Frame(self)
        
        ttk.Label(self.reg_frame, text="Registrazione").pack(pady=5)
        ttk.Label(self.reg_frame, text="Nuovo Username:").pack()
        self.new_user = ttk.Entry(self.reg_frame)
        self.new_user.pack()
        
        ttk.Label(self.reg_frame, text="Nuova Password:").pack()
        self.new_pass = ttk.Entry(self.reg_frame, show="*")
        self.new_pass.pack()
        
        ttk.Button(self.reg_frame, text="Conferma Registrazione", command=self.do_register).pack(pady=5)
        ttk.Button(self.reg_frame, text="Torna al Login", command=self.show_login_register).pack()

        self.home_frame = ttk.Frame(self)
        self.balance_label = ttk.Label(self.home_frame, text="")
        self.balance_label.pack(pady=10)
        
        buttons = [
            ("Visualizza Saldo", self.show_balance),
            ("Mostra Dati Utente", self.show_user_info),
            ("Versamento", self.deposit),
            ("Prelievo", self.withdraw),
            ("Bonifico", self.show_transfer),
            ("Storico Transazioni", self.show_history),
            ("Gestione Contatti", self.show_contacts),
            ("Logout", self.do_logout)
        ]
        
        for text, cmd in buttons:
            ttk.Button(self.home_frame, text=text, command=cmd).pack(fill=tk.X, padx=50, pady=2)

        self.contacts_frame = ttk.Frame(self)
        self.contact_iban = tk.StringVar()
        
        ttk.Label(self.contacts_frame, text="Gestione Contatti").pack(pady=5)
        self.contacts_list = tk.Listbox(self.contacts_frame)
        self.contacts_list.pack(fill=tk.BOTH, expand=True)
        
        ttk.Entry(self.contacts_frame, textvariable=self.contact_iban).pack(pady=5)
        ttk.Button(self.contacts_frame, text="Aggiungi Contatto", command=self.add_contact).pack()
        ttk.Button(self.contacts_frame, text="Rimuovi Contatto", command=self.remove_contact).pack()
        ttk.Button(self.contacts_frame, text="Torna alla Home", command=self.show_home).pack(pady=5)

        self.transfer_frame = ttk.Frame(self)
        self.transfer_amount = tk.DoubleVar()
        
        ttk.Label(self.transfer_frame, text="Seleziona Contatto per Bonifico").pack(pady=5)
        self.transfer_list = tk.Listbox(self.transfer_frame)
        self.transfer_list.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.transfer_frame, text="Importo:").pack()
        ttk.Entry(self.transfer_frame, textvariable=self.transfer_amount).pack()
        
        ttk.Button(self.transfer_frame, text="Conferma Bonifico", command=self.execute_transfer).pack(pady=5)
        ttk.Button(self.transfer_frame, text="Annulla", command=self.show_home).pack()

    def show_login_register(self):
        self.hide_all_frames()
        self.lr_frame.pack(fill=tk.BOTH, expand=True)

    def show_register(self):
        self.hide_all_frames()
        self.reg_frame.pack(fill=tk.BOTH, expand=True)

    def show_home(self):
        self.hide_all_frames()
        self.home_frame.pack(fill=tk.BOTH, expand=True)
        self.update_balance()

    def show_contacts(self):
        self.hide_all_frames()
        self.contacts_frame.pack(fill=tk.BOTH, expand=True)
        self.update_contacts()

    def show_transfer(self):
        self.hide_all_frames()
        self.transfer_frame.pack(fill=tk.BOTH, expand=True)
        self.update_transfer_list()

    def hide_all_frames(self):
        for frame in [self.lr_frame, self.reg_frame, self.home_frame, 
                     self.contacts_frame, self.transfer_frame]:
            frame.pack_forget()

    # User operations
    def do_register(self):
        username = self.new_user.get()
        password = self.new_pass.get()
        
        if not username or not password:
            messagebox.showerror("Errore", "Inserisci username e password")
            return
            
        users = self.load_users()
        if any(u["username"] == username for u in users):
            messagebox.showerror("Errore", "Username già esistente!")
            return
            
        iban = self.generate_iban(users)
        new_user = {
            "username": username,
            "password": password,
            "iban": iban,
            "balance": 0.0,
            "transactions": [],
            "contacts": []
        }
        users.append(new_user)
        self.save_users(users)
        messagebox.showinfo("Successo", f"Registrazione completata!\nIl tuo IBAN è: {iban}")
        self.show_login_register()

    def do_login(self):
        username = self.username.get()
        password = self.password.get()
        
        users = self.load_users()
        for user in users:
            if user["username"] == username and user["password"] == password:
                self.current_user = user
                self.show_home()
                return
        messagebox.showerror("Errore", "Credenziali non valide!")

    def do_logout(self):
        self.current_user = None
        self.show_login_register()

    # Banking operations
    def show_balance(self):
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                messagebox.showinfo("Saldo", f"Il tuo saldo attuale è: €{user['balance']:.2f}")
                break

    def deposit(self):
        amount = simpledialog.askfloat("Versamento", "Importo da versare:")
        if amount and amount > 0:
            users = self.load_users()
            for user in users:
                if user["iban"] == self.current_user["iban"]:
                    user["balance"] += amount
                    user["transactions"].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Versamento",
                        "amount": amount,
                        "new_balance": user["balance"]
                    })
                    self.save_users(users)
                    self.update_balance()
                    messagebox.showinfo("Successo", "Versamento effettuato con successo!")
                    return
        messagebox.showerror("Errore", "Importo non valido!")

    def withdraw(self):
        amount = simpledialog.askfloat("Prelievo", "Importo da prelevare:")
        if amount and amount > 0:
            users = self.load_users()
            for user in users:
                if user["iban"] == self.current_user["iban"]:
                    if user["balance"] >= amount:
                        user["balance"] -= amount
                        user["transactions"].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "type": "Prelievo",
                            "amount": amount,
                            "new_balance": user["balance"]
                        })
                        self.save_users(users)
                        self.update_balance()
                        messagebox.showinfo("Successo", "Prelievo effettuato con successo!")
                    else:
                        messagebox.showerror("Errore", "Saldo insufficiente!")
                    return
        messagebox.showerror("Errore", "Importo non valido!")

    def show_history(self):
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                history = "\n".join(
                    [f"{t['date']} - {t['type']}: €{t['amount']:.2f} (Saldo: €{t['new_balance']:.2f})" 
                     for t in user["transactions"]]
                )
                messagebox.showinfo("Storico Transazioni", history or "Nessuna transazione registrata")
                break

    def update_contacts(self):
        self.contacts_list.delete(0, tk.END)
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                for contact in user.get("contacts", []):
                    self.contacts_list.insert(tk.END, f"{contact['name']} - {contact['iban']}")
                break

    def add_contact(self):
        iban = self.contact_iban.get()
        users = self.load_users()
        
        if not iban:
            messagebox.showerror("Errore", "Inserisci un IBAN valido")
            return
            
        target_user = next((u for u in users if u["iban"] == iban), None)
        if not target_user:
            messagebox.showerror("Errore", "IBAN non trovato")
            return
            
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                if any(c["iban"] == iban for c in user.get("contacts", [])):
                    messagebox.showerror("Errore", "Contatto già presente")
                    return
                
                user.setdefault("contacts", []).append({
                    "name": target_user["username"],
                    "iban": iban
                })
                self.save_users(users)
                self.update_contacts()
                messagebox.showinfo("Successo", "Contatto aggiunto con successo")
                return

    def remove_contact(self):
        selection = self.contacts_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                del user["contacts"][index]
                self.save_users(users)
                self.update_contacts()
                messagebox.showinfo("Successo", "Contatto rimosso")
                return

    def update_transfer_list(self):
        self.transfer_list.delete(0, tk.END)
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                for contact in user.get("contacts", []):
                    self.transfer_list.insert(tk.END, f"{contact['name']} - {contact['iban']}")
                break

    def execute_transfer(self):
        selection = self.transfer_list.curselection()
        if not selection:
            messagebox.showerror("Errore", "Seleziona un contatto")
            return
            
        amount = self.transfer_amount.get()
        if not amount or amount <= 0:
            messagebox.showerror("Errore", "Importo non valido")
            return
            
        selected_contact = self.transfer_list.get(selection[0])
        recipient_iban = selected_contact.split(" - ")[1]
        
        users = self.load_users()
        sender = None
        recipient = None
        
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                sender = user
            if user["iban"] == recipient_iban:
                recipient = user
        
        if not sender or not recipient:
            messagebox.showerror("Errore", "Destinatario non trovato")
            return
            
        if sender["balance"] < amount:
            messagebox.showerror("Errore", "Saldo insufficiente")
            return
            
        sender["balance"] -= amount
        recipient["balance"] += amount
        
        transaction_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sender["transactions"].append({
            "date": transaction_time,
            "type": "Bonifico in uscita",
            "amount": -amount,
            "recipient": recipient_iban,
            "new_balance": sender["balance"]
        })
        
        recipient["transactions"].append({
            "date": transaction_time,
            "type": "Bonifico in entrata",
            "amount": amount,
            "sender": sender["iban"],
            "new_balance": recipient["balance"]
        })
        
        self.save_users(users)
        self.update_balance()
        messagebox.showinfo("Successo", f"Bonifico di €{amount:.2f} effettuato con successo!")
        self.show_home()

    def show_user_info(self):
        if self.current_user:
            info = f"Username: {self.current_user['username']}\nIBAN: {self.current_user['iban']}"
            messagebox.showinfo("Dati Utente", info)
        else:
            messagebox.showerror("Errore", "Nessun utente loggato")

    def update_balance(self):
        users = self.load_users()
        for user in users:
            if user["iban"] == self.current_user["iban"]:
                self.balance_label.config(text=f"Saldo attuale: €{user['balance']:.2f}")
                break

    @staticmethod
    def load_users():
        with open(FILE_NAME, "r") as file:
            return json.load(file)

    @staticmethod
    def save_users(users):
        with open(FILE_NAME, "w") as file:
            json.dump(users, file, indent=4)

    @staticmethod
    def generate_iban(users):
        while True:
            iban = f"IT{random.randint(10**9, 10**10 - 1)}"
            if not any(u["iban"] == iban for u in users):
                return iban

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()