# Birdgarden — Documentazione del notebook MobileNetV2 per Raspberry Pi AI Camera

**Versione della documentazione:** 18 ottobre 2026  
**Notebook documentato:** [`custom_mobilenet_birdgarden_fixed_dependencies.ipynb`](https://github.com/idamato/birdgarden/blob/main/custom_mobilenet_birdgarden_fixed_dependencies.ipynb)  
**Ambiente rappresentato dagli output salvati:** Google Colab, Python 3.11.13, Linux x86-64  
**Stato del progetto:** versione alfa / prova di fattibilità

Il notebook prende a riferimento e personalizza la documentazione ufficiale disponibile ai seguenti link:
Notebook di partenza: https://colab.research.google.com/github/SonySemiconductorSolutions/aitrios-rpi-tutorials-ai-model-training/blob/main/notebooks/mobilenet-rps/custom_mobilenet.ipynb
Per le specifiche del sensore Sony ed il software a corredo: https://github.com/SonySemiconductorSolutions

Il dataset utilizzato è AVONET https://opentraits.org/datasets/avonet, dal quale sono prese le immagini delle cinque specie utilizzate per la dimostrazione alla Maker Faire

> Questa documentazione descrive il codice e gli output presenti nel notebook pubblicato nel repository alla data indicata. I numeri riportati sono quelli registrati nell'esecuzione salvata: non rappresentano una garanzia di prestazioni su altri dataset, su nuove fotografie o direttamente sulla Raspberry Pi AI Camera.

---

# PARTE I — DOCUMENTAZIONE IN ITALIANO

## 1. Scopo del notebook

Il notebook implementa una pipeline per addestrare un classificatore di immagini dedicato a Birdgarden, quantizzarlo per il target Sony IMX500 e convertirlo tramite `imxconv-tf`, il convertitore previsto dal flusso Raspberry Pi AI Camera.

La pipeline è composta da queste fasi:

1. verifica di Python e installazione controllata delle dipendenze;
2. verifica di Java e preparazione delle cartelle di lavoro;
3. collegamento al dataset e controllo degli split `train`, `valid` e `test`;
4. caricamento e pre-processing delle immagini;
5. costruzione di un classificatore MobileNetV2 tramite transfer learning;
6. addestramento e salvataggio del modello a precisione floating point;
7. calibrazione e quantizzazione post-training con Model Compression Toolkit (MCT);
8. valutazione separata del modello float e di quello quantizzato sul test set;
9. visualizzazione di predizioni di esempio;
10. conversione del modello quantizzato e generazione degli artefatti per il successivo packaging IMX500.

### Che cosa fa e che cosa non fa

Il modello **classifica l'immagine intera** e restituisce un punteggio per ciascuna specie prevista dal dataset. Non identifica la posizione dell'uccello nella scena e non produce bounding box.

Per il caso d'uso Birdgarden in cui servirà un passaggio distinto per localizzare e ritagliare la fotografia o l'uccello prima di sottoporre il ritaglio al classificatore. Questo notebook costituisce principalmente la fase di classificazione.

## 2. Ambiente e dipendenze

Gli output salvati confermano l'uso di Python **3.11.13** su Linux x86-64 in Google Colab. Il notebook verifica la versione Python prima di proseguire.

Le principali versioni bloccate sono:

| Componente | Versione richiesta |
|---|---:|
| Python | 3.11.x |
| NumPy | 1.26.4 |
| `ml-dtypes` | 0.2.0 |
| TensorFlow | 2.14.1 |
| Model Compression Toolkit (`model-compression-toolkit`) | 2.2.2 |
| IMX500 Converter (`imx500-converter`) | 3.16.1 |
| scikit-learn | 1.6.1 negli output registrati |
| Matplotlib | 3.10.0 negli output registrati |
| Java | 17 |

Il blocco NumPy/`ml-dtypes`/TensorFlow serve a evitare incompatibilità dovute a versioni già installate nel runtime Colab. La cella d'installazione controlla le versioni, installa quelle attese se necessario e poi genera intenzionalmente un `RuntimeError` per fermare il notebook: quando l'ambiente è stato modificato, occorre riavviare il runtime e rieseguire le celle dall'inizio.

Quindi, se la cella produce un errore e stampa un messaggio del tipo «Ambiente aggiornato: riavvia il runtime e riesegui il notebook», il comportamento è deliberato e non indica di per sé un guasto dell'installazione. Non si devono eseguire le celle successive nella stessa sessione prima del riavvio.

Il notebook verifica inoltre la presenza di Java 17 e, in un ambiente Linux che disponga di `apt-get`, prova a installare `openjdk-17-jdk` se necessario. Java è richiesto dal passaggio di conversione IMX500.

**Nota sulle versioni:** le versioni sono quelle fissate dal notebook attuale e dell'esecuzione registrata. Prima di aggiornarle, controllare la documentazione Sony del convertitore e verificare la compatibilità fra TensorFlow, MCT e IMX500 Converter.

## 3. Percorsi, riproducibilità e artefatti

In Google Colab il notebook monta Google Drive sotto `/mnt/drive` e utilizza come percorso predefinito del dataset:

```text
/mnt/drive/MyDrive/Birdgarden
```

Fuori da Colab è possibile usare una cartella locale, ad esempio `./Birdgarden`, oppure modificare il percorso previsto dalla variabile d'ambiente `BIRDGARDEN_DATASET` e/o da `DATASET_ROOT`.

Il notebook imposta un seed per rendere più riproducibili le operazioni casuali, fra cui lo shuffle dei dati e la data augmentation. La riproducibilità non è assoluta: hardware, kernel, librerie e operazioni TensorFlow possono introdurre differenze fra esecuzioni.

Gli artefatti vengono organizzati in cartelle dedicate, in particolare:

```text
models/birdgarden/
converted/birdgarden/
```

Quando è in esecuzione in Colab, il notebook copia anche gli artefatti su Google Drive, nelle cartelle:

```text
/mnt/drive/MyDrive/Birdgarden/artifacts/models
/mnt/drive/MyDrive/Birdgarden/artifacts/converted
```

Questo conserva i file fuori dal filesystem temporaneo del runtime Colab.

## 4. Struttura del dataset

Il dataset viene letto da tre cartelle distinte:

```text
Birdgarden/
├── train/
│   ├── SPECIE_1/
│   ├── SPECIE_2/
│   └── ...
├── valid/
│   ├── SPECIE_1/
│   ├── SPECIE_2/
│   └── ...
└── test/
    ├── SPECIE_1/
    ├── SPECIE_2/
    └── ...
```

Il nome di ciascuna sottocartella viene usato come etichetta della classe. Le cartelle di classe devono quindi avere gli stessi nomi in tutti e tre gli split.

Il controllo iniziale verifica che le cartelle esistano, che contengano immagini supportate e che le classi siano coerenti. Il notebook conta anche le immagini per classe e registra la mappa delle etichette in `class_names.json`, oltre ai metadati del dataset in `dataset_metadata.json`.

### Dataset effettivamente utilizzato nell'esecuzione salvata

Il notebook ha letto **832 immagini in totale**:

| Split | Numero di immagini | Distribuzione |
|---|---:|---|
| `train` | 782 | 136–168 immagini per classe |
| `valid` | 25 | 5 immagini per classe |
| `test` | 25 | 5 immagini per classe |
| **Totale** | **832** | 5 classi |

Dettaglio dello split `train` riportato dal notebook:

| Classe | Immagini di training |
|---|---:|
| `ANDEAN SISKIN` | 154 |
| `AZARAS SPINETAIL` | 168 |
| `AZURE JAY` | 136 |
| `BANDED PITA` | 166 |
| `BARN OWL` | 158 |
| **Totale** | **782** |

Sia `valid` sia `test` contengono cinque immagini per ognuna delle classi:

- `ANDEAN SISKIN`
- `AZARAS SPINETAIL`
- `AZURE JAY`
- `BANDED PITA`
- `BARN OWL`

L'ordine effettivo delle classi viene conservato nel file `class_names.json`. Questo file è importante: gli indici prodotti dalla rete devono essere interpretati usando la stessa mappa quando si fanno predizioni o si distribuisce il modello.

## 5. Caricamento e controllo degli split

I dataset sono caricati inizialmente senza batching e senza shuffle. Questa scelta consente di controllare esplicitamente l'ordine delle classi e di mantenere separati i dati di test dal flusso di addestramento.

Il notebook utilizza le etichette inferite dalle directory e label intere, adatte a `SparseCategoricalCrossentropy`. Dopo la verifica, gli esempi di training vengono mescolati in modo riproducibile e raggruppati in batch.

La distinzione fra gli split è corretta dal punto di vista metodologico:

- **train:** aggiorna i pesi addestrabili;
- **valid:** controlla l'andamento del training e l'early stopping;
- **test:** viene utilizzato dopo il training e la quantizzazione per misurare le prestazioni finali.

La separazione delle cartelle non garantisce, però, che le immagini siano indipendenti fra loro. Prima di considerare attendibili i risultati è necessario controllare che la stessa fotografia, una sua copia ridimensionata o immagini quasi identiche non siano presenti in split diversi.

## 6. Pre-processing e data augmentation

Le immagini sono elaborate a **224 × 224 pixel** in formato RGB, la dimensione prevista dalla configurazione MobileNetV2 usata dal notebook.

Il pre-processing comprende:

1. conversione dei valori in `float32`;
2. ridimensionamento all'input previsto;
3. applicazione di `tf.keras.applications.mobilenet_v2.preprocess_input`, che trasforma i valori dei pixel nell'intervallo previsto dalla rete (approssimativamente da −1 a +1).

Sul solo training set vengono applicate trasformazioni casuali, fra cui:

- ribaltamento orizzontale (`RandomFlip`);
- rotazione casuale (`RandomRotation`, fattore 0,2).

La validazione e il test non subiscono data augmentation. Anche il dataset rappresentativo utilizzato per la calibrazione MCT non applica trasformazioni casuali: serve a descrivere immagini simili ai dati reali che il modello dovrebbe ricevere.

La data augmentation amplia la varietà apparente degli esempi durante il training, ma non sostituisce la raccolta di fotografie indipendenti, scattate con sfondi, distanze, illuminazioni e dispositivi diversi.

## 7. Architettura del classificatore

Il modello è basato su **MobileNetV2 pre-addestrata su ImageNet**, caricata senza la testa di classificazione originale (`include_top=False`). I pesi della base sono congelati (`base_model.trainable = False`), quindi in questa versione non viene eseguito il fine-tuning dei blocchi interni di MobileNetV2.

La testa specifica per Birdgarden è composta da:

1. input RGB di forma 224 × 224 × 3;
2. base convoluzionale MobileNetV2;
3. `GlobalAveragePooling2D`, che riassume le mappe di caratteristiche;
4. livello `Dense` con un neurone per classe e attivazione `softmax`.

La rete usa quindi il **transfer learning**: sfrutta le caratteristiche già apprese da ImageNet e addestra una nuova testa per distinguere le classi del dataset Birdgarden.

Il modello è compilato con:

- ottimizzatore Adam;
- funzione di perdita `SparseCategoricalCrossentropy`;
- metrica `accuracy`.

Questa impostazione è adatta a una prima prova di fattibilità e riduce il numero di parametri da addestrare, ma potrebbe non essere la configurazione migliore per un dataset più ampio o molto diverso dalle immagini di ImageNet. Una futura fase di fine-tuning controllato potrebbe migliorare la capacità di adattamento, ma andrebbe verificata con una validazione più ampia e senza usare ripetutamente il test set per scegliere le configurazioni.

## 8. Addestramento e salvataggio del modello float

I parametri principali dell'esecuzione sono:

| Parametro | Valore |
|---|---:|
| Dimensioni input | 224 × 224 |
| Batch size | 32 |
| Epoche massime | 20 |
| Numero di classi | 5 nell'esecuzione salvata |
| Base MobileNetV2 | congelata |
| Early stopping | monitora `val_loss`, `patience=5` |

L'early stopping controlla la perdita di validazione e ripristina i pesi migliori osservati. In questo run il training ha completato tutte le 20 epoche; alla ventesima epoca gli output riportano `loss=0.0107`, `accuracy=1.0000`, `val_loss=0.0067` e `val_accuracy=1.0000`. La procedura salva il modello float in:

```text
models/birdgarden/mobilenetv2_birdgarden.keras
```

Registra inoltre la configurazione del training in `training_config.json` e visualizza i grafici di accuracy e loss per training e validazione.

### Come leggere i grafici

L'accuracy indica la proporzione di esempi classificati correttamente; la loss quantifica l'errore secondo la funzione obiettivo e tiene conto anche dei punteggi assegnati alle classi. Una accuracy elevata insieme a una loss in diminuzione è un segnale positivo, ma nel caso presente la validazione è composta da sole 25 immagini: un'accuracy del 100% su tale insieme è incoraggiante, non una prova di generalizzazione.

## 9. Quantizzazione post-training per IMX500

Il modello float viene sottoposto a **Post-Training Quantization (PTQ)** tramite Model Compression Toolkit. La quantizzazione riduce la rappresentazione numerica di pesi e attivazioni in funzione del target hardware, con lo scopo di rendere il modello compatibile con il percorso d'inferenza previsto e controllare l'uso delle risorse.

Il notebook:

1. configura il target IMX500 v1 del flusso Sony utilizzato;
2. prepara un dataset rappresentativo a partire da immagini non aumentate del training set;
3. rende disponibili fino a 10 batch per la calibrazione;
4. esegue la ricerca dei parametri di quantizzazione;
5. esporta il modello quantizzato in formato Keras.

Il file principale generato è:

```text
models/birdgarden/mobilenetv2_birdgarden_quant.keras
```

Nel log della sessione salvata, la quantizzazione si completa e MCT riporta stime interne di memoria e operazioni. Queste stime sono utili per l'analisi del modello, ma non vanno confuse con misure effettive di latenza, consumo energetico o memoria libera durante l'esecuzione sulla fotocamera.

MCT raccomanda inoltre di verificare l'accuracy del modello quantizzato esportato. Il notebook confronta il modello float e quello quantizzato sul medesimo test set; il passaggio successivo consigliato è verificare il modello convertito ed eseguito sul dispositivo, perché la valutazione Keras sul computer non equivale a una prova end-to-end sulla IMX500.

## 10. Valutazione finale sul test set

Il test set è utilizzato dopo il training e la quantizzazione. Il notebook calcola loss e accuracy, genera un report per classe con precision, recall e F1-score, costruisce una matrice di confusione e salva il riepilogo in `test_metrics.json`.

### Risultati registrati

| Metrica | Modello float | Modello quantizzato |
|---|---:|---:|
| Loss | 0,0021 | 0,0013 |
| Accuracy | 1,0000 (100%) | 1,0000 (100%) |
| Immagini test | 25 | 25 |
| Precision, recall e F1 per ciascuna classe | 1,00 | 1,00 |

Il report salvato mostra cinque esempi correttamente classificati su cinque per ogni specie e una matrice di confusione diagonale:

```text
[[5 0 0 0 0]
 [0 5 0 0 0]
 [0 0 5 0 0]
 [0 0 0 5 0]
 [0 0 0 0 5]]
```

La matrice indica che in questo test non si sono osservate confusioni fra le cinque classi. Il modello float e quello quantizzato hanno entrambi classificato correttamente tutte le 25 immagini del test set registrato.

### Valutazione della bontà dei risultati in versione alfa

Per una versione alfa, i risultati sono **promettenti**: dimostrano che il flusso completo di caricamento dei dati, transfer learning, quantizzazione e conversione può essere eseguito e che, sul piccolo insieme di test usato, la quantizzazione non ha provocato una perdita di accuracy osservabile.

Occorre però interpretare l'accuracy del 100% con prudenza per almeno quattro ragioni:

1. **Test molto piccolo:** ci sono soltanto 25 immagini, cinque per classe. Una singola immagine classificata male porterebbe l'accuracy complessiva dal 100% al 96%; per una singola classe, un solo errore farebbe scendere il recall dal 100% all'80%.
2. **Incertezza statistica elevata:** cinque immagini per specie non bastano a stimare con precisione l'errore atteso su nuove fotografie.
3. **Possibile correlazione fra immagini:** bisogna verificare che train, valid e test non contengano scatti della stessa scena, copie o fotografie quasi identiche. La separazione per cartelle è necessaria ma non sufficiente.
4. **Differenza rispetto all'uso reale:** immagini naturali di uccelli possono essere più semplici del caso d'uso finale, dove la figura può comparire parzialmente coperta o inserita in uno sfondo complesso.

La loss più bassa del modello quantizzato rispetto a quella float è un dato osservato in questo test, ma **non dimostra che il modello quantizzato sia intrinsecamente migliore**: entrambi hanno classificato correttamente tutti gli esempi, e il test è troppo ridotto per trarre conclusioni generali.

La conclusione corretta è dunque: **il prototipo ha superato con esito positivo una prima prova tecnica e preliminare di classificazione; l'affidabilità su dati indipendenti e sul dispositivo resta da misurare**.

### Prossimi test raccomandati

- aumentare validazione e test con immagini indipendenti, raccolte in condizioni diverse;
- separare gli split per sessione di acquisizione, soggetto, luogo o origine della fotografia, evitando immagini quasi duplicate fra train e test;
- includere distanze, orientamenti, sfondi, livelli di luce, riflessi, sfocatura e risoluzioni diversi;
- misurare precision, recall e F1 per classe su un numero sensibilmente maggiore di esempi;
- testare il `.keras` quantizzato e soprattutto il pacchetto convertito sulla Raspberry Pi AI Camera;
- registrare tempi di inferenza, stabilità, consumo e comportamento quando l'immagine non appartiene a nessuna delle cinque classi;
- mantenere un test set nuovo e intatto per la valutazione finale, senza usarlo a ogni iterazione per scegliere le configurazioni.

## 11. Visualizzazione delle predizioni

La funzione di predizione ridimensiona e pre-processa una singola immagine RGB, aggiunge la dimensione batch, esegue il modello e seleziona la classe con il punteggio `softmax` più alto.

La visualizzazione riporta l'immagine, l'etichetta vera, la classe predetta e il punteggio. Se il punteggio massimo è inferiore alla soglia configurata (`LOW_CONFIDENCE_THRESHOLD = 0.55`), il notebook stampa un avviso invece di interrompere l'esecuzione.

**Attenzione:** il punteggio `softmax` non è automaticamente una probabilità calibrata e il suo valore non costituisce una garanzia di correttezza. Inoltre, il modello è un classificatore a classi chiuse: se riceve un'immagine senza uno degli uccelli previsti, è comunque costretto a scegliere una delle cinque classi. La gestione di immagini sconosciute o non valide andrà progettata e valutata separatamente.

## 12. Conversione IMX500

La cella conclusiva richiama `imxconv-tf` sul modello quantizzato. Imposta `HDF5_PLUGIN_PATH=disable`, crea una cartella temporanea per evitare di confondere artefatti di conversioni precedenti con quelli correnti e controlla la presenza del file `packerOut.zip`.

Il comando usa il modello quantizzato come input e una cartella temporanea come destinazione (`-o`); al termine, il notebook trasferisce gli artefatti validati nella cartella finale `converted/birdgarden`. La struttura del comando è:

```bash
imxconv-tf -i models/birdgarden/mobilenetv2_birdgarden_quant.keras \
           -o <cartella-temporanea-di-conversione>
```

Il notebook cattura il log del convertitore e lo mostra in caso di errore. Se la conversione termina correttamente e `packerOut.zip` è presente, elenca i file generati e li copia su Google Drive quando la persistenza è attiva.

### Esito della conversione negli output salvati

L'esecuzione pubblicata termina con successo. Il log riporta:

- completamento del backend del convertitore;
- tempo di conversione del backend di circa 50,57 secondi e tempo complessivo mostrato di circa 1 minuto e 50 secondi;
- generazione di `packerOut.zip`;
- copia degli artefatti su Google Drive.

Fra gli artefatti elencati figurano:

| File | Dimensione registrata |
|---|---:|
| `dnnParams.xml` | 1.382 byte |
| `mobilenetv2_birdgarden_quant.pbtxt` | 62.812 byte |
| `mobilenetv2_birdgarden_quant_MemoryReport.json` | 640 byte |
| `packerOut.zip` | 2.168.271 byte (circa 2,17 MB) |

La conversione riuscita dimostra che il convertitore ha accettato il modello quantizzato ed ha prodotto gli artefatti previsti. **Non dimostra, da sola, che il modello sia già stato caricato sulla fotocamera o che funzioni correttamente in esecuzione reale.** Per completare la validazione serve seguire la procedura di packaging/installazione compatibile con la versione del software Raspberry Pi AI Camera e testare il modello sul dispositivo.

## 13. File generati e loro significato

| File/cartella | Scopo |
|---|---|
| `class_names.json` | Mappa ordinata fra indice di output e nome della classe. |
| `dataset_metadata.json` | Informazioni sul dataset e sulla configurazione di caricamento. |
| `training_config.json` | Configurazione del modello e del training, inclusi parametri principali e nomi delle classi. |
| `mobilenetv2_birdgarden.keras` | Modello addestrato a precisione floating point. |
| `mobilenetv2_birdgarden_quant.keras` | Modello quantizzato esportato da MCT. |
| `test_metrics.json` | Metriche, report e risultati di valutazione sul test set. |
| `dnnParams.xml` | Parametri del modello generati dal convertitore. |
| `mobilenetv2_birdgarden_quant.pbtxt` | Descrizione testuale del modello convertito. |
| `mobilenetv2_birdgarden_quant_MemoryReport.json` | Report di memoria prodotto dal convertitore. |
| `packerOut.zip` | Pacchetto generato dal convertitore per il successivo processo di packaging IMX500. |

I file e i nomi esatti possono variare con future versioni del notebook e del convertitore. Il pacchetto `packerOut.zip` va trattato come un artefatto del processo di conversione, non come prova che la fase di distribuzione sul dispositivo sia già completata.

## 14. Giudizio complessivo e stato alfa

Il notebook ha raggiunto un buon livello di maturità come pipeline sperimentale:

- separa correttamente training, validazione e test;
- controlla la struttura del dataset e l'ordine delle classi;
- fissa le dipendenze critiche e segnala la necessità di riavvio del runtime;
- registra configurazioni e metadati per rendere più tracciabili gli esperimenti;
- valuta il modello float e quello quantizzato;
- produce un pacchetto IMX500 nella sessione di esecuzione documentata.

Il risultato più importante non è il 100% di accuracy preso isolatamente, ma il fatto che **l'intera pipeline tecnica sia stata eseguita con esito positivo fino alla conversione**.

La qualifica alfa resta appropriata. Per passare a una valutazione più solida occorrono un dataset più ampio e indipendente, controlli contro i duplicati, prove con immagini che rappresentino il contesto reale Birdgarden, e una verifica finale sul dispositivo. Per l'obiettivo di riconoscere una figura di uccello mostrata da un visitatore, va inoltre aggiunto e documentato un modulo separato di localizzazione/ritaglio prima della classificazione.

## 15. Riferimenti

- Notebook Birdgarden: <https://github.com/idamato/birdgarden/blob/main/custom_mobilenet_birdgarden_fixed_dependencies.ipynb>
- Documentazione Raspberry Pi AI Camera / IMX500 Converter: <https://developer.aitrios.sony-semicon.com/docs/raspberry-pi-ai-camera/imx500-converter?version=3.16.1>
- TensorFlow MobileNetV2: <https://www.tensorflow.org/api_docs/python/tf/keras/applications/MobileNetV2>
- Sony Model Compression Toolkit: <https://github.com/sony/model_optimization>

---

# PART II — ENGLISH DOCUMENTATION

## 1. Notebook purpose

This notebook implements an image-classification pipeline for Birdgarden. It trains a classifier, applies post-training quantization for the Sony IMX500 target, and converts the quantized model with `imxconv-tf` as part of the Raspberry Pi AI Camera workflow.

The pipeline covers:

1. Python environment checks and controlled dependency installation;
2. Java verification and workspace setup;
3. dataset validation for the `train`, `valid`, and `test` splits;
4. image loading and preprocessing;
5. MobileNetV2 transfer learning;
6. training and saving the floating-point model;
7. post-training quantization with Model Compression Toolkit (MCT);
8. separate evaluation of the float and quantized models on the test set;
9. visualization of sample predictions;
10. conversion of the quantized model and creation of artifacts for the subsequent IMX500 packaging process.

### What the notebook does—and does not do

The model **classifies the entire input image** and returns a score for each class in the dataset. It does not locate a bird in a scene and does not produce bounding boxes.



## 2. Runtime and dependencies

The saved outputs show a Google Colab runtime using **Python 3.11.13** on Linux x86-64. The notebook checks the Python version before proceeding.

The main pinned dependencies are:

| Component | Required version |
|---|---:|
| Python | 3.11.x |
| NumPy | 1.26.4 |
| `ml-dtypes` | 0.2.0 |
| TensorFlow | 2.14.1 |
| Model Compression Toolkit (`model-compression-toolkit`) | 2.2.2 |
| IMX500 Converter (`imx500-converter`) | 3.16.1 |
| scikit-learn | 1.6.1 in the saved outputs |
| Matplotlib | 3.10.0 in the saved outputs |
| Java | 17 |

The NumPy/`ml-dtypes`/TensorFlow pins help avoid incompatibilities caused by packages already installed in the Colab runtime. The dependency cell checks the installed versions, installs the required ones if needed, and then deliberately raises a `RuntimeError` to stop execution. After the environment changes, restart the runtime and run the notebook again from the beginning.

Therefore, a message such as “Environment updated: restart the runtime and rerun the notebook” is an intentional safety stop, not necessarily an installation failure. Do not run subsequent cells in the same session before restarting.

The notebook also checks for Java 17 and, in a Linux environment with `apt-get`, attempts to install `openjdk-17-jdk` if necessary. Java is required by the IMX500 conversion step.

**Version note:** these are the versions pinned by the current notebook and represented in its saved run. Before upgrading them, check Sony's converter documentation and compatibility across TensorFlow, MCT, and the IMX500 Converter.

## 3. Paths, reproducibility, and artifacts

In Google Colab, Google Drive is mounted under `/mnt/drive` and the default dataset path is:

```text
/mnt/drive/MyDrive/Birdgarden
```

Outside Colab, a local directory such as `./Birdgarden` can be used, or the path can be changed through the `BIRDGARDEN_DATASET` environment variable and/or `DATASET_ROOT`.

The notebook sets random seeds to improve reproducibility of operations such as shuffling and data augmentation. Reproducibility is not absolute: hardware, kernels, libraries, and TensorFlow operations can lead to differences between runs.

Artifacts are organized in dedicated directories, particularly:

```text
models/birdgarden/
converted/birdgarden/
```

When running in Colab, artifacts are also copied to Google Drive:

```text
/mnt/drive/MyDrive/Birdgarden/artifacts/models
/mnt/drive/MyDrive/Birdgarden/artifacts/converted
```

This keeps outputs outside the temporary Colab filesystem.

## 4. Dataset structure

The dataset is loaded from three separate directories:

```text
Birdgarden/
├── train/
│   ├── SPECIES_1/
│   ├── SPECIES_2/
│   └── ...
├── valid/
│   ├── SPECIES_1/
│   ├── SPECIES_2/
│   └── ...
└── test/
    ├── SPECIES_1/
    ├── SPECIES_2/
    └── ...
```

Each class subdirectory name becomes a label. Class directory names must therefore match across all three splits.

The notebook checks that the directories exist, contain supported image files, and expose consistent classes. It counts images per class and records the label mapping in `class_names.json`, together with dataset metadata in `dataset_metadata.json`.

### Dataset used in the saved run

The saved execution loaded **832 images in total**:

| Split | Number of images | Distribution |
|---|---:|---|
| `train` | 782 | 136–168 images per class |
| `valid` | 25 | 5 images per class |
| `test` | 25 | 5 images per class |
| **Total** | **832** | 5 classes |

The training split contains:

| Class | Training images |
|---|---:|
| `ANDEAN SISKIN` | 154 |
| `AZARAS SPINETAIL` | 168 |
| `AZURE JAY` | 136 |
| `BANDED PITA` | 166 |
| `BARN OWL` | 158 |
| **Total** | **782** |

Both validation and test contain five images for each class:

- `ANDEAN SISKIN`
- `AZARAS SPINETAIL`
- `AZURE JAY`
- `BANDED PITA`
- `BARN OWL`

The actual class order is stored in `class_names.json`. This mapping matters because output indices must be translated back to the correct class names during inference and deployment.

## 5. Loading and checking the splits

The datasets are initially loaded without batching or shuffling. This makes it possible to check class ordering explicitly and keep test data separate from the training data flow.

Labels are inferred from directories and represented as integer labels, suitable for `SparseCategoricalCrossentropy`. After validation, training examples are shuffled reproducibly and grouped into batches.

The split roles are methodologically appropriate:

- **train:** updates trainable weights;
- **valid:** monitors training and early stopping;
- **test:** evaluates final performance after training and quantization.

Separate folders do not guarantee that the images themselves are independent. Before trusting the metrics, check that identical photos, resized copies, or near-duplicate images have not been placed in different splits.

## 6. Preprocessing and data augmentation

Images are processed as RGB images of **224 × 224 pixels**, matching the MobileNetV2 input configuration used by the notebook.

Preprocessing steps are:

1. convert pixel values to `float32`;
2. resize to the expected input dimensions;
3. apply `tf.keras.applications.mobilenet_v2.preprocess_input`, which maps pixel values to the range expected by the network (approximately −1 to +1).

Random transformations are applied only to the training split, including:

- horizontal flipping (`RandomFlip`);
- random rotation (`RandomRotation`, factor 0.2).

Validation and test images are not augmented. The representative dataset used for MCT calibration also avoids random augmentation so that calibration is based on images more representative of the intended inputs.

Data augmentation increases the apparent variety of training examples, but it does not replace collecting independent photos with different backgrounds, distances, lighting conditions, and cameras.

## 7. Classifier architecture

The model is based on **MobileNetV2 pre-trained on ImageNet**, loaded without its original classification head (`include_top=False`). The base model is frozen (`base_model.trainable = False`), so this version does not fine-tune MobileNetV2's internal layers.

The Birdgarden-specific classifier consists of:

1. RGB input with shape 224 × 224 × 3;
2. MobileNetV2 convolutional base;
3. `GlobalAveragePooling2D` to summarize feature maps;
4. a `Dense` layer with one output per class and `softmax` activation.

This is **transfer learning**: the model reuses features learned from ImageNet and trains a new classification head for Birdgarden's classes.

The model is compiled with:

- Adam optimizer;
- `SparseCategoricalCrossentropy` loss;
- `accuracy` metric.

This setup is suitable for an initial proof of concept and reduces the number of parameters that must be trained. It may not be optimal for a larger dataset or images that differ substantially from ImageNet. Controlled fine-tuning could be explored later, but it should be assessed using a larger validation set and without repeatedly using the test set to select configurations.

## 8. Training and saving the float model

Main run parameters are:

| Parameter | Value |
|---|---:|
| Input size | 224 × 224 |
| Batch size | 32 |
| Maximum epochs | 20 |
| Number of classes | 5 in the saved run |
| MobileNetV2 base | Frozen |
| Early stopping | Monitors `val_loss`, `patience=5` |

Early stopping monitors validation loss and restores the best observed weights. In the saved run, training completed all 20 epochs. At epoch 20, the output reports `loss=0.0107`, `accuracy=1.0000`, `val_loss=0.0067`, and `val_accuracy=1.0000`. The float model is saved to:

```text
models/birdgarden/mobilenetv2_birdgarden.keras
```

The training configuration is also saved in `training_config.json`, and the notebook plots training and validation accuracy and loss.

### Interpreting the plots

Accuracy is the fraction of correctly classified examples. Loss measures error according to the objective function and also reflects the scores assigned to classes. High accuracy alongside decreasing loss is encouraging, but validation consists of only 25 images here. A validation accuracy of 100% is promising, not proof of generalization.

## 9. Post-training quantization for IMX500

The float model undergoes **Post-Training Quantization (PTQ)** using Model Compression Toolkit. Quantization changes the numerical representation of weights and activations for the hardware target, with the aim of making the model suitable for the intended inference path and controlling resource usage.

The notebook:

1. configures the IMX500 v1 target used by the Sony workflow;
2. prepares representative data from unaugmented training images;
3. makes up to 10 batches available for calibration;
4. searches for quantization parameters;
5. exports the quantized model in Keras format.

The main output file is:

```text
models/birdgarden/mobilenetv2_birdgarden_quant.keras
```

In the saved log, quantization completes and MCT prints internal estimates of memory and operations. These are useful model-analysis figures, but they are not the same as measured latency, power consumption, or available memory during actual camera inference.

MCT also recommends verifying the accuracy of the exported quantized model. The notebook compares the float and quantized models on the same test set. The next recommended step is to test the converted model on the device, because evaluation in Keras on the host does not equal an end-to-end Raspberry Pi AI Camera test.

## 10. Final evaluation on the test set

The test set is only used after training and quantization. The notebook calculates loss and accuracy, produces a per-class precision/recall/F1 report, builds a confusion matrix, and saves the summary to `test_metrics.json`.

### Recorded results

| Metric | Float model | Quantized model |
|---|---:|---:|
| Loss | 0.0021 | 0.0013 |
| Accuracy | 1.0000 (100%) | 1.0000 (100%) |
| Test images | 25 | 25 |
| Precision, recall, and F1 for each class | 1.00 | 1.00 |

The saved report shows five correct predictions out of five for every species and a diagonal confusion matrix:

```text
[[5 0 0 0 0]
 [0 5 0 0 0]
 [0 0 5 0 0]
 [0 0 0 5 0]
 [0 0 0 0 5]]
```

No confusion between the five classes was observed in this test run. Both the float and quantized models correctly classified all 25 images in the recorded test set.

### Interpreting the results for an alpha release

For an alpha version, these results are **promising**: they show that the full data-loading, transfer-learning, quantization, and conversion pipeline can run, and that quantization caused no observable accuracy loss on the small test set used here.

However, the 100% accuracy must be interpreted cautiously for at least four reasons:

1. **Very small test set:** there are only 25 images, five per class. One error would reduce overall accuracy from 100% to 96%; one error in a class would reduce that class's recall from 100% to 80%.
2. **High statistical uncertainty:** five images per species are insufficient to precisely estimate error on new photographs.
3. **Possible image correlation:** check that the train, validation, and test splits do not contain images from the same scene, copies, or near-identical photographs. Separate folders are necessary but not sufficient.
4. **Difference from the real use case:** natural bird images may be easier than the final use case, where the bird image could be small, tilted, partly occluded, or shown against a complex background.

The quantized model's lower loss than the float model is an observed result in this test, but it **does not prove that the quantized model is inherently better**. Both models classified every test image correctly, and the test is too small to support broad conclusions.

The appropriate conclusion is: **the prototype passed an initial technical classification test; reliability on independent data and on the physical device remains to be measured**.

### Recommended next tests

- expand validation and test with independent images collected under varied conditions;
- split by capture session, subject, location, or source to avoid near-duplicates across train and test;
- include different distances, orientations, backgrounds, lighting levels, reflections, blur, and image resolutions;
- measure per-class precision, recall, and F1 on a substantially larger sample;
- test the quantized `.keras` model and, especially, the converted package on the Raspberry Pi AI Camera;
- measure inference time, stability, power use, and behaviour when an image belongs to none of the five classes;
- keep a new, untouched test set for final evaluation instead of using the same test repeatedly to select configurations.

## 11. Prediction visualization

The prediction function resizes and preprocesses a single RGB image, adds a batch dimension, runs the model, and selects the class with the highest `softmax` score.

The visualization displays the image, true label, predicted class, and score. If the highest score is below the configured threshold (`LOW_CONFIDENCE_THRESHOLD = 0.55`), the notebook prints a warning instead of stopping execution.

**Note:** a `softmax` score is not automatically a calibrated probability and does not guarantee correctness. Also, this is a closed-set classifier: if it receives an image containing none of the expected birds, it is still forced to select one of the five classes. Handling unknown or invalid inputs must be designed and evaluated separately.

## 12. IMX500 conversion

The final cell runs `imxconv-tf` on the quantized model. It sets `HDF5_PLUGIN_PATH=disable`, uses a temporary output directory to avoid mistaking artifacts from an earlier conversion for current outputs, and checks for `packerOut.zip`.

The command uses the quantized model as input and a temporary output directory (`-o`). On completion, the notebook transfers validated artifacts to the final `converted/birdgarden` directory. Its structure is:

```bash
imxconv-tf -i models/birdgarden/mobilenetv2_birdgarden_quant.keras \
           -o <temporary-conversion-directory>
```

The notebook captures and displays the converter log on failure. If conversion succeeds and `packerOut.zip` exists, it lists the generated files and copies them to Google Drive if persistence is enabled.

### Conversion result in the saved outputs

The published execution completes successfully. The log reports:

- successful completion of the converter backend;
- approximately 50.57 seconds for the backend conversion and about 1 minute 50 seconds total as reported by the tool;
- successful generation of `packerOut.zip`;
- copying of artifacts to Google Drive.

The listed artifacts include:

| File | Recorded size |
|---|---:|
| `dnnParams.xml` | 1,382 bytes |
| `mobilenetv2_birdgarden_quant.pbtxt` | 62,812 bytes |
| `mobilenetv2_birdgarden_quant_MemoryReport.json` | 640 bytes |
| `packerOut.zip` | 2,168,271 bytes (about 2.17 MB) |

Successful conversion shows that the converter accepted the quantized model and produced its expected artifacts. **It does not by itself mean the model has already been installed on the camera or that it runs correctly on the real device.** Complete validation by following the packaging/deployment procedure appropriate for the installed Raspberry Pi AI Camera software and test on the hardware.

## 13. Generated files and their purpose

| File/directory | Purpose |
|---|---|
| `class_names.json` | Ordered mapping from output index to class name. |
| `dataset_metadata.json` | Dataset and loading metadata. |
| `training_config.json` | Model/training configuration, including main parameters and class names. |
| `mobilenetv2_birdgarden.keras` | Trained floating-point model. |
| `mobilenetv2_birdgarden_quant.keras` | Quantized model exported by MCT. |
| `test_metrics.json` | Test metrics, classification report, and evaluation results. |
| `dnnParams.xml` | Model parameters generated by the converter. |
| `mobilenetv2_birdgarden_quant.pbtxt` | Text description of the converted model. |
| `mobilenetv2_birdgarden_quant_MemoryReport.json` | Memory report generated by the converter. |
| `packerOut.zip` | Package produced for the subsequent IMX500 packaging process. |

Exact files and names may change as the notebook and converter evolve. Treat `packerOut.zip` as a conversion artifact, not as proof that device deployment has been completed.

## 14. Overall assessment and alpha status

The notebook has reached a useful level of maturity as an experimental pipeline:

- training, validation, and test sets are separated correctly;
- dataset structure and class order are checked;
- critical dependencies are pinned and runtime restart requirements are explicit;
- configurations and metadata are saved for experiment traceability;
- float and quantized models are evaluated;
- the recorded run successfully creates an IMX500 conversion package.

The most important result is not the isolated 100% accuracy figure, but the fact that **the complete technical pipeline ran successfully through model conversion**.

The alpha label remains appropriate. A stronger evaluation requires a larger, independent dataset, duplicate checks, photos representative of the real Birdgarden environment, and final tests on the device. For the target scenario in which a visitor presents a picture of a bird, a separate localization/cropping component must also be implemented and documented before classification.

## 15. References

- Birdgarden notebook: <https://github.com/idamato/birdgarden/blob/main/custom_mobilenet_birdgarden_fixed_dependencies.ipynb>
- Raw notebook: <https://raw.githubusercontent.com/idamato/birdgarden/main/custom_mobilenet_birdgarden_fixed_dependencies.ipynb>
- Google Colab: <https://colab.research.google.com/github/idamato/birdgarden/blob/main/custom_mobilenet_birdgarden_fixed_dependencies.ipynb>
- Raspberry Pi AI Camera / IMX500 Converter documentation: <https://developer.aitrios.sony-semicon.com/docs/raspberry-pi-ai-camera/imx500-converter?version=3.16.1>
- TensorFlow MobileNetV2: <https://www.tensorflow.org/api_docs/python/tf/keras/applications/MobileNetV2>
- Sony Model Compression Toolkit: <https://github.com/sony/model_optimization>
