(milvus)=
# Milvus

One can use [Milvus](https://milvus.io/) as the Document store for DocumentArray. It is useful when one wants to have faster Document retrieval on embeddings, i.e. `.match()`, `.find()`.

````{tip}
This feature requires `pymilvus`. You can install it via `pip install "docarray[milvus]".` 
````

## Usage

### Start Milvus service

To use Milvus as the storage backend, you need a running Milvus server. You can use the following `docker-compose.yml`
to start a Milvus server:

`````{dropdown} docker-compose.yml

```yaml
version: '3.5'

services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.0
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2022-03-17T06-34-49Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/minio:/minio_data
    command: minio server /minio_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  standalone:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.1.4
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"

networks:
  default:
    name: milvus
```

`````

Then

```bash
docker-compose up
```

You can find more installation guidance in the [Milvus documentation](https://milvus.io/docs/v2.1.x/install_standalone-docker.md).

### Create DocumentArray with Milvus backend

Assuming service is started using the default configuration (i.e. the server's gRPC address `http://localhost:19530`), you can 
instantiate a DocumentArray with Milvus storage like so:

```python
from docarray import DocumentArray

da = DocumentArray(storage='milvus', config={'n_dim': 10})
```

Here, `config` is configuration for the created Milvus collection,
and `n_dim` is a mandatory field that specified the dimensionality of stored embeddings.
You can find a complete specification of the Milvus `config` {ref}`here <milvus-config>`.

To access a previously persisted DocumentArray, you can specify the `collection_name`, the `host`  and the `port`. 


```python
from docarray import DocumentArray

da = DocumentArray(
    storage='milvus',
    config={
        'collection_name': 'persisted',
        'host': 'localhost',
        'port': '19530',
        'n_dim': 10,
    },
)

da.summary()
```

(milvus-config)=
## Config

The following configs can be set:

| Name                | Description                                                                                                                                                                                                                                   | Default                                              |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|
| `n_dim`             | Number of dimensions of embeddings to be stored and retrieved                                                                                                                                                                                 | **This is always required**                          |
| `collection_name`   | Qdrant collection name client                                                                                                                                                                                                                 | **Random collection name generated**                 |
| `host`              | Hostname of the Milvus server                                                                                                                                                                                                                 | 'localhost'                                          |
| `port`              | port of the Milvus server                                                                                                                                                                                                                     | 6333                                                 |
| `distance`          | Distance metric to be used during search. Can be 'IP', 'L2', 'JACCARD', 'TANIMOTO', 'HAMMING', 'SUPERSTRUCTURE' or 'SUBSTRUCTURE'.                                                                                                            | 'IP' (inner product)                                 |
| `index_type`        | Type of the (ANN) search index. Can be 'HNSW', 'FLAT', 'ANNOY', or one of multiple variants of IVF and RHNSW. A full list of supported index types can be found [here](https://milvus.io/docs/v2.1.x/build_index.md#Prepare-index-parameter). | 'HNSW                                                |
| `index_params`      | A dictionary of parameters used for index building. The allowed parameters depend on the index type, and can be found [here](https://milvus.io/docs/v2.1.x/index.md).                                                                         | {'M': 4, 'efConstruction': 200} (assumes HNSW index) |
| `collection_config` | Configuration for the Milvus collection. Passed as **kwargs during collection creation (`Collection(...)`).                                                                                                                                   | {}                                                   |
| `serialize_config`  | [Serialization config of each Document](../../../fundamentals/document/serialization.md)                                                                                                                                                      | {}                                                   |
 | `consistency_level` | [Consistency level](https://milvus.io/docs/v2.1.x/consistency.md#Consistency-levels) for Milvus database operations. Can be 'Session', 'Strong', 'Bounded' or 'Eventually'.                                                                   | 'Session'                                            |
| `columns`           | Additional columns to be stored in the datbase, taken from Document `tags`.                                                                                                                                                                   | None                                                 |

## Minimal example

Create `docker-compose.yml`:

`````{dropdown} docker-compose.yml

```yaml
version: '3.5'

services:
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.0
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2022-03-17T06-34-49Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/minio:/minio_data
    command: minio server /minio_data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  standalone:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.1.4
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"

networks:
  default:
    name: milvus
```

`````

Install DocArray with Milvus and launch the Milvus server:


```bash
pip install -U docarray[milvus]
docker-compose up
```

Create a DocumentArray with some random data:

```python
import numpy as np

from docarray import DocumentArray

N, D = 5, 128

da = DocumentArray.empty(
    N, storage='milvus', config={'n_dim': D, 'distance': 'IP'}
)  # init
with da:
    da.embeddings = np.random.random([N, D])
```

Perform an approximate nearest neighbor search:

```
print(da.find(np.random.random(D), limit=10))
```
Output:

```bash
<DocumentArray (length=10) at 4917906896>
```

(milvus-filter)=
## Vector search with filter

Search with `.find` can be restricted by user-defined filters.

Such filters can be constructed using the [filter expression language defined by Milvus](https://milvus.io/docs/v2.1.x/boolean.md).
Filters operate on the `tags` of a Document, which are stored as `columns` in the Milvus database.


### Example of `.find` with filtered vector search


Consider Documents with embeddings `[0,0,0]` up to ` [9,9,9]` where the Document with embedding `[i,i,i]`
has as tag `price` with value `i`. We can create such example with the following code:

```python
from docarray import Document, DocumentArray
import numpy as np

n_dim = 3
distance = 'L2'

da = DocumentArray(
    storage='milvus',
    config={'n_dim': n_dim, 'columns': {'price': 'float'}, 'distance': distance},
)

print(f'\nDocumentArray distance: {distance}')

with da:
    da.extend(
        [
            Document(id=f'r{i}', embedding=i * np.ones(n_dim), tags={'price': i})
            for i in range(10)
        ]
    )

print('\nIndexed Prices:\n')
for embedding, price in zip(da.embeddings, da[:, 'tags__price']):
    print(f'\tembedding={embedding},\t price={price}')
```

Consider we want the nearest vectors to the embedding `[8. 8. 8.]`, with the restriction that
prices must follow a filter. As an example, retrieved Documents must have `price` value lower than
or equal to `max_price`. We can encode this information in Milvus using `filter = f'price <= {max_price}'`.

Then you can implement and use the search with the proposed filter:

```python
max_price = 7
n_limit = 4

np_query = np.ones(n_dim) * 8
print(f'\nQuery vector: \t{np_query}')

filter = f'price <= {max_price}'
results = da.find(np_query, filter=filter, limit=n_limit)

print('\nEmbeddings Nearest Neighbours with "price" at most 7:\n')
for embedding, price in zip(results.embeddings, results[:, 'tags__price']):
    print(f'\tembedding={embedding},\t price={price}')
```

This will print:

```
Query vector: 	[8. 8. 8.]

Embeddings Nearest Neighbours with "price" at most 7:

	embedding=[7. 7. 7.],	 price=7
	embedding=[6. 6. 6.],	 price=6
	embedding=[5. 5. 5.],	 price=5
	embedding=[4. 4. 4.],	 price=4
```
### Example of `.find` with only a filter

The following example shows how to use DocArray with Milvus Document Store in order to filter text documents.
Consider Documents have the tag `price` with a value of `i`. We can create these with the following code:

```python
from docarray import Document, DocumentArray
import numpy as np

n_dim = 3

da = DocumentArray(
    storage='milvus',
    config={'n_dim': n_dim, 'columns': {'price': 'float'}},
)

with da:
    da.extend(
        [
            Document(id=f'r{i}', embedding=i * np.ones(n_dim), tags={'price': i})
            for i in range(10)
        ]
    )

print('\nIndexed Prices:\n')
for embedding, price in zip(da.embeddings, da[:, 'tags__price']):
    print(f'\tembedding={embedding},\t price={price}')
```

Suppose you want to filter results such that
retrieved Documents must have a `price` value less than or equal to `max_price`. You can encode 
this information in Milvus using `filter = f'price <= {max_price}'`.

Then you can implement and use the search with the proposed filter:
```python
max_price = 7
n_limit = 4

filter = f'price <= {max_price}'
results = da.find(filter=filter, limit=n_limit)

print('\nPoints with "price" at most 7:\n')
for embedding, price in zip(results.embeddings, results[:, 'tags__price']):
    print(f'\tembedding={embedding},\t price={price}')
```
This prints:

```

Points with "price" at most 7:

	embedding=[6. 6. 6.],	 price=6
	embedding=[7. 7. 7.],	 price=7
	embedding=[1. 1. 1.],	 price=1
	embedding=[2. 2. 2.],	 price=2
```

(milvus-limitations)=
## Known limitations of the Milvus Document Store

The Milvus Document Store implements the entire DocumentArray API, but there are some limitations that you should be aware of.

(milvus-collection-loading)=
### Collection loading

In Milvus, every search or query operation requires the index to be loaded into memory.
This includes simple Document access through DocArray, 

This loading operation can be costly, especially when performing multiple search or query operations in a row.

To mitigate this, you should use the `with da:` context manager whenever you perform multiple reads, searches or queries
on a Milvus DocumentArray.
This context manager loads the index into memory only once, and releases it when the context is exited.

```python
from docarray import Document, DocumentArray
import numpy as np

da = DocumentArray(
    [Document(id=f'r{i}', embedding=i * np.ones(3)) for i in range(10)],
    storage='milvus',
    config={'n_dim': 3},
)

with da:
    # index is loaded into memory
    for d in da:
        pass
# index is released from memory

with da:
    # index is loaded into memory
    embs, texts = da.embeddings, da.texts
# index is released from memory
```

Not using the `with da:` context manager will return the same results for the same operations, but will incur significant performance penalties:

````{dropdown} ⚠️ Bad code

```python
from docarray import Document, DocumentArray
import numpy as np

da = DocumentArray(
    [Document(id=f'r{i}', embedding=i * np.ones(3)) for i in range(10)],
    storage='milvus',
    config={'n_dim': 3},
)

for d in da:  # index is loaded and released at every iteration
    pass

embs, texts = (
    da.embeddings,
    da.texts,
)  # index is loaded and released for every Document in `da`
```

````

### Storing large tensors outside of `embedding` field

It is currently not possible to persist Documents with a large `.tensor` field.

A suitable workaround for this is to remove a Document's tensor after computing its embedding and before adding it to the
Document Store:

```python
from docarray import Document, DocumentArray

da = DocumentArray(storage='milvus', config={'n_dim': 128})

doc = Document(tensor=np.random.rand(224, 224))
doc.embed(...)
doc.tensor = None

da.append(doc)
```

````{dropdown} Why does this limitation exist?
By default, DocArray stores three columns in any Document Store: The Document id's, the Document embeddings and
a serialized (Base64 encoded) representation of the Document itself.

In Milvus, the the serialized Document are stored in a column of type 'VARCHAR', which imposes a limit of allowed length
per entry.
If the Base64 encoded Document exceeds this limit - which is usually the case for Documents with large tensors - the
Document cannot be stored.

The Milvus team is currently working on a 'STRING' columm type that could solve this issue in the future.
````

