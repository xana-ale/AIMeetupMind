import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sqlite3


#import the_summaries
#import the_embeddings
#import the_ask





path = 'C:/Users/alex/New folder/meetmind/' #### add path




DB_FILE = path + 'meetupmind.db'

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            meetup_name TEXT,
            transcript TEXT,
            summary TEXT
        )''')
    conn.commit()
    conn.close()



def add_transcript():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    
    if not file_path:
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        transcript = file.read()

    date = date_entry.get()
    meetup_name = meetup_name_entry.get()

    if not date or not meetup_name:
        messagebox.showerror("Error", "Please enter date and meetup name.")
        return

    summary = generate_summary(transcript)  ### from the_summaries
    process_and_store_transcript(date, meetup_name, transcript) #### from the_embeddings
    

    # Store in SQL db
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transcripts (date, meetup_name, transcript, summary)
        VALUES (?, ?, ?, ?)
    ''', (date, meetup_name, transcript, summary))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Transcript processed and added in thr dataset.")


def view_transcripts():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transcripts'")
        if cursor.fetchone() is None:
            display.delete('1.0', tk.END)
            display.insert(tk.END, " The table 'transcripts' could not be found.\n")
            conn.close()
            return

        # Fetch transcripts
        cursor.execute('SELECT id, date, meetup_name FROM transcripts')
        rows = cursor.fetchall()
        conn.close()

        display.delete('1.0', tk.END)
        if rows:
            for row in rows:
                display.insert(tk.END, f"ID: {row[0]}, Date: {row[1]}, Meetup: {row[2]}\n")
        else:
            display.insert(tk.END, "No transcripts added yet.\n")

    except Exception as e:
        display.delete('1.0', tk.END)
        display.insert(tk.END, f"Error database: {e}\n")


def view_summary():
    transcript_id = simple_entry.get()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT summary FROM transcripts WHERE id=?', (transcript_id,))
    row = cursor.fetchone()
    conn.close()

    display.delete('1.0', tk.END)
    if row:
        display.insert(tk.END, row[0])
    else:
        display.insert(tk.END, "Transcript ID not found.")


def chat_with_meetup():
    question = question = chat_entry.get("1.0", tk.END).strip()
    if not question:
        messagebox.showerror("Error", "Enter a question.")
        return

    try:
        response = ask_question(
            query=question,
            index_path=  path+  "faiss_index_meetupmind.index",
            metadata_path= path+ "metadata_meetupmind.json",
            model="mistral"
        )
        display.delete('1.0', tk.END)
        display.insert(tk.END, response)
    except Exception as e:
        display.delete('1.0', tk.END)
        display.insert(tk.END, f"Error: {e}")





initialize_database()




###### interface ##############

root = tk.Tk()
root.title("MeetupMind")

# Labels
tk.Label(root, text="Date (DD-MM-YYYY):").grid(row=0, column=0, pady=10)
tk.Label(root, text="Meetup Name:").grid(row=1, column=0)

# Inputs
date_entry = tk.Entry(root, width=30)
date_entry.grid(row=0, column=1)

meetup_name_entry = tk.Entry(root, width=30)
meetup_name_entry.grid(row=1, column=1)

# Buttons
tk.Button(root, text="Add Transcript", command=add_transcript, bg="#AEAEFF").grid(row=2, column=0, pady=15)
tk.Button(root, text="View Transcripts", command=view_transcripts, bg="#AEAEFF").grid(row=3, column=0, pady=15)

tk.Label(root, text="Transcript ID:").grid(row=4, column=0, pady = (50, 0))
simple_entry = tk.Entry(root, width=30)
simple_entry.grid(row=4, column=1, pady=(50, 0))

tk.Button(root, text="View Summary", command=view_summary, bg="#AEAEFF").grid(row=5, column=0, pady=15)

tk.Label(root, text="Chat Question:").grid(row=6, column=0, pady=(50, 0))
chat_entry = scrolledtext.ScrolledText(root, width=30, height=5)#tk.Entry(root, width=30, height=10)
chat_entry.grid(row=6, column=1, pady=(50,0))

tk.Button(root, text="Send question", command=chat_with_meetup, bg="#AEAEFF").grid(row=7, column=1, pady=15)


display = scrolledtext.ScrolledText(root, width=30, height=10)
display.grid(row=8, column=1, pady=(10, 20))

root.mainloop()
