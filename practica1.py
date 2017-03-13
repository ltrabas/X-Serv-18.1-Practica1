#!/usr/bin/python3
#LAURA TRABAS CLAVERO

import webapp
import csv
import urllib
import os


class contentApp (webapp.webApp):
    """Simple web application for managing content.
    Content is stored in a dictionary, which is intialized
    with the web content."""
    contador = -1
    urls_reales = {}
    urls_acortadas = {}

    def parse(self, request):
        """Return the resource name (including /)"""

        try:
            metodo = request.split(' ', 2)[0]
            recurso = request.split(' ', 2)[1]
            try:
                cuerpo = request.split('\r\n\r\n')[1][4:]
            except IndexError:
                cuerpo = "" #Cuerpo vacio
        except IndexError:
            return None
        return (metodo, recurso, cuerpo)

    def process(self, resourceName):
        """Process the relevant elements of the request.
        Finds the HTML text corresponding to the resource name,
        ignoring requests for resources not in the dictionary.
        """
        (metodo, recurso, cuerpo) = resourceName
        try:
        		variable = int(recurso[1:])
        except ValueError:
        		variable = ""
        if len(self.urls_reales) == 0:
            if os.access("fich.csv", 0):
                with open("fich.csv", "r") as csvfile:
                    reader = csv.reader(csvfile)
                    vacio = True
                    for row in reader:
                        vacio = False
                    if not vacio:
                        self.leerDicc("fich.csv")
        if metodo == "GET":
            if recurso =='/':
                httpCode = "200 OK"
                htmlBody = "<html><body>" + '<form method="POST" action="">'
                htmlBody += 'URL: <input type="text" name="Url"><br>'
                htmlBody += '<input type="submit" value="Enviar">'
                htmlBody += '</form>' + str(self.urls_acortadas) + "<body></html>"

            elif variable in self.urls_acortadas:
                url_real = self.urls_acortadas[int(recurso[1:])]
                url_acortada = self.urls_reales[url_real]
            	#Si la URL esta, redirigir
                httpCode = "300 Redirect"
                htmlBody = "<html><head>" + '<meta http-equiv="refresh" content="0;url=' + url_real + '" />'
                htmlBody += "</head></html>"
            else:
                httpCode = "404 Not Found"
                htmlBody = "No hay recurso"

        elif metodo == "POST":
            if cuerpo == "":
                httpCode ="404 Not Found"
                htmlBody = "Url vacia"
                return(httpCode, htmlBody)
            elif cuerpo.find("http") == -1:
                cuerpo = "http://" + cuerpo
                while cuerpo.find("%2F") != -1:
                    cuerpo = cuerpo.replace("%2F", "/")
            else:
                #Hacemos el split // = %3A%2F%2F
                cuerpo = cuerpo.split("%3A%2F%2F")[0] + "://"
                cuerpo = cuerpo + cuerpo.split("%3A%2F%2F")[1]
                while cuerpo.find("%2F") != -1:
                    cuerpo = cuerpo.replace("%2F", "/")
            if cuerpo in self.urls_acortadas:
                contador = self.urls_acortadas[cuerpo]
            else:
                self.contador = self.contador + 1
                contador = self.contador
            self.urls_acortadas[cuerpo] = contador
            self.urls_reales[contador] = cuerpo
            self.escribirURL(cuerpo, contador)
            httpCode = "200 OK"
            htmlBody = "<html><body>"
            htmlBody += "<a href=" + cuerpo + ">" + cuerpo + "</href>"
            htmlBody += "<p><a href=" + str(contador) + ">" + str(contador)
            htmlBody += "</href></body></html>"

        else:
            httpCode = "404 Not Found"
            htmlBody = "No encontrado"
        return (httpCode, htmlBody)

    def escribirURL(self, url_real, url_acortada):
        with open("fich.csv", "w") as csvfile:
            escribir = csv.writer(csvfile)
            key  = url_acortada
            valor = url_real
            escribir.writerow([int(key)] + [valor])
        return None

    def leerDicc(self, file):
        with open("fich.csv", "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.urls_acortadas[row[1]] = int(row[0])
                self.urls_reales[int(row[0])] = row[1]
                self.contador = self.contador+1
            return None
if __name__ == "__main__":
    testWebApp = contentApp("localhost", 1234)
