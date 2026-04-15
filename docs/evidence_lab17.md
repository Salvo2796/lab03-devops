# Evidence LAB03

## 1. Obiettivo compreso
Prepariamo lo stack che ci serve per fare deploy su Azure

## 2. Struttura monorepo
In un'unica repo ho due cartelle con FrontEnd e BackEnd diviso

## 3. Codice backend
Endpoint disponibili: /work /health
/work comunica con il FrontEnd e restituisce la risposta in Json
/health è un endpoint a se stante

## 4. Codice frontend
Endpoint disponibili: /demo /health
/demo fa una Request al backend attraverso Url del backend, riceve la risposta in Json
/health è un endpoint a se stante

## 5. Build locale
Ho costruito le due immagini Docker
- docker build -t backend:lab03 ./backend
- docker build -t frontend:lab03 ./frontend

## 6. Test locale
Riporto gli output di:
- GET /health backend: {"service":"backend","status":"ok"}
- GET /work backend: {"message":"backend completed","processing_time":0.336,"service":"backend"}
- GET /health frontend: {"service":"frontend","status":"ok"}
- GET /demo frontend: {"backend_response":{"message":"backend completed","processing_time":0.322,"service":"backend"},"message":"frontend completed","service":"frontend"}

## 7. Push manuale iniziale
Ho creato tag delle immagini
```bash
NOME_ACR=obsacr11696
docker tag frontend:lab03 NOME_ACR.azurecr.io/frontend:lab03-manual
docker tag backend:lab03 NOME_ACR.azurecr.io/backend:lab03-manual
```
Ho pushato sul ACR
```bash
docker push NOME_ACR.azurecr.io/frontend:lab03-manual
docker push NOME_ACR.azurecr.io/backend:lab03-manual
```

## 8. Pipeline Azure DevOps
Prima valida i file sul repository, dopo fa prima build e poi push sul ACR, inizia con il BackEnd e poi con il FrontEnd

## 9. Verifica finale ACR
Incollo l’output di:
- az acr repository show-tags --repository frontend
```bash
Result
------------
48
lab03-manual
```
- az acr repository show-tags --repository backend
```bash
Result
------------
48
lab03-manual
```

## 10. Problemi incontrati
Nessuno