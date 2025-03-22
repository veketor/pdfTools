import PyPDF2
from tkinter import Tk, filedialog, Button, Label, Entry

def split_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    start_page = int(start_entry.get()) - 1  # Convert to 0-based index
    end_page = int(end_entry.get())

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            Label(root, text="PDF split successfully!").pack()

root = Tk()
root.title("PDF Splitter")

Label(root, text="Start Page:").pack()
start_entry = Entry(root)
start_entry.pack()

Label(root, text="End Page:").pack()
end_entry = Entry(root)
end_entry.pack()

Button(root, text="Select PDF and Split", command=split_pdf).pack()

root.mainloop()