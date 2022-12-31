import os
import pdfkit

options = {
  "print-media-type": None
}

if __name__ == "__main__":

   notebooks = ['team_report']
   for nb in notebooks:
      os.system(f'jupyter nbconvert --execute --to html --no-input {nb}.ipynb')
      pdfkit.from_file(f'{nb}.html', f'{nb}.pdf')#, css='format.css', options=options)
      #os.remove(f'{nb}.html')
