# Birdgarden — Custom MobileNetV2 for Raspberry Pi AI Camera

**Documentazione italiana e inglese / Italian and English documentation**  
Notebook analizzato / Notebook reviewed: [`notebooks/mobilenet-rps/custom_mobilenet.ipynb`](https://github.com/idamato/birdgarden/blob/main/notebooks/mobilenet-rps/custom_mobilenet.ipynb)

> **Sintesi / Summary:** il notebook addestra un classificatore di immagini a cinque classi di uccelli partendo da MobileNetV2 pre-addestrata su ImageNet, quantizza il modello per il target Sony IMX500 e lo converte nel formato richiesto dalla Raspberry Pi AI Camera. Non è un object detector: classifica l'immagine intera, senza localizzare l'uccello o generare bounding box.

---

# 1. Documentazione in italiano

## 1.1 Scopo e flusso generale

Il notebook è un adattamento del tutorial Sony per creare un modello personalizzato destinato alla **Raspberry Pi AI Camera con sensore Sony IMX500**. Il flusso è:

1. prepara l'ambiente Python e installa le dipendenze;
2. monta Google Drive e individua il dataset Birdgarden;
3. carica le immagini organizzate in cartelle per classe;
4. ridimensiona e normalizza le immagini e applica data augmentation al training set;
5. costruisce un classificatore basato su MobileNetV2 pre-addestrata;
6. addestra la testa di classificazione con transfer learning;
7. quantizza il modello con Model Compression Toolkit (MCT) per il target IMX500;
8. confronta il modello originale e quello quantizzato;
9. visualizza alcune predizioni;
10. converte il modello quantizzato con `imxconv-tf` e controlla i file generati.

## 1.2 Ambiente di esecuzione e dipendenze

### Verifica della versione di Python

La prima cella controlla `sys.version_info` e interrompe l'esecuzione se l'ambiente non usa **Python 3.11**. Il notebook è predisposto per Google Colab; i metadati dell'esecuzione salvata riportano un runtime Colab con GPU T4. Una macchina locale solo CPU può eseguire parti del flusso, ma l'addestramento può richiedere più tempo e la compatibilità delle dipendenze va verificata.

### Installazione dei pacchetti

Il notebook installa:

```bash
pip install 'tensorflow~=2.14.0' 'model-compression-toolkit~=2.2.0' 'imx500-converter[tf]'
```

Questi pacchetti forniscono rispettivamente TensorFlow/Keras, gli strumenti di quantizzazione MCT e il convertitore per IMX500. La cella avverte che può essere necessario riavviare il runtime dopo l'installazione, per caricare correttamente le librerie appena installate.

Il notebook verifica inoltre la presenza di **Java 17** e tenta di installare `openjdk-17-jdk` se manca o se la versione rilevata non è quella richiesta. Il convertitore IMX500 utilizza Java. L'installazione automatica si appoggia a un ambiente Linux/Colab: su Windows o in un container diverso potrebbe essere necessario adattare i comandi di sistema.

## 1.3 Import delle librerie, Drive e variabili di configurazione

Il notebook importa TensorFlow, NumPy e Keras. Importa anche `tensorflow_datasets` (`tfds`), ma nel flusso attuale non viene utilizzato: è un residuo del tutorial originale che trattava il dataset Rock–Paper–Scissors.

Google Drive viene montato in `/mnt/drive`. Una cella esplora la directory montata per cercare una cartella denominata `Birdgarden` e mostra la posizione trovata. Il percorso usato nelle celle successive è:

```text
/mnt/drive/MyDrive/Birdgarden/
├── train/
├── valid/
└── test/
```

Le variabili principali sono:

- `MODELS_DIR = 'models/'`: cartella locale in cui salvare i modelli;
- `MODEL = 'models/mobilenet-rps'`: percorso del modello addestrato in virgola mobile;
- `MODEL_KERAS = 'models/mobilenet-quant-rps.keras'`: percorso del modello quantizzato esportato in formato Keras;
- `BATCH_SIZE = 32`: numero di immagini per batch;
- `IMAGE_SHAPE = (224, 224)`: dimensione d'ingresso della rete.

I nomi `mobilenet-rps` e `mobilenet-quant-rps.keras` conservano la sigla RPS del tutorial originale, anche se le classi correnti sono specie di uccelli. È una scelta di denominazione, non una limitazione del modello.

**Nota sulla persistenza:** `models/` e `converted/` si trovano nel filesystem locale del runtime Colab. Per non perdere gli artefatti quando il runtime viene eliminato, occorre copiarli su Drive o scaricarli.

## 1.4 Caricamento e organizzazione del dataset

`tf.keras.utils.image_dataset_from_directory()` legge le immagini dalle sottocartelle e ricava automaticamente le etichette dai nomi delle directory. `label_mode='int'` assegna a ciascuna classe un indice intero; `image_size=(224, 224)` uniforma le dimensioni delle immagini; `batch_size=32` crea batch da 32 campioni.

La cella definisce:

```python
dataset_path = "/mnt/drive/MyDrive/Birdgarden"
train_path = f"{dataset_path}/train"
val_path = f"{dataset_path}/test"
```

Il log salvato nel notebook indica **782 immagini in `train` e 25 immagini nella directory `test`, distribuite su cinque classi**. I nomi di classe rilevati, nell'ordine restituito da Keras, sono:

1. `ANDEAN SISKIN`
2. `AZARAS SPINETAIL`
3. `AZURE JAY`
4. `BANDED PITA`
5. `BARN OWL`

La variabile `class_names` contiene l'ordine delle classi, mentre `num_classes = len(class_names)` determina automaticamente il numero di uscite del classificatore.

### Problema da correggere: `test` viene usato come validation set

La cartella `valid` è presente nel Drive, ma la variabile `val_path` punta a `test`. Di conseguenza, le 25 immagini in `test` sono utilizzate durante l'addestramento per monitorare `val_accuracy` e decidere quando interrompere il training; successivamente, lo stesso insieme è valutato di nuovo e usato per le visualizzazioni. Non è quindi un test set indipendente.

Se `valid` è il set previsto per la validazione, la correzione consigliata è:

```python
val_path = f"{dataset_path}/valid"
test_path = f"{dataset_path}/test"
```

Si dovrebbe usare `valid` per l'early stopping e riservare `test` alla valutazione finale, eseguita solo dopo aver completato le scelte sul modello. La dimensione di ciascun set va controllata prima di interpretare le metriche. Dopo aver definito `preprocess_data()`, il set di test può essere caricato e valutato separatamente, ad esempio:

```python
test_path = f"{dataset_path}/test"
test_eval_ds = tf.keras.utils.image_dataset_from_directory(
    test_path, labels="inferred", label_mode="int",
    batch_size=BATCH_SIZE, image_size=IMAGE_SHAPE, shuffle=False
)
test_eval_ds = test_eval_ds.map(preprocess_data).prefetch(
    tf.data.experimental.AUTOTUNE
)

# Da eseguire dopo aver concluso il training e la quantizzazione
float_model.evaluate(test_eval_ds)
quantized_model.evaluate(test_eval_ds)
```

Il dataset usato per la visualizzazione può restare separato da `test_eval_ds`, così la trasformazione in dizionari con l'immagine originale non interferisce con la valutazione numerica.

## 1.5 Pre-processing e data augmentation

La funzione `preprocess_data()`:

1. converte i pixel in `float32`;
2. applica `tf.keras.applications.mobilenet_v2.preprocess_input()`, che porta i valori dei pixel alla scala prevista da MobileNetV2 (approssimativamente da `0`–`255` a `-1`–`1`);
3. ridimensiona l'immagine a `224 × 224`;
4. restituisce la coppia `(image, label)`.

La dimensione viene già richiesta nel caricamento del dataset; la seconda chiamata a `resize` rende esplicita la forma attesa dalla rete.

La data augmentation viene applicata **solo** al dataset di training:

```python
tf.keras.layers.RandomFlip('horizontal')
tf.keras.layers.RandomRotation(0.2)
```

In modo casuale, l'immagine viene ribaltata orizzontalmente e/o ruotata. La finalità è rendere il classificatore meno dipendente dall'orientamento e ridurre il rischio di overfitting. Le immagini di validazione non vengono aumentate artificialmente. `prefetch(AUTOTUNE)` consente a TensorFlow di preparare i batch successivi in anticipo e migliorare l'efficienza della pipeline.

## 1.6 Creazione del modello: transfer learning con MobileNetV2

Il modello di base è caricato con:

```python
MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
```

- `weights='imagenet'`: parte da pesi già addestrati sul dataset ImageNet;
- `include_top=False`: elimina la testa originale di classificazione ImageNet;
- `input_shape=(224, 224, 3)`: accetta immagini RGB di 224 × 224 pixel.

Sull'uscita della rete base vengono aggiunti:

1. `GlobalAveragePooling2D`, che riassume le mappe di caratteristiche spaziali in un vettore;
2. `Dense(num_classes, activation=softmax)`, che produce un punteggio per ciascuna delle cinque specie.

Tutti i layer di MobileNetV2 vengono impostati con `trainable = False`. Durante l'addestramento vengono quindi aggiornati i pesi della sola testa di classificazione. È il transfer learning: si riutilizzano le caratteristiche apprese da ImageNet invece di addestrare l'intera rete da zero.

Il riepilogo effettivo del modello a cinque classi riporta circa **2,264,389 parametri totali**, dei quali **6,405 addestrabili** nella testa finale. Nel codice è presente anche una stringa multilinea con un vecchio riepilogo a tre classi, rimasto dal tutorial RPS: è testo obsoleto e non descrive il modello a cinque classi costruito da `num_classes`.

## 1.7 Addestramento e salvataggio del modello float

Il modello viene compilato con:

- ottimizzatore Adam;
- `SparseCategoricalCrossentropy`, adatta a etichette rappresentate da indici interi;
- metrica `accuracy`.

Il limite è di 20 epoche. La callback `EarlyStopping` osserva `val_accuracy`, richiede un miglioramento di almeno `0.01`, usa una pazienza di 5 epoche e ripristina i pesi del miglior punto raggiunto. Il monitoraggio inizia dall'epoca 5 (`start_from_epoch=5`) e la baseline indicata è `0.8`.

Nel log salvato, l'esecuzione si interrompe all'epoca 11 e ripristina i pesi dell'epoca 6. Questo è il risultato di quella specifica esecuzione, non una garanzia per ogni nuovo training. Il modello viene salvato in `models/mobilenet-rps` tramite `float_model.save(MODEL)`.

## 1.8 Quantizzazione post-training per IMX500

Il passaggio successivo usa **Model Compression Toolkit (MCT)** per eseguire la *post-training quantization* (PTQ). La rete è già addestrata; non viene ripetuto il training con quantizzazione-aware training.

Il notebook crea un generatore di dati rappresentativi a partire da `train_ds`. `n_iter = 10` significa che il generatore esegue dieci iterazioni, ognuna delle quali fornisce il primo batch ottenuto da `dataset.take(1)`; con `BATCH_SIZE = 32`, ogni elemento fornito è normalmente un batch di immagini, non una singola immagine. MCT usa questi dati per stimare intervalli e parametri di quantizzazione.

La configurazione del target è `imx500`, versione piattaforma `v1`. La configurazione usa:

- errore di quantizzazione MSE per attivazioni e pesi;
- correzione dei bias dei pesi;
- correzione degli spostamenti negativi delle attivazioni;
- `z_threshold=16` per il trattamento dei valori anomali secondo la configurazione MCT.

`mct.ptq.keras_post_training_quantization(...)` produce il modello quantizzato e le informazioni di quantizzazione. `mct.exporter.keras_export_model(...)` lo esporta in:

```text
models/mobilenet-quant-rps.keras
```

La quantizzazione serve ad adattare il modello ai vincoli del target e può ridurre memoria e costi computazionali, ma la sua qualità va verificata confrontando prestazioni e comportamento del modello prima e dopo la quantizzazione.

## 1.9 Valutazione del modello

Il notebook valuta prima `float_model` e poi `quantized_model` sul dataset chiamato `validation_ds`. Nei risultati salvati, entrambe le valutazioni riportano `accuracy = 1.0000`; per il modello quantizzato il valore di loss riportato è circa `0.0148`.

Questi risultati **non dimostrano da soli una generalizzazione perfetta**: nel notebook corrente `validation_ds` viene caricato dalla cartella `test` e contiene solo 25 immagini secondo il log. Inoltre, quel set viene usato dall'early stopping. Prima di pubblicare o confrontare le metriche, occorre correggere la separazione tra `train`, `valid` e `test` e valutare il modello finale su immagini mai usate per scegliere i pesi.

## 1.10 Visualizzazione delle predizioni

Il notebook ricarica il dataset `test` e definisce alcune funzioni:

- `preprocess_image_visualization()`: ridimensiona e normalizza una singola immagine;
- `detect_objects()`: aggiunge la dimensione batch e chiama `model.predict()`;
- `get_top_prediction()`: trova l'indice del punteggio più alto e restituisce il nome della classe e il punteggio;
- `visualize_detection()`: visualizza l'immagine e sovrappone il nome della classe e il punteggio.

Il ciclo finale esamina al massimo quattro immagini, stampa la classe migliore e controlla che il punteggio sia maggiore di `0.55`. L'asserzione è solo un controllo sulle immagini visualizzate: non è una metrica di accuratezza e può interrompere il notebook se una predizione è meno sicura. Inoltre, il punteggio softmax più alto non va interpretato automaticamente come una probabilità ben calibrata.

**Importante per Birdgarden:** nonostante i nomi `detect_objects` e “Visualize detections”, qui non avviene object detection. Il modello assegna una classe all'intera immagine e non restituisce coordinate, maschere o bounding box. Per individuare l'uccello all'interno di una scena — ad esempio ritagliarlo prima di classificarlo — serve una fase di localizzazione separata oppure un modello di object detection addestrato con annotazioni appropriate.

## 1.11 Conversione per Raspberry Pi AI Camera

La cella finale esegue:

```bash
imxconv-tf -i models/mobilenet-quant-rps.keras -o converted
```

Il convertitore di Sony trasforma il modello quantizzato Keras in artefatti destinati alla pipeline IMX500. Il log salvato indica una conversione completata con successo e la presenza, in `converted/`, di file come:

```text
converted/
├── dnnParams.xml
├── mobilenet-quant-rps.pbtxt
├── mobilenet-quant-rps_MemoryReport.json
└── packerOut.zip
```

Il notebook controlla che `converted/packerOut.zip` esista. **Non completa però il packaging finale né installa il modello sulla fotocamera**: la sezione “Next step” rimanda alla procedura ufficiale Raspberry Pi per impacchettare il modello. Occorre conservare sia il modello quantizzato sia i file di conversione, in particolare `packerOut.zip`, e completare successivamente il packaging previsto dalla documentazione IMX500.

## 1.12 Artefatti prodotti

| Artefatto | Significato |
|---|---|
| `models/mobilenet-rps` | Modello addestrato prima della quantizzazione; il formato dipende dalla versione Keras/TensorFlow utilizzata. |
| `models/mobilenet-quant-rps.keras` | Modello quantizzato ed esportato in formato Keras. |
| `converted/dnnParams.xml` | Parametri relativi al modello convertito. |
| `converted/mobilenet-quant-rps.pbtxt` | Descrizione testuale del modello convertito. |
| `converted/mobilenet-quant-rps_MemoryReport.json` | Report relativo all'uso della memoria generato dal convertitore. |
| `converted/packerOut.zip` | Pacchetto generato dal convertitore, richiesto nel successivo processo di packaging IMX500. |

Per l'inferenza nell'applicazione finale va conservato anche l'ordine delle etichette (`class_names`) corrispondente agli indici in uscita dal modello. È opportuno esportarlo in un file di testo/JSON insieme al modello, così l'applicazione sulla Raspberry Pi potrà tradurre correttamente gli indici nelle specie.

## 1.13 Correzioni consigliate prima di considerare il notebook riproducibile

1. **Separare validazione e test:** usare `valid` per `validation_ds` e lasciare `test` per la valutazione finale indipendente.
2. **Ripulire i residui RPS:** aggiornare la descrizione iniziale, il riferimento al dataset Rock–Paper–Scissors, i nomi dei file modello e la stringa con il vecchio riepilogo a tre classi.
3. **Rinominare le funzioni di visualizzazione:** usare nomi come `predict_class()` e `visualize_classification()` per non confondere classificazione e object detection.
4. **Rendere meno fragile il controllo `score > 0.55`:** preferire un avviso di bassa confidenza invece di un'asserzione che arresta l'esecuzione.
5. **Salvare etichette e configurazione:** registrare l'ordine `class_names`, la versione del dataset, le versioni dei pacchetti e i parametri di training insieme agli artefatti.
6. **Persistenza dei file Colab:** copiare `models/` e `converted/` su Drive o scaricarli alla fine del processo.
7. **Dopo le correzioni, riavviare ed eseguire tutte le celle:** i risultati salvati nel notebook possono riflettere un'esecuzione precedente e non necessariamente il codice corrente.

## 1.14 Riferimenti

- Notebook Birdgarden: https://github.com/idamato/birdgarden/blob/main/notebooks/mobilenet-rps/custom_mobilenet.ipynb
- Documentazione Raspberry Pi AI Camera — conversione e packaging: https://www.raspberrypi.com/documentation/accessories/ai-camera.html
- Documentazione Sony IMX500 Converter: https://developer.aitrios.sony-semicon.com/en/raspberrypi-ai-camera/documentation/imx500-converter
- Model Compression Toolkit: https://github.com/sony/model_optimization

---

# 2. Documentation in English

## 2.1 Purpose and overall workflow

This notebook adapts Sony's tutorial for creating a custom model for the **Raspberry Pi AI Camera based on the Sony IMX500 sensor**. Its workflow is:

1. prepare the Python runtime and install dependencies;
2. mount Google Drive and locate the Birdgarden dataset;
3. load images arranged in class-specific directories;
4. resize and normalize the images, then augment the training set;
5. build a classifier based on a pretrained MobileNetV2;
6. train the classification head using transfer learning;
7. post-training-quantize the model for the IMX500 target with Model Compression Toolkit (MCT);
8. compare the original and quantized models;
9. visualize a few predictions;
10. convert the quantized model with `imxconv-tf` and check the generated files.

## 2.2 Runtime and dependencies

### Python version check

The first code cell checks `sys.version_info` and raises an error unless the runtime uses **Python 3.11**. The notebook is designed for Google Colab; the saved notebook metadata records a Colab runtime with a T4 GPU. A CPU-only machine can run parts of the workflow, but training may take longer and dependency compatibility must be checked.

### Installing packages

The notebook installs:

```bash
pip install 'tensorflow~=2.14.0' 'model-compression-toolkit~=2.2.0' 'imx500-converter[tf]'
```

These packages provide TensorFlow/Keras, MCT quantization tools, and the IMX500 converter, respectively. The notebook warns that the runtime may need to be restarted after installation so the newly installed libraries are loaded correctly.

The notebook also checks for **Java 17** and attempts to install `openjdk-17-jdk` if Java is missing or the detected version does not match. The IMX500 converter uses Java. The automatic installation assumes a Linux/Colab-like environment; a Windows host or a different container may require adapted system-package commands.

## 2.3 Imports, Google Drive and configuration variables

The notebook imports TensorFlow, NumPy and Keras. It also imports `tensorflow_datasets` as `tfds`, but that import is not used in the current workflow; it is a leftover from the original Rock–Paper–Scissors tutorial.

Google Drive is mounted at `/mnt/drive`. A helper cell searches the mounted directory for a folder named `Birdgarden` and prints the discovered path. Subsequent cells use:

```text
/mnt/drive/MyDrive/Birdgarden/
├── train/
├── valid/
└── test/
```

The main configuration variables are:

- `MODELS_DIR = 'models/'`: local directory for saved models;
- `MODEL = 'models/mobilenet-rps'`: path for the trained floating-point model;
- `MODEL_KERAS = 'models/mobilenet-quant-rps.keras'`: path for the exported quantized Keras model;
- `BATCH_SIZE = 32`: number of images per batch;
- `IMAGE_SHAPE = (224, 224)`: network input size.

The names `mobilenet-rps` and `mobilenet-quant-rps.keras` retain the RPS label from the original tutorial, even though the current classes are bird species. This is a naming leftover, not a model limitation.

**Persistence note:** `models/` and `converted/` are stored in the Colab runtime's local filesystem. Copy them to Drive or download them before the runtime is deleted.

## 2.4 Loading and organizing the dataset

`tf.keras.utils.image_dataset_from_directory()` reads images from subdirectories and infers labels from the directory names. With `label_mode='int'`, each class receives an integer label; `image_size=(224, 224)` standardizes image dimensions; `batch_size=32` groups samples into batches of 32.

The notebook defines:

```python
dataset_path = "/mnt/drive/MyDrive/Birdgarden"
train_path = f"{dataset_path}/train"
val_path = f"{dataset_path}/test"
```

The saved execution log reports **782 images in `train` and 25 images in the `test` directory, across five classes**. Keras reports the following class names in this order:

1. `ANDEAN SISKIN`
2. `AZARAS SPINETAIL`
3. `AZURE JAY`
4. `BANDED PITA`
5. `BARN OWL`

`class_names` stores the class order, while `num_classes = len(class_names)` determines the number of output units in the classifier.

### Issue to fix: `test` is used as the validation set

A `valid` directory exists on Drive, but `val_path` points to `test`. As a result, the 25 images in `test` are used to monitor `val_accuracy` and decide when training should stop; the same images are evaluated again and used for visualization. This is not an independent final test set.

If `valid` is intended to be the validation split, the recommended change is:

```python
val_path = f"{dataset_path}/valid"
test_path = f"{dataset_path}/test"
```

Use `valid` for early stopping and reserve `test` for the final evaluation, after all model choices have been made. Check the number of samples in each split before interpreting the metrics. After defining `preprocess_data()`, load and evaluate the test split separately, for example:

```python
test_path = f"{dataset_path}/test"
test_eval_ds = tf.keras.utils.image_dataset_from_directory(
    test_path, labels="inferred", label_mode="int",
    batch_size=BATCH_SIZE, image_size=IMAGE_SHAPE, shuffle=False
)
test_eval_ds = test_eval_ds.map(preprocess_data).prefetch(
    tf.data.experimental.AUTOTUNE
)

# Run after training and quantization are complete
float_model.evaluate(test_eval_ds)
quantized_model.evaluate(test_eval_ds)
```

Keep the visualization dataset separate from `test_eval_ds`, so converting samples into dictionaries that retain the original image does not interfere with numerical evaluation.

## 2.5 Preprocessing and data augmentation

`preprocess_data()`:

1. casts pixel values to `float32`;
2. applies `tf.keras.applications.mobilenet_v2.preprocess_input()`, which scales pixel values to the range expected by MobileNetV2 (approximately `-1` to `1` from an original `0`–`255` range);
3. resizes the image to `224 × 224`;
4. returns the `(image, label)` pair.

The dataset loader already requests the target size; the second resize makes the network's expected input shape explicit.

Data augmentation is applied **only** to the training dataset:

```python
tf.keras.layers.RandomFlip('horizontal')
tf.keras.layers.RandomRotation(0.2)
```

Images are randomly flipped horizontally and/or rotated. This encourages the classifier to be less dependent on image orientation and can reduce overfitting. Validation images are not augmented. `prefetch(AUTOTUNE)` allows TensorFlow to prepare upcoming batches in advance and improve input-pipeline efficiency.

## 2.6 Model creation: transfer learning with MobileNetV2

The base network is loaded as follows:

```python
MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
```

- `weights='imagenet'`: starts from weights pretrained on ImageNet;
- `include_top=False`: removes the original ImageNet classification head;
- `input_shape=(224, 224, 3)`: accepts 224 × 224 RGB images.

Two layers are added to the base network's output:

1. `GlobalAveragePooling2D`, which summarizes spatial feature maps into a vector;
2. `Dense(num_classes, activation=softmax)`, which returns one score for each of the five bird classes.

All MobileNetV2 base layers are marked `trainable = False`. Only the classification head is updated during training. This is transfer learning: features learned from ImageNet are reused instead of training the entire network from scratch.

The actual five-class model summary reports approximately **2,264,389 total parameters**, of which **6,405 are trainable** in the final head. The source also contains a multiline string with an old three-class model summary from the RPS tutorial; this is obsolete text and does not describe the current model, whose output size is set dynamically by `num_classes`.

## 2.7 Training and saving the floating-point model

The model is compiled with:

- the Adam optimizer;
- `SparseCategoricalCrossentropy`, which is suitable for integer class labels;
- the `accuracy` metric.

Training is limited to 20 epochs. The `EarlyStopping` callback monitors `val_accuracy`, requires an improvement of at least `0.01`, uses a patience of 5 epochs, and restores the best weights. Monitoring starts at epoch 5 (`start_from_epoch=5`), and the configured baseline is `0.8`.

In the saved log, training stops at epoch 11 and restores the weights from epoch 6. This describes that particular run, not a guaranteed result for future training. The model is saved to `models/mobilenet-rps` through `float_model.save(MODEL)`.

## 2.8 Post-training quantization for IMX500

The next stage uses **Model Compression Toolkit (MCT)** to perform *post-training quantization* (PTQ). The model has already been trained; the notebook does not perform quantization-aware training.

A representative-data generator is created from `train_ds`. `n_iter = 10` means that the generator runs ten iterations, each yielding the first batch produced by `dataset.take(1)`; with `BATCH_SIZE = 32`, each yielded item is normally a batch of images rather than one image. MCT uses these samples to estimate quantization ranges and parameters.

The target platform is configured as `imx500`, platform version `v1`. The quantization configuration uses:

- MSE as the quantization-error method for activations and weights;
- weight-bias correction;
- negative activation-shift correction;
- `z_threshold=16` for handling outliers according to the MCT configuration.

`mct.ptq.keras_post_training_quantization(...)` returns the quantized model and quantization information. `mct.exporter.keras_export_model(...)` exports the model to:

```text
models/mobilenet-quant-rps.keras
```

Quantization adapts the model to target constraints and can reduce memory and computational cost, but its quality should be checked by comparing the original and quantized models.

## 2.9 Model evaluation

The notebook evaluates `float_model` first and `quantized_model` second on the dataset named `validation_ds`. The saved outputs report `accuracy = 1.0000` for both; the quantized model's reported loss is approximately `0.0148`.

These results **do not by themselves prove perfect generalization**. In the current notebook, `validation_ds` is loaded from `test` and contains only 25 images according to the log. The same set is also used for early stopping. Before publishing or comparing metrics, separate `train`, `valid` and `test` correctly, then evaluate the final model on images that were not used to select the model weights.

## 2.10 Prediction visualization

The notebook reloads the `test` dataset and defines several helpers:

- `preprocess_image_visualization()`: resizes and normalizes one image;
- `detect_objects()`: adds a batch dimension and calls `model.predict()`;
- `get_top_prediction()`: finds the highest-scoring output index and returns the class name and score;
- `visualize_detection()`: displays the image with the predicted class and score overlaid.

The final loop processes up to four images, prints the top class and checks that its score exceeds `0.55`. This assertion is only a check on the displayed samples: it is not an accuracy metric, and it may stop the notebook if one prediction is less confident. A maximum softmax score should also not automatically be treated as a well-calibrated probability.

**Important for Birdgarden:** despite the names `detect_objects` and “Visualize detections”, this notebook does not perform object detection. It assigns a class to the entire image and returns no coordinates, masks or bounding boxes. To locate a bird inside a scene — for example, to crop it before classification — a separate localization step or an object-detection model trained with suitable annotations is required.

## 2.11 Conversion for the Raspberry Pi AI Camera

The final conversion cell runs:

```bash
imxconv-tf -i models/mobilenet-quant-rps.keras -o converted
```

Sony's converter transforms the quantized Keras model into artifacts for the IMX500 pipeline. The saved log reports successful conversion and the following files under `converted/`:

```text
converted/
├── dnnParams.xml
├── mobilenet-quant-rps.pbtxt
├── mobilenet-quant-rps_MemoryReport.json
└── packerOut.zip
```

The notebook checks that `converted/packerOut.zip` exists. **It does not complete final packaging or install the model on the camera**: the “Next step” section refers to Raspberry Pi's official procedure for packaging the model. Keep both the quantized model and the conversion output, especially `packerOut.zip`, and complete the documented IMX500 packaging workflow afterward.

## 2.12 Generated artifacts

| Artifact | Meaning |
|---|---|
| `models/mobilenet-rps` | Model trained before quantization; the exact saved format depends on the Keras/TensorFlow version. |
| `models/mobilenet-quant-rps.keras` | Quantized model exported in Keras format. |
| `converted/dnnParams.xml` | Parameters associated with the converted model. |
| `converted/mobilenet-quant-rps.pbtxt` | Text description of the converted model. |
| `converted/mobilenet-quant-rps_MemoryReport.json` | Memory-use report generated by the converter. |
| `converted/packerOut.zip` | Converter-generated package required by the next IMX500 packaging step. |

For inference in the final application, preserve the `class_names` order corresponding to the model's output indices. Export it as a text or JSON file alongside the model so that the Raspberry Pi application can map output indices back to species names correctly.

## 2.13 Recommended changes before treating the notebook as reproducible

1. **Separate validation and testing:** use `valid` for `validation_ds` and reserve `test` for final independent evaluation.
2. **Remove RPS leftovers:** update the introduction, the Rock–Paper–Scissors dataset reference, model filenames and the stale three-class summary string.
3. **Rename visualization functions:** names such as `predict_class()` and `visualize_classification()` avoid confusing image classification with object detection.
4. **Make the `score > 0.55` check less brittle:** report low confidence instead of using an assertion that stops execution.
5. **Save labels and configuration:** record the `class_names` order, dataset version, package versions and training parameters with the artifacts.
6. **Persist Colab files:** copy `models/` and `converted/` to Drive or download them before ending the session.
7. **Restart and run all cells after changes:** saved notebook outputs may come from an earlier execution and may not reflect the current source code.

## 2.14 References

- Birdgarden notebook: https://github.com/idamato/birdgarden/blob/main/notebooks/mobilenet-rps/custom_mobilenet.ipynb
- Raspberry Pi AI Camera documentation — conversion and packaging: https://www.raspberrypi.com/documentation/accessories/ai-camera.html
- Sony IMX500 Converter documentation: https://developer.aitrios.sony-semicon.com/en/raspberrypi-ai-camera/documentation/imx500-converter
- Model Compression Toolkit: https://github.com/sony/model_optimization
